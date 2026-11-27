/**
 * AI Krishi – Market Prices Module
 */

async function fetchMarketPrices() {
    const crop = document.getElementById('marketCrop').value;
    const state = document.getElementById('marketState').value;

    if (!crop) {
        showToast('Please select a crop', 'warning');
        return;
    }

    document.getElementById('marketDisplay').style.display = 'none';
    document.getElementById('marketPlaceholder').innerHTML = `
        <div class="loading-spinner"><i class="fas fa-spinner fa-spin fa-2x"></i><br>Fetching market prices...</div>`;
    document.getElementById('marketPlaceholder').style.display = 'block';

    try {
        let url = `${API_BASE}/market/prices?crop=${encodeURIComponent(crop)}`;
        if (state) url += `&state=${encodeURIComponent(state)}`;

        const resp = await fetch(url);
        const data = await resp.json();

        if (!resp.ok) {
            showToast(data.error || 'Price data not available', 'error');
            document.getElementById('marketPlaceholder').innerHTML = `
                <span>❌</span><p>${data.error || 'No data available'}</p>`;
            return;
        }

        document.getElementById('marketPlaceholder').style.display = 'none';
        renderMarketPrices(data);
        document.getElementById('marketDisplay').style.display = 'block';

    } catch (e) {
        document.getElementById('marketPlaceholder').innerHTML = `
            <span>⚠️</span><p>Failed to load prices. Please check backend connection.</p>`;
    }
}

function renderMarketPrices(data) {
    const prices = data.prices || [];
    const msp = data.msp;

    // Summary
    const allModals = prices.map(p => p.modal_price);
    const avgPrice = allModals.length ? Math.round(allModals.reduce((a,b)=>a+b,0)/allModals.length) : 0;
    const maxPrice = allModals.length ? Math.max(...allModals) : 0;
    const minPrice = allModals.length ? Math.min(...allModals) : 0;

    document.getElementById('marketSummary').innerHTML = `
        <div class="summary-item">
            <div class="summary-val" style="color:var(--green-dark);">${data.crop}</div>
            <div class="summary-label">${data.unit}</div>
        </div>
        <div class="summary-item">
            <div class="summary-val">₹${avgPrice.toLocaleString('en-IN')}</div>
            <div class="summary-label">Avg Modal Price</div>
        </div>
        <div class="summary-item">
            <div class="summary-val" style="color:var(--green);">₹${maxPrice.toLocaleString('en-IN')}</div>
            <div class="summary-label">Highest Price</div>
        </div>
        <div class="summary-item">
            <div class="summary-val" style="color:var(--red);">₹${minPrice.toLocaleString('en-IN')}</div>
            <div class="summary-label">Lowest Price</div>
        </div>
        ${msp ? `<div class="summary-item">
            <div class="summary-val" style="color:var(--amber);">₹${msp.toLocaleString('en-IN')}</div>
            <div class="summary-label">MSP (Govt.)</div>
        </div>` : ''}
        <div class="summary-item">
            <div class="summary-val" style="font-size:0.9rem;color:var(--text-light);">${data.last_updated}</div>
            <div class="summary-label">Last Updated</div>
        </div>
    `;

    // Table
    document.getElementById('marketTableBody').innerHTML = prices.map(p => {
        let mspBadge = '';
        if (msp) {
            const diff = p.modal_price - msp;
            const pct = ((diff / msp) * 100).toFixed(1);
            mspBadge = diff >= 0
                ? `<span class="msp-badge msp-above">+${pct}% above MSP</span>`
                : `<span class="msp-badge msp-below">${pct}% below MSP</span>`;
        }
        return `
            <tr>
                <td><strong>${p.market}</strong></td>
                <td>${p.state}</td>
                <td class="price-low">₹${p.min_price.toLocaleString('en-IN')}</td>
                <td class="price-high">₹${p.max_price.toLocaleString('en-IN')}</td>
                <td class="price-modal">₹${p.modal_price.toLocaleString('en-IN')}</td>
                <td>${mspBadge || '-'}</td>
            </tr>`;
    }).join('');
}
