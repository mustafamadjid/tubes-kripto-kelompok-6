# Planning Implementasi Sistem E-Voting RSA-2048 + SHA-256

> Dokumen ini dibuat sebagai instruksi kerja untuk agentic AI coding tool seperti Codex.  
> Target utama: menghasilkan prototype sistem e-voting yang maintainable, modular, mudah diuji, dan selesai dalam ±4 hari pengembangan.

---

## 0. Agent Operating Rules

Sebelum menulis kode, agent wajib mengikuti aturan berikut:

1. Inspect existing codebase terlebih dahulu.
2. Jangan langsung membuat file besar tanpa memahami struktur project.
3. Pertahankan pola yang sudah ada jika project sudah memiliki struktur.
4. Jangan mencampur business logic, database query, dan UI dalam satu file.
5. Jangan mengimplementasikan algoritma RSA manual untuk sistem aktual.
6. Gunakan library kriptografi resmi untuk RSA-OAEP, RSA-PSS, dan SHA-256.
7. Prioritaskan MVP yang selesai dan dapat didemokan dalam 4 hari.
8. Jangan menambah fitur di luar scope tanpa alasan teknis yang kuat.
9. Setelah setiap milestone, jalankan test atau minimal smoke test.
10. Jika ada konflik requirement, pilih solusi paling sederhana dan dokumentasikan trade-off.

---

## 1. Analysis

### 1.1 Project Context

Sistem yang dibangun adalah prototype e-voting yang mengintegrasikan:

- RSA-2048 dengan OAEP untuk enkripsi suara.
- SHA-256 untuk hashing ciphertext.
- RSA-2048 dengan PSS untuk digital signature terhadap hash.
- Verifikasi integritas sebelum proses dekripsi dan rekapitulasi.
- Audit log untuk mendeteksi manipulasi data suara.
- Benchmark waktu komputasi untuk enkripsi, hashing, signing, verifikasi, dan dekripsi.

Fokus utama project bukan membuat sistem pemilu production-grade, tetapi membuktikan bahwa data suara dapat:

1. Dirahasiakan melalui RSA-OAEP.
2. Diverifikasi integritasnya melalui SHA-256.
3. Diautentikasi melalui RSA-PSS signature.
4. Ditolak ketika ciphertext, hash, atau signature dimanipulasi.
5. Diukur performanya melalui waktu komputasi.

### 1.2 Scope MVP

MVP wajib selesai:

- Login voter sederhana menggunakan `nim` dan password dummy.
- Login admin sederhana.
- Seeder 500 voter dan 3 kandidat.
- Voting flow.
- RSA key generation.
- Enkripsi suara dengan RSA-2048 OAEP.
- Hash ciphertext dengan SHA-256.
- Sign hash dengan RSA-2048 PSS.
- Simpan vote ke PostgreSQL.
- Update `has_voted = true` secara atomik.
- Rekapitulasi admin:
  - verify signature,
  - verify hash,
  - decrypt ciphertext,
  - count vote per candidate.
- Audit log untuk manipulasi.
- Pengujian manipulasi data.
- Benchmark waktu komputasi.
- Dokumentasi setup dan cara menjalankan sistem.

### 1.3 Out of Scope

Jangan implementasikan fitur berikut untuk MVP 4 hari:

- Google OAuth.
- Multi-factor authentication.
- Online voter registration.
- Role management kompleks.
- Frontend SPA terpisah seperti React/Next.js.
- Real-time voting dashboard.
- Hardware Security Module.
- Deployment production.
- Microservices.
- Blockchain.
- Homomorphic encryption.
- Email/WhatsApp notification.

### 1.4 Important Domain Rules

### 1.4.1 Perubahan Login Voter: NIM

Data login voter terdiri dari:

- `nim` (Nomor Induk Mahasiswa)
- `password`

`nim` menggantikan seluruh penggunaan `voter_id` sebagai identitas login dan identitas voter di database. Perubahan schema wajib dibuat melalui migrasi Alembic:

- rename kolom `voters.voter_id` menjadi `voters.nim`;
- rename kolom `vote_records.voter_id` menjadi `vote_records.nim`;
- pertahankan constraint UNIQUE dan index pada `nim`;
- update seed data agar membuat NIM mahasiswa, bukan ID pemilih buatan seperti `VOTER001`;
- update login form, auth service, repository, session, voting service, dan plaintext vote agar menggunakan `nim`.

