const API = window.KIFAYAT_API_URL || (window.location.port === '8000' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : '/api');
const $ = s => document.querySelector(s);
const fmt = n => new Intl.NumberFormat('en-PK', { maximumFractionDigits: 2 }).format(n);

function spark(history) {
    if (!history?.length) return '';
    const p = history.map(x => x.price);
    const min = Math.min(...p);
    const max = Math.max(...p);
    const range = max - min || 1;
    const pts = p.map((v, i) => `${i / (p.length - 1 || 1) * 100},${31 - (v - min) / range * 25}`).join(' ');
    const trend = p[p.length - 1] > p[0] ? 'upward' : p[p.length - 1] < p[0] ? 'downward' : 'flat';
    return `<svg viewBox="0 0 100 35" width="100" height="35" role="img" aria-label="Price trend: ${trend}, range Rs. ${fmt(min)} to Rs. ${fmt(max)}"><polyline fill="none" stroke="#34745b" stroke-width="2" points="${pts}"/></svg>`;
}

function renderCard(x) {
    try {
        let sign = x.pct_change_1w > 0 ? '▲' : x.pct_change_1w < 0 ? '▼' : '▬';
        let cls = x.pct_change_1w > 0 ? 'up' : x.pct_change_1w < 0 ? 'down' : 'flat';
        return `<article class="card"><h3>${x.item}</h3><div class="price">Rs. ${fmt(x.current_price)}</div><span class="change ${cls}">${sign} ${Math.abs(x.pct_change_1w).toFixed(2)}% this week</span><div>${spark(x.history)}</div></article>`;
    } catch (e) {
        return `<article class="card"><h3>${x.item || 'Unknown'}</h3><div class="price">Data unavailable</div></article>`;
    }
}

async function load() {
    try {
        const r = await fetch(`${API}/items`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        $('#itemsGrid').innerHTML = data.items.map(renderCard).join('');
        setMeta(data.meta);
    } catch (e) {
        $('#itemsGrid').innerHTML = '<p>Start the Kifayat AI backend to load current data.</p>';
    }
}

async function loadChips() {
    try {
        const r = await fetch(`${API}/suggested`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        const c = $('#chipContainer');
        c.innerHTML = '';
        data.chips.forEach(ch => {
            const b = document.createElement('button');
            b.textContent = `${ch.item.toLowerCase()} ka rate?`;
            b.onclick = () => ask(b.textContent);
            c.appendChild(b);
        });
    } catch (e) {
        const c = $('#chipContainer');
        c.innerHTML = '';
        ['onions', 'pulses mash', 'sugar'].forEach(item => {
            const b = document.createElement('button');
            b.textContent = `${item} ka rate?`;
            b.onclick = () => ask(b.textContent);
            c.appendChild(b);
        });
    }
}

function setMeta(m) {
    const live = m.source === 'live';
    const label = live ? 'Live PBS data' : `Cached data${m.week_ending ? ' · ' + m.week_ending : ''}`;
    $('#sourceBadge').textContent = label;
    $('#footerSource').textContent = `— ${label}`;
    $('#updated').textContent = m.week_ending ? `Week ended ${m.week_ending}` : '';
}

function add(html, kind = 'assistant') {
    const e = document.createElement('div');
    e.className = `bubble ${kind}`;
    e.innerHTML = html;
    $('#chatMessages').append(e);
    e.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function ask(text) {
    add(text, 'user');
    $('#queryInput').value = '';
    try {
        const r = await fetch(`${API}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const d = await r.json();
        setMeta(d.meta);
        if (!d.answers.length) {
            add(d.message);
            return;
        }
        d.answers.forEach(x => add(`<div class="answer"><strong>${x.verdict}</strong><span>${x.item}: Rs. ${fmt(x.current_price)} · ${x.pct_change_1w > 0 ? '+' : ''}${x.pct_change_1w.toFixed(2)}% this week · ${x.direction} over 8 weeks</span></div>`));
    } catch (e) {
        add('I cannot reach the local price service right now. Please start the backend and try again.');
    }
}

$('#queryForm').addEventListener('submit', e => {
    e.preventDefault();
    const t = $('#queryInput').value.trim();
    if (t) ask(t);
});

load();
loadChips();
