# Dokumentasi Teknis Sistem E-Voting RSA SHA-256

## 1. Ringkasan Sistem

Sistem ini adalah prototype e-voting akademik berbasis web. Aplikasi dibangun dengan FastAPI, Jinja2, SQLAlchemy, Alembic, PostgreSQL, dan library `cryptography`.

Tujuan teknis sistem adalah menyediakan alur pemilihan satu kali untuk setiap voter, menyimpan suara dalam bentuk terenkripsi, lalu melakukan rekapitulasi dengan proses verifikasi integritas dan autentikasi data.

Secara kriptografi, sistem memakai:

- RSA-2048 OAEP untuk enkripsi plaintext suara.
- SHA-256 untuk menghitung hash ciphertext.
- RSA-2048 PSS untuk digital signature atas hash ciphertext.
- PostgreSQL untuk menyimpan voter, kandidat, vote record, audit log, dan benchmark.
- Session cookie Starlette/FastAPI untuk menyimpan status login voter dan admin.

Pipeline utama voting:

```text
voter memilih kandidat
-> sistem membuat plaintext suara
-> plaintext dienkripsi dengan public key admin memakai RSA-OAEP
-> ciphertext di-hash memakai SHA-256
-> hash ditandatangani dengan private key system memakai RSA-PSS
-> ciphertext, hash, signature, voter_id disimpan ke database
-> voter ditandai sudah memilih
```

Pipeline rekapitulasi:

```text
admin menjalankan rekapitulasi
-> sistem membaca semua vote record
-> signature diverifikasi memakai public key system
-> hash ciphertext dihitung ulang dan dibandingkan
-> ciphertext didekripsi memakai private key admin
-> plaintext di-parse menjadi voter_id, candidate_id, timestamp
-> candidate_id divalidasi
-> suara valid dihitung
-> vote invalid diberi status dan dicatat ke audit log
```

## 2. Tech Stack

### 2.1 Backend

- FastAPI sebagai framework HTTP.
- Uvicorn sebagai ASGI server.
- Jinja2 sebagai template engine HTML.
- Starlette SessionMiddleware untuk session berbasis cookie.
- SQLAlchemy 2.x sebagai ORM.
- Alembic sebagai migration tool.
- PostgreSQL sebagai database utama.

### 2.2 Kriptografi

- `cryptography.hazmat.primitives.asymmetric.rsa` untuk RSA key generation.
- RSA-OAEP dengan MGF1 SHA-256 untuk enkripsi dan dekripsi vote.
- SHA-256 untuk hashing ciphertext.
- RSA-PSS dengan MGF1 SHA-256 dan salt maksimum untuk signature.

### 2.3 Testing dan Operasional

- Pytest untuk unit test.
- Dockerfile untuk image aplikasi.
- Docker Compose untuk environment lokal dan production.
- Script Python untuk generate key, seed data, benchmark, dan manipulasi data demo.

## 3. Struktur Folder

```text
.
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   |-- main.py
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- enums.py
|   |   |-- exceptions.py
|   |   `-- plaintext.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- audit_log.py
|   |   |-- benchmark_record.py
|   |   |-- candidate.py
|   |   |-- vote_record.py
|   |   `-- voter.py
|   |-- repositories/
|   |   |-- __init__.py
|   |   |-- audit_log_repository.py
|   |   |-- benchmark_repository.py
|   |   |-- candidate_repository.py
|   |   |-- vote_repository.py
|   |   `-- voter_repository.py
|   |-- routers/
|   |   |-- __init__.py
|   |   |-- admin_router.py
|   |   |-- auth_router.py
|   |   `-- voter_router.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   `-- results.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- auth_service.py
|   |   |-- benchmark_service.py
|   |   |-- crypto_service.py
|   |   |-- factory.py
|   |   |-- recapitulation_service.py
|   |   `-- voting_service.py
|   |-- static/
|   |   `-- styles.css
|   `-- templates/
|       |-- admin_dashboard.html
|       |-- admin_login.html
|       |-- audit_logs.html
|       |-- base.html
|       |-- benchmark.html
|       |-- login.html
|       |-- recap_result.html
|       |-- vote.html
|       `-- vote_success.html
|-- alembic/
|   |-- env.py
|   |-- script.py.mako
|   `-- versions/
|       `-- 20260522_0001_initial.py
|-- scripts/
|   |-- docker-entrypoint.sh
|   |-- generate_keys.py
|   |-- manipulate_vote.py
|   |-- run_benchmark.py
|   `-- seed_data.py
|-- tests/
|   |-- test_crypto_service.py
|   |-- test_plaintext.py
|   `-- test_service_logic.py
|-- .env.example
|-- .env.production.example
|-- alembic.ini
|-- docker-compose.yml
|-- docker-compose.prod.yml
|-- Dockerfile
|-- planning.md
|-- README.md
`-- requirements.txt
```

## 4. Peran Setiap Folder

### 4.1 `app/`

Folder utama aplikasi Python. Semua kode runtime FastAPI berada di folder ini.

### 4.2 `app/domain/`

Berisi konsep domain murni yang tidak bergantung langsung pada HTTP atau database.

Isinya:

- Enum status verifikasi vote.
- Enum tipe audit event.
- Exception domain.
- Builder dan parser plaintext suara.

### 4.3 `app/models/`

Berisi SQLAlchemy ORM model. Setiap file merepresentasikan tabel database.

Model utama:

- `Voter`
- `Candidate`
- `VoteRecord`
- `AuditLog`
- `BenchmarkRecord`

### 4.4 `app/repositories/`

Lapisan akses data. Repository membungkus query SQLAlchemy agar service tidak langsung menulis query database.

Repository utama:

- `VoterRepository`
- `CandidateRepository`
- `VoteRepository`
- `AuditLogRepository`
- `BenchmarkRepository`

### 4.5 `app/services/`

Lapisan use case dan business logic.

Service utama:

- `AuthService`
- `CryptoService`
- `VotingService`
- `RecapitulationService`
- `BenchmarkService`
- Factory service untuk wiring dependency.

### 4.6 `app/routers/`

Lapisan HTTP endpoint FastAPI. Router menerima request, membaca form/session, memanggil service/repository, lalu merender template atau redirect.

Router utama:

- `auth_router.py`
- `voter_router.py`
- `admin_router.py`

### 4.7 `app/schemas/`

Berisi dataclass result object untuk response internal service.

### 4.8 `app/templates/`

Berisi template Jinja2 untuk halaman web.

### 4.9 `app/static/`

Berisi asset statis. Saat ini hanya `styles.css`.

### 4.10 `alembic/`

Berisi konfigurasi migration database dan revision schema awal.

### 4.11 `scripts/`

Berisi script operasional:

- Generate RSA key.
- Seed data demo.
- Benchmark operasi kripto.
- Manipulasi vote untuk demo deteksi integritas.
- Entrypoint Docker.

### 4.12 `tests/`

Berisi unit test untuk domain plaintext, service kripto, dan logic voting/rekapitulasi.

## 5. Entry Point Aplikasi

File entry point utama adalah `app/main.py`.

```python
app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(voter_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
```

Penjelasan:

- Membuat instance FastAPI dengan judul dari konfigurasi.
- Menambahkan `SessionMiddleware` agar aplikasi dapat memakai `request.session`.
- Mount folder static di URL `/static`.
- Mendaftarkan router voter, auth, dan admin.

Saat Docker berjalan, command default menjalankan:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Artinya Uvicorn mencari objek `app` di module `app.main`.

## 6. Konfigurasi Sistem

Konfigurasi berada di `app/config.py`.

### 6.1 Class `Settings`

`Settings` adalah dataclass frozen yang membaca environment variable.

Field:

- `app_name`: nama aplikasi, default `E-Voting RSA SHA-256`.
- `app_secret_key`: secret untuk session cookie.
- `database_url`: SQLAlchemy database URL.
- `admin_username`: username admin.
- `admin_password`: password admin.
- `admin_private_key_path`: path private key admin.
- `admin_public_key_path`: path public key admin.
- `system_private_key_path`: path private key system.
- `system_public_key_path`: path public key system.
- `enable_dev_routes`: flag boolean dari env `ENABLE_DEV_ROUTES`.

Instansiasi:

```python
settings = Settings()
```

Semua module lain mengimpor `settings` ini untuk membaca konfigurasi.

### 6.2 File Environment

`.env.example` digunakan untuk development lokal dengan service PostgreSQL dari Docker Compose.

`.env.production.example` digunakan untuk production:

- Password database lebih kuat.
- Key RSA diarahkan ke `/data/keys`.
- `ENABLE_DEV_ROUTES=false`.
- Docker volume `rsa_keys` dipakai agar key tidak hilang saat container dibuat ulang.

## 7. Database dan Session

File `app/database.py` menyiapkan koneksi database.

### 7.1 Class `Base`

