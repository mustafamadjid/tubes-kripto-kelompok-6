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
docker compose exec app alembic upgrade head
docker compose exec app python scripts/generate_keys.py
docker compose exec app python scripts/seed_data.py
```

Buka:

```txt
http://localhost:8000
```

Credential demo:

- Voter ID: `VOTER001`
- Voter password: `password123`
- Admin username: `admin`
- Admin password: `admin123`

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
- Auth memakai session sederhana.
- Tidak ada OAuth, MFA, real-time dashboard, blockchain, atau HSM.
