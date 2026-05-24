/**
 * Gemini API integration
 * - chatWithGemini(prompt, history): untuk chatbot asisten
 * - gradeEssayWithGemini(question, answer, rubric, maxPoints): untuk grade essay
 *
 * Uses Google Generative AI REST API:
 * https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent
 */

const GEMINI_MODEL = 'gemini-1.5-flash-latest';
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const GEMINI_STORAGE_KEY = 'kwgn_gemini_api_key';

function getGeminiApiKey() {
    // Priority: user-saved key > default key from students.js (jika tersedia)
    const userKey = localStorage.getItem(GEMINI_STORAGE_KEY);
    if (userKey) return userKey;
    if (typeof DEFAULT_GEMINI_API_KEY !== 'undefined' && DEFAULT_GEMINI_API_KEY) {
        return DEFAULT_GEMINI_API_KEY;
    }
    return '';
}

function setGeminiApiKey(key) {
    if (key) {
        localStorage.setItem(GEMINI_STORAGE_KEY, key.trim());
    } else {
        localStorage.removeItem(GEMINI_STORAGE_KEY);
    }
}

function hasGeminiApiKey() {
    return !!getGeminiApiKey();
}

function isUsingDefaultApiKey() {
    return !localStorage.getItem(GEMINI_STORAGE_KEY) &&
        typeof DEFAULT_GEMINI_API_KEY !== 'undefined' && !!DEFAULT_GEMINI_API_KEY;
}

/**
 * Generic Gemini call helper.
 * @param {string} systemInstruction
 * @param {Array<{role:'user'|'model', text:string}>} contents
 * @param {object} generationConfig
 */