Plaintext suara harus dibentuk dalam format:

```txt
nim:{NIM}|candidate_id:{CANDIDATE_ID}|timestamp:{ISO_8601_TIMESTAMP}
```

Contoh:

```txt
nim:122140191|candidate_id:1|timestamp:2026-05-22T14:30:00+07:00
```

Urutan pipeline voting wajib:

```txt
plaintext suara
  -> RSA-2048 OAEP encryption
  -> ciphertext
  -> SHA-256 hash(ciphertext)
  -> hash
  -> RSA-2048 PSS sign(hash)
  -> signature
  -> save {nim, ciphertext, hash, signature}
```

Urutan pipeline rekapitulasi wajib:

```txt
load {ciphertext, hash, signature}
  -> verify RSA-PSS signature
  -> recompute SHA-256 hash(ciphertext)
  -> compare hash
  -> decrypt RSA-OAEP ciphertext
  -> parse plaintext vote
  -> count valid vote
```

Jangan decrypt sebelum signature dan hash valid.

---

## 2. Architecture / Plan

### 2.1 Recommended Architecture

Gunakan modular monolith dengan layered architecture.

Alasan:

- Scope kecil dan harus selesai cepat.
- Lebih mudah diuji dibanding microservices.
- Business logic tetap bisa dipisahkan dengan baik.
- Cocok untuk prototype akademik dan demo lokal.

Layer utama:

| Layer | Responsibility |
|---|---|
| Router / Presentation | HTTP endpoint dan template rendering |
| Schema / DTO | Request/response validation |
| Service / Application | Use case orchestration |
| Domain | Entity, enum, business rule sederhana |
| Repository | Database access |
| Infrastructure | DB session, key loader, crypto implementation, config |

### 2.2 Recommended Tech Stack

Gunakan stack berikut:

| Concern | Technology |
|---|---|
| Language | Python 3.12+ |
| Backend Framework | FastAPI |
| UI | Jinja2 template + Tailwind CDN atau Bootstrap CDN |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x |
| Migration | Alembic |
| Cryptography | `cryptography` |
| Test | Pytest |
| Local Environment | Docker Compose |
| Benchmark | `time.perf_counter()` |
| Password Hashing | `passlib[bcrypt]` atau `bcrypt` |
| Settings | `pydantic-settings` |

### 2.3 Why This Stack

- FastAPI mempercepat pembuatan backend dan tetap rapi dengan type hints.
- Python memiliki library `cryptography` yang mendukung RSA-OAEP dan RSA-PSS.
- PostgreSQL cocok untuk data relational dan binary field seperti ciphertext/signature.
- SQLAlchemy menjaga query tetap modular melalui model dan repository.
- Alembic menjaga perubahan schema tetap terkontrol.
- Jinja2 lebih cepat untuk MVP dibanding frontend terpisah.
- Docker Compose membuat environment lokal mudah direplikasi.

### 2.4 High-Level Folder Structure

Agent harus membuat struktur seperti berikut jika project masih kosong:

```txt
e-voting-rsa-sha256/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   └── constants.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── voter.py
│   │   ├── candidate.py
│   │   ├── vote_record.py
│   │   ├── audit_log.py
│   │   └── benchmark_record.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth_schema.py
│   │   ├── vote_schema.py
│   │   ├── recap_schema.py
│   │   └── benchmark_schema.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── voter_repository.py
│   │   ├── candidate_repository.py
│   │   ├── vote_repository.py
│   │   ├── audit_log_repository.py
│   │   └── benchmark_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── crypto_service.py
│   │   ├── voting_service.py
│   │   ├── recapitulation_service.py
│   │   ├── audit_log_service.py
│   │   └── benchmark_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_router.py
│   │   ├── voter_router.py
│   │   └── admin_router.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── vote.html
│   │   ├── vote_success.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── recap_result.html
│   │   ├── audit_logs.html
│   │   └── benchmark.html
│   ├── static/
│   │   └── styles.css
│   └── keys/
│       └── .gitkeep
├── alembic/
├── scripts/
│   ├── generate_keys.py
│   ├── seed_data.py
│   ├── manipulate_vote.py
│   └── run_benchmark.py
├── tests/
│   ├── test_crypto_service.py
│   ├── test_voting_service.py
│   ├── test_recapitulation_service.py
│   └── test_manipulation_detection.py
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── planning.md
```

### 2.5 Separation of Responsibilities

