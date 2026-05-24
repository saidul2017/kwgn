# 🇮🇩 UAS Kewarganegaraan - Aplikasi Ujian Online

Aplikasi web untuk Ujian Akhir Semester (UAS) mata kuliah **Pendidikan Kewarganegaraan** dengan fitur:

- 🔐 **Sistem login terpisah** untuk Mahasiswa (password kelas) dan Dosen (password admin)
- 📝 **Soal pilihan ganda + essay** (15 pilgan + 4 essay, total 100 poin)
- ⏱️ **Timer ujian otomatis** (90 menit, auto-submit saat waktu habis)
- 🤖 **Asisten Chatbot Gemini AI** untuk diskusi konsep selama ujian
- ✅ **Auto-grading**: pilihan ganda otomatis, essay dinilai oleh Gemini AI
- 📊 **Dashboard dosen**: statistik, daftar peserta, detail jawaban, ekspor CSV
- 💾 **Penyimpanan lokal** menggunakan `localStorage` (tidak butuh server)

## 🚀 Cara Menjalankan

Aplikasi adalah **HTML + CSS + JavaScript murni** tanpa build step.

### Opsi 1: Buka langsung di browser
```bash
# Cukup buka file index.html di browser modern (Chrome/Edge/Firefox/Safari)
```

### Opsi 2: Jalankan dengan local server
```bash
# Python 3
python3 -m http.server 8080

# atau Node.js
npx serve .

# Kemudian buka http://localhost:8080
```

## 🔑 Password Default

| Peran | Password |
|-------|----------|
| Mahasiswa (kelas) | `kwgn2026` |
| Dosen (admin) | `dosen2026` |

> Dosen dapat mengubah kedua password melalui **Dashboard Dosen → Pengaturan Kelas**.

## 🤖 Konfigurasi Gemini API (Opsional)

Asisten chatbot dan penilaian otomatis essay menggunakan **Gemini API**. Tanpa API key, aplikasi tetap bisa digunakan dengan **fallback grading** (berdasarkan panjang & kata kunci jawaban).

### Cara mendapatkan API Key:
1. Kunjungi [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Login dengan akun Google → klik **Create API Key** (gratis)
3. Salin API key yang dihasilkan
4. Buka aplikasi → Login Mahasiswa → Dashboard → Tempel API Key di kolom yang tersedia → klik **Simpan**

API key disimpan **lokal di browser Anda** (`localStorage`), tidak dikirim ke server lain selain Google.

## 📚 Struktur Soal

| Tipe | Jumlah | Poin per Soal | Total |
|------|--------|---------------|-------|
| Pilihan Ganda | 15 | 4 | 60 |
| Essay | 4 | 10 | 40 |
| **Total** | **19** | - | **100** |

### Predikat Nilai
| Skor | Predikat |
|------|----------|
| ≥ 85 | A |
| 75-84 | B |
| 65-74 | C |
| 50-64 | D |
| < 50 | E |

## 🗂️ Struktur File

```
kwgn/
├── index.html       # Struktur halaman utama
├── styles.css       # Styling responsive
├── questions.js     # Bank soal Kewarganegaraan
├── gemini.js        # Integrasi Gemini API
├── app.js           # Logika aplikasi (auth, exam, dashboard)
└── README.md        # Dokumentasi ini
```

## 🎯 Alur Pengguna

### Mahasiswa
1. Login dengan **nama, NIM, kelas, dan password kelas**
2. (Opsional) Masukkan **Gemini API Key** untuk mengaktifkan asisten AI
3. Klik **Mulai Ujian** → Mengerjakan 19 soal
4. Gunakan tombol **🤖 Asisten Gemini** di pojok kanan bawah untuk bertanya konsep
5. Submit → Lihat **nilai otomatis + pembahasan**

### Dosen
1. Login dengan **nama dan password dosen**
2. Lihat dashboard: **statistik, daftar peserta, rata-rata nilai**
3. Klik **Detail** pada peserta untuk melihat semua jawaban
4. Ubah password kelas/dosen di **Pengaturan**
5. **Ekspor hasil ke CSV** atau hapus semua data

## 🛡️ Fitur Anti-Curang

- Peringatan saat berpindah tab/window
- Konfirmasi sebelum keluar saat ujian berlangsung
- NIM yang sudah ujian tidak bisa login ulang (dosen bisa hapus data)
- Asisten Gemini di-instruksikan **tidak memberikan jawaban langsung**, hanya menjelaskan konsep

## 🔧 Customisasi

### Mengubah Soal
Edit file `questions.js`. Format soal:

```js
// Pilihan ganda
{
    type: 'mc',
    question: 'Teks soal...',
    options: ['A', 'B', 'C', 'D', 'E'],
    correct: 0, // index jawaban benar (0-4)
    points: 4,
    explanation: 'Penjelasan jawaban...'
}

// Essay
{
    type: 'essay',
    question: 'Teks soal essay...',
    points: 10,
    rubric: 'Pedoman penilaian untuk Gemini AI...',
    keywords: ['kata', 'kunci', 'fallback'] // untuk grading tanpa Gemini
}
```

### Mengubah Durasi Ujian
Edit `EXAM_DURATION_SECONDS` di `questions.js` (default: 90 menit = 5400 detik).

## ⚠️ Catatan Penting

- **Data tersimpan di browser**: jika browser dibersihkan, data hilang. Gunakan **Ekspor CSV** secara berkala.
- **Untuk produksi**, sebaiknya tambahkan backend (Node.js/PHP/Python) untuk menyimpan data secara terpusat.
- **Gemini API gratis** memiliki rate limit (~15 request/menit pada tier gratis).

## 📄 Lisensi

Bebas digunakan untuk keperluan pendidikan.

---

**Dibangun dengan ❤️ untuk pengajaran Pendidikan Kewarganegaraan Indonesia**