```python
class Base(DeclarativeBase):
    pass
```

`Base` adalah base class SQLAlchemy Declarative. Semua model ORM mewarisi class ini.

### 7.2 `engine`

```python
engine = create_engine(settings.database_url, pool_pre_ping=True)
```

Engine memakai `settings.database_url`. Opsi `pool_pre_ping=True` membuat SQLAlchemy mengecek koneksi sebelum dipakai, sehingga koneksi mati di pool dapat dideteksi lebih awal.

### 7.3 `SessionLocal`

```python
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
```

Konfigurasi session:

- `autoflush=False`: perubahan tidak otomatis di-flush sebelum query kecuali diperlukan secara eksplisit.
- `autocommit=False`: transaksi harus di-commit manual.
- `expire_on_commit=False`: objek ORM tidak otomatis expired setelah commit.

### 7.4 Fungsi `get_db`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Fungsi ini adalah dependency FastAPI. Setiap request yang membutuhkan database akan mendapat satu `Session`. Setelah request selesai, session ditutup.

## 8. Model Database

### 8.1 Model `Voter`

File: `app/models/voter.py`

Tabel: `voters`

Kolom:

- `id`: UUID string sebagai primary key internal.
- `voter_id`: ID pemilih yang dipakai login, unique dan indexed.
- `full_name`: nama lengkap voter.
- `password_hash`: hash password voter.
- `has_voted`: boolean untuk mencegah double vote.
- `created_at`: timestamp pembuatan.
- `updated_at`: timestamp update.

Catatan teknis:

- `voter_id` unique memastikan satu voter hanya memiliki satu record.
- `has_voted` dipakai oleh `VotingService.cast_vote` sebelum membuat vote record.

### 8.2 Model `Candidate`

File: `app/models/candidate.py`

Tabel: `candidates`

Kolom:

- `id`: integer primary key kandidat.
- `name`: nama kandidat.
- `description`: deskripsi kandidat.
- `created_at`: timestamp pembuatan.

Candidate digunakan saat halaman vote ditampilkan dan saat rekapitulasi memvalidasi `candidate_id`.

### 8.3 Model `VoteRecord`

File: `app/models/vote_record.py`

Tabel: `vote_records`

Kolom:

- `id`: UUID string sebagai primary key vote.
- `voter_id`: ID voter, unique dan indexed.
- `ciphertext`: hasil enkripsi plaintext suara, tipe `LargeBinary`.
- `ciphertext_hash`: hash SHA-256 dari ciphertext dalam hex 64 karakter.
- `signature`: RSA-PSS signature atas hash ciphertext, tipe `LargeBinary`.
- `verification_status`: status hasil rekapitulasi.
- `manipulation_reason`: alasan invalid jika vote terdeteksi bermasalah.
- `created_at`: timestamp vote dibuat.

Catatan teknis:

- `voter_id` unique di `vote_records` memberi lapisan proteksi database terhadap vote ganda.
- Sistem tidak menyimpan plaintext suara.
- Candidate yang dipilih hanya dapat diketahui setelah dekripsi saat rekapitulasi.

### 8.4 Model `AuditLog`

File: `app/models/audit_log.py`

Tabel: `audit_logs`

Kolom:

- `id`: UUID string primary key.
- `event_type`: tipe event.
- `entity_type`: tipe entitas yang terkait, misalnya `vote_record` atau `voter`.
- `entity_id`: ID entitas terkait jika ada.
- `message`: pesan audit.
- `created_at`: timestamp event.

Audit log mencatat kejadian penting seperti vote berhasil, double vote attempt, signature invalid, hash mismatch, dan rekapitulasi.

### 8.5 Model `BenchmarkRecord`

File: `app/models/benchmark_record.py`

Tabel: `benchmark_records`

Kolom:

- `id`: UUID string primary key.
- `operation_name`: nama operasi kripto yang diukur.
- `duration_ms`: durasi dalam milidetik.
- `sample_size`: jumlah sampel.
- `metadata_json`: metadata tambahan bertipe JSONB.
- `created_at`: timestamp benchmark.

Model ini dipakai oleh `scripts/run_benchmark.py` dan halaman admin benchmarks.

### 8.6 `app/models/__init__.py`

File ini mengekspor model:

```python
__all__ = ["AuditLog", "BenchmarkRecord", "Candidate", "VoteRecord", "Voter"]
```

Tujuannya agar script atau Alembic dapat mengimpor model dari `app.models` dengan ringkas.

## 9. Migration Database

### 9.1 `alembic/env.py`

File ini menghubungkan Alembic dengan konfigurasi aplikasi.

Bagian penting:

