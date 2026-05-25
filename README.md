# E-Voting RSA SHA-256

Prototype sistem e-voting untuk tugas kriptografi. Sistem ini memakai RSA-2048 OAEP untuk enkripsi suara, SHA-256 untuk hash ciphertext, dan RSA-2048 PSS untuk signature hash.

## Tech Stack

- FastAPI + Jinja2
- SQLAlchemy 2.x + Alembic
- PostgreSQL 16
- `cryptography`
- Pytest
- Docker Compose

## Architecture

Project memakai modular monolith:

- `routers`: HTTP endpoint dan rendering template.
- `services`: use case seperti voting, rekapitulasi, crypto, benchmark.
- `repositories`: akses database.
- `models`: SQLAlchemy model.
- `domain`: enum, exception, plaintext builder/parser.

## Crypto Pipeline

Voting:

```txt
plaintext suara -> RSA-OAEP encryption -> ciphertext -> SHA-256 hash(ciphertext) -> RSA-PSS sign(hash) -> save
```

Rekapitulasi:

```txt
verify signature -> recompute hash -> decrypt ciphertext -> parse plaintext -> count vote
```

## Setup

```bash
cp .env.example .env
docker compose up --build
```

Di terminal lain:

```bash
docker compose exec app python scripts/seed_data.py
```

Migration dan RSA key generation berjalan otomatis saat container app start. Jangan regenerate key untuk election yang sudah punya vote, karena vote lama membutuhkan key yang sama untuk verifikasi dan dekripsi.

Buka:

```txt
http://localhost:8000
```

## Akun Demo

Setelah setup selesai, gunakan akun-akun berikut.

### Voter

| NIM | Password | Status |
|---|---|---|
| `122140001` | `password123` | Belum vote |
| `122140002` | `password123` | Belum vote |
| `122140003` | `password123` | Belum vote |
| `122140099` | `password123` | Sudah vote, untuk uji double vote |

### Admin

| Username | Password |
|---|---|
| `admin` | `admin123` |

## URL Aplikasi

| Halaman | URL |
|---|---|
| Login Voter | http://localhost:8000/login |
| Voting | http://localhost:8000/vote |
| Login Admin | http://localhost:8000/admin/login |
| Dashboard Admin | http://localhost:8000/admin/dashboard |
| Rekapitulasi | http://localhost:8000/admin/results |
| Audit Logs | http://localhost:8000/admin/audit-logs |
| Benchmarks | http://localhost:8000/admin/benchmarks |

## Deploy ke Server dengan Docker

Gunakan file produksi agar PostgreSQL tidak terbuka ke publik, container auto-restart, migration berjalan saat app start, dan RSA key tersimpan di Docker volume.

1. Copy env produksi:

```bash
cp .env.production.example .env
```

2. Edit `.env` di server:

```env
APP_SECRET_KEY=isi-dengan-random-secret-panjang
POSTGRES_PASSWORD=isi-password-db-kuat
DATABASE_URL=postgresql+psycopg://evoting_user:isi-password-db-kuat@postgres:5432/evoting_db
ADMIN_PASSWORD=isi-password-admin-kuat
ENABLE_DEV_ROUTES=false
```

Pastikan password di `DATABASE_URL` sama dengan `POSTGRES_PASSWORD`.

3. Build dan jalankan:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

