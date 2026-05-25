# Alur Encrypt, Hash, Digital Sign, dan Decrypt

Dokumen ini menjelaskan alur fungsi yang digunakan sistem saat vote dibuat sampai vote didekripsi lagi saat rekapitulasi.

## 1. Ringkasan Alur

Saat voter memilih kandidat, sistem tidak menyimpan plaintext suara. Sistem membuat plaintext, mengenkripsi plaintext menjadi ciphertext, menghitung hash dari ciphertext, menandatangani hash, lalu menyimpan hasilnya ke database.

```text
nim + candidate_id + timestamp
-> build plaintext
-> encrypt plaintext
-> hash ciphertext
-> sign hash
-> save ciphertext, hash, signature
```

Saat admin menjalankan rekapitulasi, sistem membaca vote record dari database, memverifikasi signature, memverifikasi hash, baru kemudian melakukan decrypt ciphertext dan parse plaintext.

```text
load ciphertext, hash, signature
-> verify signature
-> verify ciphertext hash
-> decrypt ciphertext
-> parse plaintext
-> count vote
```

## 2. Alur Saat Vote Dibuat

Fungsi utama:

- `VotingService.cast_vote`
- `build_vote_plaintext`
- `CryptoService.encrypt_vote_plaintext`
- `CryptoService.hash_ciphertext`
- `CryptoService.sign_hash`
- `VoteRepository.create_vote_record`

Lokasi file:

- `app/services/voting_service.py`
- `app/domain/plaintext.py`
- `app/services/crypto_service.py`
- `app/repositories/vote_repository.py`

### 2.1 Terima Data Vote

Alur voting dimulai dari:

```python
VotingService.cast_vote(nim, candidate_id)
```

Fungsi ini menerima:

- `nim`: identitas voter.
- `candidate_id`: kandidat yang dipilih.

Sebelum masuk ke proses kriptografi, fungsi ini mengecek:

- voter ada atau tidak melalui `voter_repository.find_by_nim`.
- voter sudah memilih atau belum.
- kandidat valid atau tidak melalui `candidate_repository.find_by_id`.

### 2.2 Membuat Plaintext

Plaintext dibuat oleh:

```python
build_vote_plaintext(nim, candidate_id, timestamp)
```

Format plaintext:

```text
nim:{nim}|candidate_id:{candidate_id}|timestamp:{timestamp}
```

Contoh:

```text
nim:122140191|candidate_id:2|timestamp:2026-05-22T14:30:00+07:00
```

Plaintext ini hanya dipakai sementara di memori program.

### 2.3 Encrypt Plaintext

Plaintext dienkripsi oleh:

```python
CryptoService.encrypt_vote_plaintext(plaintext)
```

Fungsi ini:

- mengubah plaintext string menjadi bytes dengan UTF-8.
- mengenkripsi plaintext memakai admin public key.
- memakai RSA-OAEP dengan SHA-256.
- menghasilkan `ciphertext` bertipe `bytes`.

Hasilnya:

```text
plaintext -> ciphertext
```

### 2.4 Hash Ciphertext

Ciphertext di-hash oleh:

```python
CryptoService.hash_ciphertext(ciphertext)
```

Fungsi ini:

- menghitung SHA-256 dari `ciphertext`.
- mengembalikan hash dalam bentuk hex string.

Hasilnya:

```text
ciphertext -> ciphertext_hash
```

Catatan penting: hash dibuat dari ciphertext, bukan dari plaintext.

### 2.5 Digital Sign Hash

Hash ditandatangani oleh:

```python
CryptoService.sign_hash(ciphertext_hash)
```

Fungsi ini:

- mengubah `ciphertext_hash` dari hex string menjadi bytes.
- menandatangani hash memakai system private key.
- memakai RSA-PSS dengan SHA-256.
- menghasilkan `signature` bertipe `bytes`.

Hasilnya:

```text
ciphertext_hash -> signature
```

### 2.6 Simpan Vote Record

Data vote disimpan oleh:

```python
VoteRepository.create_vote_record(nim, ciphertext, ciphertext_hash, signature)
```

Yang disimpan ke tabel `vote_records`:

- `nim`
- `ciphertext`
- `ciphertext_hash`
- `signature`

Plaintext tidak disimpan ke database.

## 3. Alur Saat Rekapitulasi dan Decrypt

Fungsi utama:

- `RecapitulationService.recapitulate_votes`
- `RecapitulationService._validate_and_count_vote`
- `CryptoService.verify_signature`
- `CryptoService.verify_ciphertext_hash`
- `CryptoService.decrypt_vote_ciphertext`
- `parse_vote_plaintext`
- `VoteRepository.update_verification_status`

Lokasi file:

- `app/services/recapitulation_service.py`
- `app/services/crypto_service.py`
- `app/domain/plaintext.py`
- `app/repositories/vote_repository.py`