```python
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

Artinya Alembic memakai database URL dari `settings` dan metadata model dari SQLAlchemy `Base`.

### 9.2 Fungsi `run_migrations_offline`

Menjalankan migration tanpa membuka koneksi live. Alembic hanya memakai URL dan menghasilkan SQL atau menjalankan mode offline sesuai konteks.

### 9.3 Fungsi `run_migrations_online`

Membuat engine dari konfigurasi Alembic, membuka koneksi database, lalu menjalankan migration dalam transaksi.

### 9.4 Revision `20260522_0001_initial.py`

Migration awal membuat tabel:

- `voters`
- `candidates`
- `vote_records`
- `audit_logs`
- `benchmark_records`

Fungsi `upgrade` membuat schema. Fungsi `downgrade` menghapus schema dengan urutan kebalikan agar index dan tabel tidak bentrok.

## 10. Domain Layer

### 10.1 `VerificationStatus`

File: `app/domain/enums.py`

Enum status verifikasi vote:

- `PENDING`: vote baru dibuat dan belum direkapitulasi.
- `VALID`: vote lolos signature verification, hash check, decryption, parse plaintext, dan validasi kandidat.
- `INVALID_SIGNATURE`: signature RSA-PSS tidak valid.
- `HASH_MISMATCH`: hash ciphertext tidak sesuai dengan hash yang disimpan.
- `DECRYPTION_FAILED`: dekripsi RSA-OAEP gagal.
- `MALFORMED_PLAINTEXT`: plaintext hasil dekripsi tidak valid atau kandidat tidak dikenal.

### 10.2 `AuditEventType`

File: `app/domain/enums.py`

Enum tipe audit:

- `VOTE_CAST`: vote berhasil dicatat.
- `DOUBLE_VOTE_ATTEMPT`: voter mencoba memilih lebih dari satu kali.
- `INVALID_SIGNATURE_DETECTED`: signature invalid terdeteksi saat rekapitulasi.
- `HASH_MISMATCH_DETECTED`: hash mismatch terdeteksi saat rekapitulasi.
- `DECRYPTION_FAILED`: dekripsi gagal saat rekapitulasi.
- `MALFORMED_PLAINTEXT`: plaintext tidak sesuai format.
- `RECAPITULATION_STARTED`: rekapitulasi dimulai.
- `RECAPITULATION_COMPLETED`: rekapitulasi selesai.

### 10.3 Exception Domain

File: `app/domain/exceptions.py`

Exception:

- `VoterNotFoundError`: voter_id tidak ditemukan.
- `VoterAlreadyVotedError`: voter sudah memiliki `has_voted=True`.
- `CandidateNotFoundError`: candidate_id tidak ada di database.
- `InvalidSignatureError`: tersedia untuk kasus signature invalid, meskipun saat ini service memakai boolean dari `verify_signature`.
- `HashMismatchError`: tersedia untuk kasus hash mismatch.
- `VoteDecryptionError`: tersedia untuk kasus dekripsi gagal.
- `MalformedVotePlaintextError`: plaintext vote tidak sesuai format.

Exception ini membuat error domain eksplisit dan mudah dibedakan dari error teknis lain.

### 10.4 Dataclass `ParsedVotePlaintext`

File: `app/domain/plaintext.py`

Field:

- `voter_id`
- `candidate_id`
- `timestamp`

Dataclass ini adalah hasil parsing plaintext suara.

### 10.5 Fungsi `build_vote_plaintext`

Signature:

```python
def build_vote_plaintext(voter_id: str, candidate_id: int, timestamp: str) -> str:
```

Fungsi ini membuat string plaintext suara dengan format:

```text
voter_id:{voter_id}|candidate_id:{candidate_id}|timestamp:{timestamp}
```

Contoh:

```text
voter_id:VOTER001|candidate_id:2|timestamp:2026-05-22T14:30:00+07:00
```

Plaintext ini kemudian dienkripsi oleh `CryptoService.encrypt_vote_plaintext`.

### 10.6 Fungsi `parse_vote_plaintext`

Signature:

```python
def parse_vote_plaintext(plaintext: str) -> ParsedVotePlaintext:
```

Alur validasi:

1. Split string berdasarkan `|`.
2. Pastikan ada tepat 3 segment.
3. Pastikan setiap segment memakai format `key:value`.
4. Ambil `voter_id`, `candidate_id`, dan `timestamp`.
5. Pastikan semua field wajib ada.
6. Convert `candidate_id` menjadi integer.
7. Validasi `timestamp` memakai `datetime.fromisoformat`.
8. Return `ParsedVotePlaintext`.

Jika format salah, fungsi melempar `MalformedVotePlaintextError`.

## 11. Schema Result

File: `app/schemas/results.py`

Schema ini memakai `dataclass(frozen=True)`, sehingga object result bersifat immutable setelah dibuat.

### 11.1 `VoteCastResult`

Field:

- `voter_id`
- `candidate_id`
- `vote_record_id`

Dipakai sebagai return value `VotingService.cast_vote`.

### 11.2 `CandidateVoteResult`

Field:

- `candidate_id`
- `candidate_name`
- `vote_count`

Dipakai untuk hasil akhir rekapitulasi per kandidat.

### 11.3 `InvalidVoteDetail`

Field:

- `vote_id`
- `voter_id`
- `status`
- `reason`

Dipakai untuk menampilkan detail vote invalid pada halaman hasil rekapitulasi.

### 11.4 `RecapitulationResult`

Field:

- `total_votes`
- `valid_votes`
- `invalid_votes`
- `candidate_results`
- `invalid_vote_details`

Dipakai sebagai return value `RecapitulationService.recapitulate_votes`.

### 11.5 `BenchmarkResult`

Field:

- `operation_name`
- `duration_ms`

Dipakai sebagai return value `BenchmarkService.measure_operation`.

## 12. Repository Layer

Repository adalah adapter database. Service memakai repository agar logic bisnis tidak tergantung langsung ke query SQLAlchemy.

### 12.1 `VoterRepository`

File: `app/repositories/voter_repository.py`

#### `__init__(self, db: Session)`

Menyimpan SQLAlchemy session ke `self.db`.

#### `find_by_voter_id(self, voter_id: str) -> Voter | None`

Mencari voter berdasarkan kolom `voter_id`.

Query:

```python
select(Voter).where(Voter.voter_id == voter_id)
```

Return:

- Object `Voter` jika ditemukan.
- `None` jika tidak ditemukan.

#### `mark_as_voted(self, voter_id: str) -> None`

Mencari voter berdasarkan `voter_id`. Jika ditemukan:

- Set `has_voted=True`.
- Tambahkan object voter ke session dengan `self.db.add(voter)`.

Commit tidak dilakukan di repository. Commit dilakukan oleh router setelah service selesai.

#### `count_all(self) -> int`

Menghitung semua voter dengan mengambil semua row lalu memakai `len`.

Catatan teknis:

- Untuk data besar, query `COUNT(*)` lebih efisien dibanding `len(select all)`.
- Untuk prototype, implementasi ini masih cukup sederhana.

### 12.2 `CandidateRepository`

File: `app/repositories/candidate_repository.py`

#### `__init__(self, db: Session)`

Menyimpan session database.

#### `find_by_id(self, candidate_id: int) -> Candidate | None`

Mengambil kandidat berdasarkan primary key memakai `self.db.get(Candidate, candidate_id)`.

#### `find_all(self) -> list[Candidate]`

Mengambil semua kandidat dan mengurutkan berdasarkan `Candidate.id`.

#### `count_all(self) -> int`

Menghitung jumlah kandidat dengan `len(self.find_all())`.

### 12.3 `VoteRepository`

File: `app/repositories/vote_repository.py`

#### `__init__(self, db: Session)`

Menyimpan session database.

#### `create_vote_record(self, voter_id: str, ciphertext: bytes, ciphertext_hash: str, signature: bytes) -> VoteRecord`

Membuat object `VoteRecord` baru.

Field yang diisi:

- `voter_id`
- `ciphertext`
- `ciphertext_hash`
- `signature`

Status default berasal dari model, yaitu `PENDING`.

Object ditambahkan ke session, lalu dikembalikan. Commit tetap dilakukan di router.

#### `find_all_votes(self) -> list[VoteRecord]`

Mengambil semua vote record dan mengurutkan berdasarkan `created_at`.

Dipakai saat rekapitulasi.

#### `find_by_id(self, vote_id: str) -> VoteRecord | None`

Mengambil vote berdasarkan primary key.

#### `count_all(self) -> int`

Menghitung semua vote record memakai `len(self.find_all_votes())`.

#### `update_verification_status(self, vote_id: str, status: VerificationStatus, reason: str | None = None) -> None`

Mencari vote berdasarkan ID. Jika ditemukan:

- Set `verification_status` ke `status.value`.
- Set `manipulation_reason` ke `reason`.
- Tambahkan vote ke session.

Dipakai oleh `RecapitulationService` untuk menandai vote valid maupun invalid.

### 12.4 `AuditLogRepository`

File: `app/repositories/audit_log_repository.py`

#### `__init__(self, db: Session)`

Menyimpan session database.

#### `create_log(self, event_type: str, entity_type: str, entity_id: str | None, message: str) -> AuditLog`

Membuat log audit baru.

Parameter:

- `event_type`: tipe event dari `AuditEventType`.
- `entity_type`: tipe entitas yang terkait.
- `entity_id`: ID entitas terkait, opsional.
- `message`: detail event.

Object `AuditLog` ditambahkan ke session dan dikembalikan.

#### `find_all(self) -> list[AuditLog]`

Mengambil semua audit log, diurutkan dari yang paling baru berdasarkan `created_at.desc()`.

#### `count_all(self) -> int`

Menghitung semua audit log memakai `len(self.find_all())`.

### 12.5 `BenchmarkRepository`

File: `app/repositories/benchmark_repository.py`

#### `__init__(self, db: Session)`

Menyimpan session database.

#### `create_record(self, operation_name: str, duration_ms: float, sample_size: int | None = None, metadata_json: dict | None = None) -> BenchmarkRecord`

Membuat record benchmark.

Field:

- `operation_name`
- `duration_ms`
- `sample_size`
- `metadata_json`

Object ditambahkan ke session dan dikembalikan.

#### `find_all(self) -> list[BenchmarkRecord]`

Mengambil semua benchmark record dari database, diurutkan dari yang paling baru.

## 13. Service Layer

Service adalah pusat business logic.

## 13.1 `AuthService`

File: `app/services/auth_service.py`

### Fungsi `hash_password`

Signature:

```python
def hash_password(password: str) -> str:
```

Fungsi ini:

1. Encode password ke UTF-8.
2. Hitung hash SHA-256.
3. Return hex digest.

Contoh:

```python
hashlib.sha256(password.encode("utf-8")).hexdigest()
```

Catatan keamanan:

- Ini cukup untuk demo akademik.
- Untuk production, password seharusnya memakai password hashing khusus seperti Argon2, bcrypt, atau PBKDF2 dengan salt.

### Class `AuthService`

#### `__init__(self, voter_repository=None)`

Menyimpan optional `voter_repository`.

Jika service dipakai untuk login voter, repository wajib diberikan. Jika dipakai untuk login admin, repository tidak diperlukan.

#### `authenticate_voter(self, voter_id: str, password: str)`

Alur:

1. Jika `voter_repository` tidak ada, return `None`.
2. Cari voter berdasarkan `voter_id`.
3. Jika voter tidak ditemukan, return `None`.
4. Hash password input dengan `hash_password`.
5. Bandingkan hash dari database dan hash input memakai `hmac.compare_digest`.
6. Jika cocok, return object voter.
7. Jika tidak cocok, return `None`.

`hmac.compare_digest` dipakai untuk mengurangi risiko timing attack pada comparison string.

#### `authenticate_admin(self, username: str, password: str) -> bool`

Membandingkan username dan password input dengan `settings.admin_username` dan `settings.admin_password`.

Keduanya dibandingkan memakai `hmac.compare_digest`.

Return `True` hanya jika username dan password cocok.

## 13.2 `CryptoService`

File: `app/services/crypto_service.py`

### Fungsi `generate_rsa_key_pair`

Signature:

```python
def generate_rsa_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
```

Fungsi ini membuat RSA private key:

- Public exponent: `65537`
- Key size: `2048`

Return:

- Private key.
- Public key dari private key tersebut.

### Fungsi `save_key_pair`

Signature:

```python
def save_key_pair(private_key, public_key, private_path, public_path) -> None:
```

Fungsi ini:

1. Convert path ke `Path`.
2. Membuat parent directory jika belum ada.
3. Menyimpan private key dalam format PEM PKCS8 tanpa enkripsi.
4. Menyimpan public key dalam format PEM SubjectPublicKeyInfo.

Catatan keamanan:

- Private key saat ini disimpan tanpa passphrase.
- Untuk production yang sebenarnya, private key idealnya disimpan di secret manager, KMS, HSM, atau setidaknya file permission ketat.

### Class `CryptoService`

`CryptoService` memegang empat key:

- Admin private key.
- Admin public key.
- System private key.
- System public key.

Pembagian key:

- Admin key pair dipakai untuk enkripsi dan dekripsi suara.
- System key pair dipakai untuk signing dan verification integritas record.

#### `__init__(self, admin_private_key_path, admin_public_key_path, system_private_key_path, system_public_key_path)`

Load semua key dari path.

Method ini memanggil:

- `_load_private_key` untuk private key.
- `_load_public_key` untuk public key.

Jika file tidak ada, error akan muncul saat membaca file. Pada penggunaan normal, `factory.create_crypto_service` sudah mengecek file yang hilang lebih dulu.

#### `encrypt_vote_plaintext(self, plaintext: str) -> bytes`

Mengenkripsi plaintext suara memakai admin public key.

Padding:

- OAEP
- MGF1 SHA-256
- Algorithm SHA-256
- Label `None`

Input plaintext di-encode ke UTF-8 sebelum dienkripsi.

Return berupa ciphertext bytes.

Sifat teknis OAEP:

- Probabilistic encryption.
- Plaintext yang sama akan menghasilkan ciphertext berbeda pada enkripsi berbeda.
- Unit test `test_oaep_produces_different_ciphertext_for_same_plaintext` memastikan sifat ini.

#### `decrypt_vote_ciphertext(self, ciphertext: bytes) -> str`

Mendekripsi ciphertext memakai admin private key dengan konfigurasi OAEP yang sama.

Return plaintext string UTF-8.

Jika ciphertext rusak atau key tidak cocok, cryptography akan melempar exception. Exception ini ditangkap di `RecapitulationService._validate_and_count_vote` dan ditandai sebagai `DECRYPTION_FAILED`.

#### `hash_ciphertext(self, ciphertext: bytes) -> str`

Menghitung SHA-256 dari ciphertext.

Return berupa hex string 64 karakter.

Hash dilakukan terhadap ciphertext, bukan plaintext. Ini menjaga agar integrity check tidak perlu membuka plaintext terlebih dahulu.

#### `sign_hash(self, hash_hex: str) -> bytes`

Menandatangani hash ciphertext memakai system private key.

Alur:

1. Convert `hash_hex` menjadi bytes dengan `bytes.fromhex`.
2. Sign bytes tersebut memakai RSA-PSS.

Padding:

- PSS
- MGF1 SHA-256
- Salt length `PSS.MAX_LENGTH`
- Hash algorithm SHA-256

Return berupa signature bytes.

#### `verify_signature(self, hash_hex: str, signature: bytes) -> bool`

Memverifikasi signature memakai system public key.

Alur:

1. Convert `hash_hex` ke bytes.
2. Jalankan `system_public_key.verify`.
3. Jika signature invalid atau `hash_hex` bukan hex valid, return `False`.
4. Jika tidak ada exception, return `True`.

Exception yang ditangkap:

- `InvalidSignature`
- `ValueError`

#### `verify_ciphertext_hash(self, ciphertext: bytes, expected_hash_hex: str) -> bool`

Menghitung ulang hash ciphertext lalu membandingkan dengan hash yang tersimpan.

Return:

- `True` jika cocok.
- `False` jika berbeda.

#### `_load_private_key(path: str | Path) -> RSAPrivateKey`

Static method untuk membaca private key PEM.

Alur:

1. Read bytes dari path.
2. Load memakai `serialization.load_pem_private_key`.
3. Pastikan object yang dimuat adalah `RSAPrivateKey`.
4. Jika bukan RSA private key, raise `TypeError`.
5. Return key.

#### `_load_public_key(path: str | Path) -> RSAPublicKey`

Static method untuk membaca public key PEM.

Alur:

1. Read bytes dari path.
2. Load memakai `serialization.load_pem_public_key`.
3. Pastikan object yang dimuat adalah `RSAPublicKey`.
4. Jika bukan RSA public key, raise `TypeError`.
5. Return key.

## 13.3 `VotingService`

File: `app/services/voting_service.py`

Class ini menangani use case cast vote.

### `__init__(self, voter_repository, candidate_repository, vote_repository, audit_log_repository, crypto_service)`

Menyimpan dependency:

- Repository voter.
- Repository kandidat.
- Repository vote.
- Repository audit log.
- Crypto service.

Dependency injection manual ini membuat service mudah dites memakai fake repository dan fake crypto, seperti terlihat di `tests/test_service_logic.py`.

### `cast_vote(self, voter_id: str, candidate_id: int) -> VoteCastResult`

Alur detail:

1. Cari voter dengan `voter_repository.find_by_voter_id`.
2. Jika voter tidak ditemukan, raise `VoterNotFoundError`.
3. Jika `voter.has_voted` bernilai `True`:
   - Buat audit log `DOUBLE_VOTE_ATTEMPT`.
   - Raise `VoterAlreadyVotedError`.
4. Cari kandidat dengan `candidate_repository.find_by_id`.
5. Jika kandidat tidak ditemukan, raise `CandidateNotFoundError`.
6. Buat timestamp saat ini dengan timezone:
   ```python
   datetime.now(timezone.utc).astimezone().isoformat()
   ```
7. Bangun plaintext vote dengan `build_vote_plaintext`.
8. Enkripsi plaintext memakai `crypto_service.encrypt_vote_plaintext`.
9. Hash ciphertext memakai `crypto_service.hash_ciphertext`.
10. Sign hash memakai `crypto_service.sign_hash`.
11. Buat vote record dengan `vote_repository.create_vote_record`.
12. Tandai voter sudah memilih dengan `voter_repository.mark_as_voted`.
13. Buat audit log `VOTE_CAST`.
14. Return `VoteCastResult`.

Urutan kripto yang diwajibkan:

```text
encrypt -> hash -> sign
```

Unit test `test_voting_service_uses_crypto_pipeline_in_required_order` memverifikasi urutan ini.

## 13.4 `RecapitulationService`

File: `app/services/recapitulation_service.py`

Class ini menangani validasi seluruh vote record dan menghitung hasil akhir.

### `__init__(self, vote_repository, candidate_repository, audit_log_repository, crypto_service)`

Menyimpan dependency:

- Repository vote.
- Repository kandidat.
- Repository audit log.
- Crypto service.

### `recapitulate_votes(self) -> RecapitulationResult`

Alur detail:

1. Ambil seluruh vote dengan `vote_repository.find_all_votes`.
2. Ambil seluruh kandidat dengan `candidate_repository.find_all`.
3. Bentuk dictionary kandidat:
   ```python
   {candidate.id: candidate for candidate in candidates}
   ```
4. Buat `Counter` untuk menghitung suara per candidate_id.
5. Buat list `invalid_details` untuk vote invalid.
6. Buat audit log `RECAPITULATION_STARTED`.
7. Loop setiap vote.
8. Untuk setiap vote, panggil `_validate_and_count_vote`.
9. Jika hasilnya `InvalidVoteDetail`, masukkan ke `invalid_details`.
10. Setelah loop, bentuk `candidate_results` dari semua kandidat.
11. Buat audit log `RECAPITULATION_COMPLETED`.
12. Return `RecapitulationResult`.

Hasil `valid_votes` dihitung dari total `Counter`.

Hasil `invalid_votes` dihitung dari panjang `invalid_details`.

### `_validate_and_count_vote(self, vote, candidates, counts) -> InvalidVoteDetail | None`

Method internal untuk validasi satu vote.

Tahap validasi:

1. Signature verification:
   - Panggil `crypto_service.verify_signature(vote.ciphertext_hash, vote.signature)`.
   - Jika gagal, vote ditandai `INVALID_SIGNATURE`.
   - Proses berhenti untuk vote tersebut.

2. Hash verification:
   - Panggil `crypto_service.verify_ciphertext_hash(vote.ciphertext, vote.ciphertext_hash)`.
   - Jika gagal, vote ditandai `HASH_MISMATCH`.
   - Proses berhenti untuk vote tersebut.

3. Decryption:
   - Panggil `crypto_service.decrypt_vote_ciphertext(vote.ciphertext)`.
   - Jika exception, vote ditandai `DECRYPTION_FAILED`.
   - Proses berhenti untuk vote tersebut.

4. Plaintext parsing:
   - Panggil `parse_vote_plaintext(plaintext)`.
   - Jika `MalformedVotePlaintextError`, vote ditandai `MALFORMED_PLAINTEXT`.
   - Proses berhenti untuk vote tersebut.

5. Candidate validation:
   - Periksa apakah `parsed.candidate_id` ada di dictionary kandidat.
   - Jika tidak ada, vote ditandai `MALFORMED_PLAINTEXT` dengan alasan unknown candidate.

6. Jika semua valid:
   - Update status vote menjadi `VALID`.
   - Tambah counter untuk candidate_id.
   - Return `None`.

Urutan ini penting karena:

- Signature dicek sebelum hash/dekripsi agar manipulasi signature langsung terdeteksi.
- Hash dicek sebelum dekripsi agar perubahan ciphertext dapat dikenali tanpa membuka plaintext.
- Dekripsi hanya dilakukan setelah record lolos autentikasi signature dan hash.

### `_mark_invalid(self, vote, status: VerificationStatus, event_type: str, reason: str) -> InvalidVoteDetail`

Method internal untuk menandai vote invalid.

Alur:

1. Update status vote dengan `vote_repository.update_verification_status`.
2. Buat audit log sesuai event type.
3. Return `InvalidVoteDetail`.

Method ini menyatukan logic invalid handling agar semua kasus invalid konsisten.

## 13.5 `BenchmarkService`

File: `app/services/benchmark_service.py`

### `measure_operation(self, operation_name: str, callback: Callable[[], Any]) -> BenchmarkResult`

Fungsi ini mengukur durasi eksekusi callback.

Alur:

1. Ambil waktu awal dengan `perf_counter`.
2. Jalankan callback.
3. Ambil waktu akhir dengan `perf_counter`.
4. Hitung durasi milidetik:
   ```python
   (end - start) * 1000
   ```
5. Return `BenchmarkResult`.

`perf_counter` cocok untuk benchmark durasi singkat karena memakai timer resolusi tinggi.

## 13.6 Factory Service

File: `app/services/factory.py`

Factory menggabungkan repository, service, dan konfigurasi agar router tidak membuat semua dependency secara manual.

### `create_crypto_service() -> CryptoService`

Alur:

1. Ambil empat path key dari `settings`.
2. Cek file yang hilang.
3. Jika ada yang hilang, raise `FileNotFoundError` dengan instruksi menjalankan `python scripts/generate_keys.py`.
4. Jika lengkap, return `CryptoService`.

### `create_voting_service(db: Session) -> VotingService`

Membuat `VotingService` dengan:

- `VoterRepository(db)`
- `CandidateRepository(db)`
- `VoteRepository(db)`
- `AuditLogRepository(db)`
- `create_crypto_service()`

### `create_recapitulation_service(db: Session) -> RecapitulationService`

Membuat `RecapitulationService` dengan:

- `VoteRepository(db)`
- `CandidateRepository(db)`
- `AuditLogRepository(db)`
- `create_crypto_service()`

## 14. Router dan Endpoint

## 14.1 Auth Router

File: `app/routers/auth_router.py`

Router ini tidak memakai prefix.

### `GET /login` - `login_page`

Merender template `login.html`.

Return:

```python
templates.TemplateResponse(request, "login.html")
```

### `POST /login` - `login`

Parameter form:

- `voter_id`
- `password`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Buat `AuthService(VoterRepository(db))`.
2. Authenticate voter.
3. Jika gagal, render ulang `login.html` dengan error.
4. Jika berhasil:
   - Simpan `request.session["voter_id"] = voter.voter_id`.
   - Redirect ke `/vote` dengan status 303.

Status 303 dipakai setelah form POST agar browser melakukan GET ke URL tujuan.

### `GET /admin/login` - `admin_login_page`

Merender template `admin_login.html`.

### `POST /admin/login` - `admin_login`

Parameter form:

- `username`
- `password`

Alur:

1. Panggil `AuthService().authenticate_admin`.
2. Jika gagal, render ulang `admin_login.html` dengan error.
3. Jika berhasil:
   - Set `request.session["is_admin"] = True`.
   - Redirect ke `/admin/dashboard`.

### `POST /logout` - `logout`

Membersihkan seluruh session:

```python
request.session.clear()
```

Lalu redirect ke `/login`.

## 14.2 Voter Router

File: `app/routers/voter_router.py`

Router ini tidak memakai prefix.

### `GET /` - `root`

Redirect ke `/login`.

### `GET /vote` - `vote_page`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Ambil `voter_id` dari session.
2. Jika tidak ada, redirect ke `/login`.
3. Cari voter di database.
4. Jika voter tidak ditemukan, redirect ke `/login`.
5. Ambil semua kandidat.
6. Render `vote.html` dengan data voter dan candidates.

Jika voter sudah memilih, template akan menampilkan pesan bahwa voter sudah memilih.

### `POST /vote` - `cast_vote`

Parameter form:

- `candidate_id`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Ambil `voter_id` dari session.
2. Jika tidak ada, redirect ke `/login`.
3. Panggil `create_voting_service(db).cast_vote(voter_id, candidate_id)`.
4. Jika berhasil, `db.commit()`.
5. Redirect ke `/vote/success?vote_id={result.vote_record_id}`.
6. Jika exception domain atau file key hilang:
   - `db.rollback()`.
   - Ambil ulang voter dan candidates.
   - Render `vote.html` dengan pesan error.

Exception yang ditangkap:

- `VoterNotFoundError`
- `VoterAlreadyVotedError`
- `CandidateNotFoundError`
- `FileNotFoundError`

### `GET /vote/success` - `vote_success`

Parameter query:

- `vote_id`

Merender `vote_success.html` dengan vote ID.

## 14.3 Admin Router

File: `app/routers/admin_router.py`

Router memakai prefix:

```python
router = APIRouter(prefix="/admin")
```

### `require_admin(request: Request)`

Helper untuk proteksi route admin.

Alur:

1. Cek `request.session.get("is_admin")`.
2. Jika tidak ada, return redirect ke `/admin/login`.
3. Jika ada, return `None`.

Setiap endpoint admin memanggil helper ini di awal.

### `GET /admin/dashboard` - `dashboard`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Panggil `require_admin`.
2. Jika redirect, return redirect.
3. Hitung:
   - total voters
   - total candidates
   - total vote records
   - total audit logs
4. Render `admin_dashboard.html`.

### `POST /admin/recapitulate` - `recapitulate`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Panggil `require_admin`.
2. Jika redirect, return redirect.
3. Panggil `create_recapitulation_service(db).recapitulate_votes()`.
4. Commit perubahan database.
5. Simpan hasil rekapitulasi terbaru ke session `latest_recap`.
6. Redirect ke `/admin/results`.

Hasil disimpan ke session dalam bentuk dict agar bisa ditampilkan di halaman results tanpa query ulang.

### `GET /admin/results` - `results`

Alur:

1. Panggil `require_admin`.
2. Jika redirect, return redirect.
3. Ambil `latest_recap` dari session.
4. Render `recap_result.html`.

Jika belum ada rekapitulasi, template menampilkan pesan bahwa rekapitulasi belum dijalankan.

### `GET /admin/audit-logs` - `audit_logs`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Panggil `require_admin`.
2. Ambil semua audit log dari repository.
3. Render `audit_logs.html`.

### `GET /admin/benchmarks` - `benchmarks`

Dependency:

- `db: Session = Depends(get_db)`

Alur:

1. Panggil `require_admin`.
2. Ambil semua benchmark record.
3. Render `benchmark.html`.

## 15. Template HTML dan UI

### 15.1 `base.html`

Template dasar seluruh halaman.

Komponen:

- Deklarasi HTML.
- Meta viewport.
- Link CSS `/static/styles.css`.
- Header topbar.
- Block Jinja `{% block content %}{% endblock %}`.

Semua template lain melakukan extend ke `base.html`.

### 15.2 `login.html`

Halaman login voter.

Elemen utama:

- Hero text.
- Form login voter dengan field `voter_id` dan `password`.
- Error message jika login gagal.
- Link ke admin login.
- Elemen ilustrasi CSS.

Form dikirim ke `POST /login`.

### 15.3 `admin_login.html`

Halaman login admin.

Form:

- `username`
- `password`

Form dikirim ke `POST /admin/login`.

### 15.4 `vote.html`

Halaman ballot voter.

Data input template:

- `voter`
- `candidates`
- optional `error`

Behavior:

- Jika ada error, tampilkan alert.
- Jika `voter.has_voted`, tampilkan pesan bahwa voter sudah memilih.
- Jika belum memilih, render radio button untuk setiap kandidat dan tombol submit.

Form dikirim ke `POST /vote`.

### 15.5 `vote_success.html`

Halaman sukses setelah vote.

Menampilkan:

- Pesan bahwa suara berhasil disimpan.
- Vote ID.
- Informasi bahwa data melewati RSA-OAEP, SHA-256, dan RSA-PSS.

### 15.6 `admin_dashboard.html`

Dashboard admin.

Menampilkan statistik:

- Total voters.
- Total candidates.
- Total vote records.
- Total audit logs.

Action:

- Run Recapitulation.
- Results.
- Audit Logs.
- Benchmarks.

### 15.7 `recap_result.html`

Halaman hasil rekapitulasi.

Jika belum ada result:

- Tampilkan alert.

Jika ada result:

- Tampilkan total vote, valid vote, invalid vote.
- Tabel jumlah suara per kandidat.
- Tabel detail vote invalid.

### 15.8 `audit_logs.html`

Menampilkan tabel audit log:

- Time.
- Event.
- Entity.
- Message.

### 15.9 `benchmark.html`

Menampilkan tabel benchmark:

- Operation.
- Duration ms.
- Sample.
- Created.

### 15.10 `styles.css`

CSS mengatur:

- Layout utama.
- Topbar.
- Hero login.
- Form.
- Candidate card.
- Stats grid.
- Tabel.
- Responsive layout untuk viewport kecil.

## 16. Alur Program Lengkap

## 16.1 Startup Aplikasi

Alur saat aplikasi dijalankan via Docker production:

1. Container dibuat dari `Dockerfile`.
2. `ENTRYPOINT ["sh", "./scripts/docker-entrypoint.sh"]` dijalankan.
3. Entrypoint membaca environment:
   - `RUN_MIGRATIONS`
   - `GENERATE_KEYS_IF_MISSING`
4. Jika `RUN_MIGRATIONS=true`, jalankan:
   ```text
   alembic upgrade head
   ```
5. Jika key belum ada dan `GENERATE_KEYS_IF_MISSING=true`, jalankan:
   ```text
   python scripts/generate_keys.py
   ```
6. Entrypoint menjalankan command utama:
   ```text
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
7. FastAPI memuat router, session middleware, dan static files.

