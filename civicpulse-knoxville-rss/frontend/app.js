
const API = 'http://localhost:8000';
async function load() {
  const city = document.getElementById('city').value.trim();
  const category = document.getElementById('category').value;
  const params = new URLSearchParams();
  if (city) params.set('city', city);
  if (category) params.set('category', category);
  const res = await fetch(`${API}/items?${params.toString()}`);
  const data = await res.json();
  const feed = document.getElementById('feed');
  feed.innerHTML = '';
  data.forEach(i => {
    const li = document.createElement('li');
    li.className = 'card';
    li.innerHTML = `
      <h3><a href="${i.url || '#'}" target="_blank" rel="noopener">${i.title}</a></h3>
      <div class="meta">
        ${i.category || 'news'} • ${i.source || 'community'} • score ${i.importance.toFixed(2)}${i.city ? ' • ' + i.city : ''}
      </div>
      <p class="summary">${i.summary || ''}</p>
    `;
    feed.appendChild(li);
  });
}
document.getElementById('load').addEventListener('click', load);
window.addEventListener('load', async () => {
  // Seed some placeholder data if empty
  try {
    const r = await fetch(`${API}/items?limit=1`);
    const d = await r.json();
    if (!Array.isArray(d) || d.length === 0) {
      await fetch(`${API}/ingest/from-config`, { method: 'POST' });
    }
  } catch (e) {
    console.warn('API not reachable. Start backend first.');
  }
  load();
});


async function loadMarketplace() {
  try {
    const res = await fetch(`${API}/listings?city=Knoxville,%20TN`);
    const data = await res.json();
    const el = document.getElementById('market-list');
    el.innerHTML = data.map(x => `<div class="card"><strong>${x.title}</strong> — $${x.price.toFixed(2)}<br><small>${x.category||''} • ${x.city||''}</small><p>${x.description||''}</p></div>`).join('');
  } catch(e) {}
}

document.getElementById('m_post')?.addEventListener('click', async () => {
  const payload = {
    title: document.getElementById('m_title').value,
    price: parseFloat(document.getElementById('m_price').value||'0'),
    category: document.getElementById('m_category').value || 'for_sale',
    city: 'Knoxville, TN',
    contact: document.getElementById('m_contact').value,
    description: document.getElementById('m_desc').value,
    is_active: true
  };
  await fetch(`${API}/listings`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  loadMarketplace();
});

async function loadEvents() {
  try {
    const res = await fetch(`${API}/community-events?city=Knoxville,%20TN&upcoming_only=true`);
    const data = await res.json();
    const el = document.getElementById('events-list');
    el.innerHTML = data.map(x => {
      const starts = x.starts_at?.replace('T',' ').slice(0,16);
      const ends = x.ends_at ? x.ends_at.replace('T',' ').slice(0,16) : '';
      return `<div class="card"><strong>${x.title}</strong><br><small>${starts}${ends? ' → ' + ends: ''} • ${x.venue||''} • ${x.city||''}</small><p>${x.description||''}</p></div>`;
    }).join('');
  } catch(e) {}
}

document.getElementById('e_submit')?.addEventListener('click', async () => {
  const payload = {
    title: document.getElementById('e_title').value,
    venue: document.getElementById('e_venue').value,
    starts_at: new Date(document.getElementById('e_start').value).toISOString(),
    ends_at: document.getElementById('e_end').value ? new Date(document.getElementById('e_end').value).toISOString() : null,
    host_contact: document.getElementById('e_contact').value,
    description: document.getElementById('e_desc').value,
    city: 'Knoxville, TN',
    is_approved: false
  };
  await fetch(`${API}/community-events`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  alert('Submitted! An admin must approve it before it appears.');
  loadEvents();
});

// re-run loaders
window.addEventListener('load', () => { loadMarketplace(); loadEvents(); });


document.getElementById('load_incumbents')?.addEventListener('click', async () => {
  const res = await fetch(`${API}/incumbents?jurisdiction=City%20of%20Knoxville`);
  const data = await res.json();
  const el = document.getElementById('incumbent-list');
  el.innerHTML = data.map(x => `<div class="card"><strong>${x.office.name}</strong><br>${x.person.full_name} (${x.person.party||'—'})</div>`).join('');
});

document.getElementById('load_candidates')?.addEventListener('click', async () => {
  const id = document.getElementById('race_id').value;
  const url = id ? `${API}/candidates?race_id=${id}` : `${API}/candidates`;
  const res = await fetch(url);
  const data = await res.json();
  const el = document.getElementById('candidate-list');
  el.innerHTML = data.map(x => `<div class="card"><strong>${x.person.full_name}</strong> (${x.person.party||'—'})<br><small>Status: ${x.candidacy.status||'—'} • Race #${x.candidacy.race_id}</small><p>${x.candidacy.platform||''}</p></div>`).join('');
});
