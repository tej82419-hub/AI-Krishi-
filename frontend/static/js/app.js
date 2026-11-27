/**
 * AI Krishi – Main Application JavaScript
 * Handles navigation, chat, auth, FAQ, schemes
 */

// ===== CONFIG =====
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';

// ===== STATE =====
const AppState = {
    currentPage: 'home',
    currentLang: 'en',
    farmer: null,
    chatHistory: [],
    isSpeaking: false
};

// ===== LOADER =====
window.addEventListener('load', () => {
    setTimeout(() => {
        const loader = document.getElementById('pageLoader');
        if (loader) loader.classList.add('hidden');
    }, 1200);

    initApp();
});

function initApp() {
    // Handle navbar scroll
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 10);
    });

    // Handle nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) navigateTo(page);
            closeMobileNav();
        });
    });

    // Load FAQs
    loadFAQs();

    // Load market crops
    loadMarketCrops();

    // Load market states
    loadMarketStates();

    // Load schemes
    loadSchemes();

    // Restore session
    const savedFarmer = localStorage.getItem('krishi_farmer');
    if (savedFarmer) {
        AppState.farmer = JSON.parse(savedFarmer);
        updateAuthButton();
    }

    // Handle URL hash navigation
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(hash)) navigateTo(hash);
}

// ===== NAVIGATION =====
function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    const target = document.getElementById(page);
    if (target) {
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    document.querySelectorAll(`.nav-link[data-page="${page}"]`).forEach(l => l.classList.add('active'));
    AppState.currentPage = page;
    window.location.hash = page;
}

function toggleMobileNav() {
    document.getElementById('navLinks').classList.toggle('open');
}

function closeMobileNav() {
    document.getElementById('navLinks').classList.remove('open');
}

// ===== LANGUAGE =====
function setLanguage(lang) {
    AppState.currentLang = lang;
    document.getElementById('globalLang').value = lang;
    document.getElementById('chatLang').value = lang;

    // Update active pill
    document.querySelectorAll('.lang-pill').forEach(p => p.classList.remove('active'));
    document.querySelectorAll(`.lang-pill`).forEach(p => {
        if (p.textContent.trim() === getLangLabel(lang)) p.classList.add('active');
    });

    Voice.setLanguage(lang);
    showToast(`Language changed to ${getLangLabel(lang)}`);
}

function getLangLabel(lang) {
    return { en: 'English', hi: 'हिंदी', ta: 'தமிழ்', te: 'తెలుగు' }[lang] || lang;
}

function updateChatLanguage(lang) {
    setLanguage(lang);
}

document.getElementById('globalLang')?.addEventListener('change', (e) => setLanguage(e.target.value));

// ===== CHAT / AI ASSISTANT =====
let chatConversationHistory = [];

function sendQuickQuestion(q) {
    document.getElementById('chatInput').value = q;
    sendMessage();
}