### 3.1 Ambil Semua Vote

Rekapitulasi dimulai dari:

```python
RecapitulationService.recapitulate_votes()
```

Fungsi ini mengambil semua vote melalui:

```python
vote_repository.find_all_votes()
```

Setiap vote lalu diperiksa satu per satu oleh:

```python
RecapitulationService._validate_and_count_vote(vote, candidates, counts)
```

### 3.2 Verify Signature

Langkah pertama validasi adalah memverifikasi signature:

```python
CryptoService.verify_signature(vote.ciphertext_hash, vote.signature)
```

Fungsi ini:

- memakai system public key.
- memverifikasi apakah `signature` valid untuk `ciphertext_hash`.
- return `True` jika valid.
- return `False` jika signature tidak valid.

Jika gagal, vote diberi status:

```text
INVALID_SIGNATURE
```

Decrypt tidak dilakukan jika signature invalid.

### 3.3 Verify Hash Ciphertext

Jika signature valid, sistem memeriksa hash ciphertext:

```python
CryptoService.verify_ciphertext_hash(vote.ciphertext, vote.ciphertext_hash)
```

Fungsi ini:

- menghitung ulang SHA-256 dari `vote.ciphertext`.
- membandingkan hasil hash baru dengan `vote.ciphertext_hash`.

Di dalamnya fungsi ini memakai:

```python
CryptoService.hash_ciphertext(ciphertext)
```

Jika hash tidak cocok, vote diberi status:

```text
HASH_MISMATCH
```

Decrypt tidak dilakukan jika hash mismatch.

### 3.4 Decrypt Ciphertext

Jika signature dan hash valid, ciphertext baru didekripsi:

```python
CryptoService.decrypt_vote_ciphertext(vote.ciphertext)
```

Fungsi ini:

- memakai admin private key.
- mendekripsi ciphertext memakai RSA-OAEP dengan SHA-256.
- mengubah hasil bytes menjadi string UTF-8.
- menghasilkan plaintext suara.

Hasilnya:

```text
ciphertext -> plaintext
```

Jika dekripsi gagal, vote diberi status:

```text
DECRYPTION_FAILED
```

### 3.5 Parse Plaintext

Plaintext hasil decrypt diparse oleh:

```python
parse_vote_plaintext(plaintext)
```

Fungsi ini:

- memecah plaintext berdasarkan karakter `|`.
- membaca field `nim`, `candidate_id`, dan `timestamp`.
- mengubah `candidate_id` menjadi integer.
- memvalidasi format timestamp.
- mengembalikan `ParsedVotePlaintext`.

Jika format plaintext tidak valid, vote diberi status:

```text
MALFORMED_PLAINTEXT
```

### 3.6 Hitung Vote Valid

Jika plaintext valid dan `candidate_id` ada di daftar kandidat:

```python
vote_repository.update_verification_status(vote.id, VerificationStatus.VALID)
counts[parsed.candidate_id] += 1
```

Vote dianggap valid dan dihitung ke kandidat terkait.

## 4. Urutan Fungsi Utama

### 4.1 Urutan Encrypt sampai Save

```text
VotingService.cast_vote
-> build_vote_plaintext
-> CryptoService.encrypt_vote_plaintext
-> CryptoService.hash_ciphertext
-> CryptoService.sign_hash
-> VoteRepository.create_vote_record
```

### 4.2 Urutan Verify sampai Decrypt

```text
RecapitulationService.recapitulate_votes
-> VoteRepository.find_all_votes
-> RecapitulationService._validate_and_count_vote
-> CryptoService.verify_signature
-> CryptoService.verify_ciphertext_hash
-> CryptoService.decrypt_vote_ciphertext
-> parse_vote_plaintext
-> VoteRepository.update_verification_status
```

## 5. Data yang Disimpan

Model yang menyimpan hasil proses ini adalah:

```python
VoteRecord
```

Lokasi:

```text
app/models/vote_record.py
```

Field penting:

- `nim`
- `ciphertext`
- `ciphertext_hash`
- `signature`
- `verification_status`
- `manipulation_reason`

Yang tidak disimpan:

- plaintext suara.
- candidate pilihan dalam bentuk terbuka.

## 6. Poin Penting

- Enkripsi memakai `CryptoService.encrypt_vote_plaintext`.
- Hash memakai `CryptoService.hash_ciphertext`.
- Digital signature memakai `CryptoService.sign_hash`.
- Verifikasi signature memakai `CryptoService.verify_signature`.
- Verifikasi hash memakai `CryptoService.verify_ciphertext_hash`.
- Decrypt memakai `CryptoService.decrypt_vote_ciphertext`.
- Plaintext dibuat dengan `build_vote_plaintext`.
- Plaintext hasil decrypt dibaca dengan `parse_vote_plaintext`.
- Decrypt hanya dilakukan setelah signature dan hash valid.