## 16.2 Alur Login Voter

```text
GET /login
-> render login.html
-> user submit voter_id dan password
POST /login
-> AuthService.authenticate_voter
-> VoterRepository.find_by_voter_id
-> hash_password(password)
-> compare dengan voter.password_hash
-> jika valid, session["voter_id"] diset
-> redirect /vote
```

Jika invalid, halaman login dirender ulang dengan error.

## 16.3 Alur Menampilkan Ballot

```text
GET /vote
-> cek session["voter_id"]
-> jika tidak ada, redirect /login
-> cari voter
-> ambil semua kandidat
-> render vote.html
```

Template memutuskan apakah voter masih bisa memilih berdasarkan `voter.has_voted`.

## 16.4 Alur Cast Vote

```text
POST /vote
-> baca candidate_id dari form
-> baca voter_id dari session
-> create_voting_service(db)
-> VotingService.cast_vote(voter_id, candidate_id)
```

Detail dalam `VotingService.cast_vote`:

```text
find voter
-> reject jika voter tidak ada
-> reject jika sudah memilih
-> find candidate
-> reject jika candidate tidak ada
-> generate timestamp ISO
-> build plaintext
-> encrypt plaintext dengan admin public key
-> hash ciphertext
-> sign hash dengan system private key
-> create vote record
-> mark voter as voted
-> create audit log
-> return result
```

