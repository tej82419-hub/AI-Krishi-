"""
Fertilizer and Irrigation Guidance Route
"""

from flask import Blueprint, request, jsonify

fertilizer_bp = Blueprint('fertilizer', __name__)

CROP_DATA = {
    "Rice": {
        "fertilizer": {
            "npk": "120:60:60 kg/ha",
            "schedule": [
                {"stage": "Basal (before transplanting)", "fertilizer": "DAP 150 kg/ha + MOP 60 kg/ha"},
                {"stage": "Tillering (21-25 days)", "fertilizer": "Urea 65 kg/ha"},
                {"stage": "Panicle Initiation (45-50 days)", "fertilizer": "Urea 65 kg/ha"}
            ],
            "micronutrients": "Zinc Sulphate 25 kg/ha if zinc deficiency symptoms appear"
        },
        "irrigation": {
            "water_requirement": "1200-1400 mm per season",
            "schedule": [
                "Maintain 5-7 cm standing water during tillering",
                "Drain field at tillering stage for 7-10 days",
                "Keep field moist (not flooded) during grain filling",
                "Stop irrigation 10 days before harvest"
            ],
            "critical_stages": ["Transplanting", "Tillering", "Panicle Initiation", "Flowering"]
        }
    },
    "Wheat": {
        "fertilizer": {
            "npk": "120:60:40 kg/ha",
            "schedule": [
                {"stage": "Basal (at sowing)", "fertilizer": "DAP 130 kg/ha + MOP 67 kg/ha"},
                {"stage": "Crown Root Initiation (21 days)", "fertilizer": "Urea 87 kg/ha"},
                {"stage": "Tillering (45 days)", "fertilizer": "Urea 87 kg/ha (if needed)"}
            ],
            "micronutrients": "Ferrous Sulphate 25 kg/ha for iron deficiency areas"
        },
        "irrigation": {
            "water_requirement": "400-500 mm per season",
            "schedule": [
                "1st irrigation at Crown Root Initiation (21 DAS)",
                "2nd at Tillering stage (45 DAS)",
                "3rd at Jointing stage (65 DAS)",
                "4th at Flowering (85 DAS)",
                "5th at Dough stage (100 DAS)"
            ],
            "critical_stages": ["Crown Root Initiation", "Tillering", "Flowering", "Grain Filling"]
        }
    },
    "Tomato": {
        "fertilizer": {
            "npk": "150:75:75 kg/ha",
            "schedule": [
                {"stage": "Basal (at planting)", "fertilizer": "FYM 25 tonnes/ha + DAP 163 kg/ha + MOP 125 kg/ha"},
                {"stage": "30 days after planting", "fertilizer": "Urea 109 kg/ha"},
                {"stage": "60 days (fruiting stage)", "fertilizer": "Urea 109 kg/ha + Potash 62 kg/ha"}
            ],
            "micronutrients": "Boron 1 kg/ha, Calcium spray at fruit setting"
        },
        "irrigation": {
            "water_requirement": "700-900 mm per season",
            "schedule": [
                "Irrigate immediately after transplanting",
                "Every 5-7 days during establishment",
                "Every 7-10 days during fruiting",
                "Avoid water stress at flowering and fruit setting"
            ],
            "critical_stages": ["Transplanting", "Flowering", "Fruit Setting", "Fruit Development"]
        }
    },
    "Cotton": {
        "fertilizer": {
            "npk": "150:60:60 kg/ha",
            "schedule": [
                {"stage": "Basal (at sowing)", "fertilizer": "FYM 10 tonnes/ha + DAP 130 kg + MOP 100 kg"},
                {"stage": "40-45 days (squaring)", "fertilizer": "Urea 109 kg/ha"},
                {"stage": "75-80 days (boll development)", "fertilizer": "Urea 109 kg/ha + Potash 50 kg"}
            ],
            "micronutrients": "Zinc Sulphate 25 kg/ha at sowing"
        },
        "irrigation": {
            "water_requirement": "600-800 mm per season",
            "schedule": [
                "Light irrigation at sowing if needed",
                "Critical irrigation at squaring (40-45 days)",
                "At boll development (70-75 days)",
                "Avoid irrigation when picking"
            ],
            "critical_stages": ["Germination", "Squaring", "Flowering", "Boll Development"]
        }
    },
    "Maize": {
        "fertilizer": {
            "npk": "120:60:40 kg/ha",
            "schedule": [
                {"stage": "Basal (at sowing)", "fertilizer": "DAP 130 kg/ha + MOP 67 kg/ha"},
                {"stage": "Knee-high stage (25-30 days)", "fertilizer": "Urea 87 kg/ha"},
                {"stage": "Tasseling (55-60 days)", "fertilizer": "Urea 87 kg/ha"}
            ],
            "micronutrients": "Zinc Sulphate 25 kg/ha"
        },
        "irrigation": {
            "water_requirement": "500-600 mm per season",
            "schedule": [
                "Pre-sowing irrigation",
                "At germination (7-10 days)",
                "At knee-high (25-30 days)",
                "At tasseling and silking (55-65 days)",
                "At grain filling (80-85 days)"
            ],
            "critical_stages": ["Germination", "Knee-high", "Tasseling", "Silking", "Grain Filling"]
        }
    }
}


def get_fertilizer_route():
    from flask import Blueprint
    bp = Blueprint('fertilizer_guidance', __name__)

    @bp.route('/guidance', methods=['POST'])
    def get_guidance():
        data = request.get_json()
        crop = data.get('crop', '').strip().title()
        soil_type = data.get('soil_type', 'Medium')
        area = float(data.get('area', 1.0))

        if crop not in CROP_DATA:
            return jsonify({
                'error': f'Guidance for {crop} not available yet.',
                'available_crops': list(CROP_DATA.keys())
            }), 404

        crop_info = CROP_DATA[crop]
        result = {
            'crop': crop,
            'area': area,
            'soil_type': soil_type,
            'fertilizer': crop_info['fertilizer'],
            'irrigation': crop_info['irrigation'],
            'notes': [
                f"All quantities are for 1 hectare. Multiply by {area} for your {area} ha field.",
                "FYM = Farm Yard Manure, DAP = Di-Ammonium Phosphate, MOP = Muriate of Potash",
                "Get a Soil Health Card for personalized recommendations",
                "Consult your local agricultural officer for variety-specific advice"
            ]
        }
        return jsonify(result)

    @bp.route('/crops', methods=['GET'])
    def get_crops():
        return jsonify({'crops': list(CROP_DATA.keys())})

    return bp
