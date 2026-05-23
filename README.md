# E-Voting RSA SHA-256

Prototype sistem e-voting untuk tugas kriptografi. Sistem ini memakai RSA-2048 OAEP untuk enkripsi suara, SHA-256 untuk hash ciphertext, dan RSA-2048 PSS untuk signature hash.

## Tech Stack

- FastAPI + Jinja2
- SQLAlchemy 2.x + Alembic
- PostgreSQL 16
- `cryptography`, `authlib`
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

## Auth

Sistem mendukung dua metode login:

1. **Manual** — Voter ID + password, Admin username + password (tetap tersedia).
2. **Google OAuth** — Login via akun Google, mendukung dua mode:

| Mode | `OAUTH_MODE` | Domain | voter_id di DB |
|---|---|---|---|
| Demo/simulasi | `demo` | bebas (misal `gmail.com`) | username sebelum `@`, titik → underscore |
| Production ITERA | `production` | `student.itera.ac.id` | NIM 9 digit dari email |

Contoh mode production: `muhammad.123140148@student.itera.ac.id` → `voter_id = "123140148"`

Contoh mode demo: `budi.santoso@gmail.com` → `voter_id = "budi_santoso"`

## Setup — Mode Demo (simulasi lokal)

Cocok untuk pengembangan dan presentasi tanpa akun ITERA asli.

```bash
cp .env.demo.example .env
# Edit .env: isi GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ADMIN_GOOGLE_EMAILS
docker compose up --build
```

Di terminal lain:

```bash
docker compose exec app alembic upgrade head
docker compose exec app python scripts/generate_keys.py
docker compose exec app python scripts/seed_data.py --demo
```

Buka:

```txt
http://localhost:8000
```

Credential demo (login manual):

- Voter ID: sesuai `voter_id` di `DEMO_VOTERS` pada `scripts/seed_data.py`
- Voter password: `password123`
- Admin username: `admin`
- Admin password: `admin123`

Login Google: gunakan akun Gmail yang sudah ditambahkan sebagai test user di Google Cloud Console dan voter_id-nya terdaftar di database.

## Setup — Mode Production (ITERA)

Digunakan setelah Google Cloud app di-publish dan domain `student.itera.ac.id` siap.

```bash
cp .env.production.example .env
# Edit .env: isi semua variabel termasuk APP_BASE_URL production
docker compose up --build
```

Di terminal lain:

```bash
docker compose exec app alembic upgrade head
docker compose exec app python scripts/generate_keys.py
docker compose exec app python scripts/seed_data.py --prod
```

Edit `PRODUCTION_VOTERS` di `scripts/seed_data.py` terlebih dahulu — isi dengan NIM mahasiswa peserta voting.

## Setup Google Cloud Console

1. Buat project di [console.cloud.google.com](https://console.cloud.google.com)
2. APIs & Services → OAuth consent screen → External → isi nama app
3. Credentials → Create Credentials → OAuth Client ID → Web Application
4. Tambahkan Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback/voter` (dev)
   - `http://localhost:8000/auth/google/callback/admin` (dev)
   - `https://domain-production/auth/google/callback/voter` (prod)
   - `https://domain-production/auth/google/callback/admin` (prod)
5. Copy Client ID dan Client Secret ke `.env`
6. Untuk mode demo: tambahkan akun Gmail peserta sebagai test user di consent screen

## Kelola Kandidat

Admin dapat menambah, mengubah, dan menghapus kandidat melalui dashboard:

```txt
http://localhost:8000/admin/dashboard → Kelola Kandidat
```

Kandidat juga bisa di-seed awal melalui `scripts/seed_data.py` (edit bagian `CANDIDATES`).

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

## Manipulation Demo

1. Login sebagai voter dan lakukan vote.
2. Ambil `vote_id` dari halaman sukses atau database.
3. Manipulasi data:

```bash
docker compose exec app python scripts/manipulate_vote.py <vote_id> ciphertext
docker compose exec app python scripts/manipulate_vote.py <vote_id> hash
docker compose exec app python scripts/manipulate_vote.py <vote_id> signature
```

4. Login admin.
5. Jalankan recapitulation.
6. Buka audit logs untuk melihat vote invalid.

## Limitations

- Prototype akademik, bukan sistem pemilu production-grade.
- Password hashing dibuat sederhana untuk demo lokal.
- Key RSA disimpan di filesystem lokal dan tidak boleh di-commit.
- Auth memakai session sederhana + Google OAuth (tanpa MFA, HSM, atau blockchain).
- Hapus kandidat setelah ada vote dapat mempengaruhi hasil rekapitulasi.
