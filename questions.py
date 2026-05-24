"""
Bank Soal UAS Pendidikan Kewarganegaraan (Python version untuk Streamlit).

Format:
- type: 'mc' (multiple choice) | 'essay'
- mc: { question, options: [a,b,c,d,e], correct: index, points, explanation }
- essay: { question, points, rubric, keywords }
"""

QUESTIONS = [
    # ==================== PILIHAN GANDA (15 soal x 4 = 60 poin) ====================
    {
        "type": "mc",
        "question": "Pancasila sebagai dasar negara Indonesia secara yuridis-konstitusional ditetapkan pada tanggal...",
        "options": [
            "1 Juni 1945",
            "17 Agustus 1945",
            "18 Agustus 1945",
            "22 Juni 1945",
            "29 Mei 1945",
        ],
        "correct": 2,
        "points": 4,
        "explanation": "Pancasila ditetapkan sebagai dasar negara pada tanggal 18 Agustus 1945 melalui sidang PPKI yang juga mengesahkan UUD 1945.",
    },
    {
        "type": "mc",
        "question": "Sumber dari segala sumber hukum di Indonesia adalah...",
        "options": [
            "UUD 1945",
            "Pancasila",
            "Tap MPR",
            "Undang-Undang",
            "Peraturan Pemerintah",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Berdasarkan UU No. 12 Tahun 2011, Pancasila merupakan sumber dari segala sumber hukum negara (staatsfundamentalnorm).",
    },
    {
        "type": "mc",
        "question": "Bentuk negara Republik Indonesia berdasarkan UUD 1945 Pasal 1 ayat (1) adalah...",
        "options": [
            "Negara federal",
            "Negara kesatuan yang berbentuk republik",
            "Negara kesatuan yang berbentuk monarki",
            "Negara serikat",
            "Negara konfederasi",
        ],
        "correct": 1,
        "points": 4,
        "explanation": 'Pasal 1 ayat (1) UUD 1945 menyatakan: "Negara Indonesia ialah Negara Kesatuan, yang berbentuk Republik."',
    },
    {
        "type": "mc",
        "question": "Demokrasi yang dianut oleh Indonesia adalah demokrasi...",
        "options": [
            "Liberal",
            "Terpimpin",
            "Pancasila",
            "Sosialis",
            "Parlementer",
        ],
        "correct": 2,
        "points": 4,
        "explanation": "Indonesia menganut Demokrasi Pancasila yang berakar pada nilai-nilai musyawarah-mufakat dan kekeluargaan.",
    },
    {
        "type": "mc",
        "question": "Hak Asasi Manusia yang melekat pada manusia sejak lahir merupakan pemberian dari...",
        "options": [
            "Negara",
            "Pemerintah",
            "Tuhan Yang Maha Esa",
            "Masyarakat",
            "Konstitusi",
        ],
        "correct": 2,
        "points": 4,
        "explanation": "HAM adalah hak yang melekat pada manusia sebagai anugerah Tuhan Yang Maha Esa, yang wajib dihormati, dijunjung tinggi, dan dilindungi negara.",
    },
    {
        "type": "mc",
        "question": "Berikut ini yang bukan termasuk lembaga negara hasil amandemen UUD 1945 adalah...",
        "options": [
            "Mahkamah Konstitusi (MK)",
            "Komisi Yudisial (KY)",
            "Dewan Perwakilan Daerah (DPD)",
            "Dewan Pertimbangan Agung (DPA)",
            "Mahkamah Agung (MA)",
        ],
        "correct": 3,
        "points": 4,
        "explanation": "DPA telah dihapuskan melalui amandemen keempat UUD 1945 tahun 2002 dan tidak lagi menjadi bagian dari struktur ketatanegaraan Indonesia.",
    },
    {
        "type": "mc",
        "question": "Wawasan Nusantara merupakan cara pandang bangsa Indonesia tentang diri dan lingkungannya berdasarkan...",
        "options": [
            "Geopolitik dan Pancasila",
            "Pancasila dan UUD 1945",
            "UUD 1945 dan Bhinneka Tunggal Ika",
            "Geopolitik dan UUD 1945",
            "Sumpah Pemuda dan Pancasila",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Wawasan Nusantara adalah cara pandang bangsa Indonesia tentang diri dan lingkungannya berdasarkan Pancasila dan UUD NRI 1945.",
    },
    {
        "type": "mc",
        "question": "Tujuan negara Indonesia tertuang dalam pembukaan UUD 1945 alinea ke...",
        "options": ["Pertama", "Kedua", "Ketiga", "Keempat", "Kelima"],
        "correct": 3,
        "points": 4,
        "explanation": "Tujuan negara Indonesia tercantum pada alinea ke-4 Pembukaan UUD 1945: melindungi segenap bangsa, memajukan kesejahteraan, mencerdaskan kehidupan bangsa, dan ikut serta mewujudkan ketertiban dunia.",
    },
    {
        "type": "mc",
        "question": "Asas kewarganegaraan yang menetapkan kewarganegaraan seseorang berdasarkan tempat kelahirannya disebut...",
        "options": [
            "Ius Sanguinis",
            "Ius Soli",
            "Apatride",
            "Bipatride",
            "Naturalisasi",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Ius Soli (asas tempat kelahiran) menentukan kewarganegaraan berdasarkan tempat lahir, sedangkan Ius Sanguinis berdasarkan keturunan/darah.",
    },
    {
        "type": "mc",
        "question": "Sistem pertahanan dan keamanan rakyat semesta (Sishankamrata) menempatkan rakyat sebagai...",
        "options": [
            "Komponen utama",
            "Komponen cadangan",
            "Komponen pendukung",
            "Komponen tambahan",
            "Komponen pelengkap",
        ],
        "correct": 2,
        "points": 4,
        "explanation": "Dalam Sishankamrata, TNI/Polri sebagai komponen utama, sedangkan rakyat berperan sebagai komponen pendukung sebagaimana tercantum dalam UU No. 3 Tahun 2002.",
    },
    {
        "type": "mc",
        "question": "Berikut yang merupakan ciri khas demokrasi Pancasila adalah...",
        "options": [
            "Voting mayoritas mutlak",
            "Musyawarah untuk mufakat",
            "Otoritas pemimpin tunggal",
            "Kepatuhan absolut pada partai",
            "Kebebasan tanpa batas",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Ciri khas Demokrasi Pancasila adalah musyawarah untuk mencapai mufakat, sesuai sila keempat Pancasila.",
    },
    {
        "type": "mc",
        "question": "Pelanggaran HAM berat menurut UU No. 26 Tahun 2000 meliputi...",
        "options": [
            "Pencemaran nama baik dan penistaan",
            "Genosida dan kejahatan terhadap kemanusiaan",
            "Penganiayaan ringan dan pencurian",
            "Korupsi dan kolusi",
            "Pelanggaran lalu lintas",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "UU No. 26 Tahun 2000 tentang Pengadilan HAM mendefinisikan pelanggaran HAM berat sebagai kejahatan genosida dan kejahatan terhadap kemanusiaan.",
    },
    {
        "type": "mc",
        "question": "Otonomi daerah di Indonesia diatur dalam UU...",
        "options": [
            "UU No. 32 Tahun 2004",
            "UU No. 23 Tahun 2014",
            "UU No. 22 Tahun 1999",
            "UU No. 5 Tahun 1974",
            "UU No. 12 Tahun 2008",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Saat ini otonomi daerah diatur oleh UU No. 23 Tahun 2014 tentang Pemerintahan Daerah, menggantikan UU No. 32 Tahun 2004.",
    },
    {
        "type": "mc",
        "question": "Identitas nasional bangsa Indonesia yang membedakan dengan bangsa lain antara lain...",
        "options": [
            "Bahasa Inggris dan budaya barat",
            "Bahasa Indonesia, Bendera Merah Putih, dan Pancasila",
            "Lagu pop dan film Hollywood",
            "Mata uang dolar dan kuliner cepat saji",
            "Adat istiadat luar negeri",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Identitas nasional Indonesia meliputi Bahasa Indonesia, Bendera Merah Putih, Lambang Garuda Pancasila, Lagu Indonesia Raya, Pancasila, UUD 1945, dan Bhinneka Tunggal Ika.",
    },
    {
        "type": "mc",
        "question": "Integrasi nasional adalah upaya menyatukan...",
        "options": [
            "Berbagai partai politik dalam satu wadah",
            "Perbedaan suku, agama, ras, dan budaya menjadi kesatuan bangsa",
            "Berbagai negara ASEAN menjadi satu",
            "Kelompok ekonomi atas dan bawah",
            "Perbedaan ideologi dunia",
        ],
        "correct": 1,
        "points": 4,
        "explanation": "Integrasi nasional adalah proses penyatuan berbagai kelompok sosial budaya, suku, agama, dan ras dalam satu kesatuan wilayah dan identitas nasional.",
    },

    # ==================== ESSAY (4 soal x 10 = 40 poin) ====================
    {
        "type": "essay",
        "question": "Jelaskan kedudukan dan fungsi Pancasila sebagai dasar negara dan pandangan hidup bangsa Indonesia! Berikan contoh konkret penerapannya dalam kehidupan bermasyarakat dan bernegara.",
        "points": 10,
        "rubric": "Mahasiswa diharapkan menjelaskan: (1) Pancasila sebagai dasar negara/staatsfundamentalnorm yang menjadi sumber hukum, (2) Pancasila sebagai pandangan hidup/way of life yang menjadi pedoman moral bangsa, (3) memberikan minimal 2 contoh konkret penerapan dalam kehidupan sehari-hari.",
        "keywords": [
            "dasar negara", "pandangan hidup", "sumber hukum", "pedoman", "sila",
            "persatuan", "keadilan", "musyawarah", "gotong royong", "toleransi",
        ],
    },
    {
        "type": "essay",
        "question": "Bagaimana implementasi nilai-nilai demokrasi Pancasila dalam kehidupan kampus? Jelaskan minimal 3 contoh konkret dan kaitkan dengan sila-sila Pancasila yang relevan.",
        "points": 10,
        "rubric": "Mahasiswa diharapkan menyebut: (1) musyawarah dalam organisasi mahasiswa terkait sila ke-4, (2) toleransi antar mahasiswa beragam latar belakang terkait sila ke-3, (3) pemilihan ketua BEM/HMJ secara demokratis, (4) kebebasan menyampaikan pendapat akademik, dengan kaitan ke sila Pancasila yang relevan.",
        "keywords": [
            "musyawarah", "mufakat", "BEM", "HMJ", "pemilihan", "organisasi",
            "kebebasan", "pendapat", "toleransi", "sila keempat", "persatuan",
        ],
    },
    {
        "type": "essay",
        "question": "Apa yang dimaksud dengan integrasi nasional? Jelaskan tantangan dan ancaman terhadap integrasi nasional Indonesia di era digital saat ini, serta strategi yang dapat dilakukan generasi muda untuk mengatasinya.",
        "points": 10,
        "rubric": "Mahasiswa diharapkan: (1) mendefinisikan integrasi nasional sebagai penyatuan berbagai unsur bangsa, (2) menyebut tantangan era digital seperti hoaks, ujaran kebencian, polarisasi medsos, separatisme digital, (3) menyebut strategi seperti literasi digital, toleransi, bela negara non-fisik, kampanye persatuan online.",
        "keywords": [
            "integrasi nasional", "persatuan", "kesatuan", "hoaks", "ujaran kebencian",
            "media sosial", "literasi digital", "bhinneka tunggal ika", "toleransi",
            "bela negara", "generasi muda",
        ],
    },
    {
        "type": "essay",
        "question": "Sebagai mahasiswa, bagaimana Anda mewujudkan sikap bela negara dalam kehidupan sehari-hari? Berikan minimal 4 contoh konkret tindakan bela negara non-fisik yang relevan dengan profesi dan keilmuan Anda.",
        "points": 10,
        "rubric": "Mahasiswa diharapkan menyebut: (1) belajar tekun untuk meningkatkan SDM bangsa, (2) menjaga lingkungan dan disiplin, (3) menggunakan produk dalam negeri, (4) melawan hoaks/disinformasi, (5) menjaga nama baik bangsa di media sosial, (6) taat hukum dan membayar pajak. Minimal 4 contoh dan dikaitkan dengan profesi/keilmuan.",
        "keywords": [
            "bela negara", "cinta tanah air", "kesadaran berbangsa", "pancasila",
            "rela berkorban", "belajar", "produk dalam negeri", "hoaks", "disiplin",
            "taat hukum", "pajak", "lingkungan",
        ],
    },
]

# Hitung total poin maksimal
TOTAL_POINTS = sum(q["points"] for q in QUESTIONS)
MC_QUESTIONS = [q for q in QUESTIONS if q["type"] == "mc"]
ESSAY_QUESTIONS = [q for q in QUESTIONS if q["type"] == "essay"]
MC_TOTAL_POINTS = sum(q["points"] for q in MC_QUESTIONS)
ESSAY_TOTAL_POINTS = sum(q["points"] for q in ESSAY_QUESTIONS)

# Durasi ujian dalam detik (90 menit)
EXAM_DURATION_SECONDS = 90 * 60
