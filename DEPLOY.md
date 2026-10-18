# Deploy Produksi (VPS + Docker Compose)

Panduan ini untuk `docker-compose.prod.yml` (Postgres + Redis + backend + frontend).
Untuk dev lokal tetap pakai `docker-compose.yml`.

## 0. Prasyarat

- VPS Linux dengan Docker Engine + plugin `docker compose`.
- Port 80/443 dibuka di firewall (lihat bagian HTTPS). Port 8000/3000 sebaiknya
  **tidak** diekspos langsung ke internet — akses lewat reverse proxy.
- Repo sudah di-clone di VPS.

## 1. Generate secret

Jalankan dua kali, simpan hasilnya:

```bash
python3 -c "import secrets;print(secrets.token_hex(32))"
```

- hasil pertama → `JWT_SECRET`
- hasil kedua → `SETTINGS_ENCRYPTION_KEY`

Jangan commit nilai ini. `JWT_SECRET` yang berubah akan membatalkan semua token
lama; `SETTINGS_ENCRYPTION_KEY` yang berubah membuat API key LLM tersimpan tidak
bisa didekripsi (harus diisi ulang lewat UI/API).

## 2. Isi `.env`

```bash
cp .env.example .env
```

Edit `.env` minimal:

```dotenv
ENVIRONMENT=production
DEBUG=false

# Wajib — compose gagal start bila kosong.
JWT_SECRET=<hasil generate>
SETTINGS_ENCRYPTION_KEY=<hasil generate>

# Dipaksa true oleh compose, tetapi isi juga agar konsisten.
AUTH_ENABLED=true
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=<api key>

# Origin browser yang benar (bukan localhost) — dipisah koma.
CORS_ORIGINS=https://app.contoh.com
NEXT_PUBLIC_API_URL=https://api.contoh.com
NEXT_PUBLIC_AUTH_ENABLED=true

# Ganti kredensial Postgres (jangan default).
POSTGRES_USER=cci
POSTGRES_PASSWORD=<password kuat>
POSTGRES_DB=construction_db
```

Validasi tanpa menjalankan container:

```bash
docker compose -f docker-compose.prod.yml config
```

Perintah ini akan **gagal** bila `JWT_SECRET` atau `SETTINGS_ENCRYPTION_KEY`
kosong — memang disengaja.

## 3. Jalankan stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
curl -fsS http://localhost:8000/health/ready
```

Healthcheck backend memakai `GET /health/ready` (DB + status konfigurasi LLM).

## 4. Buat admin pertama (bootstrap)

`POST /api/auth/register` tetap publik **hanya** selama belum ada user. User
pertama otomatis ber-role `ADMIN`; pendaftar berikutnya (bila registrasi masih
terbuka) selalu `ENGINEER`.

```bash
curl -X POST https://api.contoh.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@contoh.com","password":"<password kuat>","full_name":"Admin"}'
```

Lalu login:

```bash
curl -X POST https://api.contoh.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@contoh.com","password":"<password kuat>"}'
```

Simpan `access_token` dan uji endpoint terproteksi:

```bash
curl https://api.contoh.com/api/projects -H "Authorization: Bearer <token>"
```

## 5. Registrasi tertutup setelah user pertama

Saat `AUTH_ENABLED=true` dan tabel `users` sudah berisi minimal satu akun,
`POST /api/auth/register` mengembalikan **403**. Ini mencegah siapa pun membuat
akun sendiri di instance publik.

Konsekuensi:

- Tidak ada pendaftaran mandiri. Tambah user lewat skrip admin (lihat bawah).
- Jangan mematikan `AUTH_ENABLED` untuk "membuka pendaftaran" — itu membuka
  seluruh API tanpa token. Gunakan skrip.

Tambah user dari dalam container:

```bash
docker compose -f docker-compose.prod.yml exec backend python - <<'PY'
from app.database import SessionLocal
from app.kernel.auth.security import hash_password
from app.models import User, UserRole

db = SessionLocal()
db.add(User(
    email="engineer@contoh.com",
    hashed_password=hash_password("password-kuat"),
    full_name="Engineer",
    role=UserRole.ENGINEER,
    is_active=1,
))
db.commit()
print("user dibuat")
PY
```

## 6. Backup

Data persisten ada di volume Docker. Untuk Postgres (default compose):

```bash
# Backup
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup-$(date +%F).sql

# Restore (DB kosong)
cat backup-2026-10-19.sql | docker compose -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Bila memakai SQLite (`DATABASE_URL=sqlite:///...`), file DB berada di volume
`backend_data` (`/app/data` atau path yang dikonfigurasi). Backup dengan
`docker run --rm -v <volume>:/data -v "$PWD":/backup alpine tar czf /backup/db.tgz /data`.

Simpan backup di luar VPS dan uji restore secara berkala.

## 7. HTTPS / reverse proxy

Backend tidak menangani TLS. Pasang Caddy/Nginx/Traefik di depan:

- `https://api.contoh.com` → `127.0.0.1:8000`
- `https://app.contoh.com` → `127.0.0.1:3000`
- Teruskan header `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Set `CORS_ORIGINS` ke origin frontend yang sebenarnya (https, tanpa trailing slash).
- `NEXT_PUBLIC_API_URL` di-inline saat build frontend — ubah nilai ini berarti
  perlu `docker compose ... up -d --build frontend`.

## 8. Peringatan: `/static/data` terbuka

`/static/data/*` sengaja publik (gambar diff/crop harus bisa dimuat browser),
bahkan saat `AUTH_ENABLED=true`. Artinya siapa pun yang tahu URL-nya dapat
mengunduh file di folder tersebut.

- Jangan menaruh dokumen rahasia/API key di `backend/data`.
- Gunakan nama file yang tidak mudah ditebak, atau pindahkan aset ke object
  storage dengan signed URL bila kerahasiaan diperlukan.
- Batasi akses di reverse proxy bila aset harus privat.

## 9. Rollback / matikan auth (darurat)

Set `AUTH_ENABLED=false` lalu restart backend akan membuka **semua** endpoint
tanpa token. Hanya lakukan sementara di lingkungan tepercaya, dan segera
kembalikan ke `true`.

```bash
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```