#### Router Layer

Router hanya boleh:

- menerima request,
- validasi input melalui schema,
- memanggil service,
- mengembalikan response atau render template.

Router tidak boleh:

- menjalankan query database langsung,
- melakukan enkripsi langsung,
- menghitung rekapitulasi langsung,
- memformat plaintext suara secara manual.

#### Service Layer

Service bertanggung jawab terhadap use case.

Contoh:

- `VotingService.cast_vote()` mengorkestrasi validasi voter, plaintext builder, crypto pipeline, penyimpanan vote, dan update status.
- `RecapitulationService.recapitulate_votes()` mengorkestrasi verify signature, verify hash, decrypt, parsing plaintext, dan counting.

#### Repository Layer

Repository hanya bertanggung jawab terhadap database operation.

Contoh:

- `VoterRepository.find_by_nim()`
- `VoterRepository.mark_as_voted()`
- `VoteRepository.create_vote_record()`
- `VoteRepository.find_all_votes()`
- `AuditLogRepository.create_log()`

#### Crypto Layer

`CryptoService` hanya bertanggung jawab terhadap operasi kriptografi:

- load key,
- generate key,
- encrypt plaintext,
- decrypt ciphertext,
- hash bytes,
- sign hash,
- verify signature,
- compare hash securely.

Jangan masukkan query DB atau business rule voter ke `CryptoService`.

---

## 3. Database Design

### 3.1 Tables

#### `voters`

| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| nim | VARCHAR(32) | UNIQUE, NOT NULL |
| full_name | VARCHAR(150) | NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| has_voted | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

#### `candidates`

| Column | Type | Constraint |
|---|---|---|
| id | INTEGER | PK |
| name | VARCHAR(150) | NOT NULL |
| description | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

#### `vote_records`

| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| nim | VARCHAR(32) | NOT NULL, UNIQUE |
| ciphertext | BYTEA | NOT NULL |
| ciphertext_hash | VARCHAR(64) | NOT NULL |
| signature | BYTEA | NOT NULL |
| verification_status | VARCHAR(32) | DEFAULT 'PENDING' |
| manipulation_reason | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

Important:

- `nim` pada `vote_records` dibuat UNIQUE untuk mencegah double vote pada level DB.
- `ciphertext` dan `signature` gunakan `BYTEA`.
- `ciphertext_hash` disimpan sebagai 64 hex character.

#### `audit_logs`

| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| event_type | VARCHAR(80) | NOT NULL |
| entity_type | VARCHAR(80) | NOT NULL |
| entity_id | VARCHAR(100) | NULL |
| message | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

#### `benchmark_records`

| Column | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| operation_name | VARCHAR(80) | NOT NULL |
| duration_ms | NUMERIC(12, 6) | NOT NULL |
| sample_size | INTEGER | NULL |
| metadata_json | JSONB | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

### 3.2 Suggested Enums

```python
class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    HASH_MISMATCH = "HASH_MISMATCH"
    DECRYPTION_FAILED = "DECRYPTION_FAILED"
    MALFORMED_PLAINTEXT = "MALFORMED_PLAINTEXT"
```

```python
class AuditEventType(str, Enum):
    VOTE_CAST = "VOTE_CAST"
    DOUBLE_VOTE_ATTEMPT = "DOUBLE_VOTE_ATTEMPT"
    INVALID_SIGNATURE_DETECTED = "INVALID_SIGNATURE_DETECTED"
    HASH_MISMATCH_DETECTED = "HASH_MISMATCH_DETECTED"
    DECRYPTION_FAILED = "DECRYPTION_FAILED"
    RECAPITULATION_STARTED = "RECAPITULATION_STARTED"
    RECAPITULATION_COMPLETED = "RECAPITULATION_COMPLETED"
```

---

## 4. Security and Cryptography Rules

### 4.1 Key Separation

Sistem wajib menggunakan dua pasang RSA-2048 key:

| Key Pair | Public Key | Private Key | Purpose |
|---|---|---|---|
| Admin Key Pair | `admin_public_key.pem` | `admin_private_key.pem` | Encrypt/decrypt vote plaintext |
| System Key Pair | `system_public_key.pem` | `system_private_key.pem` | Sign/verify ciphertext hash |

Rules:

- Jangan gunakan admin key untuk signing.
- Jangan gunakan system key untuk encryption.
- Jangan commit file `.pem` ke git.
- Simpan path key di environment variable.
- Untuk MVP, key boleh disimpan lokal di `app/keys`, tetapi harus masuk `.gitignore`.

