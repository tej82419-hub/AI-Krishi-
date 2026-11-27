"""
AI Krishi – Smart Farming Assistant
Main Flask Application
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
from routes.ai_assistant import ai_bp
from routes.weather import weather_bp
from routes.market import market_bp
from routes.disease import disease_bp
from routes.auth import auth_bp
from routes.schemes import schemes_bp

app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(market_bp, url_prefix='/api/market')
app.register_blueprint(disease_bp, url_prefix='/api/disease')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(schemes_bp, url_prefix='/api/schemes')

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'AI Krishi Backend'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
