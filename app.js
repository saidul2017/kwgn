/**
 * Main Application Logic
 * UAS Kewarganegaraan - Online Exam System
 */

// ==================== STATE ====================
const STORAGE_KEYS = {
    classPwd: 'kwgn_class_pwd',
    lecturerPwd: 'kwgn_lecturer_pwd',
    results: 'kwgn_results',
    currentSession: 'kwgn_current_session'
};

const DEFAULT_CLASS_PASSWORD = 'kwgn2026';
const DEFAULT_LECTURER_PASSWORD = 'dosen2026';

const state = {
    role: null, // 'student' | 'lecturer'
    student: null, // { name, nim, class }
    lecturer: null, // { name }
    answers: {}, // { qIndex: answer }
    currentQuestion: 0,
    timer: null,
    timeLeft: EXAM_DURATION_SECONDS,
    examStarted: false,
    chatHistory: []
};

// ==================== STORAGE HELPERS ====================
function getClassPassword() {
    return localStorage.getItem(STORAGE_KEYS.classPwd) || DEFAULT_CLASS_PASSWORD;
}
function setClassPassword(pwd) {
    localStorage.setItem(STORAGE_KEYS.classPwd, pwd);
}
function getLecturerPassword() {
    return localStorage.getItem(STORAGE_KEYS.lecturerPwd) || DEFAULT_LECTURER_PASSWORD;
}
function setLecturerPassword(pwd) {
    localStorage.setItem(STORAGE_KEYS.lecturerPwd, pwd);
}
function getAllResults() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEYS.results) || '[]');
    } catch (e) {
        return [];
    }
}
function saveResult(result) {
    const all = getAllResults();
    all.push(result);
    localStorage.setItem(STORAGE_KEYS.results, JSON.stringify(all));
}
function clearAllResults() {
    localStorage.removeItem(STORAGE_KEYS.results);
}

// ==================== UTILITIES ====================
function $(selector) { return document.querySelector(selector); }
function $$(selector) { return Array.from(document.querySelectorAll(selector)); }