### 4.2 RSA-OAEP Encryption

Gunakan:

- RSA key size: 2048 bit.
- Public exponent: 65537.
- Padding: OAEP.
- MGF: MGF1 dengan SHA-256.
- OAEP algorithm: SHA-256.
- Label: `None`.

Pseudo-code:

```python
ciphertext = admin_public_key.encrypt(
    plaintext_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
```

### 4.3 SHA-256 Hashing

Hash input harus berupa `ciphertext`, bukan plaintext.

Pseudo-code:

```python
digest = hashes.Hash(hashes.SHA256())
digest.update(ciphertext)
hash_hex = digest.finalize().hex()
```

### 4.4 RSA-PSS Signature

Signature input harus `hash_hex.encode("utf-8")` atau raw digest bytes. Pilih satu pendekatan dan konsisten.

Rekomendasi:

- Gunakan raw digest bytes untuk signing.
- Simpan hash sebagai hex string di DB.
- Saat verify, convert kembali hex ke bytes.

Pseudo-code:

```python
signature = system_private_key.sign(
    hash_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)
```

### 4.5 Verification Order

Rekapitulasi wajib memakai urutan ini:

1. Verify signature.
2. Recompute hash from ciphertext.
3. Compare stored hash with recomputed hash.
4. Decrypt ciphertext.
5. Parse plaintext.
6. Count vote.

Jika step 1 gagal:

- set status `INVALID_SIGNATURE`,
- create audit log,
- skip vote.

Jika step 2/3 gagal:

- set status `HASH_MISMATCH`,
- create audit log,
- skip vote.

Jika step 4 gagal:

- set status `DECRYPTION_FAILED`,
- create audit log,
- skip vote.

Jika step 5 gagal:

- set status `MALFORMED_PLAINTEXT`,
- create audit log,
- skip vote.

---

## 5. API and Page Plan

### 5.1 Routes

#### Voter Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Redirect ke `/login` |
| GET | `/login` | Render voter login page |
| POST | `/login` | Authenticate voter |
| GET | `/vote` | Render candidate selection page |
| POST | `/vote` | Cast vote |
| GET | `/vote/success` | Render success page |
| POST | `/logout` | Clear session |

#### Admin Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/login` | Render admin login page |
| POST | `/admin/login` | Authenticate admin |
| GET | `/admin/dashboard` | Render admin dashboard |
| POST | `/admin/recapitulate` | Run verification + recapitulation |
| GET | `/admin/results` | Show latest recap result |
| GET | `/admin/audit-logs` | Show audit logs |
| GET | `/admin/benchmarks` | Show benchmark results |

#### Development/Test Routes

Boleh dibuat hanya untuk local dev:

| Method | Path | Purpose |
|---|---|---|
| POST | `/dev/manipulate/ciphertext/{vote_id}` | Flip one byte ciphertext |
| POST | `/dev/manipulate/hash/{vote_id}` | Alter stored hash |
| POST | `/dev/manipulate/signature/{vote_id}` | Alter signature |

Development routes harus mudah dimatikan dengan env:

```env
ENABLE_DEV_ROUTES=false
```

---

## 6. Service Contracts

### 6.1 `CryptoService`

Required methods:

```python
class CryptoService:
    def encrypt_vote_plaintext(self, plaintext: str) -> bytes:
        ...

    def decrypt_vote_ciphertext(self, ciphertext: bytes) -> str:
        ...

    def hash_ciphertext(self, ciphertext: bytes) -> str:
        ...

    def sign_hash(self, hash_hex: str) -> bytes:
        ...

    def verify_signature(self, hash_hex: str, signature: bytes) -> bool:
        ...

    def verify_ciphertext_hash(self, ciphertext: bytes, expected_hash_hex: str) -> bool:
        ...
```

Maintainability notes:

- Jangan return tuple ambigu seperti `(result, error)`.
- Gunakan explicit exception untuk crypto failure.
- Jangan expose private key object keluar dari service.

### 6.2 `VotingService`

Required method:

```python
class VotingService:
    def cast_vote(self, nim: str, candidate_id: int) -> VoteCastResult:
        ...
```

Responsibilities:

1. Validate voter exists.
2. Validate voter has not voted.
3. Validate candidate exists.
4. Build vote plaintext.
5. Encrypt plaintext.
6. Hash ciphertext.
7. Sign hash.
8. Save vote record.
9. Mark voter as voted.
10. Create audit log.

