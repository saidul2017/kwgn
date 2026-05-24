"""
Gemini API integration untuk Streamlit app.
- chat_with_gemini: chatbot asisten edukasi
- grade_essay: AI grading untuk soal essay
- generate_overall_feedback: ringkasan & motivasi setelah ujian
- grade_essay_fallback: fallback grading bila API tidak tersedia
"""

import json
import re

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    GENAI_AVAILABLE = False

MODEL_NAME = "gemini-2.0-flash"

CHAT_SYSTEM_PROMPT = """Anda adalah asisten edukasi untuk mata kuliah Pendidikan Kewarganegaraan Indonesia.

ATURAN PENTING:
1. JANGAN PERNAH memberikan jawaban langsung untuk soal ujian. Mahasiswa sedang ujian.
2. Anda HANYA boleh menjelaskan konsep, teori, sejarah, dan prinsip umum.
3. Jika ditanya soal pilihan ganda atau essay spesifik, balas dengan: "Maaf, saya tidak bisa memberikan jawaban langsung. Tapi saya bisa menjelaskan konsepnya. Mau saya jelaskan tentang topik X?"
4. Berikan penjelasan singkat (maksimal 4-6 kalimat), padat, dan dalam Bahasa Indonesia.
5. Fokus pada topik: Pancasila, UUD 1945, HAM, Demokrasi, Wawasan Nusantara, Bela Negara, Otonomi Daerah, Kewarganegaraan, Identitas Nasional, Integrasi Nasional, Konstitusi.
6. Gunakan tone ramah, edukatif, dan memotivasi.
7. Jika pertanyaan di luar topik kewarganegaraan, arahkan kembali ke topik yang relevan."""


def _ensure_genai(api_key: str):
    if not GENAI_AVAILABLE:
        raise RuntimeError("Library google-generativeai belum terinstall. Jalankan: pip install google-generativeai")
    if not api_key:
        raise ValueError("API_KEY_MISSING")
    genai.configure(api_key=api_key)


def chat_with_gemini(message: str, history: list, api_key: str) -> str:
    """
    Chat dengan Gemini sebagai asisten ujian.
    history: list of {role: 'user'|'assistant', text: str}
    """
    _ensure_genai(api_key)

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=CHAT_SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 512,
        },
    )

    # Convert history to Gemini format
    gemini_history = []
    for h in history:
        role = "user" if h["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [h["text"]]})

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(message)
    return response.text or ""


def grade_essay(question: str, student_answer: str, rubric: str, max_points: int, api_key: str) -> dict:
    """
    Grade essay menggunakan Gemini.
    Mengembalikan {'score': float, 'feedback': str}
    """
    if not student_answer or not student_answer.strip():
        return {"score": 0.0, "feedback": "Tidak ada jawaban yang diberikan."}

    _ensure_genai(api_key)

    system_prompt = f"""Anda adalah dosen Pendidikan Kewarganegaraan yang menilai esai mahasiswa secara objektif dan adil.

TUGAS:
- Berikan skor 0 hingga {max_points} berdasarkan rubrik penilaian.
- Berikan umpan balik singkat (maksimal 2 kalimat) dalam Bahasa Indonesia.
- Bersikap proporsional: jawaban sangat singkat/asal-asalan = 0-3, jawaban cukup = 4-6, jawaban baik = 7-8, jawaban sempurna = 9-{max_points}.
- Output WAJIB dalam format JSON valid: {{"score": <angka>, "feedback": "<umpan balik>"}}
- Jangan tambahkan markdown, code fence, atau teks lain di luar JSON."""

    user_prompt = f"""SOAL:
{question}

RUBRIK PENILAIAN (skor maks {max_points}):
{rubric}

JAWABAN MAHASISWA:
{student_answer}

Berikan penilaian dalam JSON: {{"score": <0-{max_points}>, "feedback": "<umpan balik singkat>"}}"""

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 256,
        },
    )

    try:
        response = model.generate_content(user_prompt)
        text = (response.text or "").strip()
        # Hapus code fence kalau ada
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        # Cari JSON object pertama
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON in response")

        parsed = json.loads(match.group(0))
        score = float(parsed.get("score", 0))
        score = max(0.0, min(float(max_points), score))
        feedback = str(parsed.get("feedback", "Tidak ada umpan balik."))

        return {"score": round(score, 1), "feedback": feedback}
    except Exception as e:
        # Fallback
        return grade_essay_fallback(student_answer, max_points, [])


def grade_essay_fallback(student_answer: str, max_points: int, keywords: list = None) -> dict:
    """
    Fallback grading bila Gemini tidak tersedia.
    Menggunakan kombinasi panjang jawaban + keyword matching.
    """
    keywords = keywords or []
    text = (student_answer or "").lower()
    word_count = len([w for w in text.split() if w])

    # Skor berdasar panjang jawaban
    if word_count >= 100:
        length_score = 0.6
    elif word_count >= 50:
        length_score = 0.4
    elif word_count >= 20:
        length_score = 0.25
    elif word_count >= 5:
        length_score = 0.1
    else:
        length_score = 0.0

    # Skor berdasar keyword
    if keywords:
        matched = sum(1 for kw in keywords if kw.lower() in text)
        keyword_score = min(0.4, (matched / len(keywords)) * 0.4)
    else:
        keyword_score = 0.2

    ratio = min(1.0, length_score + keyword_score)
    score = round(max_points * ratio, 1)

    return {
        "score": score,
        "feedback": "Penilaian otomatis berdasarkan panjang & kata kunci jawaban. Aktifkan Gemini API untuk penilaian AI yang lebih akurat.",
    }


def generate_overall_feedback(student_name: str, mc_score: float, essay_score: float, total: float, api_key: str = "") -> str:
    """
    Generate ringkasan & motivasi setelah ujian.
    """
    if not api_key or not GENAI_AVAILABLE:
        return _fallback_overall_feedback(total)

    try:
        _ensure_genai(api_key)
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction="Anda adalah dosen Pendidikan Kewarganegaraan yang memberikan umpan balik untuk mahasiswa setelah ujian. Berikan umpan balik singkat (3-4 kalimat) dalam Bahasa Indonesia: tonjolkan kekuatan, area perbaikan, dan motivasi.",
            generation_config={"temperature": 0.7, "max_output_tokens": 256},
        )
        prompt = f"""Mahasiswa: {student_name}
Nilai Pilihan Ganda: {mc_score}
Nilai Essay: {essay_score}
Total: {total}/100

Berikan umpan balik singkat dan motivasional."""
        response = model.generate_content(prompt)
        return response.text or _fallback_overall_feedback(total)
    except Exception:
        return _fallback_overall_feedback(total)


def _fallback_overall_feedback(total: float) -> str:
    if total >= 85:
        return "Selamat! Hasil ujian Anda sangat baik. Pemahaman Anda terhadap materi Kewarganegaraan tergolong istimewa. Pertahankan dan terus tingkatkan kontribusi sebagai warga negara yang baik."
    if total >= 70:
        return "Hasil yang baik! Anda menunjukkan pemahaman yang solid. Perdalam beberapa konsep yang masih lemah untuk mencapai pemahaman yang lebih komprehensif."
    if total >= 55:
        return "Hasil cukup. Masih ada beberapa konsep yang perlu diperdalam, terutama pada soal essay. Teruslah belajar dan diskusi dengan teman."
    return "Anda perlu belajar lebih giat lagi. Tinjau kembali materi Pancasila, UUD 1945, dan HAM. Konsultasikan dengan dosen untuk pemahaman yang lebih baik."