async function callGemini(systemInstruction, contents, generationConfig = {}) {
    const apiKey = getGeminiApiKey();
    if (!apiKey) {
        throw new Error('API_KEY_MISSING');
    }

    const body = {
        systemInstruction: systemInstruction
            ? { parts: [{ text: systemInstruction }] }
            : undefined,
        contents: contents.map(c => ({
            role: c.role,
            parts: [{ text: c.text }]
        })),
        generationConfig: {
            temperature: 0.7,
            topP: 0.95,
            maxOutputTokens: 1024,
            ...generationConfig
        },
        safetySettings: [
            { category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_ONLY_HIGH' },
            { category: 'HARM_CATEGORY_HATE_SPEECH', threshold: 'BLOCK_ONLY_HIGH' },
            { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_ONLY_HIGH' },
            { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_ONLY_HIGH' }
        ]
    };

    const url = `${GEMINI_ENDPOINT}?key=${encodeURIComponent(apiKey)}`;

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (!response.ok) {
        const errorBody = await response.text();
        console.error('Gemini API error:', response.status, errorBody);
        if (response.status === 400 || response.status === 403) {
            throw new Error('API_KEY_INVALID');
        }
        if (response.status === 429) {
            throw new Error('API_RATE_LIMIT');
        }
        throw new Error('API_ERROR');
    }

    const data = await response.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    if (!text) {
        throw new Error('EMPTY_RESPONSE');
    }
    return text;
}

/**
 * Chat dengan Gemini sebagai asisten ujian.
 * Gemini diinstruksikan untuk TIDAK memberikan jawaban langsung,
 * hanya menjelaskan konsep & teori.
 */
async function chatWithGemini(userMessage, history = []) {
    const systemInstruction = `Anda adalah asisten edukasi untuk mata kuliah Pendidikan Kewarganegaraan Indonesia.

ATURAN PENTING:
1. JANGAN PERNAH memberikan jawaban langsung untuk soal ujian. Mahasiswa sedang ujian.
2. Anda HANYA boleh menjelaskan konsep, teori, sejarah, dan prinsip umum.
3. Jika ditanya soal pilihan ganda atau essay spesifik, balas dengan: "Maaf, saya tidak bisa memberikan jawaban langsung. Tapi saya bisa menjelaskan konsepnya. Mau saya jelaskan tentang topik X?"
4. Berikan penjelasan singkat (maksimal 4-6 kalimat), padat, dan dalam Bahasa Indonesia.
5. Fokus pada topik: Pancasila, UUD 1945, HAM, Demokrasi, Wawasan Nusantara, Bela Negara, Otonomi Daerah, Kewarganegaraan, Identitas Nasional, Integrasi Nasional, Konstitusi.
6. Gunakan tone ramah, edukatif, dan memotivasi.
7. Jika pertanyaan di luar topik kewarganegaraan, arahkan kembali ke topik yang relevan.`;

    const contents = [
        ...history,
        { role: 'user', text: userMessage }
    ];

    return await callGemini(systemInstruction, contents, { maxOutputTokens: 512 });
}

/**
 * Grade essay menggunakan Gemini.
 * Mengembalikan { score: number, feedback: string }
 */
async function gradeEssayWithGemini(question, studentAnswer, rubric, maxPoints) {
    if (!studentAnswer || studentAnswer.trim().length === 0) {
        return { score: 0, feedback: 'Tidak ada jawaban yang diberikan.' };
    }

    const systemInstruction = `Anda adalah dosen Pendidikan Kewarganegaraan yang menilai esai mahasiswa secara objektif dan adil.

TUGAS:
- Berikan skor 0 hingga ${maxPoints} berdasarkan rubrik penilaian.
- Berikan umpan balik singkat (maksimal 2 kalimat) dalam Bahasa Indonesia.
- Bersikap proporsional: jawaban sangat singkat/asal-asalan = 0-3, jawaban cukup = 4-6, jawaban baik = 7-8, jawaban sempurna = 9-10.
- Output WAJIB dalam format JSON valid: {"score": <angka>, "feedback": "<umpan balik>"}
- Jangan tambahkan markdown, code fence, atau teks lain di luar JSON.`;

    const userPrompt = `SOAL:
${question}

RUBRIK PENILAIAN (skor maks ${maxPoints}):
${rubric}

JAWABAN MAHASISWA:
${studentAnswer}

Berikan penilaian dalam JSON: {"score": <0-${maxPoints}>, "feedback": "<umpan balik singkat>"}`;

    try {
        const responseText = await callGemini(systemInstruction, [
            { role: 'user', text: userPrompt }
        ], { temperature: 0.3, maxOutputTokens: 256 });

        // Coba parse JSON dari response
        let cleaned = responseText.trim();
        // Hapus code fence kalau ada
        cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();
        // Cari JSON object pertama
        const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
        if (!jsonMatch) throw new Error('NO_JSON');

        const parsed = JSON.parse(jsonMatch[0]);
        let score = Number(parsed.score);
        if (isNaN(score)) score = 0;
        score = Math.max(0, Math.min(maxPoints, score));

        return {
            score: Math.round(score * 10) / 10,
            feedback: parsed.feedback || 'Tidak ada umpan balik.'
        };
    } catch (err) {
        console.warn('Gemini grading failed, using fallback:', err);
        return gradeEssayFallback(studentAnswer, rubric, maxPoints);
    }
}

/**
 * Fallback grading jika Gemini API tidak tersedia.
 * Menggunakan keyword matching dari rubric.
 */
function gradeEssayFallback(studentAnswer, rubric, maxPoints, keywords = []) {
    const text = (studentAnswer || '').toLowerCase();
    const wordCount = text.split(/\s+/).filter(Boolean).length;

    // Skor minimum berdasarkan panjang
    let lengthScore = 0;
    if (wordCount >= 100) lengthScore = 0.6;
    else if (wordCount >= 50) lengthScore = 0.4;
    else if (wordCount >= 20) lengthScore = 0.25;
    else if (wordCount >= 5) lengthScore = 0.1;

    // Skor berdasarkan keyword (kalau tersedia)
    let keywordScore = 0;
    if (keywords && keywords.length > 0) {
        const matched = keywords.filter(kw => text.includes(kw.toLowerCase())).length;
        keywordScore = Math.min(0.4, (matched / keywords.length) * 0.4);
    } else {
        keywordScore = 0.2;
    }

    const ratio = Math.min(1, lengthScore + keywordScore);
    const score = Math.round(maxPoints * ratio * 10) / 10;

    return {
        score,
        feedback: hasGeminiApiKey()
            ? 'Penilaian otomatis berdasarkan panjang dan kata kunci jawaban (AI grading gagal).'
            : 'Penilaian otomatis berdasarkan panjang & kata kunci. Aktifkan Gemini API untuk penilaian AI yang lebih akurat.'
    };
}

/**
 * Generate ringkasan/feedback total ujian
 */
async function generateOverallFeedback(studentName, mcScore, essayScore, total) {
    if (!hasGeminiApiKey()) {
        return generateOverallFeedbackFallback(mcScore, essayScore, total);
    }

    try {
        const systemInstruction = `Anda adalah dosen Pendidikan Kewarganegaraan yang memberikan umpan balik untuk mahasiswa setelah ujian.
Berikan umpan balik singkat (3-4 kalimat) dalam Bahasa Indonesia: tonjolkan kekuatan, area perbaikan, dan motivasi.`;

        const prompt = `Mahasiswa: ${studentName}
Nilai Pilihan Ganda: ${mcScore}
Nilai Essay: ${essayScore}
Total: ${total}/100

Berikan umpan balik singkat dan motivasional.`;

        return await callGemini(systemInstruction, [{ role: 'user', text: prompt }], { maxOutputTokens: 256 });
    } catch (err) {
        return generateOverallFeedbackFallback(mcScore, essayScore, total);
    }
}

function generateOverallFeedbackFallback(mcScore, essayScore, total) {
    if (total >= 85) return 'Selamat! Hasil ujian Anda sangat baik. Pemahaman Anda terhadap materi Kewarganegaraan tergolong istimewa. Pertahankan dan terus tingkatkan kontribusi sebagai warga negara yang baik.';
    if (total >= 70) return 'Hasil yang baik! Anda menunjukkan pemahaman yang solid. Perdalam beberapa konsep yang masih lemah untuk mencapai pemahaman yang lebih komprehensif.';
    if (total >= 55) return 'Hasil cukup. Masih ada beberapa konsep yang perlu diperdalam, terutama pada soal essay. Teruslah belajar dan diskusi dengan teman.';
    return 'Anda perlu belajar lebih giat lagi. Tinjau kembali materi Pancasila, UUD 1945, dan HAM. Konsultasikan dengan dosen untuk pemahaman yang lebih baik.';
}