Critical rule:

- Save vote and update `has_voted` in the same DB transaction.

### 6.3 `RecapitulationService`

Required method:

```python
class RecapitulationService:
    def recapitulate_votes(self) -> RecapitulationResult:
        ...
```

Responsibilities:

1. Load all vote records.
2. For each vote:
   - verify signature,
   - verify hash,
   - decrypt ciphertext,
   - parse plaintext,
   - validate candidate id,
   - count valid vote.
3. Update verification status per vote.
4. Create audit log for invalid vote.
5. Return recap summary.

Return shape:

```python
class RecapitulationResult(BaseModel):
    total_votes: int
    valid_votes: int
    invalid_votes: int
    candidate_results: list[CandidateVoteResult]
    invalid_vote_details: list[InvalidVoteDetail]
```

### 6.4 `BenchmarkService`

Required methods:

```python
class BenchmarkService:
    def measure_operation(self, operation_name: str, callback: Callable[[], Any]) -> BenchmarkResult:
        ...

    def run_crypto_benchmark(self, sample_size: int = 100) -> CryptoBenchmarkSummary:
        ...
```

Operations to measure:

- plaintext building,
- RSA-OAEP encryption,
- SHA-256 hashing,
- RSA-PSS signing,
- RSA-PSS verification,
- hash verification,
- RSA-OAEP decryption,
- full vote casting flow,
- full recapitulation flow.

---

## 7. Implementation Roadmap

## Day 1 — Project Foundation

Goal: project bisa running lokal dengan DB, migration, dan seed data.

### Tasks

1. Create FastAPI project structure.
2. Add Dockerfile.
3. Add docker-compose.yml with:
   - `app`,
   - `postgres`.
4. Add `.env.example`.
5. Add SQLAlchemy database connection.
6. Add Alembic migration setup.
7. Create models:
   - `Voter`,
   - `Candidate`,
   - `VoteRecord`,
   - `AuditLog`,
   - `BenchmarkRecord`.
8. Create initial migration.
9. Create seed script:
   - 500 voters,
   - 3 candidates,
   - 1 admin credential through env or simple config.
10. Create basic templates:
   - login,
   - vote,
   - admin dashboard.

### Acceptance Criteria

- `docker compose up --build` works.
- App is accessible at `http://localhost:8000`.
- PostgreSQL container healthy.
- Alembic migration runs successfully.
- Seed script inserts 500 voters and 3 candidates.
- `/login` page renders.
- `/admin/login` page renders.

---

## Day 2 — Cryptography Pipeline

Goal: semua operasi crypto selesai dan teruji secara unit test.

### Tasks

1. Implement `scripts/generate_keys.py`.
2. Generate:
   - admin public/private key,
   - system public/private key.
3. Implement `CryptoService`.
4. Implement unit tests:
   - encryption produces bytes,
   - decryption returns original plaintext,
   - same plaintext encrypted twice produces different ciphertext,
   - hash length is 64 hex characters,
   - same ciphertext produces same hash,
   - modified ciphertext produces different hash,
   - signature verification succeeds for valid hash/signature,
   - signature verification fails for modified hash,
   - signature verification fails for modified signature.
5. Implement plaintext builder utility.
6. Implement plaintext parser utility.

### Acceptance Criteria

- `pytest tests/test_crypto_service.py` passes.
- RSA-OAEP encryption and decryption works.
- RSA-PSS sign and verify works.
- SHA-256 hash verification works.
- Plaintext parser validates format strictly.

---

## Day 3 — Voting and Recapitulation Flow

Goal: voter bisa vote, admin bisa rekapitulasi, manipulasi bisa ditolak.

### Tasks

1. Implement `AuthService`.
2. Implement voter login session.
3. Implement admin login session.
4. Implement `VotingService.cast_vote()`.
5. Implement `VoteRepository`.
6. Implement `VoterRepository`.
7. Implement `CandidateRepository`.
8. Implement `AuditLogRepository`.
9. Implement voting UI:
   - list candidate,
   - submit vote,
   - success page.
10. Implement `RecapitulationService.recapitulate_votes()`.
11. Implement admin dashboard.
12. Implement result page.
13. Implement audit log page.
14. Implement dev manipulation script:
   - mutate ciphertext,
   - mutate hash,
   - mutate signature.