Router kemudian:

```text
db.commit()
-> redirect /vote/success?vote_id=...
```

Jika error:

```text
db.rollback()
-> render vote.html dengan pesan error
```

## 16.5 Alur Login Admin

```text
GET /admin/login
-> render admin_login.html
POST /admin/login
-> AuthService.authenticate_admin
-> compare username/password dengan settings
-> jika valid, session["is_admin"] = True
-> redirect /admin/dashboard
```

## 16.6 Alur Dashboard Admin

```text
GET /admin/dashboard
-> require_admin
-> count voters
-> count candidates
-> count vote records
-> count audit logs
-> render admin_dashboard.html
```

## 16.7 Alur Rekapitulasi

```text
POST /admin/recapitulate
-> require_admin
-> create_recapitulation_service(db)
-> RecapitulationService.recapitulate_votes()
-> db.commit()
-> simpan latest_recap ke session
-> redirect /admin/results
```

Detail validasi vote:

```text
for each vote:
  verify RSA-PSS signature atas stored ciphertext_hash
  jika invalid -> INVALID_SIGNATURE

  hitung ulang SHA-256(ciphertext)
  bandingkan dengan stored ciphertext_hash
  jika beda -> HASH_MISMATCH

  decrypt ciphertext dengan admin private key
  jika gagal -> DECRYPTION_FAILED

  parse plaintext
  jika format salah -> MALFORMED_PLAINTEXT

  cek candidate_id
  jika tidak ada -> MALFORMED_PLAINTEXT

  update status VALID
  increment counter candidate_id
```

