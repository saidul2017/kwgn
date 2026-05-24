"""
UAS Kewarganegaraan - Streamlit App
====================================
Aplikasi ujian online dengan:
- Login mahasiswa (password kelas) & dosen (password admin)
- Soal pilihan ganda + essay
- Auto-grading + AI grading via Gemini
- Asisten chatbot Gemini
- Dashboard dosen dengan statistik & ekspor CSV

Deploy: https://share.streamlit.io
Main file: streamlit_app.py
"""
import json
import os
import time
from datetime import datetime
from io import StringIO
import csv

import streamlit as st

from questions import (
    QUESTIONS,
    MC_QUESTIONS,
    ESSAY_QUESTIONS,
    MC_TOTAL_POINTS,
    ESSAY_TOTAL_POINTS,
    EXAM_DURATION_SECONDS,
)
from gemini_helper import (
    chat_with_gemini,
    grade_essay,
    grade_essay_fallback,
    generate_overall_feedback,
)

# ==================== CONFIG ====================
st.set_page_config(
    page_title="UAS Kewarganegaraan",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_CLASS_PWD = "kwgn2026"
DEFAULT_LECTURER_PWD = "dosen2026"

# ==================== STORAGE ====================
def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "class_password": DEFAULT_CLASS_PWD,
        "lecturer_password": DEFAULT_LECTURER_PWD,
    }


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def load_results() -> list:
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_results(results: list) -> None:
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)


def append_result(result: dict) -> None:
    results = load_results()
    results.append(result)
    save_results(results)


# ==================== HELPERS ====================
def get_grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "E"