### Acceptance Criteria

- Voter can login.
- Voter can vote once.
- Same voter cannot vote twice.
- Vote record contains ciphertext, hash, and signature.
- Admin can trigger recapitulation.
- Valid votes are counted.
- Invalid votes are skipped.
- Audit logs are created for invalid vote.

---

## Day 4 — Testing, Benchmark, Documentation

Goal: prototype siap demo dan hasil eksperimen bisa dipakai dalam laporan.

### Tasks

1. Add test for double vote prevention.
2. Add test for manipulated ciphertext.
3. Add test for manipulated hash.
4. Add test for manipulated signature.
5. Add benchmark script.
6. Store benchmark results in DB.
7. Add benchmark page.
8. Add README setup instructions.
9. Add demo scenario.
10. Add limitations section.
11. Run final smoke test.
12. Clean unused code.
13. Check naming consistency.
14. Check service boundaries.

### Acceptance Criteria

- All tests pass.
- Unit tests for crypto, plaintext, and service logic pass.
- Benchmark result available.
- Demo flow documented.
- README explains setup from zero.
- Manipulation detection demonstrable.
- No route contains direct crypto logic.
- No route contains direct SQLAlchemy query.

---

## 8. Testing Plan

### 8.1 Unit Tests

Unit testing wajib dibuat dengan Pytest untuk logic yang tidak bergantung langsung pada HTTP route atau template.
Minimal unit test harus mencakup crypto pipeline, plaintext builder/parser, voting service, recapitulation service, dan error handling utama.

#### Crypto Tests

- Encrypt/decrypt returns original plaintext.
- OAEP generates different ciphertext for same plaintext.
- SHA-256 hash length is 64 hex chars.
- Hash changes when ciphertext changes.
- PSS signature verifies valid hash.
- PSS signature rejects modified hash.
- PSS signature rejects modified signature.

#### Plaintext Tests

- Valid plaintext can be parsed.
- Missing nim is rejected.
- Missing candidate_id is rejected.
- Missing timestamp is rejected.
- Invalid candidate_id format is rejected.

#### Service Unit Tests

- `VotingService.cast_vote()` rejects unknown voter.
- `VotingService.cast_vote()` rejects voter that already voted.
- `VotingService.cast_vote()` rejects unknown candidate.
- `VotingService.cast_vote()` calls crypto pipeline in the required order.
- `RecapitulationService.recapitulate_votes()` skips invalid signature.
- `RecapitulationService.recapitulate_votes()` skips hash mismatch.
- `RecapitulationService.recapitulate_votes()` skips malformed plaintext.
- Domain-specific exceptions are raised consistently.

### 8.2 Integration Tests

- Voter can cast vote.
- Voter cannot cast vote twice.
- Vote and `has_voted` update are atomic.
- Admin can run recapitulation.
- Recap count is correct for valid votes.

### 8.3 Security Manipulation Tests

Test cases:

| Test ID | Manipulation | Expected Result |
|---|---|---|
| SEC-01 | Modify one byte of ciphertext | Hash mismatch or signature invalid |
| SEC-02 | Modify stored hash | Signature invalid or hash mismatch |
| SEC-03 | Modify signature | Invalid signature |
| SEC-04 | Delete ciphertext bytes | Invalid signature / hash mismatch / decryption failed |
| SEC-05 | Replace ciphertext from another record | Invalid signature or malformed vote consistency |

### 8.4 Benchmark Tests

Measure average duration in milliseconds:

- encryption,
- hashing,
- signing,
- signature verification,
- hash verification,
- decryption,
- full voting flow,
- full recapitulation for 500 votes.

Benchmark output example:

```txt
Operation                  Avg Duration (ms)
RSA-OAEP Encryption        0.850
SHA-256 Hashing            0.030
RSA-PSS Signing            1.250
RSA-PSS Verification       0.070
RSA-OAEP Decryption        1.500
Full Recap 500 Votes       820.000
```

---

## 9. UI Plan

UI harus sederhana dan fungsional.
Desain website harus sejalan dengan konteks mahasiswa: ringan, mudah dipahami, modern secukupnya, dan cocok untuk prototype akademik.
Tema warna utama website adalah `#bfa344`; gunakan sebagai warna aksen utama untuk tombol, highlight, dan elemen identitas visual.

### 9.1 Pages

#### Login Page

Fields:

- nim,
- password.

Actions:

- login,
- link to admin login.

