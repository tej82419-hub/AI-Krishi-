"""
AI Assistant Route – handles chat and voice queries
"""

from flask import Blueprint, request, jsonify
import os
import json
import google.generativeai as genai
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are AI Krishi, a smart farming assistant designed to help Indian farmers.
You specialize in:
- Crop disease diagnosis and prevention
- Fertilizer and nutrient management
- Irrigation advice and water management
- Weather-based farming decisions
- Pest management (using safe, recommended practices)
- Soil health and improvement
- Market price guidance
- Government agricultural schemes

Guidelines:
1. Always give practical, actionable advice suited to Indian farming conditions
2. Use simple language that farmers can understand
3. When diagnosing diseases or pests from descriptions, list possible causes and ask clarifying questions
4. Never claim certainty for disease diagnosis without professional inspection
5. Recommend consulting local Krishi Vigyan Kendra (KVK) or agricultural officers for serious issues
6. Mention safe, government-approved pesticides/fertilizers when relevant
7. Consider local climate and crop varieties common in India
8. Be culturally sensitive and empathetic to farmer challenges
9. If asked in Hindi or Tamil or Telugu, respond in the same language
10. Keep responses concise but complete – farmers need quick answers

Always end serious disease/pest queries with: "Please consult your nearest Krishi Vigyan Kendra or agricultural officer for professional advice."
"""

AGRICULTURAL_KNOWLEDGE = {
    "common_diseases": {
        "tomato": ["Early Blight", "Late Blight", "Leaf Curl Virus", "Fusarium Wilt"],
        "rice": ["Blast", "Brown Spot", "Bacterial Leaf Blight", "Sheath Blight"],
        "wheat": ["Rust (Yellow/Brown/Black)", "Powdery Mildew", "Loose Smut"],
        "cotton": ["Bollworm", "Whitefly", "Alternaria Leaf Spot"],
    },
    "fertilizer_guide": {
        "rice": "NPK 120:60:60 kg/ha, split in 3 doses",
        "wheat": "NPK 120:60:40 kg/ha",
        "tomato": "NPK 150:75:75 kg/ha with micronutrients",
        "cotton": "NPK 150:60:60 kg/ha",
    }
}


def get_fallback_response(query):
    """Fallback response when API is unavailable"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['yellow', 'leaves', 'turning']):
        return """**Yellowing Leaves – Possible Causes:**

1. **Nitrogen Deficiency** – Most common cause. Apply urea (46% N) @ 10-15 kg per bigha
2. **Overwatering** – Reduce irrigation frequency, ensure proper drainage
3. **Disease (Early Blight/Fusarium)** – Look for brown spots or wilting alongside yellowing
4. **Pest Attack** – Check leaf undersides for aphids, mites, or whiteflies

**Immediate Steps:**
- Take 3-4 affected leaves to your nearest Krishi Vigyan Kendra
- Spray Neem oil (5ml/litre) as a safe first measure
- Avoid applying chemical pesticides without confirmed diagnosis

Please consult your nearest Krishi Vigyan Kendra or agricultural officer for professional advice."""

    if any(word in query_lower for word in ['rain', 'water', 'flood', 'drought']):
        return """**Weather & Irrigation Advisory:**

🌧️ **Excess Rain/Flooding:**
- Ensure field drainage channels are clear
- Apply fungicide (Mancozeb) preventively after flooding
- Delay fertilizer application until soil dries

☀️ **Drought/Low Rainfall:**
- Use drip irrigation if available (subsidized under PMKSY)
- Mulch soil surface to retain moisture
- Consider drought-tolerant varieties

Contact PM Kisan Helpline: 155261 for emergency assistance."""

    return """**AI Krishi Assistant**

Thank you for your question. Here are general farming recommendations:

1. **Soil Health** – Test soil every 2-3 years at your nearest soil testing lab (free/subsidized)
2. **Integrated Pest Management** – Use biological controls before chemicals
3. **Water Management** – Drip/sprinkler irrigation saves 40-50% water
4. **Crop Rotation** – Rotate crops each season to maintain soil health

🔗 **Resources:**
- Kisan Call Centre: **1800-180-1551** (Free, 24/7)
- eNAM Market: www.enam.gov.in
- PM Kisan: www.pmkisan.gov.in

Please consult your nearest Krishi Vigyan Kendra for specific advice."""


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from farmers"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_message = data.get('message', '').strip()
    language = data.get('language', 'en')
    conversation_history = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    if len(user_message) > 2000:
        return jsonify({'error': 'Message too long. Please keep it under 2000 characters.'}), 400

    try:
        if GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Build conversation
            messages = [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\nUser query: " + user_message]}]
            
            # Add history (last 6 exchanges)
            for item in conversation_history[-12:]:
                role = "user" if item.get('role') == 'user' else "model"
                messages.append({"role": role, "parts": [item.get('content', '')]})

            chat_session = model.start_chat(history=messages[:-1])
            response = chat_session.send_message(user_message)
            ai_response = response.text
        else:
            ai_response = get_fallback_response(user_message)

        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'language': language
        })

    except Exception as e:
        logger.error(f"AI chat error: {e}")
        fallback = get_fallback_response(user_message)
        return jsonify({
            'response': fallback,
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'note': 'Using offline response – AI service temporarily unavailable'
        })