function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Clear quick questions on first message
    const welcome = document.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    input.value = '';

    // Show user message
    appendMessage('user', message);

    // Show typing indicator
    const typingId = showTyping();

    try {
        const response = await fetch(`${API_BASE}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                language: AppState.currentLang,
                history: chatConversationHistory.slice(-12)
            })
        });

        const data = await response.json();
        removeTyping(typingId);

        if (!response.ok) throw new Error(data.error || 'Server error');

        const aiResponse = data.response;
        appendMessage('ai', aiResponse);

        // Update history
        chatConversationHistory.push(
            { role: 'user', content: message },
            { role: 'ai', content: aiResponse }
        );

        // Save to DB if logged in
        if (AppState.farmer) {
            saveChatHistory(AppState.farmer.id, message, aiResponse);
        }

        // Auto-speak if enabled
        if (document.getElementById('autoSpeak')?.checked) {
            Voice.speak(aiResponse, AppState.currentLang);
        }

    } catch (error) {
        removeTyping(typingId);
        appendMessage('ai', `⚠️ Could not connect to AI service. Please check your internet connection and try again.\n\n**Offline Tip:** Call Kisan Call Centre: **1800-180-1551** (Free, 24/7)`);
        console.error('Chat error:', error);
    }
}

function appendMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message-bubble ${role}`;

    const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const formattedContent = formatMarkdown(content);

    div.innerHTML = `
        <div class="msg-avatar">${role === 'ai' ? '🌾' : '👤'}</div>
        <div>
            <div class="msg-content">${formattedContent}</div>
            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                <span class="msg-time">${time}</span>
                ${role === 'ai' ? `<button class="msg-speak-btn" onclick="speakMessage(this, '${escapeAttr(content)}')">🔊 Listen</button>` : ''}
            </div>
        </div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function speakMessage(btn, text) {
    if (Voice.isSpeaking) {
        Voice.stopSpeaking();
        btn.textContent = '🔊 Listen';
        return;
    }
    btn.textContent = '⏹️ Stop';
    Voice.speak(text, AppState.currentLang, () => {
        btn.textContent = '🔊 Listen';
    });
}

function formatMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/#{3}\s(.*)/g, '<h5>$1</h5>')
        .replace(/#{2}\s(.*)/g, '<h4>$1</h4>')
        .replace(/#{1}\s(.*)/g, '<h4>$1</h4>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/\n{2,}/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function escapeAttr(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    const id = 'typing-' + Date.now();
    container.insertAdjacentHTML('beforeend', `
        <div class="typing-indicator" id="${id}">
            <div class="msg-avatar">🌾</div>
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTyping(id) {
    document.getElementById(id)?.remove();
}

function clearChat() {
    if (!confirm('Clear chat history?')) return;
    document.getElementById('chatMessages').innerHTML = `
        <div class="chat-welcome">
            <div class="welcome-icon">🌾</div>
            <h3>Namaste! I'm AI Krishi</h3>
            <p>Ask me anything about farming, crop diseases, fertilizers, or market prices!</p>
        </div>`;
    chatConversationHistory = [];
}

// ===== VOICE INPUT =====
let voiceTimeout = null;

function toggleVoiceInput() {
    if (Voice.isListening) {
        stopVoiceInput();
        return;
    }

    const micBtn = document.getElementById('micBtn');
    const voiceStatus = document.getElementById('voiceStatus');

    if (!Voice.isSupported) {
        showToast('Voice not supported in this browser. Please use Chrome.', 'error');
        return;
    }

    const started = Voice.start(
        (transcript, isFinal) => {
            document.getElementById('chatInput').value = transcript;
            document.getElementById('voiceStatusText').textContent = `Listening: "${transcript}"`;
        },
        (finalTranscript) => {
            stopVoiceInput();
            if (finalTranscript.trim()) {
                setTimeout(() => sendMessage(), 300);
            }
        },
        (errorMsg) => {
            stopVoiceInput();
            showToast(errorMsg, 'error');
        }
    );

    if (started) {
        micBtn.classList.add('listening');
        micBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceStatus.style.display = 'flex';
        document.getElementById('voiceStatusText').textContent = 'Listening...';

        // Auto-stop after 10 seconds
        voiceTimeout = setTimeout(() => stopVoiceInput(), 10000);
    }
}

function stopVoiceInput() {
    Voice.stop();
    clearTimeout(voiceTimeout);
    const micBtn = document.getElementById('micBtn');
    micBtn.classList.remove('listening');
    micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    document.getElementById('voiceStatus').style.display = 'none';
}

// ===== FERTILIZER GUIDANCE =====
async function getGuidance() {
    const crop = document.getElementById('guidanceCrop').value;
    const area = document.getElementById('guidanceArea').value;
    const soil = document.getElementById('guidanceSoil').value;

    if (!crop) {
        showToast('Please select a crop first', 'warning');
        return;
    }

    const result = document.getElementById('guidanceResult');
    result.style.display = 'block';
    result.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading guidance...</div>';

    // Build the guidance query and send to AI
    const query = `Give me fertilizer and irrigation schedule for ${crop} crop on ${area} hectare ${soil} soil. Include NPK doses, timing and water requirements.`;
    
    try {
        const resp = await fetch(`${API_BASE}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query, language: 'en', history: [] })
        });
        const data = await resp.json();
        result.innerHTML = `<h5>🌱 ${crop} Guidance (${area} ha, ${soil} soil)</h5>` + formatMarkdown(data.response);
    } catch (e) {
        result.innerHTML = getOfflineGuidance(crop, area);
    }
}

function getOfflineGuidance(crop, area) {
    const guides = {
        'Rice': { npk: '120:60:60 kg/ha', doses: ['Basal: DAP 150 kg + MOP 60 kg', 'Tillering (21d): Urea 65 kg', 'Panicle (45d): Urea 65 kg'], water: '5-7 cm standing water during tillering' },
        'Wheat': { npk: '120:60:40 kg/ha', doses: ['Basal: DAP 130 kg + MOP 67 kg', 'CRI (21d): Urea 87 kg', 'Tillering (45d): Urea 87 kg'], water: '5 irrigations at critical stages' },
        'Tomato': { npk: '150:75:75 kg/ha', doses: ['Basal: FYM 25t + DAP 163 kg', '30d: Urea 109 kg', '60d: Urea 109 kg + Potash 62 kg'], water: 'Every 7-10 days, avoid flooding' },
        'Cotton': { npk: '150:60:60 kg/ha', doses: ['Basal: FYM 10t + DAP 130 kg', 'Squaring (40d): Urea 109 kg', 'Boll dev (75d): Urea 109 kg'], water: 'Critical: squaring and boll development' },
        'Maize': { npk: '120:60:40 kg/ha', doses: ['Basal: DAP 130 kg + MOP 67 kg', 'Knee-high (25d): Urea 87 kg', 'Tasseling (55d): Urea 87 kg'], water: '5 irrigations including at tasseling' }
    };
    const g = guides[crop];
    if (!g) return `<p>Guidance for ${crop} loading... Please try asking the AI assistant above.</p>`;
    return `
        <h5>🌱 ${crop} – ${area} ha</h5>
        <strong>NPK:</strong> ${g.npk}<br>
        <strong>Doses:</strong><ul>${g.doses.map(d => `<li>${d}</li>`).join('')}</ul>
        <strong>Irrigation:</strong> ${g.water}<br><br>
        <small>⚠️ Consult local KVK for variety-specific advice</small>
    `;
}

// ===== FAQ =====
async function loadFAQs() {
    const container = document.getElementById('faqContainer');
    if (!container) return;

    try {
        const resp = await fetch(`${API_BASE}/ai/faq`);
        const data = await resp.json();
        renderFAQs(data.faqs, container);
    } catch (e) {
        // Fallback FAQs
        renderFAQs([
            { id: 1, question: "What are the signs of nitrogen deficiency?", answer: "Yellowing of older leaves starting from bottom, stunted growth. Apply urea @ 10-15 kg/bigha.", category: "fertilizer" },
            { id: 2, question: "How often to irrigate wheat?", answer: "Wheat needs 4-6 irrigations: at crown root (21d), tillering (45d), jointing (65d), flowering (85d), dough stage (100d).", category: "irrigation" },
            { id: 3, question: "How to control pests organically in rice?", answer: "Use Neem oil (5ml/litre), install light traps, use Trichoderma for soil treatment.", category: "pest" },
            { id: 4, question: "What government schemes are available?", answer: "PM-KISAN (₹6000/year), PMFBY (Crop Insurance), KCC (Kisan Credit Card), PMKSY (Irrigation).", category: "schemes" },
            { id: 5, question: "How to test soil health?", answer: "Collect soil from 15cm depth from multiple spots. Send to nearest Soil Testing Lab (free under Soil Health Card scheme).", category: "soil" }
        ], container);
    }
}

function renderFAQs(faqs, container) {
    container.innerHTML = faqs.map(faq => `
        <div class="faq-item" id="faq-${faq.id}">
            <div class="faq-question" onclick="toggleFAQ(${faq.id})">
                <span>${faq.question}</span>
                <div style="display:flex;gap:8px;align-items:center;">
                    <span class="faq-category">${faq.category}</span>
                    <span class="faq-icon">▼</span>
                </div>
            </div>
            <div class="faq-answer" id="faq-answer-${faq.id}">${faq.answer}</div>
        </div>
    `).join('');
}

function toggleFAQ(id) {
    const question = document.querySelector(`#faq-${id} .faq-question`);
    const answer = document.getElementById(`faq-answer-${id}`);
    question.classList.toggle('open');
    answer.classList.toggle('open');
}

// ===== SCHEMES =====
async function loadSchemes() {
    const grid = document.getElementById('schemesGrid');
    if (!grid) return;

    try {
        const resp = await fetch(`${API_BASE}/schemes/`);
        const data = await resp.json();
        allSchemes = data.schemes;
        renderSchemes(allSchemes);
        renderHelplines(data.helplines || []);
    } catch (e) {
        grid.innerHTML = '<p class="text-center" style="color:var(--text-light);padding:40px;">Unable to load schemes. Please check backend connection.</p>';
    }
}

let allSchemes = [];

function renderSchemes(schemes) {
    const grid = document.getElementById('schemesGrid');
    if (!schemes.length) {
        grid.innerHTML = '<p class="text-center">No schemes found</p>';
        return;
    }
    grid.innerHTML = schemes.map(s => `
        <div class="scheme-card" data-category="${s.category}">
            <div class="scheme-header">
                <span class="scheme-icon">${s.icon}</span>
                <div class="scheme-name">${s.name}</div>
            </div>
            <div class="scheme-benefit">💰 ${s.benefit}</div>
            <div class="scheme-details"><strong>Eligibility:</strong> ${s.eligibility}</div>
            <div class="scheme-docs">
                <strong>Documents:</strong><br>
                ${(s.documents || []).map(d => `<span>${d}</span>`).join('')}
            </div>
            <div class="scheme-details"><strong>How to Apply:</strong> ${s.how_to_apply}</div>
            <a href="${s.link}" target="_blank" class="scheme-link">
                <i class="fas fa-external-link-alt"></i> Official Website
            </a>
        </div>
    `).join('');
}

function filterSchemes(category, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filtered = category === 'all' ? allSchemes : allSchemes.filter(s => s.category === category);
    renderSchemes(filtered);
}

function renderHelplines(helplines) {
    const grid = document.getElementById('helplinesGrid');
    if (!grid) return;
    grid.innerHTML = helplines.map(h => `
        <div class="helpline-card">
            <div class="helpline-name">📞 ${h.name}</div>
            <div class="helpline-num">${h.number}</div>
            <div class="helpline-availability">${h.available}</div>
        </div>
    `).join('');
}

// ===== AUTH =====
function showModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'flex';
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'none';
}

function closeModalOnOverlay(event, id) {
    if (event.target.id === id) closeModal(id);
}

function switchTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll(`.auth-tab[onclick*="${tab}"]`).forEach(t => t.classList.add('active'));

    document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('registerForm').style.display = tab === 'register' ? 'block' : 'none';
    document.getElementById('authMessage').style.display = 'none';
    document.getElementById('authTitle').textContent = tab === 'login' ? '🌾 Farmer Login' : '🌱 Create Account';
}

async function handleLogin(e) {
    e.preventDefault();
    const phone = document.getElementById('loginPhone').value;
    const password = document.getElementById('loginPassword').value;

    showAuthMessage('Logging in...', 'info');

    try {
        const resp = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });
        const data = await resp.json();

        if (!resp.ok) {
            showAuthMessage(data.error || 'Login failed', 'error');
            return;
        }

        AppState.farmer = data.farmer;
        localStorage.setItem('krishi_farmer', JSON.stringify(data.farmer));
        updateAuthButton();
        showAuthMessage(`✅ ${data.message}`, 'success');
        setTimeout(() => closeModal('authModal'), 1500);
        showToast(`Welcome back, ${data.farmer.name}!`);

    } catch (e) {
        showAuthMessage('Connection error. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('regName').value,
        phone: document.getElementById('regPhone').value,
        village: document.getElementById('regVillage').value,
        district: document.getElementById('regDistrict').value,
        primary_crop: document.getElementById('regCrop').value,
        land_acres: document.getElementById('regLand').value,
        password: document.getElementById('regPassword').value,
        language: AppState.currentLang
    };

    showAuthMessage('Creating account...', 'info');

    try {
        const resp = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await resp.json();

        if (!resp.ok) {
            showAuthMessage(result.error || 'Registration failed', 'error');
            return;
        }

        showAuthMessage(`✅ ${result.message}`, 'success');
        setTimeout(() => switchTab('login'), 2000);

    } catch (e) {
        showAuthMessage('Connection error. Please try again.', 'error');
    }
}

function showAuthMessage(msg, type) {
    const el = document.getElementById('authMessage');
    el.textContent = msg;
    el.className = `auth-message ${type}`;
    el.style.display = 'block';
}

function updateAuthButton() {
    const btn = document.getElementById('authBtn');
    if (AppState.farmer) {
        btn.innerHTML = `<i class="fas fa-user-check"></i> ${AppState.farmer.name.split(' ')[0]}`;
        btn.onclick = logoutFarmer;
    } else {
        btn.innerHTML = `<i class="fas fa-user"></i> Login`;
        btn.onclick = () => showModal('authModal');
    }
}

function logoutFarmer() {
    if (!confirm('Are you sure you want to logout?')) return;
    AppState.farmer = null;
    localStorage.removeItem('krishi_farmer');
    updateAuthButton();
    showToast('Logged out successfully');
}

async function saveChatHistory(farmerId, userMsg, aiMsg) {
    try {
        await fetch(`${API_BASE}/auth/save-chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                farmer_id: farmerId,
                user_message: userMsg,
                ai_response: aiMsg,
                language: AppState.currentLang
            })
        });
    } catch (e) {
        console.warn('Could not save chat history:', e);
    }
}

// ===== TOAST =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 4000);
}

// ===== MARKET PRICES =====
async function loadMarketCrops() {
    try {
        const resp = await fetch(`${API_BASE}/market/crops`);
        const data = await resp.json();
        const select = document.getElementById('marketCrop');
        if (select) {
            data.crops.forEach(crop => {
                select.insertAdjacentHTML('beforeend', `<option value="${crop}">${crop}</option>`);
            });
        }
    } catch (e) {
        console.warn('Could not load market crops');
    }
}

async function loadMarketStates() {
    try {
        const resp = await fetch(`${API_BASE}/market/states`);
        const data = await resp.json();
        const select = document.getElementById('marketState');
        if (select) {
            data.states.forEach(state => {
                select.insertAdjacentHTML('beforeend', `<option value="${state}">${state}</option>`);
            });
        }
    } catch (e) {
        console.warn('Could not load states');
    }
}