#### Vote Page

Displays:

- voter name,
- candidate list,
- vote button.

Rules:

- If voter already voted, redirect to success/already-voted page.

#### Admin Dashboard

Displays:

- total voters,
- total candidates,
- total vote records,
- total audit logs,
- button: run recapitulation,
- link: audit logs,
- link: benchmark.

#### Recap Result Page

Displays:

- total votes,
- valid votes,
- invalid votes,
- table candidate result,
- table invalid vote details.

#### Audit Logs Page

Displays:

- timestamp,
- event type,
- entity type,
- entity id,
- message.

#### Benchmark Page

Displays:

- operation name,
- duration ms,
- sample size,
- created_at.

---

## 10. Environment Configuration

Create `.env.example`:

```env
APP_NAME="E-Voting RSA SHA-256"
APP_ENV=local
APP_DEBUG=true
APP_SECRET_KEY=change-this-secret

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/evoting_db

POSTGRES_DB=evoting_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

ADMIN_PRIVATE_KEY_PATH=app/keys/admin_private_key.pem
ADMIN_PUBLIC_KEY_PATH=app/keys/admin_public_key.pem
SYSTEM_PRIVATE_KEY_PATH=app/keys/system_private_key.pem
SYSTEM_PUBLIC_KEY_PATH=app/keys/system_public_key.pem

ENABLE_DEV_ROUTES=true
```

Rules:

- `.env` must not be committed.
- `.pem` files must not be committed.
- `.env.example` should be committed.

---

## 11. Docker Plan

### 11.1 `docker-compose.yml`

Services:

- `postgres`
- `app`

Requirements:

- PostgreSQL volume.
- Healthcheck for postgres.
- App depends on postgres healthcheck.
- Port mapping `8000:8000`.

### 11.2 Required Commands

```bash
docker compose up --build
```

```bash
docker compose exec app alembic upgrade head
```

```bash
docker compose exec app python scripts/generate_keys.py
```

```bash
docker compose exec app python scripts/seed_data.py
```

```bash
docker compose exec app pytest
```

---

## 12. Codex Task Execution Order

Agent must execute tasks in this exact order:

1. Inspect repository.
2. Create/update `planning.md` if needed.
3. Create project skeleton.
4. Add dependencies.
5. Configure environment loading.
6. Configure database connection.
7. Configure SQLAlchemy models.
8. Configure Alembic.
9. Add initial migration.
10. Add seed script.
11. Add key generation script.
12. Implement `CryptoService`.
13. Add crypto tests.
14. Implement repositories.
15. Implement auth service.
16. Implement voting service.
17. Implement recapitulation service.
18. Implement audit service.
19. Implement benchmark service.
20. Implement routers.
21. Implement templates.
22. Implement dev manipulation scripts/routes.
23. Add integration tests.
24. Add README.
25. Run full test.
26. Fix issues.
27. Self-review architecture.

---

## 13. Suggested Dependencies

Create `requirements.txt`:

```txt
fastapi
uvicorn[standard]
jinja2
python-multipart
sqlalchemy>=2.0
psycopg[binary]
alembic
pydantic
pydantic-settings
cryptography
passlib[bcrypt]
pytest
httpx
```

Optional:

```txt
ruff
mypy
```

If adding `ruff`, configure basic linting but do not block MVP if time is limited.

---

## 14. Error Handling Strategy

Use clear custom exceptions:

```python
class VoterNotFoundError(Exception):
    pass

class VoterAlreadyVotedError(Exception):
    pass

class CandidateNotFoundError(Exception):
    pass

class InvalidSignatureError(Exception):
    pass

class HashMismatchError(Exception):
    pass

class VoteDecryptionError(Exception):
    pass

class MalformedVotePlaintextError(Exception):
    pass
```

Rules:

- Service raises domain-specific exceptions.
- Router converts exceptions into HTTP response or UI error message.
- Crypto exception details should not leak private key/path internals to UI.
- Audit logs should store enough information for debugging.

---

## 15. Transaction Rules

Voting transaction must be atomic:

```txt
BEGIN
  validate voter has_voted = false
  insert vote record
  update voter has_voted = true
  insert audit log
COMMIT
```

If any step fails:

```txt
ROLLBACK
```

Reason:

- Prevent vote record saved without voter marked as voted.
- Prevent voter marked as voted without vote record.
- Prevent inconsistent data during demo/testing.

---

## 16. Manipulation Demo Scenario

