# 🇮🇩 UAS Kewarganegaraan – Aplikasi Ujian Online

Aplikasi web untuk **Ujian Akhir Semester** mata kuliah Pendidikan Kewarganegaraan dengan asisten AI Gemini.

Tersedia dalam **dua versi**:
- 🐍 **Streamlit (Python)** — untuk deploy gratis ke [Streamlit Cloud](https://share.streamlit.io)
- 🌐 **HTML/CSS/JS murni** — untuk hosting statis (GitHub Pages, Netlify, dll.)

---

## ✨ Fitur

- 🔐 Login terpisah untuk **Mahasiswa** (password kelas) dan **Dosen** (password admin)
- 👥 **Whitelist roster 43 mahasiswa** — login pakai dropdown nama, NIM otomatis
- 📝 15 soal pilihan ganda + 4 soal essay = **100 poin**
- ⏱️ Timer ujian **90 menit** dengan auto-submit
- 🤖 Asisten chatbot **Gemini AI** (sudah aktif default, bisa override)
- ✅ **Auto-grading** pilihan ganda + **AI grading** untuk essay
- 📊 Dashboard dosen: statistik, **roster status**, detail jawaban, ekspor CSV
- 🛡️ Anti-cheat: NIM lock, peringatan tab switch
- 📱 Responsive di mobile

---

## 🚀 Deploy ke Streamlit Cloud (Recommended)

### 1. Push repo ke GitHub
Repo sudah tersedia di: `https://github.com/saidul2017/kwgn`

### 2. Login ke Streamlit Cloud
1. Buka https://share.streamlit.io
2. Klik **"Sign in"** lalu pilih **"Continue with GitHub"**
3. Authorize Streamlit untuk mengakses repo Anda

### 3. Deploy aplikasi
1. Klik tombol **"New app"** atau **"Create app"**
2. Isi form deployment:
   - **Repository:** `saidul2017/kwgn`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL (opsional):** misal `kwgn-uas` (akan jadi `https://kwgn-uas.streamlit.app`)
3. Klik **"Deploy"**

Streamlit akan otomatis menginstall dependencies dari `requirements.txt` dan menjalankan `streamlit_app.py`. Tunggu 1-3 menit hingga app live.

### 4. (Opsional) Ganti Gemini API key di Streamlit Cloud
Aplikasi sudah include API key default di `students.py`, tapi sebaiknya untuk produksi:
1. Di dashboard Streamlit Cloud → klik app Anda → **Settings** → **Secrets**
2. Tambahkan:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
3. Save → app akan auto-restart dengan API key tersebut.

> Aplikasi membaca API key dengan urutan prioritas: **input mahasiswa > Streamlit Secrets > default di `students.py`**.

---

## 💻 Menjalankan Lokal (Streamlit)

```bash
# 1. Clone repo
git clone https://github.com/saidul2017/kwgn.git
cd kwgn

# 2. Install dependencies (rekomendasi pakai virtualenv)
python3 -m venv venv
source venv/bin/activate           # Linux/Mac
# venv\Scripts\activate            # Windows

pip install -r requirements.txt

# 3. Jalankan
streamlit run streamlit_app.py
```

Buka http://localhost:8501 di browser.

---

## 🌐 Versi HTML/CSS/JS (Statis)

Versi statis (`index.html` + `styles.css` + `app.js` + `gemini.js` + `questions.js`) bisa di-host di:

- **GitHub Pages**: Settings → Pages → Branch: `main` → Save → buka `https://saidul2017.github.io/kwgn/`
- **Netlify / Vercel**: drag-drop folder
- **Local**: `python3 -m http.server 8080`

> Versi statis menyimpan data di `localStorage` browser, sedangkan versi Streamlit menyimpan ke file `data/results.json` di server.

---

## 🔑 Password Default

| Peran | Password |
|-------|----------|
| Mahasiswa (kelas) | `kwgn2026` |
| Dosen (admin) | `dosen2026` |

> Dosen dapat mengubah password melalui **Dashboard Dosen → Pengaturan**.

---

## 🤖 Konfigurasi Gemini API

Asisten chatbot dan AI grading essay menggunakan **Gemini API**.

### Cara mendapatkan API Key (gratis):
1. Kunjungi [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Login dengan akun Google → **Create API Key**
3. Salin API key yang dihasilkan

### Cara setup:
- **Streamlit**: Mahasiswa input sendiri di dashboard, **atau** dosen set di Streamlit Secrets (lihat di atas)
- **HTML versi**: Mahasiswa input di dashboard (disimpan di localStorage)

> Tanpa API key, app tetap berjalan dengan **fallback grading** (berdasarkan panjang & kata kunci jawaban).

---

## 📚 Struktur Soal

| Tipe | Jumlah | Poin/Soal | Total |
|------|--------|-----------|-------|
| Pilihan Ganda | 15 | 4 | 60 |
| Essay | 4 | 10 | 40 |
| **Total** | **19** | – | **100** |

### Predikat Nilai
| Skor | Predikat |
|------|----------|
| ≥ 85 | A |
| 75–84 | B |
| 65–74 | C |
| 50–64 | D |
| < 50 | E |

---

## 🗂️ Struktur File

```
kwgn/
├── streamlit_app.py     # 🐍 Main Streamlit app
├── questions.py         # 🐍 Bank soal (Python)
├── students.py          # 🐍 Roster mahasiswa + default API key
├── gemini_helper.py     # 🐍 Gemini API helper
├── requirements.txt     # 🐍 Dependencies
├── .streamlit/
│   ├── config.toml      # 🐍 Tema & konfigurasi
│   └── secrets.toml.example
│
├── index.html           # 🌐 HTML versi
├── styles.css           # 🌐
├── app.js               # 🌐
├── gemini.js            # 🌐
├── questions.js         # 🌐
├── students.js          # 🌐 Roster + default API key
│
├── data/                # 💾 Auto-created (results.json, settings.json)
└── README.md
```

---

## 👥 Mengelola Roster Mahasiswa

Edit `students.py` (Streamlit) atau `students.js` (HTML versi) untuk menambah/menghapus peserta:

```python
STUDENT_ROSTER = {
    "25104080001": "FATIHA SAJDA AJI",
    "25104080002": "GHILMATUS SHOLIKHAH",
    # ... tambahkan peserta baru
}
```

Setelah edit, push ke GitHub → app auto-redeploy.

---

## 🎯 Alur Penggunaan

### Mahasiswa
1. Login dengan **nama, NIM, kelas, password kelas**
2. (Opsional) Masukkan **Gemini API Key** untuk asisten AI
3. Klik **"Mulai Ujian"** → mengerjakan 19 soal selama 90 menit
4. Gunakan tab **🤖 Asisten Gemini** untuk bertanya konsep
5. Submit → lihat **nilai otomatis + pembahasan + catatan AI**

### Dosen
1. Login dengan **nama dan password dosen**
2. Lihat **statistik** (jumlah peserta, rata-rata, tertinggi, terendah)
3. Tab **Hasil Ujian**: cari peserta, lihat detail jawaban, **ekspor CSV**
4. Tab **Pengaturan**: ubah password kelas/dosen
5. Tombol **🗑️ Hapus Semua** untuk reset semester baru

---

## 🔧 Customisasi Soal

Edit `questions.py` (Streamlit) atau `questions.js` (HTML versi). Format:

```python
# Pilihan ganda
{
    "type": "mc",
    "question": "Teks soal...",
    "options": ["A", "B", "C", "D", "E"],
    "correct": 0,           # index jawaban benar (0-4)
    "points": 4,
    "explanation": "Penjelasan..."
}

# Essay
{
    "type": "essay",
    "question": "Teks soal essay...",
    "points": 10,
    "rubric": "Pedoman penilaian untuk Gemini AI...",
    "keywords": ["kata", "kunci", "fallback"]  # untuk fallback grading
}
```

Setelah edit di Streamlit Cloud, push ke GitHub → app auto-redeploy.

### Mengubah Durasi
Edit `EXAM_DURATION_SECONDS` di `questions.py` (default: 5400 detik = 90 menit).

---

## ⚠️ Catatan Penting

- **Streamlit Cloud Free Tier**: file `data/results.json` **akan terhapus** saat app restart (setelah idle ~7 hari atau redeploy). **Selalu Ekspor CSV secara berkala!**
- Untuk persistensi data jangka panjang, gunakan database eksternal (Google Sheets, Firestore, Supabase) atau upgrade Streamlit Cloud.
- **Gemini API Free Tier** punya rate limit ~15 req/menit. Hindari ujian massal dengan AI grading bersamaan, atau gunakan tier berbayar.
- Versi HTML cocok untuk **demo / pengujian individual**; versi Streamlit cocok untuk **kelas dengan beberapa mahasiswa simultan**.

---

## 🧪 Testing Lokal

```bash
# Compile-check syntax
python3 -m py_compile streamlit_app.py questions.py gemini_helper.py

# Jalankan
streamlit run streamlit_app.py

# Test sebagai mahasiswa: pakai password "kwgn2026"
# Test sebagai dosen: pakai password "dosen2026"
```

---

## 📄 Lisensi

Bebas digunakan untuk keperluan pendidikan.

---

**Dibangun dengan ❤️ untuk pengajaran Pendidikan Kewarganegaraan Indonesia**