@ai_bp.route('/faq', methods=['GET'])
def get_faq():
    """Return frequently asked farming questions"""
    faqs = [
        {
            "id": 1,
            "question": "What are the signs of nitrogen deficiency in crops?",
            "question_hi": "फसलों में नाइट्रोजन की कमी के लक्षण क्या हैं?",
            "question_ta": "பயிர்களில் நைட்ரஜன் குறைபாட்டின் அறிகுறிகள் என்ன?",
            "answer": "Yellowing of older leaves starting from bottom, stunted growth, pale green color overall. Apply urea @ 10-15 kg/bigha.",
            "category": "fertilizer"
        },
        {
            "id": 2,
            "question": "How often should I irrigate my wheat crop?",
            "question_hi": "मुझे अपनी गेहूं की फसल में कितनी बार सिंचाई करनी चाहिए?",
            "question_ta": "என் கோதுமை பயிருக்கு எத்தனை முறை நீர்ப்பாசனம் செய்ய வேண்டும்?",
            "answer": "Wheat needs 4-6 irrigations: at crown root initiation (21 days), tillering (45 days), jointing (65 days), flowering (85 days), dough stage (100 days).",
            "category": "irrigation"
        },
        {
            "id": 3,
            "question": "How do I control pests in my rice crop organically?",
            "question_hi": "मैं अपनी धान की फसल में कीटों को जैविक तरीके से कैसे नियंत्रित करूं?",
            "question_ta": "என் நெல் பயிரில் பூச்சிகளை இயற்கையாக எப்படி கட்டுப்படுத்துவது?",
            "answer": "Use neem-based pesticides (Neem oil 5ml/litre), install light traps, encourage natural predators, use Trichoderma for soil treatment.",
            "category": "pest"
        },
        {
            "id": 4,
            "question": "What government schemes are available for small farmers?",
            "question_hi": "छोटे किसानों के लिए कौन सी सरकारी योजनाएं उपलब्ध हैं?",
            "question_ta": "சிறு விவசாயிகளுக்கு என்ன அரசு திட்டங்கள் உள்ளன?",
            "answer": "PM-KISAN (₹6000/year), PMFBY (Crop Insurance), KCC (Kisan Credit Card), PMKSY (Irrigation), Soil Health Card scheme.",
            "category": "schemes"
        },
        {
            "id": 5,
            "question": "How do I test my soil health?",
            "question_hi": "मैं अपनी मिट्टी का स्वास्थ्य कैसे जांचूं?",
            "question_ta": "என் மண்ணின் ஆரோக்கியத்தை எப்படி சோதிப்பது?",
            "answer": "Collect soil sample from 15cm depth from multiple spots. Send to nearest Soil Testing Laboratory (free under Soil Health Card scheme). Results in 15-20 days.",
            "category": "soil"
        }
    ]
    return jsonify({'faqs': faqs})