## 16.8 Alur Menampilkan Hasil

```text
GET /admin/results
-> require_admin
-> ambil latest_recap dari session
-> render recap_result.html
```

Jika admin belum menjalankan rekapitulasi, result kosong.

## 16.9 Alur Audit Log

Audit log dibuat pada event:

- Vote berhasil dicatat.
- Double vote attempt.
- Rekapitulasi dimulai.
- Rekapitulasi selesai.
- Signature invalid.
- Hash mismatch.
- Dekripsi gagal.
- Plaintext malformed.

Halaman:

```text
GET /admin/audit-logs
-> require_admin
-> AuditLogRepository.find_all()
-> render audit_logs.html
```

## 16.10 Alur Benchmark

Benchmark dijalankan melalui script, bukan tombol UI.

```text
python scripts/run_benchmark.py
```

Script mengukur:

- RSA-OAEP Encryption.
- SHA-256 Hashing.
- RSA-PSS Signing.
- RSA-PSS Verification.
- Hash Verification.
- RSA-OAEP Decryption.

Hasil disimpan ke `benchmark_records`.

Halaman:

```text
GET /admin/benchmarks
-> require_admin
-> BenchmarkRepository.find_all()
-> render benchmark.html
```

## 17. Detail Kriptografi Sistem

## 17.1 Key Pair

Sistem memakai dua pasangan RSA key.

### Admin key pair

Dipakai untuk:

- Public key: enkripsi plaintext vote.
- Private key: dekripsi ciphertext saat rekapitulasi.

Rasional:

- Saat vote dibuat, sistem hanya perlu public key untuk menyimpan suara terenkripsi.
- Plaintext kandidat baru dapat dibuka saat rekapitulasi dengan private key admin.

### System key pair

Dipakai untuk:

- Private key: sign hash ciphertext.
- Public key: verify signature saat rekapitulasi.

Rasional:

- Signature membuktikan bahwa hash yang tersimpan dibuat oleh sistem yang memiliki private key.
- Jika signature berubah atau hash berubah tanpa signature baru yang valid, vote dianggap invalid.

## 17.2 Kenapa Hash Dibuat dari Ciphertext

Sistem menghitung:

```text
hash = SHA-256(ciphertext)
```

Bukan:

```text
hash = SHA-256(plaintext)
```

Keuntungannya:

- Integritas data terenkripsi dapat dicek sebelum dekripsi.
- Plaintext tidak perlu dibuka untuk mendeteksi perubahan ciphertext.
- Jika ciphertext dimanipulasi, hash mismatch akan terdeteksi.

## 17.3 Kenapa Hash Ditandatangani

Signature dibuat atas hash ciphertext:

```text
signature = RSA-PSS-SIGN(system_private_key, hash)
```

Saat rekapitulasi:

```text
RSA-PSS-VERIFY(system_public_key, stored_hash, signature)
```

Jika attacker mengubah ciphertext dan hash sekaligus, signature lama tidak lagi valid terhadap hash baru. Tanpa system private key, attacker tidak dapat membuat signature valid.

## 17.4 Urutan Deteksi Manipulasi

Urutan validasi rekapitulasi saat ini:

1. Signature invalid.
2. Hash mismatch.
3. Decryption failed.
4. Malformed plaintext.
5. Unknown candidate.

Konsekuensi:

- Jika signature dimanipulasi, sistem melaporkan `INVALID_SIGNATURE`.
- Jika ciphertext dimanipulasi tetapi hash dan signature tetap, signature atas hash lama masih valid, lalu hash check gagal dan sistem melaporkan `HASH_MISMATCH`.
- Jika ciphertext, hash, dan signature konsisten tetapi ciphertext tidak bisa didekripsi, sistem melaporkan `DECRYPTION_FAILED`.
- Jika dekripsi sukses tetapi format plaintext rusak, sistem melaporkan `MALFORMED_PLAINTEXT`.

## 18. Script Operasional

## 18.1 `scripts/generate_keys.py`

Fungsi utama: `main()`.

Alur:

1. Tambahkan root project ke `sys.path`.
2. Generate admin RSA key pair.
3. Generate system RSA key pair.
4. Simpan admin key pair ke path dari settings.
5. Simpan system key pair ke path dari settings.
6. Print lokasi key.

Command:

```bash
python scripts/generate_keys.py
```

Output key default:

```text
app/keys/admin_private_key.pem
app/keys/admin_public_key.pem
app/keys/system_private_key.pem
app/keys/system_public_key.pem
```

Pada production, path diarahkan ke `/data/keys`.

## 18.2 `scripts/seed_data.py`

