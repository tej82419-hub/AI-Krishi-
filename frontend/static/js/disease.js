/**
 * AI Krishi – Disease Detection Module
 */

let selectedImageData = null;
let cameraStream = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
        showToast('Image too large. Please select an image under 10MB.', 'error');
        return;
    }
    loadImagePreview(file);
}

function handleDragOver(event) {
    event.preventDefault();
    document.getElementById('uploadArea').classList.add('drag-over');
}

function handleFileDrop(event) {
    event.preventDefault();
    document.getElementById('uploadArea').classList.remove('drag-over');
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        loadImagePreview(file);
    } else {
        showToast('Please drop an image file', 'error');
    }
}

function loadImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        selectedImageData = e.target.result;
        document.getElementById('previewImg').src = selectedImageData;
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('uploadArea').style.display = 'none';
        document.querySelector('.camera-option').style.display = 'none';
        // Reset analysis
        document.getElementById('analysisResult').innerHTML = `
            <div class="analysis-placeholder">
                <span>📸</span>
                <p>Image loaded! Click "Analyze for Diseases" to get AI analysis.</p>
            </div>`;
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    selectedImageData = null;
    document.getElementById('previewImg').src = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.querySelector('.camera-option').style.display = 'flex';
    document.getElementById('fileInput').value = '';
    document.getElementById('analysisResult').innerHTML = `
        <div class="analysis-placeholder">
            <span>🌱</span>
            <p>Upload a crop image to get AI-powered disease analysis</p>
            <div class="tips-box">
                <h4>📌 Tips for Best Results:</h4>
                <ul>
                    <li>Take a close-up photo of the affected leaves or plant parts</li>
                    <li>Ensure good lighting – natural daylight is best</li>
                    <li>Include both healthy and affected plant parts</li>
                    <li>Take photos from multiple angles if possible</li>
                </ul>
            </div>
        </div>`;
}

async function analyzeDisease() {
    if (!selectedImageData) {
        showToast('Please select an image first', 'error');
        return;
    }

    const result = document.getElementById('analysisResult');
    result.innerHTML = `
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:3rem;margin-bottom:16px;">🔬</div>
            <h3 style="color:var(--green-dark);margin-bottom:8px;">Analyzing Your Crop...</h3>
            <p style="color:var(--text-light);margin-bottom:20px;">AI is examining the image for diseases, deficiencies and pest damage</p>
            <div class="loading-spinner"><i class="fas fa-spinner fa-spin fa-2x"></i></div>
        </div>`;

    try {
        const resp = await fetch(`${API_BASE}/disease/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_data: selectedImageData })
        });

        const data = await resp.json();

        if (!resp.ok) {
            result.innerHTML = `
                <div class="analysis-placeholder">
                    <span>❌</span>
                    <p style="color:var(--red)">${data.error || 'Analysis failed'}</p>
                    <p>${data.suggestion || ''}</p>
                </div>`;
            return;
        }

        const isDemo = data.is_demo ? `
            <div style="background:#FFF8E1;border:1px solid #FFD54F;border-radius:10px;padding:12px;margin-bottom:16px;font-size:0.85rem;color:#795548;">
                ⚠️ <strong>Demo Mode:</strong> ${data.disclaimer}
            </div>` : '';

        result.innerHTML = `
            <div class="analysis-content">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                    <span style="font-size:1.5rem;">🔬</span>
                    <h3 style="color:var(--green-dark);">Analysis Complete</h3>
                    ${data.is_ai_powered ? '<span style="background:var(--green-pale);color:var(--green);padding:4px 12px;border-radius:15px;font-size:0.75rem;font-weight:600;">AI Powered</span>' : ''}
                </div>
                ${isDemo}
                ${formatMarkdown(data.analysis)}
                <div style="margin-top:20px;padding:14px;background:#FFF3E0;border-radius:10px;font-size:0.85rem;color:#E65100;">
                    <strong>⚠️ Important:</strong> ${data.disclaimer}
                </div>
                <div style="margin-top:12px;padding:12px;background:var(--green-pale);border-radius:10px;font-size:0.85rem;">
                    📞 <strong>${data.emergency_contact || 'Kisan Call Centre: 1800-180-1551 (Free, 24/7)'}</strong>
                </div>
                <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap;">
                    <button class="btn btn-primary" onclick="speakAnalysis('${escapeAttr(data.analysis)}')">
                        🔊 Listen to Analysis
                    </button>
                    <button class="btn btn-outline" onclick="askAIAboutDisease('${escapeAttr(data.analysis)}')">
                        💬 Ask Follow-up Question
                    </button>
                </div>
            </div>`;

    } catch (e) {
        result.innerHTML = `
            <div class="analysis-placeholder">
                <span>⚠️</span>
                <p style="color:var(--red);">Unable to analyze. Please check backend connection.</p>
                <p>Describe your crop symptoms to the <a onclick="navigateTo('assistant')" style="color:var(--green);cursor:pointer;font-weight:600;">AI Chat Assistant</a> instead.</p>
            </div>`;
    }
}

function speakAnalysis(text) {
    Voice.speak(text, AppState.currentLang);
}

function askAIAboutDisease(analysis) {
    const shortAnalysis = analysis.substring(0, 200) + '...';
    navigateTo('assistant');
    setTimeout(() => {
        document.getElementById('chatInput').value = `Based on this disease analysis: "${shortAnalysis}" - What additional steps should I take?`;
    }, 500);
}

// ===== CAMERA =====
async function openCamera() {
    const modal = document.getElementById('cameraModal');
    const video = document.getElementById('cameraVideo');

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        video.srcObject = cameraStream;
        modal.style.display = 'flex';
    } catch (e) {
        showToast('Camera access denied. Please allow camera permission.', 'error');
    }
}

function capturePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    selectedImageData = canvas.toDataURL('image/jpeg', 0.9);

    document.getElementById('previewImg').src = selectedImageData;
    document.getElementById('imagePreview').style.display = 'block';
    document.getElementById('uploadArea').style.display = 'none';
    document.querySelector('.camera-option').style.display = 'none';

    closeCamera();
    showToast('Photo captured! Click Analyze to check for diseases.');
}

function closeCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
        cameraStream = null;
    }
    document.getElementById('cameraModal').style.display = 'none';
}
