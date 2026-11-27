"""
Auth Route – Farmer registration, login and profile
Uses SQLite for local storage
"""

from flask import Blueprint, request, jsonify, session
import sqlite3
import hashlib
import os
import json
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/krishi.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            village TEXT,
            district TEXT,
            state TEXT,
            land_acres REAL,
            primary_crop TEXT,
            password_hash TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        );

        CREATE TABLE IF NOT EXISTS disease_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            crop_name TEXT,
            analysis TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        );
    ''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Initialize DB on import
try:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
except Exception as e:
    print(f"DB init warning: {e}")


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['name', 'phone', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    phone = data['phone'].strip()
    if len(phone) < 10:
        return jsonify({'error': 'Please enter a valid mobile number'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO farmers (name, phone, village, district, state, land_acres, primary_crop, password_hash, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'].strip(),
            phone,
            data.get('village', ''),
            data.get('district', ''),
            data.get('state', ''),
            data.get('land_acres', 0),
            data.get('primary_crop', ''),
            hash_password(data['password']),
            data.get('language', 'en')
        ))
        farmer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'farmer_id': farmer_id,
            'message': f"Welcome to AI Krishi, {data['name']}! Your account has been created."
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'This phone number is already registered. Please login.'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not phone or not password:
        return jsonify({'error': 'Phone and password are required'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM farmers WHERE phone = ? AND password_hash = ?',
                       (phone, hash_password(password)))
        farmer = cursor.fetchone()
        conn.close()

        if not farmer:
            return jsonify({'error': 'Invalid phone number or password'}), 401

        farmer_dict = dict(farmer)
        farmer_dict.pop('password_hash', None)

        return jsonify({
            'success': True,
            'farmer': farmer_dict,
            'message': f"Welcome back, {farmer_dict['name']}!"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/save-chat', methods=['POST'])
def save_chat():
    data = request.get_json()
    farmer_id = data.get('farmer_id')
    user_message = data.get('user_message', '')
    ai_response = data.get('ai_response', '')
    language = data.get('language', 'en')

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (farmer_id, user_message, ai_response, language)
            VALUES (?, ?, ?, ?)
        ''', (farmer_id, user_message, ai_response, language))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/history/<int:farmer_id>', methods=['GET'])
def get_history(farmer_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, ai_response, language, created_at
            FROM chat_history
            WHERE farmer_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (farmer_id,))
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