Fungsi utama: `main()`.

Alur:

1. Tambahkan root project ke `sys.path`.
2. Jalankan `Base.metadata.create_all(bind=engine)`.
3. Buka database session.
4. Jika tabel candidates kosong, tambahkan 3 kandidat.
5. Jika tabel voters kosong, tambahkan 500 voter demo.
6. Semua voter demo memakai password `password123` yang di-hash dengan `hash_password`.
7. Commit transaksi.
8. Tutup session.

Command:

```bash
python scripts/seed_data.py
```

Data demo:

- Kandidat A.
- Kandidat B.
- Kandidat C.
- VOTER001 sampai VOTER500.

## 18.3 `scripts/run_benchmark.py`

Fungsi utama: `main()`.

Alur:

1. Tambahkan root project ke `sys.path`.
2. Buat `CryptoService`.
3. Buat `BenchmarkService`.
4. Buka session database.
5. Siapkan plaintext sample.
6. Buat ciphertext, hash, dan signature awal.
7. Definisikan daftar operasi kripto.
8. Ukur setiap operasi dengan `measure_operation`.
9. Simpan setiap hasil ke `benchmark_records`.
10. Print durasi.
11. Commit dan close session.

Command:

```bash
python scripts/run_benchmark.py
```

## 18.4 `scripts/manipulate_vote.py`

Script ini dipakai untuk demo deteksi manipulasi.

### Fungsi `flip_first_byte`

Signature:

```python
def flip_first_byte(value: bytes) -> bytes:
```

Alur:

1. Jika bytes kosong, return apa adanya.
2. Convert bytes ke `bytearray`.
3. XOR byte pertama dengan `0x01`.
4. Return bytes baru.

Efeknya adalah mengubah satu bit pada byte pertama.

### Fungsi `main`

Argumen CLI:

- `vote_id`
- `field`, salah satu dari `ciphertext`, `hash`, `signature`

Alur:

1. Parse argumen.
2. Buka database session.
3. Ambil vote berdasarkan ID.
4. Jika tidak ditemukan, exit dengan pesan.
5. Jika field `ciphertext`, ubah byte pertama ciphertext.
6. Jika field `hash`, ubah karakter pertama hash.
7. Jika field `signature`, ubah byte pertama signature.
8. Commit.
9. Print pesan sukses.
10. Close session.

Command:

```bash
python scripts/manipulate_vote.py <vote_id> ciphertext
python scripts/manipulate_vote.py <vote_id> hash
python scripts/manipulate_vote.py <vote_id> signature
```

## 18.5 `scripts/docker-entrypoint.sh`

Script shell yang dijalankan saat container app start.

Alur:

1. `set -eu` agar script berhenti saat error atau variable tidak terdefinisi.
2. Jika `RUN_MIGRATIONS=true`, jalankan `alembic upgrade head`.
3. Jika `GENERATE_KEYS_IF_MISSING=true`, cek empat file key.
4. Jika salah satu key hilang, jalankan `python scripts/generate_keys.py`.
5. Jalankan command container dengan `exec "$@"`.

## 19. Docker dan Deployment

## 19.1 `Dockerfile`

Alur build:

1. Base image `python:3.12-slim`.
2. Set environment:
   - `PYTHONDONTWRITEBYTECODE=1`
   - `PYTHONUNBUFFERED=1`
   - `PIP_NO_CACHE_DIR=1`
3. Set working directory `/app`.
4. Copy `requirements.txt`.
5. Install dependency.
6. Copy seluruh source code.
7. Buat user system `app`.
8. Buat `/data/keys`.
9. Ubah ownership `/app` dan `/data`.
10. Jalankan container sebagai user `app`.
11. Expose port 8000.
12. Set entrypoint.
13. Set command Uvicorn.

## 19.2 `docker-compose.yml`

Dipakai untuk development lokal.

Service:

- `postgres`
- `app`

PostgreSQL:

- Image `postgres:16`.
- Port `5432:5432`.
- Volume `postgres_data`.
- Healthcheck `pg_isready`.

App:

- Build dari Dockerfile.
- Membaca `.env`.
- Port `8000:8000`.
- Menunggu PostgreSQL sehat.

## 19.3 `docker-compose.prod.yml`

Dipakai untuk deployment production sederhana.

Perbedaan utama:

- `restart: unless-stopped`.
- PostgreSQL tidak expose port publik.
- App expose `${APP_PORT:-8000}:8000`.
- RSA key disimpan di volume `rsa_keys`.
- App healthcheck memanggil `/login`.
- Migration dan key generation otomatis via environment.

## 20. Testing

## 20.1 `tests/test_plaintext.py`

Test:

- `test_build_vote_plaintext_uses_required_format`
- `test_parse_vote_plaintext_returns_structured_data`
- `test_parse_vote_plaintext_rejects_malformed_values`

Yang diverifikasi:

- Format plaintext sesuai kontrak.
- Parser mengembalikan object terstruktur.
- Parser menolak missing field, candidate non-integer, dan timestamp invalid.

## 20.2 `tests/test_crypto_service.py`

Helper:

- `create_crypto_service(tmp_path)`

Helper ini membuat key sementara di folder test agar tidak memakai key aplikasi asli.

Test:

- `test_encrypt_decrypt_roundtrip`
- `test_oaep_produces_different_ciphertext_for_same_plaintext`
- `test_hash_and_signature_validation`

Yang diverifikasi:

- Enkripsi dan dekripsi berjalan roundtrip.
- OAEP menghasilkan ciphertext berbeda untuk plaintext sama.
- Hash panjangnya 64 hex char.
- Signature valid diterima.
- Signature/hash yang dimanipulasi ditolak.

## 20.3 `tests/test_service_logic.py`

File ini memakai fake object agar logic service bisa dites tanpa database dan tanpa RSA asli.

Fake class:

- `FakeVoter`
- `FakeCandidate`
- `FakeVote`
- `FakeVoterRepository`
- `FakeCandidateRepository`
- `FakeVoteRepository`
- `FakeAuditLogRepository`
- `FakeCrypto`

Test:

- `test_voting_service_rejects_unknown_voter`
- `test_voting_service_rejects_already_voted_voter`
- `test_voting_service_rejects_unknown_candidate`
- `test_voting_service_uses_crypto_pipeline_in_required_order`
- `test_recapitulation_skips_invalid_signature`
- `test_recapitulation_counts_valid_votes`

Yang diverifikasi:

- Voter tidak dikenal ditolak.
- Double vote ditolak.
- Kandidat tidak dikenal ditolak.
- Pipeline kripto voting berjalan dalam urutan `encrypt`, `hash`, `sign`.
- Rekapitulasi menolak invalid signature.
- Rekapitulasi menghitung vote valid.

Command test:

```bash
pytest
```

## 21. Detail Keamanan

## 21.1 Proteksi Double Vote

Ada dua lapisan:

1. Application layer:
   - `VotingService.cast_vote` mengecek `voter.has_voted`.
   - Jika sudah memilih, raise `VoterAlreadyVotedError`.

2. Database layer:
   - `vote_records.voter_id` unique.
   - Ini mencegah dua vote record dengan voter_id sama.

## 21.2 Kerahasiaan Vote

Vote plaintext tidak disimpan.

Database hanya menyimpan:

- `ciphertext`
- `ciphertext_hash`
- `signature`

Candidate pilihan hanya dapat diketahui setelah dekripsi dengan admin private key.

## 21.3 Integritas Vote

Integritas dijaga dengan:

- Hash SHA-256 atas ciphertext.
- Signature RSA-PSS atas hash.

Jika ciphertext berubah, hash verification gagal.

Jika hash berubah, signature verification gagal kecuali attacker memiliki system private key.

## 21.4 Auditability

Audit log mencatat:

- Vote sukses.
- Double vote.
- Rekapitulasi dimulai dan selesai.
- Manipulasi atau kegagalan validasi vote.

Ini membantu menunjukkan bukti sistem mendeteksi perubahan data.

## 21.5 Batasan Keamanan

Sistem ini prototype akademik, bukan production-grade election system.

Batasan:

- Password hashing memakai SHA-256 biasa tanpa salt.
- Private key disimpan di filesystem tanpa passphrase.
- Session sederhana, belum memakai OAuth, MFA, CSRF protection eksplisit, atau role management kompleks.
- Tidak ada HSM/KMS.
- Tidak ada mekanisme anonymous credential.
- Tidak ada public verifiability end-to-end.
- Admin password berasal dari environment dan dibandingkan langsung.
- Count repository memakai select-all lalu `len`, tidak optimal untuk data besar.
- Tidak ada concurrency control eksplisit untuk race condition double vote selain unique constraint database.

## 22. Penjelasan Relasi Data

Relasi logis:

