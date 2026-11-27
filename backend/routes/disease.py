"""
Crop Disease Detection Route
Uses Google Gemini Vision API for image analysis
"""

from flask import Blueprint, request, jsonify
import os
import base64
import google.generativeai as genai
from datetime import datetime
import json

disease_bp = Blueprint('disease', __name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DISEASE_ANALYSIS_PROMPT = """You are an expert plant pathologist and agricultural advisor specializing in Indian crops.

Analyze this crop/plant image and provide:

1. **Plant Identification**: What crop/plant is visible?
2. **Health Status**: Is the plant healthy or showing signs of disease/stress?
3. **Possible Issues** (if any): List possible diseases, deficiencies, or pest damage with confidence level (High/Medium/Low)
4. **Symptoms Observed**: What specific symptoms are visible in the image?
5. **Likely Causes**: What could have caused this condition?
6. **Recommended Actions**: 
   - Immediate steps to take
   - Safe, government-approved treatments
   - Preventive measures
7. **When to Seek Expert Help**: Under what conditions should they contact KVK or agricultural officer?

Important guidelines:
- Never claim 100% certainty – always mention this is a preliminary assessment
- Use simple language understandable to farmers
- Recommend only safe, commonly available treatments
- If image quality is poor or plant is not clearly visible, say so
- If the image doesn't show a plant/crop, politely mention that

Format your response with clear sections and bullet points."""


FALLBACK_DISEASES = {
    "general": {
        "name": "Plant Health Assessment",
        "confidence": "medium",
        "symptoms": ["Discoloration", "Spots", "Wilting"],
        "causes": ["Fungal infection", "Bacterial infection", "Nutrient deficiency", "Pest damage"],
        "treatment": [
            "Remove and destroy severely affected plant parts",
            "Avoid overhead irrigation",
            "Apply Mancozeb (2g/litre) as preventive spray",
            "Ensure proper plant spacing for air circulation"
        ],
        "prevention": [
            "Use disease-resistant varieties",
            "Practice crop rotation",
            "Maintain field hygiene",
            "Regular scouting every 7-10 days"
        ]
    }
}


@disease_bp.route('/analyze', methods=['POST'])
def analyze_disease():
    """Analyze crop image for diseases"""
    if 'image' not in request.files and 'image_data' not in request.json if request.is_json else True:
        # Check for base64 image in JSON
        pass

    image_data = None
    image_mime = 'image/jpeg'

    if request.is_json:
        data = request.get_json()
        image_b64 = data.get('image_data', '')
        if image_b64:
            if ',' in image_b64:
                header, image_b64 = image_b64.split(',', 1)
                if 'png' in header:
                    image_mime = 'image/png'
                elif 'webp' in header:
                    image_mime = 'image/webp'
            image_data = base64.b64decode(image_b64)
    elif 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        image_data = file.read()
        image_mime = file.content_type or 'image/jpeg'

    if not image_data:
        return jsonify({'error': 'Image data is required'}), 400

    if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
        return jsonify({'error': 'Image too large. Please use an image under 10MB.'}), 400

    try:
        if GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-1.5-flash')
            image_part = {
                "mime_type": image_mime,
                "data": base64.b64encode(image_data).decode()
            }
            response = model.generate_content([DISEASE_ANALYSIS_PROMPT, image_part])
            analysis_text = response.text

            result = {
                'analysis': analysis_text,
                'is_ai_powered': True,
                'disclaimer': 'This is a preliminary AI assessment only. Please consult a qualified agricultural expert or Krishi Vigyan Kendra for confirmation.',
                'emergency_contact': 'Kisan Call Centre: 1800-180-1551 (Free, 24/7)',
                'timestamp': datetime.now().isoformat()
            }
        else:
            result = {
                'analysis': """**Plant Health Assessment (Demo Mode)**

ℹ️ **API Key Required**: To use real AI image analysis, please add your GEMINI_API_KEY to the .env file.

**General Disease Detection Guide:**

🔍 **Common Signs to Look For:**
- **Yellow/Brown Spots**: May indicate fungal diseases (blight, rust) or nutrient deficiency
- **Wilting**: Check for root rot, water stress, or bacterial wilt
- **White Powdery Coating**: Likely Powdery Mildew – treat with sulfur-based fungicide
- **Holes in Leaves**: Pest damage – check for caterpillars, beetles

🌿 **Recommended First Steps:**
1. Remove severely affected plant parts
2. Avoid wetting foliage during irrigation  
3. Apply Neem oil spray (5ml/litre water) as safe first treatment
4. Consult KVK if symptoms worsen

📞 **Expert Help**: Kisan Call Centre: **1800-180-1551** (Free, 24/7)""",
                'is_ai_powered': False,
                'is_demo': True,
                'disclaimer': 'Demo mode. Add GEMINI_API_KEY for real AI image analysis.',
                'timestamp': datetime.now().isoformat()
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'suggestion': 'Please try with a clearer image or describe the symptoms to the AI chat assistant.'
        }), 500
