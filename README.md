# Mini Sistem Manajemen Inventaris Laboratorium Komputer

Aplikasi terminal interaktif menggunakan **Python + Textual** dan **MySQL**. Data dikelola dalam tiga tabel: `lab`, `komputer`, dan `item_lab`.

## Fitur
- Mengelola Lab beserta jumlah komputer dan item yang dihitung langsung dari tabel terkait.
- Mengelola komputer beserta kode PC, monitor, CPU, keyboard, mouse, kondisi, dan catatan.
- Mengelola item Lab beserta kode, nama, kondisi, dan catatan.
- Kondisi tersedia sebagai enum: `Baik`, `Perlu Perbaikan`, dan `Rusak`.
- Pencarian langsung dan CRUD untuk setiap jenis data.
- Foreign key `id_lab` menghubungkan komputer dan item Lab ke tabel Lab.

## Struktur folder

```text
lab_inventory/
├── main.py
├── requirements.txt
├── .env.example
├── models/
│   └── item.py
├── storage/
│   ├── base.py
│   ├── json_storage.py
│   └── mysql_storage.py
├── ui/
│   └── app.py
├── data/
│   └── inventaris.json
└── sql/
    └── schema.sql
```

## 1. Persiapan

Disarankan Python 3.11 atau lebih baru. Pastikan Python dan pip terpasang:

```bash
python --version
python -m pip --version
```

Buka terminal pada folder proyek, lalu buat virtual environment (opsional tetapi disarankan).

### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Jika PowerShell memblokir aktivasi, jalankan perintah berikut di Command Prompt (CMD) atau gunakan `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Siapkan database MySQL

1. Jalankan MySQL Server melalui MySQL Workbench, XAMPP, Laragon, atau layanan MySQL yang kamu gunakan.
2. Buka MySQL Workbench, pilih koneksi lokal, lalu buka tab SQL baru.
3. Salin dan jalankan seluruh isi file `sql/schema.sql`. File ini membuat database `lab_inventory` serta tabel `lab`, `komputer`, dan `item_lab`.
4. Atur variabel lingkungan. Contoh untuk PowerShell:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="password_mysql_kamu"
$env:MYSQL_DATABASE="lab_inventory"
python main.py
```

Ganti `password_mysql_kamu` dengan password MySQL lokalmu. Jika akun MySQL tidak memakai password, set `MYSQL_PASSWORD` ke string kosong. Jangan unggah password asli ke GitHub.

Jalankan `python main.py`. Program akan terhubung ke MySQL dan membuat tabel `lab`, `komputer`, dan `item_lab` secara otomatis jika belum tersedia. Jika gagal, periksa apakah MySQL Server sedang berjalan, kredensial benar, dan database sudah dibuat.

## 4. Cara menggunakan aplikasi

- **Tambah**: klik tombol `＋ Tambah` atau tekan `A`.
- **Cari**: ketik di kolom pencarian. Tabel terfilter secara langsung.
- **Ubah**: pilih baris barang lalu klik `✎ Ubah` atau tekan `E`.
- **Hapus**: pilih baris lalu klik `⌫ Hapus` atau tekan `D`, kemudian konfirmasi.
- **Muat ulang**: klik tombol atau tekan `R`.
- **Keluar**: tekan `Q`.

Pada terminal sempit, perbesar jendela terminal supaya semua kolom terlihat.

## 5. Struktur data

- Lab memiliki `id` dan `nama_lab`; jumlah komputer serta item dihitung dari data terkait.
- Komputer memiliki `id`, `id_lab`, `kode_pc`, `monitor`, `cpu`, `keyboard`, `mouse`, `kondisi`, dan `catatan`.
- Item Lab memiliki `id`, `id_lab`, `kode_item`, `nama_item`, `kondisi`, dan `catatan`.
- Semua enum kondisi menggunakan pilihan `Baik`, `Perlu Perbaikan`, atau `Rusak`.

## Catatan pengembangan

Ini adalah mini project edukasi, bukan sistem produksi. MySQL digunakan untuk penyimpanan data pada versi proyek ini. Proyek ini belum mencakup login, transaksi peminjaman, multi-user, ekspor laporan, dan audit log.
