# 🌾 AI Krishi – Smart Farming Assistant

> **Smart Farming, Better Future.**  
> AI-powered agriculture assistant for Indian farmers — voice chat, crop disease detection, real-time weather, market prices and government scheme finder.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🤖 **AI Voice Assistant** | Ask farming questions by voice or text in English, Hindi, Tamil, Telugu |
| 🔬 **Crop Disease Detection** | Upload crop photo → AI diagnoses diseases and suggests treatment |
| 🌤️ **Real Weather Alerts** | Live weather + farming-specific alerts (heat, rain, drought) |
| 📈 **Market Prices** | Commodity prices across Indian mandis with MSP comparison |
| 🌱 **Fertilizer & Irrigation** | Crop-specific NPK schedules and water management advice |
| 📋 **Govt. Schemes** | PM-KISAN, PMFBY, KCC, PMKSY and 8+ schemes with official links |
| 👤 **Farmer Registration** | Save your profile, chat history and preferences |
| 📞 **Emergency Helplines** | Kisan Call Centre and other agricultural helplines |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python 3.10+, Flask, Flask-CORS |
| **AI Model** | Google Gemini 1.5 Flash (chat + vision) |
| **Speech Recognition** | Web Speech API (browser-native, free) |
| **Text-to-Speech** | Web Speech Synthesis API (browser-native) |
| **Weather** | OpenWeatherMap API (free tier) |
| **Database** | SQLite (via Python `sqlite3`) |
| **Image Analysis** | Google Gemini Vision API |

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.10 or higher
- A modern browser (Chrome recommended for voice features)
- API keys (see below)

### Step 1 – Clone / Navigate to project
```bash
cd /Users/jp/scalar/ai-krishi
```

### Step 2 – Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows
```

### Step 3 – Install dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4 – Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your API keys:

| Key | Where to get it | Required? |
|---|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) – Free | Yes (for AI chat + disease) |
| `OPENWEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api) – Free tier | Yes (for real weather) |

> **Without API keys**, the app still works in **Demo Mode** with offline fallback responses. All UI features remain functional.

### Step 5 – Start the backend server
```bash
cd backend
python app.py
```
Server starts at: **http://localhost:5000**

### Step 6 – Open the frontend
Open `frontend/index.html` in your browser, **OR** visit **http://localhost:5000** (the Flask server also serves the frontend).

---

## 📁 Project Structure

```
ai-krishi/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── requirements.txt        # Python dependencies
│   └── routes/
│       ├── ai_assistant.py     # Gemini AI chat + FAQ
│       ├── disease.py          # Crop disease image analysis
│       ├── weather.py          # OpenWeatherMap integration
│       ├── market.py           # Market prices & MSP data
│       ├── auth.py             # Farmer registration/login (SQLite)
│       ├── schemes.py          # Government schemes data
│       └── fertilizer.py       # Fertilizer/irrigation guidance
├── frontend/
│   ├── index.html              # Main SPA page
│   └── static/
│       ├── css/
│       │   └── style.css       # Full responsive stylesheet
│       └── js/
│           ├── app.js          # Core app logic, navigation, auth
│           ├── voice.js        # Voice recognition & TTS module
│           ├── disease.js      # Disease detection UI
│           ├── weather.js      # Weather UI
│           └── market.js       # Market prices UI
├── database/
│   └── krishi.db               # SQLite DB (auto-created)
├── .env.example                # Environment variables template
├── .gitignore
└── README.md
```

---

## 🎙️ Voice Features

Voice is powered by the **browser's native Web Speech API** — no extra API key needed.

| Feature | Details |
|---|---|
| **Languages** | English (en-IN), Hindi (hi-IN), Tamil (ta-IN), Telugu (te-IN) |
| **Browser Support** | Chrome ✅ · Edge ✅ · Safari ✅ · Firefox ⚠️ (limited) |
| **Listen to AI** | Each AI response has a 🔊 "Listen" button |
| **Speak to AI** | Click the 🎙️ microphone button in the chat |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/chat` | AI farming question (text or voice transcript) |
| GET | `/api/ai/faq` | Frequently asked farming questions |
| GET | `/api/weather/current` | Real-time weather by location or GPS |
| GET | `/api/weather/forecast` | 5-day weather forecast |
| GET | `/api/market/prices` | Commodity prices by crop and state |
| GET | `/api/market/crops` | List of available crops |
| POST | `/api/disease/analyze` | Crop disease image analysis |
| POST | `/api/auth/register` | Farmer registration |
| POST | `/api/auth/login` | Farmer login |
| GET | `/api/schemes/` | Government schemes list |
| GET | `/health` | Health check |

---

## ⚠️ Important Disclaimers

1. **Disease Detection** – AI analysis is a preliminary assessment only. Always consult a qualified agricultural expert or Krishi Vigyan Kendra for confirmation before applying treatments.

2. **Market Prices** – Sample data is shown for demonstration. For real-time prices, visit [agmarknet.gov.in](https://agmarknet.gov.in) or [enam.gov.in](https://www.enam.gov.in).

3. **Weather** – Real data requires a free OpenWeatherMap API key. Without it, demo data is shown with a clear disclaimer.

4. **AI Advice** – AI responses are for general guidance only. Always verify with local agricultural officers or Krishi Vigyan Kendra before making major farming decisions.

---

## 📞 Important Helplines (Always Available)

| Helpline | Number | Timing |
|---|---|---|
| Kisan Call Centre | **1800-180-1551** | 24/7, Free |
| PM Kisan Helpline | **155261** | Working hours |
| PMFBY Helpline | **1800-200-7710** | Working hours |

---

## 🏫 For College Presentation

This project demonstrates:
- **AI Integration** – Real LLM API (Gemini) for natural language farming advice
- **Computer Vision** – Image-based crop disease detection
- **Voice Technology** – Speech recognition + TTS in Indian languages
- **Full-Stack Development** – Python Flask backend + HTML/CSS/JS frontend
- **Database Integration** – SQLite for farmer profiles and chat history
- **Real APIs** – OpenWeatherMap, Google Gemini
- **Responsive Design** – Works on mobile, tablet and desktop
- **Multilingual** – English, Hindi, Tamil, Telugu support

---

## 🤝 Contributing

This is an academic project. For improvements:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

*Built with ❤️ for Indian Farmers | AI Krishi 2024*