function showPage(pageId) {
    $$('.page').forEach(p => p.classList.remove('active'));
    $(`#${pageId}`).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showHeader(show = true) {
    const header = $('#appHeader');
    if (show) header.classList.remove('hidden');
    else header.classList.add('hidden');
}

function showToast(message, type = '') {
    const toast = $('#toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

function showConfirm(title, message) {
    return new Promise(resolve => {
        $('#confirmTitle').textContent = title;
        $('#confirmMessage').textContent = message;
        const modal = $('#confirmModal');
        modal.classList.remove('hidden');

        const cleanup = (result) => {
            modal.classList.add('hidden');
            $('#confirmOk').onclick = null;
            $('#confirmCancel').onclick = null;
            resolve(result);
        };
        $('#confirmOk').onclick = () => cleanup(true);
        $('#confirmCancel').onclick = () => cleanup(false);
    });
}

function getGrade(score) {
    if (score >= 85) return 'A';
    if (score >= 75) return 'B';
    if (score >= 65) return 'C';
    if (score >= 50) return 'D';
    return 'E';
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function formatDateTime(iso) {
    const d = new Date(iso);
    return d.toLocaleString('id-ID', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ==================== LOGIN ====================
function initLogin() {
    // Populate student dropdown dari roster
    const select = $('#studentNimSelect');
    if (select && typeof STUDENT_ROSTER !== 'undefined') {
        const sortedNims = Object.keys(STUDENT_ROSTER).sort();
        sortedNims.forEach(nim => {
            const opt = document.createElement('option');
            opt.value = nim;
            opt.textContent = `${nim} — ${STUDENT_ROSTER[nim]}`;
            select.appendChild(opt);
        });
    }

    // Pre-fill default class
    if (typeof DEFAULT_CLASS_NAME !== 'undefined') {
        const clsInput = $('#studentClass');
        if (clsInput && !clsInput.value) clsInput.value = DEFAULT_CLASS_NAME;
    }

    // Tampilkan info NIM/nama saat dropdown berubah
    if (select) {
        select.addEventListener('change', e => {
            const nim = e.target.value;
            const info = $('#studentInfo');
            if (nim && STUDENT_ROSTER[nim]) {
                $('#selectedNim').textContent = nim;
                $('#selectedName').textContent = STUDENT_ROSTER[nim];
                info.classList.remove('hidden');
            } else {
                info.classList.add('hidden');
            }
        });
    }

    // Tab switching
    $$('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const role = btn.dataset.role;
            $('#studentLoginForm').classList.toggle('hidden', role !== 'student');
            $('#lecturerLoginForm').classList.toggle('hidden', role !== 'lecturer');
            $('#loginError').classList.add('hidden');
        });
    });

    // Student login
    $('#studentLoginForm').addEventListener('submit', e => {
        e.preventDefault();
        const nim = $('#studentNimSelect').value;
        const cls = $('#studentClass').value.trim();
        const pwd = $('#classPassword').value;

        if (!nim) {
            showLoginError('Silakan pilih nama Anda dari daftar peserta.');
            return;
        }
        if (!STUDENT_ROSTER[nim]) {
            showLoginError(`NIM ${nim} tidak terdaftar di roster kelas.`);
            return;
        }
        if (!cls) {
            showLoginError('Nama kelas wajib diisi.');
            return;
        }
        if (pwd !== getClassPassword()) {
            showLoginError('Password kelas salah. Silakan tanyakan kepada dosen Anda.');
            return;
        }

        const name = STUDENT_ROSTER[nim];

        // Cek apakah NIM sudah pernah ujian
        const existing = getAllResults().find(r => r.nim === nim);
        if (existing) {
            showLoginError(`NIM ${nim} (${name}) sudah menyelesaikan ujian pada ${formatDateTime(existing.submittedAt)}. Hubungi dosen jika perlu mengulang.`);
            return;
        }

        state.role = 'student';
        state.student = { name, nim, class: cls };
        showHeader(true);
        $('#userInfo').textContent = `${name} · ${cls}`;
        $('#headerSubtitle').textContent = 'Mode Mahasiswa';
        renderStudentDashboard();
        showPage('studentDashboard');
    });

    // Lecturer login
    $('#lecturerLoginForm').addEventListener('submit', e => {
        e.preventDefault();
        const name = $('#lecturerName').value.trim();
        const pwd = $('#lecturerPassword').value;

        if (pwd !== getLecturerPassword()) {
            showLoginError('Password dosen salah.');
            return;
        }

        state.role = 'lecturer';
        state.lecturer = { name };
        showHeader(true);
        $('#userInfo').textContent = `${name} · Dosen`;
        $('#headerSubtitle').textContent = 'Mode Dosen';
        renderLecturerDashboard();
        showPage('lecturerDashboard');
    });

    // Logout
    $('#logoutBtn').addEventListener('click', async () => {
        if (state.examStarted) {
            const ok = await showConfirm('Keluar?', 'Anda sedang dalam ujian. Yakin ingin keluar? Progres tidak akan tersimpan.');
            if (!ok) return;
        }
        logout();
    });
}

function showLoginError(msg) {
    const el = $('#loginError');
    el.textContent = msg;
    el.classList.remove('hidden');
}

function logout() {
    if (state.timer) {
        clearInterval(state.timer);
        state.timer = null;
    }
    state.role = null;
    state.student = null;
    state.lecturer = null;
    state.answers = {};
    state.currentQuestion = 0;
    state.examStarted = false;
    state.chatHistory = [];
    showHeader(false);
    showPage('loginPage');
    // Clear forms
    $('#studentLoginForm').reset();
    $('#lecturerLoginForm').reset();
    $('#loginError').classList.add('hidden');
}

// ==================== STUDENT DASHBOARD ====================
function renderStudentDashboard() {
    $('#welcomeName').textContent = state.student.name;
    $('#totalQuestionsInfo').textContent = QUESTIONS.length;
    $('#mcCount').textContent = MC_QUESTIONS.length;
    $('#essayCount').textContent = ESSAY_QUESTIONS.length;

    // Tampilkan input override (kosong, karena pakai default)
    $('#geminiApiKey').value = '';
    $('#geminiApiKey').placeholder = isUsingDefaultApiKey()
        ? 'Default API key aktif (kosongkan untuk pakai default)'
        : 'Masukkan Gemini API Key Anda';
}

function initStudentDashboard() {
    $('#saveApiKey').addEventListener('click', () => {
        const key = $('#geminiApiKey').value.trim();
        setGeminiApiKey(key);
        if (key) {
            showToast('✅ Gemini API key tersimpan! Asisten AI siap digunakan.', 'success');
        } else {
            showToast('API key dihapus.', '');
        }
    });

    $('#startExamBtn').addEventListener('click', async () => {
        const ok = await showConfirm(
            'Mulai Ujian?',
            `Anda akan memulai ujian dengan durasi 90 menit. Pastikan koneksi internet stabil. Lanjutkan?`
        );
        if (ok) startExam();
    });
}

// ==================== EXAM ====================
function startExam() {
    state.examStarted = true;
    state.currentQuestion = 0;
    state.answers = {};
    state.timeLeft = EXAM_DURATION_SECONDS;

    renderNavigator();
    renderQuestion(0);
    startTimer();
    showPage('examPage');
}

function startTimer() {
    updateTimerDisplay();
    state.timer = setInterval(() => {
        state.timeLeft--;
        updateTimerDisplay();
        if (state.timeLeft <= 0) {
            clearInterval(state.timer);
            state.timer = null;
            showToast('⏰ Waktu habis! Ujian disubmit otomatis.', 'error');
            submitExam(true);
        }
    }, 1000);
}

function updateTimerDisplay() {
    const display = $('#timerDisplay');
    display.textContent = formatTime(state.timeLeft);
    const box = $('.timer-box');
    box.classList.remove('warning', 'danger');
    if (state.timeLeft <= 60) box.classList.add('danger');
    else if (state.timeLeft <= 5 * 60) box.classList.add('warning');
}

function renderNavigator() {
    const nav = $('#questionNavigator');
    nav.innerHTML = '';
    QUESTIONS.forEach((_, idx) => {
        const item = document.createElement('button');
        item.className = 'nav-item';
        item.textContent = idx + 1;
        if (idx === state.currentQuestion) item.classList.add('current');
        if (state.answers[idx] !== undefined && state.answers[idx] !== '') {
            item.classList.add('answered');
        }
        item.addEventListener('click', () => {
            saveCurrentAnswer();
            renderQuestion(idx);
        });
        nav.appendChild(item);
    });
}

function renderQuestion(idx) {
    state.currentQuestion = idx;
    const q = QUESTIONS[idx];
    const container = $('#questionContainer');

    let html = `
        <div class="question-meta">
            <span class="question-number">Soal ${idx + 1} dari ${QUESTIONS.length}</span>
            <span class="question-type">${q.type === 'mc' ? 'Pilihan Ganda' : 'Essay'}</span>
            <span class="question-points">📌 ${q.points} poin</span>
        </div>
        <div class="question-text">${escapeHtml(q.question)}</div>
    `;

    if (q.type === 'mc') {
        const selected = state.answers[idx];
        html += '<div class="options-list">';
        q.options.forEach((opt, i) => {
            const isSelected = selected === i;
            const letter = String.fromCharCode(65 + i);
            html += `
                <label class="option-item ${isSelected ? 'selected' : ''}">
                    <input type="radio" name="mc_${idx}" value="${i}" ${isSelected ? 'checked' : ''}>
                    <span class="option-letter">${letter}.</span>
                    <span>${escapeHtml(opt)}</span>
                </label>
            `;
        });
        html += '</div>';
    } else {
        const answer = state.answers[idx] || '';
        html += `
            <textarea
                class="essay-input"
                id="essay_${idx}"
                placeholder="Tulis jawaban Anda di sini... Minimal 50 kata."
            >${escapeHtml(answer)}</textarea>
            <div class="essay-counter" id="essayCounter_${idx}">${countWords(answer)} kata</div>
        `;
    }

    container.innerHTML = html;

    // Bind events
    if (q.type === 'mc') {
        $$(`input[name="mc_${idx}"]`).forEach(input => {
            input.addEventListener('change', () => {
                state.answers[idx] = parseInt(input.value, 10);
                renderNavigator();
                $$('.option-item').forEach(o => o.classList.remove('selected'));
                input.closest('.option-item').classList.add('selected');
            });
        });
    } else {
        const textarea = $(`#essay_${idx}`);
        const counter = $(`#essayCounter_${idx}`);
        textarea.addEventListener('input', () => {
            state.answers[idx] = textarea.value;
            counter.textContent = `${countWords(textarea.value)} kata`;
            renderNavigator();
        });
    }

    // Update controls
    $('#prevQuestionBtn').disabled = idx === 0;
    $('#nextQuestionBtn').textContent = idx === QUESTIONS.length - 1 ? 'Ke Ringkasan →' : 'Selanjutnya →';
    $('#questionProgress').textContent = `Soal ${idx + 1} / ${QUESTIONS.length}`;

    renderNavigator();
}

function countWords(text) {
    return (text || '').trim().split(/\s+/).filter(Boolean).length;
}

function saveCurrentAnswer() {
    const idx = state.currentQuestion;
    const q = QUESTIONS[idx];
    if (q.type === 'essay') {
        const textarea = $(`#essay_${idx}`);
        if (textarea) state.answers[idx] = textarea.value;
    }
}

function initExam() {
    $('#prevQuestionBtn').addEventListener('click', () => {
        saveCurrentAnswer();
        if (state.currentQuestion > 0) renderQuestion(state.currentQuestion - 1);
    });

    $('#nextQuestionBtn').addEventListener('click', () => {
        saveCurrentAnswer();
        if (state.currentQuestion < QUESTIONS.length - 1) {
            renderQuestion(state.currentQuestion + 1);
        } else {
            confirmAndSubmit();
        }
    });

    $('#submitExamBtn').addEventListener('click', confirmAndSubmit);

    // Chat widget
    $('#chatToggle').addEventListener('click', () => {
        $('#chatWidget').classList.toggle('collapsed');
    });
    $('#chatClose').addEventListener('click', () => {
        $('#chatWidget').classList.add('collapsed');
    });
    $('#chatForm').addEventListener('submit', handleChatSubmit);

    // Anti-cheat: warn on tab switch
    document.addEventListener('visibilitychange', () => {
        if (document.hidden && state.examStarted) {
            showToast('⚠️ Hindari berpindah tab/window selama ujian!', 'error');
        }
    });

    // Prevent accidental close
    window.addEventListener('beforeunload', e => {
        if (state.examStarted) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

async function confirmAndSubmit() {
    saveCurrentAnswer();
    const unanswered = QUESTIONS.filter((_, i) => {
        const a = state.answers[i];
        return a === undefined || a === '' || a === null;
    });

    let msg = 'Yakin ingin submit ujian? Jawaban tidak dapat diubah setelah disubmit.';
    if (unanswered.length > 0) {
        msg = `Ada ${unanswered.length} soal yang belum dijawab. ${msg}`;
    }
    const ok = await showConfirm('Submit Ujian?', msg);
    if (ok) submitExam(false);
}

// ==================== CHAT ASSISTANT ====================
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = $('#chatInput');
    const message = input.value.trim();
    if (!message) return;
    input.value = '';

    appendChatMessage('user', message);

    if (!hasGeminiApiKey()) {
        appendChatMessage('bot', '⚠️ Gemini API key belum diatur. Kembali ke dashboard untuk memasukkan API key, atau lanjutkan ujian tanpa asisten AI.');
        return;
    }

    const loadingEl = appendChatMessage('bot', '🤔 Sedang berpikir...', 'loading');

    try {
        const response = await chatWithGemini(message, state.chatHistory);
        loadingEl.remove();
        appendChatMessage('bot', response);
        state.chatHistory.push({ role: 'user', text: message });
        state.chatHistory.push({ role: 'model', text: response });
        // Limit history to last 10 turns
        if (state.chatHistory.length > 20) {
            state.chatHistory = state.chatHistory.slice(-20);
        }
    } catch (err) {
        loadingEl.remove();
        let errMsg = '❌ Gagal terhubung ke Gemini. ';
        if (err.message === 'API_KEY_MISSING') errMsg += 'API key belum diatur.';
        else if (err.message === 'API_KEY_INVALID') errMsg += 'API key tidak valid. Periksa kembali.';
        else if (err.message === 'API_RATE_LIMIT') errMsg += 'Batas request tercapai. Coba lagi sebentar.';
        else errMsg += 'Coba lagi nanti.';
        appendChatMessage('bot', errMsg);
    }
}

function appendChatMessage(role, text, extraClass = '') {
    const container = $('#chatMessages');
    const msg = document.createElement('div');
    msg.className = `chat-msg ${role} ${extraClass}`.trim();
    // Simple paragraph splitting
    const paragraphs = text.split(/\n\n+/).filter(Boolean);
    if (paragraphs.length === 0) paragraphs.push(text);
    paragraphs.forEach(p => {
        const pEl = document.createElement('p');
        pEl.textContent = p;
        msg.appendChild(pEl);
    });
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
    return msg;
}

// ==================== SUBMIT & GRADING ====================
async function submitExam(autoSubmit) {
    saveCurrentAnswer();
    state.examStarted = false;
    if (state.timer) {
        clearInterval(state.timer);
        state.timer = null;
    }

    showPage('resultPage');
    $('#aiFeedbackText').textContent = 'Menilai jawaban Anda... Mohon tunggu sebentar.';
    $('#finalScore').textContent = '...';
    $('#mcScore').textContent = '...';
    $('#essayScore').textContent = '...';
    $('#totalScore').textContent = '...';
    $('#gradeLabel').textContent = '...';

    // Grade Multiple Choice
    let mcScore = 0;
    const mcDetails = [];
    QUESTIONS.forEach((q, idx) => {
        if (q.type !== 'mc') return;
        const userAnswer = state.answers[idx];
        const correct = userAnswer === q.correct;
        if (correct) mcScore += q.points;
        mcDetails.push({
            index: idx,
            question: q.question,
            userAnswer,
            correctAnswer: q.correct,
            options: q.options,
            correct,
            points: q.points,
            earned: correct ? q.points : 0,
            explanation: q.explanation
        });
    });

    // Grade Essay (use Gemini if available)
    let essayScore = 0;
    const essayDetails = [];
    for (let idx = 0; idx < QUESTIONS.length; idx++) {
        const q = QUESTIONS[idx];
        if (q.type !== 'essay') continue;
        const userAnswer = state.answers[idx] || '';
        let result;

        if (hasGeminiApiKey()) {
            try {
                result = await gradeEssayWithGemini(q.question, userAnswer, q.rubric, q.points);
            } catch (e) {
                result = gradeEssayFallback(userAnswer, q.rubric, q.points, q.keywords);
            }
        } else {
            result = gradeEssayFallback(userAnswer, q.rubric, q.points, q.keywords);
        }

        essayScore += result.score;
        essayDetails.push({
            index: idx,
            question: q.question,
            userAnswer,
            points: q.points,
            earned: result.score,
            feedback: result.feedback,
            rubric: q.rubric
        });
    }

    // Total (sudah dalam skala 100 karena MC=60 + Essay=40)
    const total = Math.round((mcScore + essayScore) * 10) / 10;
    const grade = getGrade(total);

    // Display
    $('#mcScore').textContent = `${mcScore} / ${MC_TOTAL_POINTS}`;
    $('#essayScore').textContent = `${essayScore} / ${ESSAY_TOTAL_POINTS}`;
    $('#totalScore').textContent = `${total} / 100`;
    $('#finalScore').textContent = total;
    $('#gradeLabel').textContent = grade;

    // Save result
    const result = {
        id: `${state.student.nim}_${Date.now()}`,
        name: state.student.name,
        nim: state.student.nim,
        class: state.student.class,
        mcScore,
        essayScore,
        totalScore: total,
        grade,
        autoSubmit,
        timeUsed: EXAM_DURATION_SECONDS - state.timeLeft,
        submittedAt: new Date().toISOString(),
        mcDetails,
        essayDetails
    };
    saveResult(result);

    // AI feedback
    try {
        const feedback = await generateOverallFeedback(state.student.name, mcScore, essayScore, total);
        $('#aiFeedbackText').textContent = feedback;
    } catch (e) {
        $('#aiFeedbackText').textContent = generateOverallFeedbackFallback(mcScore, essayScore, total);
    }

    // Render review
    renderReview(mcDetails, essayDetails);
}

function renderReview(mcDetails, essayDetails) {
    const section = $('#reviewSection');
    let html = '<h3 style="margin-bottom:1rem;">📝 Pembahasan Jawaban</h3>';

    mcDetails.forEach(d => {
        const userLetter = d.userAnswer !== undefined ? String.fromCharCode(65 + d.userAnswer) : '-';
        const correctLetter = String.fromCharCode(65 + d.correctAnswer);
        html += `
            <div class="review-item ${d.correct ? 'correct' : 'incorrect'}">
                <h4>Soal ${d.index + 1} ${d.correct ? '✅' : '❌'} (${d.earned}/${d.points} poin)</h4>
                <p>${escapeHtml(d.question)}</p>
                <div class="answer-row"><strong>Jawaban Anda:</strong> ${userLetter}. ${escapeHtml(d.userAnswer !== undefined ? d.options[d.userAnswer] : 'Tidak dijawab')}</div>
                <div class="answer-row"><strong>Jawaban Benar:</strong> ${correctLetter}. ${escapeHtml(d.options[d.correctAnswer])}</div>
                <div class="explanation"><strong>📚 Penjelasan:</strong> ${escapeHtml(d.explanation)}</div>
            </div>
        `;
    });

    essayDetails.forEach(d => {
        html += `
            <div class="review-item essay">
                <h4>Soal ${d.index + 1} - Essay (${d.earned}/${d.points} poin)</h4>
                <p>${escapeHtml(d.question)}</p>
                <div class="answer-row"><strong>Jawaban Anda:</strong></div>
                <p style="background:white;padding:0.75rem;border-radius:6px;white-space:pre-wrap;">${escapeHtml(d.userAnswer || '(Kosong)')}</p>
                <div class="explanation"><strong>💬 Catatan AI:</strong> ${escapeHtml(d.feedback)}</div>
                <div class="explanation"><strong>📋 Rubrik:</strong> ${escapeHtml(d.rubric)}</div>
            </div>
        `;
    });

    section.innerHTML = html;
}

function initResult() {
    $('#reviewAnswersBtn').addEventListener('click', () => {
        const section = $('#reviewSection');
        section.classList.toggle('hidden');
        const btn = $('#reviewAnswersBtn');
        btn.textContent = section.classList.contains('hidden') ? '📝 Lihat Pembahasan' : '🙈 Sembunyikan Pembahasan';
    });

    $('#finishBtn').addEventListener('click', () => {
        logout();
    });
}

// ==================== LECTURER DASHBOARD ====================
function renderLecturerDashboard() {
    const results = getAllResults();

    // Stats
    $('#statTotal').textContent = results.length;
    if (results.length > 0) {
        const scores = results.map(r => r.totalScore);
        const avg = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
        $('#statAvg').textContent = avg;
        $('#statMax').textContent = Math.max(...scores).toFixed(1);
        $('#statMin').textContent = Math.min(...scores).toFixed(1);
    } else {
        $('#statAvg').textContent = '-';
        $('#statMax').textContent = '-';
        $('#statMin').textContent = '-';
    }

    // Settings
    $('#settingsClassPwd').value = getClassPassword();
    $('#settingsLecturerPwd').value = getLecturerPassword();

    // Roster
    renderRoster(results);

    // Table
    renderResultsTable(results);
}

function renderRoster(results) {
    if (typeof STUDENT_ROSTER === 'undefined') return;

    const nimToResult = {};
    results.forEach(r => { nimToResult[r.nim] = r; });

    const total = Object.keys(STUDENT_ROSTER).length;
    const done = Object.keys(STUDENT_ROSTER).filter(nim => nimToResult[nim]).length;
    const pending = total - done;

    $('#rosterTotal').textContent = total;
    $('#rosterDone').textContent = done;
    $('#rosterPending').textContent = pending;
    $('#rosterPercent').textContent = total ? `${Math.round(done / total * 100)}%` : '0%';

    const filter = $('#rosterFilter').value || 'all';
    const sortedNims = Object.keys(STUDENT_ROSTER).sort();
    const tbody = $('#rosterTableBody');

    let rows = '';
    let counter = 0;
    sortedNims.forEach(nim => {
        const name = STUDENT_ROSTER[nim];
        const r = nimToResult[nim];
        const isDone = !!r;

        if (filter === 'done' && !isDone) return;
        if (filter === 'pending' && isDone) return;

        counter++;
        const status = isDone
            ? '<span class="badge badge-A">✅ Sudah</span>'
            : '<span class="badge badge-D">⏳ Belum</span>';
        const total = isDone ? r.totalScore : '-';
        const grade = isDone ? `<span class="badge badge-${r.grade}">${r.grade}</span>` : '-';
        const submittedAt = isDone ? formatDateTime(r.submittedAt) : '-';

        rows += `
            <tr>
                <td>${counter}</td>
                <td>${escapeHtml(nim)}</td>
                <td>${escapeHtml(name)}</td>
                <td>${status}</td>
                <td>${total}</td>
                <td>${grade}</td>
                <td>${submittedAt}</td>
            </tr>
        `;
    });

    if (!rows) rows = '<tr><td colspan="7" class="text-center muted">Tidak ada data sesuai filter.</td></tr>';
    tbody.innerHTML = rows;
}

function renderResultsTable(results) {
    const tbody = $('#resultsTableBody');
    if (results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center muted">Belum ada peserta yang menyelesaikan ujian.</td></tr>';
        return;
    }

    // Sort by submitted desc
    const sorted = [...results].sort((a, b) =>
        new Date(b.submittedAt) - new Date(a.submittedAt)
    );

    tbody.innerHTML = sorted.map((r, i) => `
        <tr>
            <td>${i + 1}</td>
            <td>${escapeHtml(r.name)}</td>
            <td>${escapeHtml(r.nim)}</td>
            <td>${escapeHtml(r.class)}</td>
            <td>${r.mcScore}</td>
            <td>${r.essayScore}</td>
            <td><strong>${r.totalScore}</strong></td>
            <td><span class="badge badge-${r.grade}">${r.grade}</span></td>
            <td>${formatDateTime(r.submittedAt)}${r.autoSubmit ? ' <small>(auto)</small>' : ''}</td>
            <td><button class="btn btn-ghost detail-btn" data-id="${r.id}">Detail</button></td>
        </tr>
    `).join('');

    $$('.detail-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const r = results.find(x => x.id === btn.dataset.id);
            if (r) showDetailModal(r);
        });
    });
}

function showDetailModal(result) {
    const body = $('#modalBody');
    let html = `
        <div style="margin-bottom:1.5rem;">
            <h2 style="margin-bottom:0.25rem;">${escapeHtml(result.name)}</h2>
            <p class="muted">NIM: ${escapeHtml(result.nim)} · Kelas: ${escapeHtml(result.class)}</p>
            <p class="muted">Disubmit: ${formatDateTime(result.submittedAt)} ${result.autoSubmit ? '(auto-submit)' : ''}</p>
            <p class="muted">Waktu pengerjaan: ${formatTime(result.timeUsed)}</p>
        </div>
        <div class="info-grid" style="margin-bottom:1.5rem;">
            <div class="info-box"><span class="info-label">Pilgan</span><span class="info-value">${result.mcScore}/${MC_TOTAL_POINTS}</span></div>
            <div class="info-box"><span class="info-label">Essay</span><span class="info-value">${result.essayScore}/${ESSAY_TOTAL_POINTS}</span></div>
            <div class="info-box"><span class="info-label">Total</span><span class="info-value">${result.totalScore}</span></div>
            <div class="info-box"><span class="info-label">Predikat</span><span class="info-value">${result.grade}</span></div>
        </div>
        <h3 style="margin-bottom:0.75rem;">Detail Jawaban Pilihan Ganda</h3>
    `;

    result.mcDetails.forEach(d => {
        const userLetter = d.userAnswer !== undefined ? String.fromCharCode(65 + d.userAnswer) : '-';
        const correctLetter = String.fromCharCode(65 + d.correctAnswer);
        html += `
            <div class="review-item ${d.correct ? 'correct' : 'incorrect'}">
                <h4>Soal ${d.index + 1} ${d.correct ? '✅' : '❌'} (${d.earned}/${d.points})</h4>
                <p>${escapeHtml(d.question)}</p>
                <div class="answer-row"><strong>Jawaban:</strong> ${userLetter} ${d.userAnswer !== undefined ? '· ' + escapeHtml(d.options[d.userAnswer]) : ''}</div>
                <div class="answer-row"><strong>Benar:</strong> ${correctLetter} · ${escapeHtml(d.options[d.correctAnswer])}</div>
            </div>
        `;
    });

    html += '<h3 style="margin:1.5rem 0 0.75rem;">Detail Jawaban Essay</h3>';
    result.essayDetails.forEach(d => {
        html += `
            <div class="review-item essay">
                <h4>Soal ${d.index + 1} (${d.earned}/${d.points} poin)</h4>
                <p>${escapeHtml(d.question)}</p>
                <div class="answer-row"><strong>Jawaban:</strong></div>
                <p style="background:white;padding:0.75rem;border-radius:6px;white-space:pre-wrap;">${escapeHtml(d.userAnswer || '(Kosong)')}</p>
                <div class="explanation"><strong>Catatan AI:</strong> ${escapeHtml(d.feedback)}</div>
            </div>
        `;
    });

    body.innerHTML = html;
    $('#detailModal').classList.remove('hidden');
}

function exportToCSV() {
    const results = getAllResults();
    if (results.length === 0) {
        showToast('Belum ada data untuk diekspor.', 'error');
        return;
    }

    const headers = ['No', 'Nama', 'NIM', 'Kelas', 'Pilihan Ganda', 'Essay', 'Total', 'Predikat', 'Waktu Submit', 'Durasi'];
    const rows = results.map((r, i) => [
        i + 1,
        `"${r.name.replace(/"/g, '""')}"`,
        r.nim,
        r.class,
        r.mcScore,
        r.essayScore,
        r.totalScore,
        r.grade,
        formatDateTime(r.submittedAt),
        formatTime(r.timeUsed)
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hasil-uas-kewarganegaraan-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('✅ File CSV berhasil diunduh.', 'success');
}

function initLecturerDashboard() {
    $('#exportCsvBtn').addEventListener('click', exportToCSV);

    // Roster filter
    const rosterFilter = $('#rosterFilter');
    if (rosterFilter) {
        rosterFilter.addEventListener('change', () => {
            renderRoster(getAllResults());
        });
    }

    $('#clearResultsBtn').addEventListener('click', async () => {
        const ok = await showConfirm(
            'Hapus Semua Hasil?',
            'Semua hasil ujian mahasiswa akan dihapus permanen. Lanjutkan?'
        );
        if (ok) {
            clearAllResults();
            renderLecturerDashboard();
            showToast('Semua hasil ujian dihapus.', '');
        }
    });

    $('#saveClassPwdBtn').addEventListener('click', () => {
        const pwd = $('#settingsClassPwd').value.trim();
        if (!pwd) {
            showToast('Password tidak boleh kosong.', 'error');
            return;
        }
        setClassPassword(pwd);
        showToast('✅ Password kelas berhasil disimpan.', 'success');
    });

    $('#saveLecturerPwdBtn').addEventListener('click', () => {
        const pwd = $('#settingsLecturerPwd').value.trim();
        if (!pwd) {
            showToast('Password tidak boleh kosong.', 'error');
            return;
        }
        setLecturerPassword(pwd);
        showToast('✅ Password dosen berhasil disimpan.', 'success');
    });

    $('#searchInput').addEventListener('input', e => {
        const q = e.target.value.toLowerCase().trim();
        const all = getAllResults();
        const filtered = q
            ? all.filter(r =>
                r.name.toLowerCase().includes(q) ||
                r.nim.toLowerCase().includes(q) ||
                r.class.toLowerCase().includes(q)
            )
            : all;
        renderResultsTable(filtered);
    });

    // Modal close
    $('#closeModalBtn').addEventListener('click', () => {
        $('#detailModal').classList.add('hidden');
    });
    $('#detailModal .modal-backdrop').addEventListener('click', () => {
        $('#detailModal').classList.add('hidden');
    });
}

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    initLogin();
    initStudentDashboard();
    initExam();
    initResult();
    initLecturerDashboard();
    showHeader(false);
    showPage('loginPage');
});
