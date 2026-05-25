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


---

## Cara Menjalankan (1 Command)

```bash
# Clone repo, lalu:
./setup.sh
```

Script ini otomatis: build Docker image, start PostgreSQL + app, jalankan migrasi, generate RSA key pairs, dan seed data demo.

Untuk reset ulang dari nol (hapus semua data):

```bash
./setup.sh --reset
```

**Syarat:** Docker dan Docker Compose sudah terinstall.

---

## Akun Demo

Setelah setup selesai, gunakan akun-akun berikut:

### Voter

| NIM | Password | Status |
|---|---|---|
| `122140001` | `password123` | Belum vote |
| `122140002` | `password123` | Belum vote |
| `122140003` | `password123` | Belum vote |
| `122140099` | `password123` | Sudah vote (untuk uji double vote) |

### Admin

| Username | Password |
|---|---|
| `admin` | `admin123` |

---

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

---

## Skenario Demo Lengkap

### Skenario 1 — Vote Normal (Happy Path)

**Tujuan:** Membuktikan alur enkripsi, signing, dan penyimpanan vote berjalan benar.

1. Buka http://localhost:8000/login
2. Login dengan NIM `122140001`, password `password123`
3. Pilih salah satu kandidat, klik **Kirim Suara**
4. Catat **Vote ID** yang tampil di halaman sukses
5. Login admin → Dashboard → klik **Run Recapitulation**
6. Buka halaman **Results** — suara voter terhitung di kandidat yang dipilih dengan status `VALID`

**Yang terjadi di balik layar:**
- Plaintext `nim:122140001|candidate_id:1|timestamp:...` dibentuk
- Dienkripsi dengan RSA-2048 OAEP menggunakan public key admin
- Hash SHA-256 dari ciphertext dihitung
- Hash ditandatangani dengan RSA-PSS menggunakan system private key
- Ketiganya disimpan ke tabel `vote_records`

---

### Skenario 2 — Double Vote (Pencegahan)

**Tujuan:** Membuktikan sistem menolak voter yang mencoba memilih dua kali.

1. Login dengan NIM `122140099` (akun yang sudah vote di seed)
2. Coba kirim suara ke kandidat manapun
3. Sistem menampilkan error: **"Voter already voted"**
4. Login admin → **Audit Logs** — tampak event `DOUBLE_VOTE_ATTEMPT` tercatat dengan nim `122140099`

---

### Skenario 3 — Manipulasi Ciphertext (Deteksi Hash Mismatch)

**Tujuan:** Membuktikan hash SHA-256 mendeteksi perubahan data vote.

1. Jalankan vote normal dulu (Skenario 1) — catat Vote ID
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
4. Keluar dari psql: `\q`
5. Login admin → **Run Recapitulation**
6. Buka **Results** → bagian **Invalid Vote Details** — vote tersebut muncul dengan status `HASH_MISMATCH`
7. Buka **Audit Logs** — ada event `HASH_MISMATCH_DETECTED`

---

### Skenario 4 — Manipulasi Signature (Deteksi Invalid Signature)

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
3. Keluar: `\q`
4. Login admin → **Run Recapitulation**
5. **Invalid Vote Details** — status `INVALID_SIGNATURE`
6. **Audit Logs** — event `INVALID_SIGNATURE_DETECTED`

---

### Skenario 5 — Verifikasi Integrity Keseluruhan

**Tujuan:** Membuktikan sistem bisa membedakan vote valid dan tidak valid secara bersamaan.

1. Vote dengan NIM `122140001` → valid
2. Vote dengan NIM `122140002` → valid
3. Manipulasi salah satu record (Skenario 3 atau 4)
4. **Run Recapitulation**
5. Di **Results**: `total_votes=2, valid_votes=1, invalid_votes=1`
6. Tabel kandidat hanya menghitung suara dari vote yang valid

---

## Arsitektur Sistem

```
Voter Browser
    │
    ▼
[POST /vote]  →  VotingService.cast_vote()
                    │
                    ├─ build_vote_plaintext()
                    │    nim:{nim}|candidate_id:{id}|timestamp:{ts}
                    │
                    ├─ CryptoService.encrypt_vote_plaintext()
                    │    RSA-2048 OAEP (public key admin)
                    │
                    ├─ CryptoService.hash_ciphertext()
                    │    SHA-256
                    │
                    └─ CryptoService.sign_hash()
                         RSA-PSS (system private key)
                              │
                              ▼
                        vote_records table
                        (ciphertext, ciphertext_hash, signature)

Admin Browser
    │
    ▼
[POST /admin/recapitulate]  →  RecapitulationService.recapitulate_votes()
                                    │
                                    ├─ verify_signature()     → INVALID_SIGNATURE
                                    ├─ verify_ciphertext_hash() → HASH_MISMATCH
                                    ├─ decrypt_vote_ciphertext() → DECRYPTION_FAILED
                                    └─ parse_vote_plaintext()  → MALFORMED_PLAINTEXT
```

---

## Struktur Direktori

```
.
├── setup.sh                    ← 1-command setup
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── alembic/                    ← migrasi database
└── app/
    ├── domain/                 ← plaintext format, enums, exceptions
    ├── models/                 ← SQLAlchemy models (voters, candidates, vote_records, audit_logs)
    ├── repositories/           ← data access layer
    ├── routers/                ← HTTP endpoints (auth, voter, admin)
    ├── services/
    │   ├── auth_service.py     ← autentikasi NIM + SHA-256 password
    │   ├── crypto_service.py   ← RSA encrypt/decrypt/sign/verify
    │   ├── voting_service.py   ← alur casting vote
    │   └── recapitulation_service.py ← verifikasi & penghitungan
    ├── static/styles.css
    └── templates/              ← Jinja2 HTML templates
```

---

## Environment Variables

Salin `.env.example` ke `.env` (dilakukan otomatis oleh `setup.sh`):

| Variable | Default | Keterangan |
|---|---|---|
| `DATABASE_URL` | postgresql://postgres:postgres@postgres:5432/evoting_db | Koneksi DB |
| `ADMIN_USERNAME` | admin | Username admin |
| `ADMIN_PASSWORD` | admin123 | Password admin |
| `APP_SECRET_KEY` | change-this-secret | Secret untuk session cookie |
| `RUN_MIGRATIONS` | true | Jalankan alembic otomatis saat startup |
| `GENERATE_KEYS_IF_MISSING` | true | Generate RSA keys jika belum ada |
| `ENABLE_DEV_ROUTES` | true | Aktifkan endpoint seeding data demo |

---

## Commands Berguna

```bash
# Lihat log aplikasi
docker compose logs -f app

# Akses database langsung
docker compose exec postgres psql -U postgres -d evoting_db

# Stop semua container
docker compose down

# Reset total (hapus semua data dan volume)
./setup.sh --reset
```
## Limitations

- Prototype akademik, bukan sistem pemilu production-grade.
- Password hashing dibuat sederhana untuk demo lokal.
- Key RSA disimpan di filesystem lokal dan tidak boleh di-commit.
- Auth memakai session sederhana.
- Tidak ada OAuth, MFA, real-time dashboard, blockchain, atau HSM.