4. Lihat status:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f app
```

5. Seed data demo hanya jika memang dibutuhkan:

```bash
docker compose -f docker-compose.prod.yml exec app python scripts/seed_data.py
```

6. Buka aplikasi:

```txt
http://SERVER_IP:8000
```

Untuk domain production, letakkan reverse proxy seperti Nginx/Caddy di depan port app, lalu arahkan HTTPS ke container app port `8000`.

### Catatan Persistensi

- Data PostgreSQL disimpan di volume `postgres_data`.
- RSA key disimpan di volume `rsa_keys`.
  - Local compose: mounted ke `/app/app/keys`.
  - Production compose: mounted ke `/data/keys`.
- Jangan jalankan `docker compose down -v` atau `docker compose -f docker-compose.prod.yml down -v` kecuali ingin menghapus database dan RSA key.
- Jika RSA key hilang sementara database vote masih ada, vote lama tidak bisa diverifikasi atau didekripsi ulang.
- `python scripts/generate_keys.py` tidak menimpa key yang sudah ada. Gunakan `python scripts/generate_keys.py --force` hanya untuk election baru/fresh database.

## Run Tests

```bash
pytest
```

atau di Docker:

```bash
docker compose exec app pytest
```

## Run Benchmark

```bash
docker compose exec app python scripts/run_benchmark.py
```

Lihat hasil di:

```txt
http://localhost:8000/admin/benchmarks
```

## Skenario Demo Lengkap

### Skenario 1 - Vote Normal (Happy Path)

**Tujuan:** Membuktikan alur enkripsi, signing, dan penyimpanan vote berjalan benar.

1. Buka http://localhost:8000/login.
2. Login dengan NIM `122140001`, password `password123`.
3. Pilih salah satu kandidat, lalu klik **Kirim Suara**.
4. Catat **Vote ID** yang tampil di halaman sukses.
5. Login admin, buka **Dashboard**, lalu klik **Run Recapitulation**.
6. Buka halaman **Results**. Suara voter terhitung pada kandidat yang dipilih dengan status `VALID`.

Yang terjadi di balik layar:

- Plaintext `nim:122140001|candidate_id:1|timestamp:...` dibentuk.
- Plaintext dienkripsi dengan RSA-2048 OAEP menggunakan public key admin.
- Hash SHA-256 dari ciphertext dihitung.
- Hash ditandatangani dengan RSA-PSS menggunakan system private key.
- Ciphertext, hash, dan signature disimpan ke tabel `vote_records`.

### Skenario 2 - Double Vote (Pencegahan)

**Tujuan:** Membuktikan sistem menolak voter yang mencoba memilih dua kali.

1. Buka http://localhost:8000/login.
2. Login dengan NIM `122140099`, password `password123`.
3. Coba kirim suara ke kandidat manapun.
4. Sistem menampilkan error seperti `Voter 122140099 already voted`.
5. Login admin, lalu buka **Audit Logs**.
6. Event `DOUBLE_VOTE_ATTEMPT` tercatat dengan NIM `122140099`.

### Skenario 3 - Manipulasi Ciphertext (Deteksi Hash Mismatch)

**Tujuan:** Membuktikan hash SHA-256 mendeteksi perubahan data vote.

1. Jalankan vote normal dari Skenario 1, lalu catat Vote ID.
2. Akses database langsung:

```bash
docker compose exec postgres psql -U postgres -d evoting_db
```

3. Manipulasi ciphertext salah satu vote:

```sql
UPDATE vote_records
SET ciphertext = '\x00000000'
WHERE id = '<vote-id-dari-langkah-1>';
```

4. Keluar dari psql:

```sql
\q
```

5. Login admin, lalu klik **Run Recapitulation**.
6. Buka **Results**, lalu cek bagian **Invalid Vote Details**. Vote tersebut muncul dengan status `HASH_MISMATCH`.
7. Buka **Audit Logs**. Event `HASH_MISMATCH_DETECTED` tercatat.

Alternatif tanpa masuk psql:

```bash
docker compose exec app python scripts/manipulate_vote.py <vote-id> ciphertext
```

### Skenario 4 - Manipulasi Signature (Deteksi Invalid Signature)

**Tujuan:** Membuktikan RSA-PSS mendeteksi signature yang dipalsukan.

1. Akses database:

```bash
docker compose exec postgres psql -U postgres -d evoting_db
```

2. Korupsi signature salah satu vote:

```sql
UPDATE vote_records
SET signature = '\xdeadbeef'
WHERE id = '<vote-id>';
```

3. Keluar dari psql:

```sql
\q
```

4. Login admin, lalu klik **Run Recapitulation**.
5. Buka **Results**, lalu cek bagian **Invalid Vote Details**. Vote tersebut muncul dengan status `INVALID_SIGNATURE`.
6. Buka **Audit Logs**. Event `INVALID_SIGNATURE_DETECTED` tercatat.

Alternatif tanpa masuk psql:

```bash
docker compose exec app python scripts/manipulate_vote.py <vote-id> signature
```

### Skenario 5 - Verifikasi Integrity Keseluruhan

**Tujuan:** Membuktikan sistem bisa membedakan vote valid dan tidak valid secara bersamaan.

1. Vote dengan NIM `122140001`, lalu pastikan Vote ID tercatat.
2. Vote dengan NIM `122140002`, lalu pastikan Vote ID tercatat.
3. Manipulasi salah satu record menggunakan Skenario 3 atau Skenario 4.
4. Login admin, lalu klik **Run Recapitulation**.
5. Di **Results**, pastikan ringkasan menunjukkan `total_votes=2`, `valid_votes=1`, dan `invalid_votes=1`.
6. Tabel kandidat hanya menghitung suara dari vote yang valid.

## Limitations

- Prototype akademik, bukan sistem pemilu production-grade.
- Password hashing dibuat sederhana untuk demo lokal.
- Key RSA disimpan di filesystem lokal dan tidak boleh di-commit.
- Auth memakai session sederhana.
- Tidak ada OAuth, MFA, real-time dashboard, blockchain, atau HSM.
