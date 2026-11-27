/**
 * AI Krishi – Weather Module
 */

const WEATHER_ICONS = {
    '01d': '☀️', '01n': '🌙',
    '02d': '⛅', '02n': '⛅',
    '03d': '☁️', '03n': '☁️',
    '04d': '☁️', '04n': '☁️',
    '09d': '🌧️', '09n': '🌧️',
    '10d': '🌦️', '10n': '🌦️',
    '11d': '⛈️', '11n': '⛈️',
    '13d': '❄️', '13n': '❄️',
    '50d': '🌫️', '50n': '🌫️'
};

async function fetchWeather() {
    const location = document.getElementById('weatherLocation').value.trim();
    if (!location) {
        showToast('Please enter a location', 'warning');
        return;
    }
    await loadWeather({ location });
}

async function getLocationWeather() {
    if (!navigator.geolocation) {
        showToast('Geolocation not supported by this browser', 'error');
        return;
    }

    showToast('Getting your location...', 'success');
    navigator.geolocation.getCurrentPosition(
        async (pos) => {
            await loadWeather({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        },
        (err) => {
            showToast('Could not get location. Please enter manually.', 'error');
        }
    );
}

async function loadWeather(params) {
    document.getElementById('weatherPlaceholder').style.display = 'none';
    document.getElementById('weatherDisplay').style.display = 'none';

    // Show loading
    document.getElementById('weatherPlaceholder').innerHTML = `
        <div class="loading-spinner"><i class="fas fa-spinner fa-spin fa-2x"></i><br>Getting weather data...</div>`;
    document.getElementById('weatherPlaceholder').style.display = 'block';

    try {
        let url = `${API_BASE}/weather/current?`;
        if (params.lat) {
            url += `lat=${params.lat}&lon=${params.lon}`;
        } else {
            url += `location=${encodeURIComponent(params.location)}`;
        }

        const resp = await fetch(url);
        const data = await resp.json();

        if (!resp.ok) {
            showToast(data.error || 'Location not found. Try a city name.', 'error');
            document.getElementById('weatherPlaceholder').innerHTML = `
                <span>❌</span><p>${data.error || 'Location not found'}</p>`;
            return;
        }

        document.getElementById('weatherPlaceholder').style.display = 'none';
        renderWeather(data);
        document.getElementById('weatherDisplay').style.display = 'flex';

        // Load forecast
        if (!data.is_demo && params.location) {
            loadForecast(params.location);
        }

    } catch (e) {
        document.getElementById('weatherPlaceholder').innerHTML = `
            <span>⚠️</span><p>Failed to load weather. Please check your connection.</p>`;
        console.error('Weather error:', e);
    }
}

function renderWeather(data) {
    document.getElementById('wLocation').textContent = data.location;
    document.getElementById('wTimestamp').textContent = `Updated: ${new Date(data.timestamp).toLocaleTimeString('en-IN')}`;
    document.getElementById('wTemp').textContent = `${data.temperature}°C`;
    document.getElementById('wFeels').textContent = `Feels like ${data.feels_like}°C`;
    document.getElementById('wDesc').textContent = data.description;
    document.getElementById('wIcon').textContent = WEATHER_ICONS[data.icon] || '🌤️';
    document.getElementById('wHumidity').textContent = `${data.humidity}%`;
    document.getElementById('wWind').textContent = `${(data.wind_speed * 3.6).toFixed(1)} km/h`;
    document.getElementById('wRain').textContent = `${data.rain_1h} mm`;
    document.getElementById('wVis').textContent = `${data.visibility} km`;
    document.getElementById('wSunrise').textContent = data.sunrise;
    document.getElementById('wSunset').textContent = data.sunset;

    // Render alerts
    const alertsContainer = document.getElementById('alertsContainer');
    alertsContainer.innerHTML = (data.alerts || []).map(alert => `
        <div class="alert-card ${alert.type}">
            <span class="alert-icon">${alert.icon}</span>
            <div>
                <div class="alert-title">${alert.title}</div>
                <div class="alert-message">${alert.message}</div>
            </div>
        </div>
    `).join('');

    // Show demo notice if applicable
    if (data.is_demo) {
        alertsContainer.insertAdjacentHTML('afterbegin', `
            <div class="alert-card info">
                <span class="alert-icon">ℹ️</span>
                <div>
                    <div class="alert-title">Demo Mode</div>
                    <div class="alert-message">Sample weather data shown. Add OPENWEATHER_API_KEY to .env for real data.</div>
                </div>
            </div>`);
    }
}

async function loadForecast(location) {
    try {
        const resp = await fetch(`${API_BASE}/weather/forecast?location=${encodeURIComponent(location)}`);
        const data = await resp.json();

        if (data.forecast && data.forecast.length > 0) {
            const grid = document.getElementById('forecastGrid');
            const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
            grid.innerHTML = data.forecast.map(day => {
                const date = new Date(day.date);
                return `
                    <div class="forecast-card">
                        <div class="fc-date">${days[date.getDay()]}, ${date.getDate()}/${date.getMonth()+1}</div>
                        <div style="font-size:1.5rem;margin:6px 0;">🌤️</div>
                        <div class="fc-temp">${day.max_temp}° / ${day.min_temp}°</div>
                        <div class="fc-desc">${day.description}</div>
                        ${day.rain > 0 ? `<div style="color:var(--blue);font-size:0.75rem;">💧 ${day.rain}mm</div>` : ''}
                    </div>`;
            }).join('');
            document.getElementById('forecastSection').style.display = 'block';
        }
    } catch (e) {
        console.warn('Forecast not available');
    }
}