```text
Voter
  voter_id unique
  has_voted

VoteRecord
  voter_id unique
  ciphertext
  ciphertext_hash
  signature
  verification_status

Candidate
  id
  name

AuditLog
  event_type
  entity_type
  entity_id

BenchmarkRecord
  operation_name
  duration_ms
```

Tidak ada foreign key eksplisit pada schema saat ini antara `vote_records.voter_id` dan `voters.voter_id`.

Secara aplikasi, relasi dijaga oleh `VotingService`:

- Vote record hanya dibuat setelah voter ditemukan.
- Candidate hanya diterima setelah candidate ditemukan.

## 23. Penjelasan Transaksi Database

Repository hanya menambahkan atau mengubah object di SQLAlchemy session. Commit dilakukan di router atau script.

Contoh cast vote:

```text
create vote record
mark voter as voted
create audit log
db.commit()
```

Jika terjadi exception:

```text
db.rollback()
```

Ini membuat operasi voting bersifat atomic di level request:

- Jika sukses, vote record, status voter, dan audit log tersimpan bersama.
- Jika gagal, perubahan dibatalkan.

Contoh rekapitulasi:

```text
update verification status untuk banyak vote
create audit logs
db.commit()
```

## 24. Cara Menjalankan Sistem

### 24.1 Development dengan Docker

```bash
cp .env.example .env
docker compose up --build
```

Terminal lain:

```bash
docker compose exec app alembic upgrade head
docker compose exec app python scripts/generate_keys.py
docker compose exec app python scripts/seed_data.py
```

Buka:

```text
http://localhost:8000
```

Credential demo:

```text
Voter ID: VOTER001
Voter password: password123
Admin username: admin
Admin password: admin123
```

### 24.2 Production dengan Docker Compose

```bash
cp .env.production.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

Production compose menjalankan migration dan generate key otomatis jika environment mengaktifkannya.

## 25. Simulasi Manipulasi Data

Tujuan simulasi adalah menunjukkan bahwa sistem dapat mendeteksi perubahan pada vote record.

Alur:

1. Login sebagai voter.
2. Lakukan voting.
3. Ambil vote ID dari halaman sukses.
4. Jalankan script manipulasi.
5. Login admin.
6. Jalankan rekapitulasi.
7. Lihat hasil invalid vote dan audit log.

Contoh:

```bash
python scripts/manipulate_vote.py <vote_id> ciphertext
```

Ekspektasi:

- Jika ciphertext diubah, hash mismatch atau decryption failed dapat terjadi tergantung kombinasi data.
- Jika hash diubah, signature invalid terdeteksi.
- Jika signature diubah, signature invalid terdeteksi.

## 26. Ringkasan Fungsi dan Class

### 26.1 `app/config.py`

- `Settings`: dataclass konfigurasi aplikasi dari environment variable.
- `settings`: singleton konfigurasi global.

### 26.2 `app/database.py`

- `Base`: base class SQLAlchemy model.
- `engine`: koneksi SQLAlchemy ke database.
- `SessionLocal`: factory session database.
- `get_db`: dependency FastAPI untuk membuka dan menutup session per request.

### 26.3 `app/main.py`

- `app`: instance FastAPI, session middleware, static mount, dan router registration.

### 26.4 `app/domain/plaintext.py`

- `ParsedVotePlaintext`: representasi hasil parse plaintext.
- `build_vote_plaintext`: membuat plaintext vote dengan format tetap.
- `parse_vote_plaintext`: memvalidasi dan mem-parse plaintext vote.

### 26.5 `app/domain/enums.py`

- `VerificationStatus`: status validasi vote.
- `AuditEventType`: tipe event audit.

### 26.6 `app/domain/exceptions.py`

- `VoterNotFoundError`: voter tidak ditemukan.
- `VoterAlreadyVotedError`: voter sudah memilih.
- `CandidateNotFoundError`: kandidat tidak ditemukan.
- `InvalidSignatureError`: signature invalid.
- `HashMismatchError`: hash tidak cocok.
- `VoteDecryptionError`: dekripsi gagal.
- `MalformedVotePlaintextError`: plaintext tidak valid.

### 26.7 `app/models/*.py`

- `Voter`: model tabel voter.
- `Candidate`: model tabel kandidat.
- `VoteRecord`: model tabel vote terenkripsi.
- `AuditLog`: model tabel audit.
- `BenchmarkRecord`: model tabel benchmark.

### 26.8 `app/repositories/*.py`

- `VoterRepository.find_by_voter_id`: cari voter.
- `VoterRepository.mark_as_voted`: tandai voter sudah memilih.
- `VoterRepository.count_all`: hitung voter.
- `CandidateRepository.find_by_id`: cari kandidat.
- `CandidateRepository.find_all`: ambil semua kandidat.
- `CandidateRepository.count_all`: hitung kandidat.
- `VoteRepository.create_vote_record`: buat vote record terenkripsi.
- `VoteRepository.find_all_votes`: ambil semua vote.
- `VoteRepository.find_by_id`: cari vote.
- `VoteRepository.count_all`: hitung vote.
- `VoteRepository.update_verification_status`: update status validasi vote.
- `AuditLogRepository.create_log`: buat audit log.
- `AuditLogRepository.find_all`: ambil semua audit log.
- `AuditLogRepository.count_all`: hitung audit log.
- `BenchmarkRepository.create_record`: buat record benchmark.
- `BenchmarkRepository.find_all`: ambil semua benchmark.

### 26.9 `app/services/*.py`

- `hash_password`: hash password memakai SHA-256.
- `AuthService.authenticate_voter`: autentikasi voter.
- `AuthService.authenticate_admin`: autentikasi admin.
- `generate_rsa_key_pair`: buat RSA key pair.
- `save_key_pair`: simpan RSA key pair ke file PEM.
- `CryptoService.encrypt_vote_plaintext`: enkripsi plaintext vote.
- `CryptoService.decrypt_vote_ciphertext`: dekripsi ciphertext vote.
- `CryptoService.hash_ciphertext`: hash ciphertext.
- `CryptoService.sign_hash`: sign hash ciphertext.
- `CryptoService.verify_signature`: verifikasi signature.
- `CryptoService.verify_ciphertext_hash`: validasi hash ciphertext.
- `CryptoService._load_private_key`: load private key.
- `CryptoService._load_public_key`: load public key.
- `VotingService.cast_vote`: menjalankan proses voting.
- `RecapitulationService.recapitulate_votes`: menjalankan rekapitulasi.
- `RecapitulationService._validate_and_count_vote`: validasi satu vote.
- `RecapitulationService._mark_invalid`: tandai vote invalid.
- `BenchmarkService.measure_operation`: ukur durasi operasi.
- `create_crypto_service`: buat crypto service dari file key.
- `create_voting_service`: buat voting service.
- `create_recapitulation_service`: buat recapitulation service.

### 26.10 `app/routers/*.py`

- `login_page`: tampilkan login voter.
- `login`: proses login voter.
- `admin_login_page`: tampilkan login admin.
- `admin_login`: proses login admin.
- `logout`: hapus session.
- `root`: redirect root ke login.
- `vote_page`: tampilkan halaman vote.
- `cast_vote`: proses submit vote.
- `vote_success`: tampilkan vote sukses.
- `require_admin`: guard route admin.
- `dashboard`: tampilkan dashboard admin.
- `recapitulate`: proses rekapitulasi.
- `results`: tampilkan hasil rekapitulasi.
- `audit_logs`: tampilkan audit log.
- `benchmarks`: tampilkan benchmark.

### 26.11 `scripts/*.py`

- `generate_keys.main`: generate dua RSA key pair.
- `seed_data.main`: seed kandidat dan voter demo.
- `run_benchmark.main`: benchmark operasi kripto.
- `manipulate_vote.flip_first_byte`: ubah bit pertama bytes.
- `manipulate_vote.main`: manipulasi vote record.

### 26.12 `alembic/*.py`

- `run_migrations_offline`: migration mode offline.
- `run_migrations_online`: migration mode online.
- `upgrade`: membuat schema awal.
- `downgrade`: menghapus schema awal.

## 27. Kesimpulan Teknis

Sistem ini memakai arsitektur modular monolith dengan pemisahan yang cukup jelas:

- Router menangani HTTP dan template.
- Service menangani use case.
- Repository menangani database.
- Model mendefinisikan schema ORM.
- Domain mendefinisikan enum, exception, dan format plaintext.
- Script menangani kebutuhan operasional.

Bagian inti sistem adalah pipeline kriptografi voting dan rekapitulasi. Saat voting, plaintext suara dienkripsi, ciphertext di-hash, lalu hash ditandatangani. Saat rekapitulasi, signature dan hash diverifikasi sebelum ciphertext didekripsi dan dihitung. Dengan desain ini, sistem dapat mendemonstrasikan kerahasiaan suara, integritas data, deteksi manipulasi, dan audit trail dalam konteks prototype akademik.
