"""
Weather Route – fetches real weather data using OpenWeatherMap API
"""

from flask import Blueprint, request, jsonify
import os
import requests
from datetime import datetime

weather_bp = Blueprint('weather', __name__)

OWM_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
OWM_BASE = 'https://api.openweathermap.org/data/2.5'


def get_farming_alerts(weather_data):
    """Generate farming-specific alerts based on weather"""
    alerts = []
    temp = weather_data.get('main', {}).get('temp', 25)
    humidity = weather_data.get('main', {}).get('humidity', 60)
    wind_speed = weather_data.get('wind', {}).get('speed', 0)
    weather_main = weather_data.get('weather', [{}])[0].get('main', '').lower()
    rain = weather_data.get('rain', {}).get('1h', 0)

    if temp > 40:
        alerts.append({
            'type': 'danger',
            'icon': '🌡️',
            'title': 'Extreme Heat Warning',
            'message': 'Temperature above 40°C. Irrigate crops in early morning or evening. Avoid applying fertilizers.'
        })
    elif temp < 10:
        alerts.append({
            'type': 'warning',
            'icon': '❄️',
            'title': 'Cold Wave Alert',
            'message': 'Low temperature may damage sensitive crops. Cover seedlings and young plants.'
        })

    if humidity > 85:
        alerts.append({
            'type': 'warning',
            'icon': '💧',
            'title': 'High Humidity Alert',
            'message': 'High humidity increases risk of fungal diseases (blight, rust). Apply preventive fungicide spray.'
        })

    if wind_speed > 10:
        alerts.append({
            'type': 'warning',
            'icon': '💨',
            'title': 'Strong Wind Warning',
            'message': 'High winds may lodge tall crops. Avoid spraying pesticides today.'
        })

    if 'rain' in weather_main or 'thunderstorm' in weather_main:
        alerts.append({
            'type': 'info',
            'icon': '🌧️',
            'title': 'Rain Alert',
            'message': 'Rain expected. Delay irrigation and fertilizer application. Ensure field drainage is clear.'
        })

    if not alerts:
        alerts.append({
            'type': 'success',
            'icon': '✅',
            'title': 'Good Farming Conditions',
            'message': 'Weather conditions are suitable for field activities today.'
        })

    return alerts


@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """Get current weather for a location"""
    location = request.args.get('location', '').strip()
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not location and not (lat and lon):
        return jsonify({'error': 'Location or coordinates required'}), 400

    if not OWM_API_KEY:
        # Return demo data with clear disclaimer
        demo_data = {
            'location': location or 'Demo Location',
            'temperature': 28,
            'feels_like': 30,
            'humidity': 65,
            'description': 'Partly Cloudy',
            'wind_speed': 4.5,
            'visibility': 10,
            'rain_1h': 0,
            'icon': '02d',
            'sunrise': '06:15',
            'sunset': '18:30',
            'alerts': [
                {
                    'type': 'info',
                    'icon': '⚠️',
                    'title': 'Demo Mode',
                    'message': 'Add OPENWEATHER_API_KEY to .env for real weather data.'
                }
            ],
            'is_demo': True,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(demo_data)

    try:
        if lat and lon:
            url = f"{OWM_BASE}/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
        else:
            url = f"{OWM_BASE}/weather?q={location},IN&appid={OWM_API_KEY}&units=metric"

        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            return jsonify({'error': 'Location not found. Please try a nearby city name.'}), 404
        resp.raise_for_status()
        data = resp.json()

        from datetime import datetime as dt
        sunrise = dt.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = dt.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')

        result = {
            'location': f"{data['name']}, {data['sys']['country']}",
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'].title(),
            'wind_speed': data['wind']['speed'],
            'visibility': data.get('visibility', 0) // 1000,
            'rain_1h': data.get('rain', {}).get('1h', 0),
            'icon': data['weather'][0]['icon'],
            'sunrise': sunrise,
            'sunset': sunset,
            'alerts': get_farming_alerts(data),
            'is_demo': False,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(result)

    except requests.RequestException as e:
        return jsonify({'error': f'Weather service error: {str(e)}'}), 503


@weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """Get 5-day weather forecast"""
    location = request.args.get('location', '').strip()

    if not OWM_API_KEY:
        return jsonify({
            'forecast': [],
            'is_demo': True,
            'message': 'Add OPENWEATHER_API_KEY for real forecast data'
        })

    try:
        url = f"{OWM_BASE}/forecast?q={location},IN&appid={OWM_API_KEY}&units=metric&cnt=40"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Group by day
        days = {}
        for item in data['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in days:
                days[date] = {
                    'date': date,
                    'temps': [],
                    'humidity': [],
                    'descriptions': [],
                    'rain': 0
                }
            days[date]['temps'].append(item['main']['temp'])
            days[date]['humidity'].append(item['main']['humidity'])
            days[date]['descriptions'].append(item['weather'][0]['description'])
            days[date]['rain'] += item.get('rain', {}).get('3h', 0)

        forecast = []
        for date, d in list(days.items())[:5]:
            forecast.append({
                'date': date,
                'max_temp': round(max(d['temps'])),
                'min_temp': round(min(d['temps'])),
                'humidity': round(sum(d['humidity']) / len(d['humidity'])),
                'description': max(set(d['descriptions']), key=d['descriptions'].count).title(),
                'rain': round(d['rain'], 1)
            })

        return jsonify({'forecast': forecast, 'is_demo': False})

    except Exception as e:
        return jsonify({'error': str(e)}), 503