def format_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def format_dt(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d %b %Y %H:%M")
    except Exception:
        return iso_str


def init_state():
    defaults = {
        "role": None,             # 'student' | 'lecturer' | None
        "page": "login",          # 'login' | 'student_dashboard' | 'exam' | 'result' | 'lecturer_dashboard'
        "student": None,          # {name, nim, class}
        "lecturer": None,         # {name}
        "answers": {},
        "current_q": 0,
        "exam_start_time": None,  # epoch seconds
        "submitted": False,
        "result": None,
        "chat_history": [],
        "gemini_key": "",
        "show_review": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    keys_to_clear = [
        "role", "page", "student", "lecturer", "answers", "current_q",
        "exam_start_time", "submitted", "result", "chat_history",
        "show_review",
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    init_state()


# ==================== CUSTOM CSS ====================
def inject_css():
    st.markdown(
        """
        <style>
        /* Hero card */
        .hero-card {
            background: linear-gradient(135deg, #fef2f2 0%, #eff6ff 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid #fecaca;
        }
        .hero-card h1 { color: #dc2626; margin-bottom: 0.5rem; }

        /* Score circle */
        .score-circle {
            background: linear-gradient(135deg, #dc2626, #1e40af);
            color: white;
            border-radius: 50%;
            width: 180px;
            height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .score-circle .num { font-size: 3.5rem; font-weight: 700; line-height: 1; }
        .score-circle .small { font-size: 1rem; opacity: 0.9; }

        /* Question card */
        .q-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        .q-meta {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }
        .q-tag {
            background: #fee2e2;
            color: #dc2626;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .q-tag.blue { background: #dbeafe; color: #1e40af; }
        .q-tag.gray { background: #f3f4f6; color: #6b7280; }

        /* Timer styles */
        .timer-ok { color: #16a34a; }
        .timer-warn { color: #f59e0b; }
        .timer-danger { color: #dc2626; }

        /* Predikat badge */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.85rem;
        }
        .badge-A { background: #dcfce7; color: #16a34a; }
        .badge-B { background: #dbeafe; color: #1e40af; }
        .badge-C { background: #fef3c7; color: #92400e; }
        .badge-D, .badge-E { background: #fee2e2; color: #dc2626; }

        /* Hide streamlit branding for cleaner UI */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==================== LOGIN ====================
def login_page():
    settings = load_settings()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="hero-card">
                <div style="font-size:4rem;">🇮🇩</div>
                <h1>Ujian Akhir Semester</h1>
                <h3 style="color:#1f2937;">Pendidikan Kewarganegaraan</h3>
                <p style="color:#6b7280;">Sistem ujian online dengan asisten AI Gemini.</p>
                <ul style="line-height:1.8;">
                    <li>✅ Soal Pilihan Ganda &amp; Essay</li>
                    <li>✅ Penilaian Otomatis dengan AI</li>
                    <li>✅ Asisten Chatbot Gemini</li>
                    <li>✅ Dashboard Hasil untuk Dosen</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        tab_student, tab_lecturer = st.tabs(["👨‍🎓 Mahasiswa", "👨‍🏫 Dosen"])

        with tab_student:
            st.subheader("Login Mahasiswa")
            with st.form("student_login"):
                name = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
                nim = st.text_input("NIM", placeholder="Contoh: 2021010101")
                cls = st.text_input("Kelas", placeholder="Contoh: TI-3A")
                pwd = st.text_input("Password Kelas", type="password", placeholder="Diberikan oleh dosen")
                submitted = st.form_submit_button("Masuk Ujian", type="primary", use_container_width=True)

                if submitted:
                    if not all([name.strip(), nim.strip(), cls.strip(), pwd]):
                        st.error("Semua field wajib diisi.")
                    elif pwd != settings["class_password"]:
                        st.error("Password kelas salah. Silakan tanyakan kepada dosen.")
                    else:
                        # Cek apakah NIM sudah pernah ujian
                        existing = next((r for r in load_results() if r["nim"] == nim.strip()), None)
                        if existing:
                            st.error(f"NIM {nim} sudah menyelesaikan ujian pada {format_dt(existing['submitted_at'])}. Hubungi dosen jika perlu mengulang.")
                        else:
                            st.session_state.role = "student"
                            st.session_state.student = {
                                "name": name.strip(),
                                "nim": nim.strip(),
                                "class": cls.strip(),
                            }
                            st.session_state.page = "student_dashboard"
                            st.rerun()

            st.caption(f"Password kelas default: `{DEFAULT_CLASS_PWD}`")

        with tab_lecturer:
            st.subheader("Login Dosen")
            with st.form("lecturer_login"):
                lname = st.text_input("Nama Dosen", placeholder="Contoh: Dr. Andi")
                lpwd = st.text_input("Password Dosen", type="password", placeholder="Password admin")
                lsubmitted = st.form_submit_button("Masuk Dashboard", type="primary", use_container_width=True)

                if lsubmitted:
                    if not lname.strip() or not lpwd:
                        st.error("Nama dan password wajib diisi.")
                    elif lpwd != settings["lecturer_password"]:
                        st.error("Password dosen salah.")
                    else:
                        st.session_state.role = "lecturer"
                        st.session_state.lecturer = {"name": lname.strip()}
                        st.session_state.page = "lecturer_dashboard"
                        st.rerun()

            st.caption(f"Password dosen default: `{DEFAULT_LECTURER_PWD}`")


# ==================== STUDENT DASHBOARD ====================
def student_dashboard():
    s = st.session_state.student
    st.markdown(
        f"""
        <div class="hero-card">
            <h1>Selamat Datang, {s['name']} 👋</h1>
            <p style="color:#6b7280;">NIM: {s['nim']} · Kelas: {s['class']}</p>
            <p>Anda akan mengikuti Ujian Akhir Semester mata kuliah Pendidikan Kewarganegaraan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Info ringkas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Soal", len(QUESTIONS))
    c2.metric("Pilihan Ganda", len(MC_QUESTIONS))
    c3.metric("Essay", len(ESSAY_QUESTIONS))
    c4.metric("Durasi", "90 Menit")

    # Tata tertib
    with st.expander("📋 Tata Tertib Ujian", expanded=True):
        st.markdown(
            """
            1. Bacalah setiap soal dengan teliti sebelum menjawab.
            2. Anda dapat berpindah antar soal dan kembali untuk merevisi jawaban.
            3. Asisten AI Gemini boleh dipakai untuk **diskusi konsep**, bukan jawaban langsung.
            4. Waktu ujian akan terus berjalan. Ujian akan tersubmit otomatis saat waktu habis.
            5. Pastikan menekan tombol **Submit Ujian** sebelum waktu habis.
            """
        )

    # Konfigurasi Gemini
    with st.expander("🤖 Konfigurasi Asisten Gemini (Opsional)", expanded=not st.session_state.gemini_key):
        st.markdown(
            "Untuk mengaktifkan chatbot AI dan penilaian otomatis essay, masukkan **Gemini API Key**. "
            "Dapatkan API key gratis di [Google AI Studio](https://aistudio.google.com/app/apikey)."
        )
        # Cek apakah sudah ada di secrets
        secret_key = ""
        try:
            secret_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
        except Exception:
            secret_key = ""

        if secret_key and not st.session_state.gemini_key:
            st.session_state.gemini_key = secret_key
            st.success("✅ Gemini API key terdeteksi dari secrets server.")

        api_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.gemini_key,
            help="API key disimpan hanya selama sesi browser.",
        )
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("Simpan", key="save_api"):
                st.session_state.gemini_key = api_input.strip()
                if st.session_state.gemini_key:
                    st.success("✅ Gemini API key tersimpan untuk sesi ini.")
                else:
                    st.info("API key dihapus.")
        with col_b:
            if st.session_state.gemini_key:
                st.success("Asisten AI aktif")
            else:
                st.warning("Asisten AI nonaktif (tetap bisa ujian, essay dinilai dengan fallback)")

    st.divider()

    if st.button("🚀 Mulai Ujian Sekarang", type="primary", use_container_width=True):
        st.session_state.exam_start_time = time.time()
        st.session_state.page = "exam"
        st.session_state.current_q = 0
        st.session_state.answers = {}
        st.session_state.submitted = False
        st.rerun()


# ==================== EXAM PAGE ====================
def exam_page():
    if not st.session_state.exam_start_time:
        st.session_state.exam_start_time = time.time()

    elapsed = int(time.time() - st.session_state.exam_start_time)
    remaining = EXAM_DURATION_SECONDS - elapsed

    # Auto-submit jika waktu habis
    if remaining <= 0 and not st.session_state.submitted:
        st.warning("⏰ Waktu habis! Ujian akan disubmit otomatis.")
        do_submit(auto=True)
        return

    # === SIDEBAR ===
    with st.sidebar:
        # Timer
        timer_class = "timer-ok"
        if remaining <= 60:
            timer_class = "timer-danger"
        elif remaining <= 5 * 60:
            timer_class = "timer-warn"

        st.markdown(
            f"""
            <div style="background:#fee2e2;padding:1rem;border-radius:12px;text-align:center;margin-bottom:1rem;">
                <div style="font-size:0.85rem;color:#7f1d1d;">⏱️ Sisa Waktu</div>
                <div class="{timer_class}" style="font-size:2.25rem;font-weight:700;font-family:monospace;">
                    {format_time(remaining)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tombol refresh timer
        if st.button("🔄 Refresh Timer", use_container_width=True, key="refresh_timer"):
            st.rerun()

        st.markdown("### 📋 Navigasi Soal")
        # Render navigator dalam grid 5 kolom
        for row_start in range(0, len(QUESTIONS), 5):
            cols = st.columns(5)
            for i in range(5):
                idx = row_start + i
                if idx >= len(QUESTIONS):
                    break
                ans = st.session_state.answers.get(idx)
                is_answered = ans is not None and (
                    (isinstance(ans, str) and ans.strip()) or
                    (isinstance(ans, int))
                )
                label = f"{idx + 1}"
                if is_answered:
                    label += "✓"
                btn_type = "primary" if idx == st.session_state.current_q else "secondary"
                if cols[i].button(label, key=f"nav_{idx}", type=btn_type, use_container_width=True):
                    st.session_state.current_q = idx
                    st.rerun()

        # Legenda
        st.caption("✓ = sudah dijawab · biru = soal aktif")

        st.divider()
        if st.button("✅ Submit Ujian", type="primary", use_container_width=True, key="submit_btn"):
            st.session_state.show_submit_dialog = True

        if st.button("🚪 Keluar", use_container_width=True):
            if st.session_state.get("confirm_logout"):
                reset_session()
                st.rerun()
            else:
                st.session_state.confirm_logout = True
                st.warning("Klik sekali lagi untuk konfirmasi keluar (progres hilang).")

    # === MAIN AREA ===
    st.markdown(f"### 📝 Ujian Akhir Semester · {st.session_state.student['name']}")

    # Submit confirmation
    if st.session_state.get("show_submit_dialog"):
        unanswered = sum(
            1 for i in range(len(QUESTIONS))
            if st.session_state.answers.get(i) is None or
            (isinstance(st.session_state.answers.get(i), str) and not st.session_state.answers.get(i, "").strip())
        )
        msg = "Yakin ingin submit ujian? Jawaban tidak dapat diubah."
        if unanswered:
            msg = f"⚠️ Ada **{unanswered} soal** yang belum dijawab. " + msg

        st.warning(msg)
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            if st.button("Ya, Submit", type="primary", key="confirm_submit"):
                st.session_state.show_submit_dialog = False
                do_submit(auto=False)
                return
        with c2:
            if st.button("Batal", key="cancel_submit"):
                st.session_state.show_submit_dialog = False
                st.rerun()

    # Tabs: Soal | Asisten Gemini
    tab_soal, tab_asisten = st.tabs(["📝 Soal", "🤖 Asisten Gemini"])

    with tab_soal:
        render_current_question()

    with tab_asisten:
        render_chat_assistant()


def render_current_question():
    idx = st.session_state.current_q
    q = QUESTIONS[idx]

    type_label = "Pilihan Ganda" if q["type"] == "mc" else "Essay"
    type_class = "" if q["type"] == "mc" else "blue"

    st.markdown(
        f"""
        <div class="q-card">
            <div class="q-meta">
                <span class="q-tag">Soal {idx + 1} dari {len(QUESTIONS)}</span>
                <span class="q-tag {type_class}">{type_label}</span>
                <span class="q-tag gray">📌 {q['points']} poin</span>
            </div>
            <div style="font-size:1.05rem;line-height:1.7;white-space:pre-wrap;">
                {q['question']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if q["type"] == "mc":
        current_ans = st.session_state.answers.get(idx)
        options = [f"{chr(65 + i)}. {opt}" for i, opt in enumerate(q["options"])]
        default_idx = current_ans if isinstance(current_ans, int) else None

        choice = st.radio(
            "Pilih jawaban Anda:",
            options=list(range(len(q["options"]))),
            format_func=lambda i: options[i],
            index=default_idx,
            key=f"mc_{idx}",
        )
        if choice is not None:
            st.session_state.answers[idx] = choice
    else:
        current_ans = st.session_state.answers.get(idx, "")
        answer = st.text_area(
            "Tulis jawaban Anda (minimal 50 kata):",
            value=current_ans if isinstance(current_ans, str) else "",
            height=250,
            key=f"essay_{idx}",
            placeholder="Tulis jawaban yang lengkap dan terstruktur. Sebut konsep, jelaskan, dan beri contoh.",
        )
        st.session_state.answers[idx] = answer
        word_count = len([w for w in answer.split() if w])
        st.caption(f"📏 {word_count} kata")

    # Navigation
    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        if idx > 0:
            if st.button("← Sebelumnya", use_container_width=True, key="prev_btn"):
                st.session_state.current_q = idx - 1
                st.rerun()
    with col_mid:
        st.markdown(
            f"<div style='text-align:center;color:#6b7280;'>Soal {idx + 1} / {len(QUESTIONS)}</div>",
            unsafe_allow_html=True,
        )
    with col_next:
        if idx < len(QUESTIONS) - 1:
            if st.button("Selanjutnya →", type="primary", use_container_width=True, key="next_btn"):
                st.session_state.current_q = idx + 1
                st.rerun()
        else:
            if st.button("✅ Submit Ujian", type="primary", use_container_width=True, key="submit_inline"):
                st.session_state.show_submit_dialog = True
                st.rerun()


def render_chat_assistant():
    st.markdown("**🤖 Asisten AI Gemini** – Tanyakan konsep, bukan jawaban langsung.")

    if not st.session_state.gemini_key:
        st.info("⚠️ Gemini API key belum diatur. Kembali ke dashboard untuk memasukkan API key, atau lanjut ujian tanpa asisten.")
        return

    # Display messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])

    # Input
    if prompt := st.chat_input("Tanyakan konsep yang ingin Anda pahami..."):
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Sedang berpikir..."):
                try:
                    # Pass history excluding the just-added user message
                    history_for_api = st.session_state.chat_history[:-1]
                    response = chat_with_gemini(prompt, history_for_api, st.session_state.gemini_key)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "text": response})
                except ValueError as e:
                    if str(e) == "API_KEY_MISSING":
                        st.error("API key belum diatur.")
                    else:
                        st.error(f"Error: {e}")
                except Exception as e:
                    st.error(f"❌ Gagal menghubungi Gemini: {e}")

        # Limit history to last 20 turns
        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-20:]


# ==================== SUBMIT & GRADE ====================
def do_submit(auto: bool = False):
    if st.session_state.submitted:
        return

    st.session_state.submitted = True
    elapsed = int(time.time() - (st.session_state.exam_start_time or time.time()))

    with st.spinner("Sedang menilai jawaban Anda..."):
        # ===== Grade MC =====
        mc_score = 0.0
        mc_details = []
        for idx, q in enumerate(QUESTIONS):
            if q["type"] != "mc":
                continue
            user_ans = st.session_state.answers.get(idx)
            is_correct = user_ans == q["correct"]
            if is_correct:
                mc_score += q["points"]
            mc_details.append({
                "index": idx,
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": q["correct"],
                "options": q["options"],
                "correct": is_correct,
                "points": q["points"],
                "earned": q["points"] if is_correct else 0,
                "explanation": q["explanation"],
            })

        # ===== Grade Essay =====
        essay_score = 0.0
        essay_details = []
        essay_indices = [(i, q) for i, q in enumerate(QUESTIONS) if q["type"] == "essay"]

        if essay_indices:
            progress = st.progress(0.0, text="Menilai essay...")
            for n, (idx, q) in enumerate(essay_indices):
                user_ans = st.session_state.answers.get(idx, "") or ""
                progress.progress(
                    (n) / len(essay_indices),
                    text=f"Menilai essay {n + 1} dari {len(essay_indices)}...",
                )

                if st.session_state.gemini_key:
                    try:
                        result = grade_essay(
                            q["question"], user_ans, q["rubric"],
                            q["points"], st.session_state.gemini_key,
                        )
                    except Exception:
                        result = grade_essay_fallback(user_ans, q["points"], q.get("keywords", []))
                else:
                    result = grade_essay_fallback(user_ans, q["points"], q.get("keywords", []))

                essay_score += result["score"]
                essay_details.append({
                    "index": idx,
                    "question": q["question"],
                    "user_answer": user_ans,
                    "points": q["points"],
                    "earned": result["score"],
                    "feedback": result["feedback"],
                    "rubric": q["rubric"],
                })

            progress.progress(1.0, text="✅ Selesai!")
            time.sleep(0.3)
            progress.empty()

        # ===== Total =====
        total = round(mc_score + essay_score, 1)
        grade = get_grade(total)

        # ===== Overall feedback =====
        feedback = generate_overall_feedback(
            st.session_state.student["name"],
            mc_score, essay_score, total,
            st.session_state.gemini_key,
        )

        # ===== Save =====
        s = st.session_state.student
        result = {
            "id": f"{s['nim']}_{int(time.time())}",
            "name": s["name"],
            "nim": s["nim"],
            "class": s["class"],
            "mc_score": mc_score,
            "essay_score": essay_score,
            "total_score": total,
            "grade": grade,
            "auto_submit": auto,
            "time_used": elapsed,
            "submitted_at": datetime.now().isoformat(),
            "mc_details": mc_details,
            "essay_details": essay_details,
            "overall_feedback": feedback,
        }
        append_result(result)
        st.session_state.result = result
        st.session_state.page = "result"
        st.rerun()


# ==================== RESULT PAGE ====================
def result_page():
    r = st.session_state.result
    if not r:
        st.error("Tidak ada hasil ujian.")
        if st.button("Kembali"):
            reset_session()
            st.rerun()
        return

    st.markdown(
        f"""
        <div class="hero-card" style="text-align:center;">
            <h1>🎉 Ujian Selesai!</h1>
            <p>Jawaban Anda telah dinilai secara otomatis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_circle, col_detail = st.columns([1, 2], gap="large")

    with col_circle:
        st.markdown(
            f"""
            <div class="score-circle">
                <span class="num">{r['total_score']}</span>
                <span class="small">/ 100</span>
            </div>
            <div style="text-align:center;margin-top:1rem;">
                <span class="badge badge-{r['grade']}" style="font-size:1.5rem;">Predikat {r['grade']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_detail:
        st.markdown("### 📊 Rincian Nilai")
        st.markdown(f"- **Pilihan Ganda:** {r['mc_score']:.1f} / {MC_TOTAL_POINTS}")
        st.markdown(f"- **Essay (AI Grading):** {r['essay_score']:.1f} / {ESSAY_TOTAL_POINTS}")
        st.markdown(f"- **Total:** {r['total_score']:.1f} / 100")
        st.markdown(f"- **Predikat:** **{r['grade']}**")
        st.markdown(f"- **Waktu Pengerjaan:** {format_time(r['time_used'])}")
        if r.get("auto_submit"):
            st.caption("⏰ Disubmit otomatis karena waktu habis.")

    st.divider()

    st.markdown("### 💬 Catatan AI")
    st.info(r.get("overall_feedback", "-"))

    # Toggle review
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("📝 Lihat / Sembunyikan Pembahasan", use_container_width=True):
            st.session_state.show_review = not st.session_state.show_review
            st.rerun()
    with col_b:
        if st.button("🚪 Selesai & Keluar", type="primary", use_container_width=True):
            reset_session()
            st.rerun()

    if st.session_state.show_review:
        render_review(r)


def render_review(r: dict):
    st.divider()
    st.markdown("## 📝 Pembahasan Jawaban")

    # MC review
    for d in r["mc_details"]:
        ua = d["user_answer"]
        user_letter = chr(65 + ua) if isinstance(ua, int) else "-"
        correct_letter = chr(65 + d["correct_answer"])
        icon = "✅" if d["correct"] else "❌"

        with st.expander(f"{icon} Soal {d['index'] + 1} (PG) – {d['earned']}/{d['points']} poin"):
            st.write(d["question"])
            st.markdown(f"**Jawaban Anda:** {user_letter}. {d['options'][ua] if isinstance(ua, int) else 'Tidak dijawab'}")
            st.markdown(f"**Jawaban Benar:** {correct_letter}. {d['options'][d['correct_answer']]}")
            st.info(f"📚 **Penjelasan:** {d['explanation']}")

    # Essay review
    for d in r["essay_details"]:
        with st.expander(f"📄 Soal {d['index'] + 1} (Essay) – {d['earned']}/{d['points']} poin"):
            st.write(d["question"])
            st.markdown("**Jawaban Anda:**")
            st.text(d["user_answer"] or "(Kosong)")
            st.success(f"💬 **Catatan AI:** {d['feedback']}")
            st.caption(f"📋 **Rubrik:** {d['rubric']}")


# ==================== LECTURER DASHBOARD ====================
def lecturer_dashboard():
    settings = load_settings()
    results = load_results()

    l = st.session_state.lecturer
    st.markdown(
        f"""
        <div class="hero-card">
            <h1>📊 Dashboard Dosen</h1>
            <p>Selamat datang, <strong>{l['name']}</strong>. Monitor hasil ujian, kelola soal, dan unduh nilai mahasiswa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown(f"**👨‍🏫 {l['name']}**")
        st.caption("Mode Dosen")
        st.divider()
        if st.button("🚪 Keluar", use_container_width=True):
            reset_session()
            st.rerun()

    # Stats
    if results:
        scores = [r["total_score"] for r in results]
        avg = sum(scores) / len(scores)
        max_s = max(scores)
        min_s = min(scores)
    else:
        avg = max_s = min_s = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Peserta", len(results))
    c2.metric("Rata-rata", f"{avg:.1f}")
    c3.metric("Tertinggi", f"{max_s:.1f}")
    c4.metric("Terendah", f"{min_s:.1f}")

    st.divider()

    # Tabs: Hasil | Pengaturan
    tab_results, tab_settings = st.tabs(["📋 Hasil Ujian", "⚙️ Pengaturan"])

    with tab_results:
        render_results_tab(results)

    with tab_settings:
        render_settings_tab(settings)


def render_results_tab(results: list):
    if not results:
        st.info("Belum ada peserta yang menyelesaikan ujian.")
        return

    # Search
    search = st.text_input("🔍 Cari nama / NIM / kelas", "")

    filtered = results
    if search.strip():
        s = search.lower().strip()
        filtered = [
            r for r in results
            if s in r["name"].lower()
            or s in r["nim"].lower()
            or s in r["class"].lower()
        ]

    # Sort by submitted_at desc
    filtered = sorted(filtered, key=lambda x: x.get("submitted_at", ""), reverse=True)

    # Action buttons
    col_csv, col_clear, _ = st.columns([1, 1, 3])
    with col_csv:
        csv_data = generate_csv(results)
        st.download_button(
            "⬇️ Ekspor CSV",
            data=csv_data,
            file_name=f"hasil-uas-kewarganegaraan-{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_clear:
        if st.button("🗑️ Hapus Semua", use_container_width=True):
            if st.session_state.get("confirm_clear"):
                save_results([])
                st.session_state.confirm_clear = False
                st.success("Semua hasil ujian dihapus.")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Klik sekali lagi untuk konfirmasi penghapusan.")

    # Tabel
    st.markdown(f"**Menampilkan {len(filtered)} peserta**")

    # Render dengan native st.dataframe + tombol detail terpisah
    table_rows = []
    for i, r in enumerate(filtered):
        table_rows.append({
            "No": i + 1,
            "Nama": r["name"],
            "NIM": r["nim"],
            "Kelas": r["class"],
            "Pilgan": f"{r['mc_score']:.1f}",
            "Essay": f"{r['essay_score']:.1f}",
            "Total": f"{r['total_score']:.1f}",
            "Predikat": r["grade"],
            "Waktu": format_dt(r["submitted_at"]),
            "Auto": "⏰" if r.get("auto_submit") else "",
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    # Detail per peserta
    st.markdown("### 🔍 Lihat Detail Jawaban")
    if filtered:
        names = [f"{r['name']} ({r['nim']}) — {r['total_score']:.1f}" for r in filtered]
        selected_idx = st.selectbox("Pilih peserta:", range(len(names)), format_func=lambda i: names[i])
        if selected_idx is not None:
            render_student_detail(filtered[selected_idx])


def render_student_detail(r: dict):
    st.markdown(f"#### {r['name']} · NIM {r['nim']} · {r['class']}")
    st.caption(f"Disubmit: {format_dt(r['submitted_at'])} · Waktu: {format_time(r.get('time_used', 0))}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilgan", f"{r['mc_score']:.1f}/{MC_TOTAL_POINTS}")
    c2.metric("Essay", f"{r['essay_score']:.1f}/{ESSAY_TOTAL_POINTS}")
    c3.metric("Total", f"{r['total_score']:.1f}/100")
    c4.metric("Predikat", r["grade"])

    if r.get("overall_feedback"):
        st.info(f"💬 {r['overall_feedback']}")

    st.markdown("##### Detail Pilihan Ganda")
    for d in r["mc_details"]:
        ua = d["user_answer"]
        user_letter = chr(65 + ua) if isinstance(ua, int) else "-"
        correct_letter = chr(65 + d["correct_answer"])
        icon = "✅" if d["correct"] else "❌"
        with st.expander(f"{icon} Soal {d['index'] + 1} ({d['earned']}/{d['points']})"):
            st.write(d["question"])
            user_text = f"{user_letter} · {d['options'][ua]}" if isinstance(ua, int) else "-"
            st.markdown(f"**Jawaban:** {user_text}")
            st.markdown(f"**Benar:** {correct_letter} · {d['options'][d['correct_answer']]}")

    st.markdown("##### Detail Essay")
    for d in r["essay_details"]:
        with st.expander(f"📄 Soal {d['index'] + 1} ({d['earned']}/{d['points']})"):
            st.write(d["question"])
            st.markdown("**Jawaban:**")
            st.text(d["user_answer"] or "(Kosong)")
            st.success(f"💬 {d['feedback']}")


def render_settings_tab(settings: dict):
    st.markdown("### 🔐 Password Akses")
    col1, col2 = st.columns(2)
    with col1:
        new_class_pwd = st.text_input("Password Kelas", value=settings["class_password"])
        if st.button("Simpan Password Kelas", key="save_class_pwd"):
            settings["class_password"] = new_class_pwd.strip()
            save_settings(settings)
            st.success("✅ Password kelas berhasil disimpan.")
            st.rerun()

    with col2:
        new_lec_pwd = st.text_input("Password Dosen", value=settings["lecturer_password"])
        if st.button("Simpan Password Dosen", key="save_lec_pwd"):
            settings["lecturer_password"] = new_lec_pwd.strip()
            save_settings(settings)
            st.success("✅ Password dosen berhasil disimpan.")
            st.rerun()

    st.divider()
    st.markdown("### ℹ️ Informasi Soal")
    st.markdown(f"- Total soal: **{len(QUESTIONS)}**")
    st.markdown(f"- Pilihan Ganda: **{len(MC_QUESTIONS)}** soal × 4 poin = **{MC_TOTAL_POINTS} poin**")
    st.markdown(f"- Essay: **{len(ESSAY_QUESTIONS)}** soal × 10 poin = **{ESSAY_TOTAL_POINTS} poin**")
    st.markdown(f"- Durasi ujian: **{EXAM_DURATION_SECONDS // 60} menit**")
    st.caption("Untuk mengubah soal, edit file `questions.py` lalu redeploy.")


def generate_csv(results: list) -> str:
    output = StringIO()
    output.write("\ufeff")  # BOM agar Excel baca UTF-8
    writer = csv.writer(output)
    writer.writerow([
        "No", "Nama", "NIM", "Kelas",
        "Pilihan Ganda", "Essay", "Total", "Predikat",
        "Waktu Submit", "Durasi", "Auto Submit",
    ])
    for i, r in enumerate(results, 1):
        writer.writerow([
            i, r["name"], r["nim"], r["class"],
            f"{r['mc_score']:.1f}",
            f"{r['essay_score']:.1f}",
            f"{r['total_score']:.1f}",
            r["grade"],
            format_dt(r["submitted_at"]),
            format_time(r.get("time_used", 0)),
            "Ya" if r.get("auto_submit") else "Tidak",
        ])
    return output.getvalue()


# ==================== ROUTER ====================
def main():
    init_state()
    inject_css()

    page = st.session_state.page
    role = st.session_state.role

    if role is None or page == "login":
        login_page()
    elif role == "student":
        if page == "student_dashboard":
            student_dashboard()
        elif page == "exam":
            exam_page()
        elif page == "result":
            result_page()
        else:
            student_dashboard()
    elif role == "lecturer":
        lecturer_dashboard()
    else:
        login_page()


if __name__ == "__main__":
    main()
