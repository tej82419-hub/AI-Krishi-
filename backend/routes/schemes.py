"""
Government Schemes Route
"""

from flask import Blueprint, request, jsonify

schemes_bp = Blueprint('schemes', __name__)

SCHEMES = [
    {
        "id": 1,
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
        "name_ta": "பிரதமர் கிசான் சம்மான் நிதி",
        "benefit": "₹6,000 per year (3 installments of ₹2,000)",
        "eligibility": "Small and marginal farmers with landholding up to 2 hectares",
        "documents": ["Aadhaar Card", "Bank Account", "Land Records"],
        "how_to_apply": "Apply at Common Service Centre (CSC) or pmkisan.gov.in",
        "link": "https://pmkisan.gov.in",
        "category": "financial",
        "icon": "💰"
    },
    {
        "id": 2,
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "benefit": "Crop insurance at low premium (2% for Kharif, 1.5% for Rabi)",
        "eligibility": "All farmers growing notified crops",
        "documents": ["Aadhaar Card", "Bank Account", "Land Records", "Sowing Certificate"],
        "how_to_apply": "Contact nearest bank or insurance company before sowing",
        "link": "https://pmfby.gov.in",
        "category": "insurance",
        "icon": "🛡️"
    },
    {
        "id": 3,
        "name": "KCC (Kisan Credit Card)",
        "benefit": "Short-term credit at 7% interest (4% with timely repayment)",
        "eligibility": "All farmers, sharecroppers, and tenant farmers",
        "documents": ["Aadhaar Card", "Land Records", "Passport Photo"],
        "how_to_apply": "Apply at nearest bank branch",
        "link": "https://www.nabard.org/content.aspx?id=591",
        "category": "credit",
        "icon": "💳"
    },
    {
        "id": 4,
        "name": "PMKSY (Pradhan Mantri Krishi Sinchayee Yojana)",
        "benefit": "Subsidy on drip/sprinkler irrigation equipment (50-90%)",
        "eligibility": "All farmers",
        "documents": ["Aadhaar Card", "Land Records", "Bank Account"],
        "how_to_apply": "Apply at district agriculture office or state agriculture portal",
        "link": "https://pmksy.gov.in",
        "category": "irrigation",
        "icon": "💧"
    },
    {
        "id": 5,
        "name": "Soil Health Card Scheme",
        "benefit": "Free soil testing and crop-specific nutrient recommendations",
        "eligibility": "All farmers",
        "documents": ["Aadhaar Card"],
        "how_to_apply": "Contact nearest Krishi Vigyan Kendra or agriculture office",
        "link": "https://soilhealth.dac.gov.in",
        "category": "soil",
        "icon": "🌱"
    },
    {
        "id": 6,
        "name": "eNAM (National Agriculture Market)",
        "benefit": "Online trading platform for better price discovery",
        "eligibility": "All farmers registered with local APMC",
        "documents": ["Aadhaar Card", "Bank Account", "APMC Registration"],
        "how_to_apply": "Register at enam.gov.in or contact local APMC",
        "link": "https://www.enam.gov.in",
        "category": "market",
        "icon": "🏪"
    },
    {
        "id": 7,
        "name": "RKVY (Rashtriya Krishi Vikas Yojana)",
        "benefit": "Infrastructure development, training and equipment support",
        "eligibility": "Farmer groups, FPOs, and individual farmers",
        "documents": ["Aadhaar Card", "Land Records", "Project Proposal"],
        "how_to_apply": "Contact district agriculture office",
        "link": "https://rkvy.nic.in",
        "category": "infrastructure",
        "icon": "🏗️"
    },
    {
        "id": 8,
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "benefit": "₹50,000/ha over 3 years for organic farming",
        "eligibility": "Farmers forming groups of minimum 50 members",
        "documents": ["Aadhaar Card", "Land Records", "Group Formation Certificate"],
        "how_to_apply": "Contact district agriculture officer",
        "link": "https://pgsindia-ncof.gov.in",
        "category": "organic",
        "icon": "🌿"
    }
]

HELPLINES = [
    {"name": "Kisan Call Centre", "number": "1800-180-1551", "available": "24/7, Free"},
    {"name": "PM Kisan Helpline", "number": "155261", "available": "Working Hours"},
    {"name": "PMFBY Helpline", "number": "1800-200-7710", "available": "Working Hours"},
    {"name": "Weather SMS Alert", "number": "SMS 'MAUSAM' to 7738299899", "available": "Free"},
]


@schemes_bp.route('/', methods=['GET'])
def get_schemes():
    category = request.args.get('category', '')
    if category:
        filtered = [s for s in SCHEMES if s['category'] == category]
    else:
        filtered = SCHEMES
    return jsonify({'schemes': filtered, 'helplines': HELPLINES})


@schemes_bp.route('/helplines', methods=['GET'])
def get_helplines():
    return jsonify({'helplines': HELPLINES})
