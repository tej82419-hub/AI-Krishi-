"""
Market Prices Route – agricultural commodity prices
Uses data-driven approach with eNAM/Agmarknet structure
"""

from flask import Blueprint, request, jsonify
import os
import requests
from datetime import datetime, date
import json

market_bp = Blueprint('market', __name__)

# Agmarknet API (Government of India) - free access
AGMARKNET_BASE = 'https://agmarknet.gov.in/SearchCmmMkt.aspx'

# Fallback sample data (clearly marked as sample/demo)
SAMPLE_PRICES = {
    "Tomato": [
        {"market": "Azadpur Mandi, Delhi", "state": "Delhi", "min_price": 1200, "max_price": 2200, "modal_price": 1800},
        {"market": "Vashi APMC, Mumbai", "state": "Maharashtra", "min_price": 1500, "max_price": 2500, "modal_price": 2000},
        {"market": "KR Market, Bengaluru", "state": "Karnataka", "min_price": 1000, "max_price": 1800, "modal_price": 1400},
        {"market": "Koyambedu, Chennai", "state": "Tamil Nadu", "min_price": 1100, "max_price": 2000, "modal_price": 1600},
    ],
    "Potato": [
        {"market": "Azadpur Mandi, Delhi", "state": "Delhi", "min_price": 800, "max_price": 1400, "modal_price": 1100},
        {"market": "Vashi APMC, Mumbai", "state": "Maharashtra", "min_price": 900, "max_price": 1600, "modal_price": 1200},
        {"market": "KR Market, Bengaluru", "state": "Karnataka", "min_price": 700, "max_price": 1200, "modal_price": 950},
    ],
    "Onion": [
        {"market": "Lasalgaon APMC, Nashik", "state": "Maharashtra", "min_price": 1500, "max_price": 3000, "modal_price": 2200},
        {"market": "Azadpur Mandi, Delhi", "state": "Delhi", "min_price": 1800, "max_price": 3500, "modal_price": 2800},
        {"market": "Bangalore APMC", "state": "Karnataka", "min_price": 1600, "max_price": 2800, "modal_price": 2200},
    ],
    "Rice": [
        {"market": "Nizamabad APMC", "state": "Telangana", "min_price": 2000, "max_price": 2500, "modal_price": 2200},
        {"market": "Warangal APMC", "state": "Telangana", "min_price": 1900, "max_price": 2400, "modal_price": 2100},
        {"market": "Nellore APMC", "state": "Andhra Pradesh", "min_price": 2100, "max_price": 2600, "modal_price": 2300},
    ],
    "Wheat": [
        {"market": "Khanna Grain Market", "state": "Punjab", "min_price": 2050, "max_price": 2200, "modal_price": 2125},
        {"market": "Karnal Grain Market", "state": "Haryana", "min_price": 2050, "max_price": 2150, "modal_price": 2100},
        {"market": "Vidisha APMC", "state": "Madhya Pradesh", "min_price": 2050, "max_price": 2180, "modal_price": 2110},
    ],
    "Cotton": [
        {"market": "Akola APMC", "state": "Maharashtra", "min_price": 6500, "max_price": 7200, "modal_price": 6800},
        {"market": "Guntur APMC", "state": "Andhra Pradesh", "min_price": 6400, "max_price": 7100, "modal_price": 6750},
        {"market": "Rajkot APMC", "state": "Gujarat", "min_price": 6600, "max_price": 7300, "modal_price": 6950},
    ],
    "Maize": [
        {"market": "Davangere APMC", "state": "Karnataka", "min_price": 1800, "max_price": 2200, "modal_price": 2000},
        {"market": "Gulbarga APMC", "state": "Karnataka", "min_price": 1750, "max_price": 2100, "modal_price": 1950},
    ],
    "Soybean": [
        {"market": "Indore APMC", "state": "Madhya Pradesh", "min_price": 4000, "max_price": 4800, "modal_price": 4400},
        {"market": "Nagpur APMC", "state": "Maharashtra", "min_price": 4100, "max_price": 4900, "modal_price": 4500},
    ],
}

AVAILABLE_CROPS = sorted(SAMPLE_PRICES.keys())


@market_bp.route('/crops', methods=['GET'])
def get_crops():
    """Get list of available crops"""
    return jsonify({'crops': AVAILABLE_CROPS})


@market_bp.route('/prices', methods=['GET'])
def get_prices():
    """Get market prices for a commodity"""
    crop = request.args.get('crop', '').strip()
    state = request.args.get('state', '').strip()

    if not crop:
        return jsonify({'error': 'Crop name is required'}), 400

    # Try to match crop name case-insensitively
    matched_crop = None
    for c in AVAILABLE_CROPS:
        if c.lower() == crop.lower():
            matched_crop = c
            break

    if not matched_crop:
        return jsonify({
            'error': f'Price data not available for {crop}.',
            'available_crops': AVAILABLE_CROPS
        }), 404

    prices = SAMPLE_PRICES[matched_crop]
    
    # Filter by state if provided
    if state:
        filtered = [p for p in prices if state.lower() in p['state'].lower()]
        if filtered:
            prices = filtered

    # Add MSP data
    msps = {
        "Rice": 2183, "Wheat": 2275, "Maize": 2090, "Cotton": 7020,
        "Soybean": 4600, "Onion": None, "Tomato": None, "Potato": None
    }

    result = {
        'crop': matched_crop,
        'prices': prices,
        'unit': 'INR per Quintal (100 kg)',
        'msp': msps.get(matched_crop),
        'last_updated': date.today().isoformat(),
        'is_demo': True,
        'disclaimer': 'Sample data shown for demonstration. For real-time prices, visit agmarknet.gov.in or enam.gov.in',
        'sources': {
            'agmarknet': 'https://agmarknet.gov.in',
            'enam': 'https://www.enam.gov.in'
        }
    }
    return jsonify(result)


@market_bp.route('/states', methods=['GET'])
def get_states():
    """Get list of Indian states"""
    states = [
        "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Odisha",
        "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh",
        "Uttarakhand", "West Bengal", "Delhi"
    ]
    return jsonify({'states': states})