Use this scenario for final demo:

### Scenario A — Normal Voting

1. Seed database.
2. Login as voter `122140191`.
3. Vote candidate A.
4. Login as voter `122140192`.
5. Vote candidate B.
6. Admin runs recapitulation.
7. System shows 2 valid votes.

### Scenario B — Double Vote Prevention

1. Login again as `122140191`.
2. Try voting again.
3. System rejects with already voted message.

### Scenario C — Ciphertext Manipulation

1. Run script to flip one byte ciphertext.
2. Admin runs recapitulation.
3. System marks vote invalid.
4. Audit log records manipulation.

### Scenario D — Hash Manipulation

1. Run script to change one character in stored hash.
2. Admin runs recapitulation.
3. System marks vote invalid.
4. Audit log records hash mismatch or invalid signature.

### Scenario E — Signature Manipulation

1. Run script to alter signature bytes.
2. Admin runs recapitulation.
3. System marks vote invalid signature.
4. Audit log records invalid signature.

---

## 17. README Requirements

README must contain:

1. Project title.
2. Short description.
3. Tech stack.
4. Architecture overview.
5. Crypto pipeline.
6. Prerequisites.
7. Setup instructions.
8. How to generate keys.
9. How to run migration.
10. How to seed data.
11. How to run app.
12. How to run tests.
13. How to run benchmark.
14. How to demo manipulation detection.
15. Limitations.

---

## 18. Definition of Done

Project is considered done when:

- App runs with Docker Compose.
- Migration works.
- Seed works.
- RSA keys can be generated.
- Voter can login.
- Voter can vote once.
- Vote is encrypted, hashed, signed, and stored.
- Admin can run recapitulation.
- Valid votes are counted correctly.
- Manipulated ciphertext/hash/signature is detected.
- Audit log records invalid vote.
- Benchmark records are generated.
- Tests pass.
- README explains how to run everything.
- Code follows separation of concerns.
- No private key is committed.

---

## 19. Potential Risks

### 19.1 Scope Creep

Risk:

- Agent may try to add OAuth, complex UI, or production deployment.

Mitigation:

- Stick to MVP.
- Use dummy auth.
- Server-rendered UI only.

### 19.2 Crypto Misuse

Risk:

- Agent may implement textbook RSA manually.
- Agent may sign plaintext instead of hash.
- Agent may hash plaintext instead of ciphertext.

Mitigation:

- Use `cryptography` library.
- Enforce crypto pipeline exactly as defined.
- Add unit tests.

### 19.3 Inconsistent Vote State

Risk:

- Vote saved but voter not marked as voted.
- Voter marked as voted but vote not saved.

Mitigation:

- Use DB transaction.
- Add unique constraint on `vote_records.nim`.

### 19.4 Weak Demo Data

Risk:

- Not enough data for benchmark.

Mitigation:

- Seed 500 voters.
- Add script to cast simulated votes if needed.

### 19.5 UI Takes Too Much Time

Risk:

- Styling consumes too much time.

Mitigation:

- Use Bootstrap/Tailwind CDN.
- Keep UI functional and minimal.

---

## 20. Self Review / Refactor Suggestions

After implementation, agent must review:

1. Are routes thin?
2. Is crypto logic isolated in `CryptoService`?
3. Are DB queries isolated in repository classes?
4. Is vote casting atomic?
5. Is verification order correct?
6. Are private keys excluded from git?
7. Are names descriptive?
8. Are there any files larger than necessary?
9. Are there duplicate crypto/hash/signature functions?
10. Are tests covering manipulation detection?
11. Can a new developer understand the folder structure quickly?
12. Can the demo be run from README only?

Refactor if:

- Router contains business logic.
- Service directly renders templates.
- Repository performs cryptography.
- Crypto service accesses database.
- Same query appears in multiple files.
- Same validation appears in multiple services.
- Function names are vague, such as `process_data`, `handle`, `do_vote`, or `check`.

---

## 21. Final Instruction for Agentic AI Codex

Implement the project incrementally.

Do not generate all code blindly in one pass.

Work by milestones:

1. Foundation.
2. Crypto.
3. Voting.
4. Recapitulation.
5. Manipulation testing.
6. Benchmark.
7. Documentation.

After each milestone:

- run relevant tests,
- fix errors,
- keep code modular,
- document important decisions.

The final system must prioritize correctness, maintainability, and demonstrability over visual polish.
