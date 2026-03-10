const API = '';
let currentTable = 'departments';
let currentTableData = [];
let hiredData = [];

// ── Navigation ──────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  document.querySelectorAll('.nav-link').forEach(l => {
    if (l.getAttribute('onclick') && l.getAttribute('onclick').includes(name)) {
      l.classList.add('active');
    }
  });
  if (name === 'dashboard') loadDashboard();
  if (name === 'tables') loadTable(currentTable, null);
  if (name === 'hired') loadHired();
}

// ── Toast ────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
  const colors = { success: '#2ecc71', error: '#e74c3c', info: '#4f8ef7' };
  const el = document.createElement('div');
  el.className = `toast-msg ${type}`;
  el.innerHTML = `<i class="fa-solid ${icons[type]}" style="color:${colors[type]}"></i><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ── API helpers ───────────────────────────────────────────────
async function apiGet(path) {
  const res = await fetch(API + path);
  return res.json();
}

async function apiPost(path, body = null) {
  const opts = { method: 'POST', headers: {} };
  if (body) { opts.body = body; }
  const res = await fetch(API + path, opts);
  return res.json();
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  if (loading) {
    btn._orig = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Loading...`;
  } else {
    btn.innerHTML = btn._orig;
  }
}

// ── Dashboard ─────────────────────────────────────────────────
async function loadDashboard() {
  const tables = ['departments', 'jobs', 'hired_employees'];
  const ids = ['count-departments', 'count-jobs', 'count-hired'];
  for (let i = 0; i < tables.length; i++) {
    try {
      const data = await apiGet(`/table/${tables[i]}`);
      document.getElementById(ids[i]).textContent =
        data.data ? data.data.length.toLocaleString() : '—';
    } catch {
      document.getElementById(ids[i]).textContent = 'err';
    }
  }
}

// ── Browse Tables ─────────────────────────────────────────────
async function loadTable(name, tabEl) {
  currentTable = name;
  document.getElementById('table-title').textContent = name;
  document.getElementById('table-search').value = '';
  document.getElementById('table-body-container').innerHTML =
    '<div class="empty-state"><span class="spinner" style="width:32px;height:32px;border-width:3px"></span></div>';

  if (tabEl) {
    document.querySelectorAll('.table-tab').forEach(t => t.classList.remove('active'));
    tabEl.classList.add('active');
  }

  try {
    const res = await apiGet(`/table/${name}`);
    if (res.error) { toast(res.error, 'error'); return; }
    currentTableData = res.data || [];
    renderTable(currentTableData);
  } catch (e) {
    toast('Failed to load table: ' + e.message, 'error');
  }
}

function refreshCurrentTable() { loadTable(currentTable, null); }

function renderTable(data) {
  if (!data || data.length === 0) {
    document.getElementById('table-body-container').innerHTML =
      '<div class="empty-state"><i class="fa-solid fa-inbox"></i>No data found</div>';
    document.getElementById('table-row-count').textContent = '0 rows';
    return;
  }
  const cols = Object.keys(data[0]);
  let html = `<table class="etl-table"><thead><tr>`;
  cols.forEach(c => { html += `<th>${c}</th>`; });
  html += `</tr></thead><tbody>`;
  data.forEach(row => {
    html += '<tr>';
    cols.forEach(c => { html += `<td>${row[c] ?? ''}</td>`; });
    html += '</tr>';
  });
  html += '</tbody></table>';
  document.getElementById('table-body-container').innerHTML = html;
  document.getElementById('table-row-count').textContent = `${data.length.toLocaleString()} rows`;
}

function filterTable() {
  const q = document.getElementById('table-search').value.toLowerCase();
  if (!q) { renderTable(currentTableData); return; }
  const filtered = currentTableData.filter(row =>
    Object.values(row).some(v => String(v).toLowerCase().includes(q))
  );
  renderTable(filtered);
}

// ── Hired by Quarter ──────────────────────────────────────────
async function loadHired() {
  document.getElementById('hired-container').innerHTML =
    '<div class="empty-state"><span class="spinner" style="width:32px;height:32px;border-width:3px"></span></div>';
  document.getElementById('hired-search').value = '';
  try {
    const res = await apiGet('/getNumHired');
    if (res.error) { toast(res.error, 'error'); return; }
    hiredData = JSON.parse(res.message);
    renderHired(hiredData);
  } catch (e) {
    toast('Failed to load data: ' + e.message, 'error');
  }
}

function renderHired(data) {
  if (!data || data.length === 0) {
    document.getElementById('hired-container').innerHTML =
      '<div class="empty-state"><i class="fa-solid fa-inbox"></i>No data found</div>';
    document.getElementById('hired-row-count').textContent = '0 rows';
    return;
  }
  let html = `<table class="etl-table">
    <thead><tr>
      <th>Department</th><th>Job</th>
      <th style="text-align:center">Q1</th>
      <th style="text-align:center">Q2</th>
      <th style="text-align:center">Q3</th>
      <th style="text-align:center">Q4</th>
      <th style="text-align:center">Total</th>
    </tr></thead><tbody>`;
  data.forEach(row => {
    const total = (row.Q1 || 0) + (row.Q2 || 0) + (row.Q3 || 0) + (row.Q4 || 0);
    const q = (v) => v > 0
      ? `<td style="text-align:center" class="q-has">${v}</td>`
      : `<td style="text-align:center" class="q-zero">0</td>`;
    html += `<tr>
      <td>${row.department ?? ''}</td>
      <td>${row.job ?? ''}</td>
      ${q(row.Q1)} ${q(row.Q2)} ${q(row.Q3)} ${q(row.Q4)}
      <td style="text-align:center;font-weight:600">${total}</td>
    </tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('hired-container').innerHTML = html;
  document.getElementById('hired-row-count').textContent = `${data.length.toLocaleString()} rows`;
}

function filterHired() {
  const q = document.getElementById('hired-search').value.toLowerCase();
  if (!q) { renderHired(hiredData); return; }
  const filtered = hiredData.filter(r =>
    (r.department || '').toLowerCase().includes(q) ||
    (r.job || '').toLowerCase().includes(q)
  );
  renderHired(filtered);
}

// ── Operations ────────────────────────────────────────────────
async function fullMigrate() {
  setLoading('btn-migrate', true);
  toast('Starting full migration...', 'info');
  try {
    const res = await apiPost('/fullmigrate');
    if (res.error) { toast('Migration failed: ' + res.error, 'error'); }
    else { toast('Full migration completed successfully!', 'success'); }
  } catch (e) {
    toast('Request failed: ' + e.message, 'error');
  } finally {
    setLoading('btn-migrate', false);
  }
}

async function backupTable() {
  const table = document.getElementById('backup-table').value;
  toast(`Backing up ${table}...`, 'info');
  try {
    const res = await apiPost(`/backup/${table}`);
    if (res.error) toast('Backup failed: ' + res.error, 'error');
    else toast(res.message, 'success');
  } catch (e) { toast('Request failed: ' + e.message, 'error'); }
}

async function restoreTable() {
  const table = document.getElementById('restore-table').value;
  toast(`Restoring ${table}...`, 'info');
  try {
    const res = await apiPost(`/restore/${table}`);
    if (res.error) toast('Restore failed: ' + res.error, 'error');
    else toast(res.message, 'success');
  } catch (e) { toast('Request failed: ' + e.message, 'error'); }
}

async function insertData() {
  const table = document.getElementById('insert-table').value;
  const raw = document.getElementById('insert-json').value.trim();
  if (!raw) { toast('Please enter JSON data', 'error'); return; }
  let parsed;
  try { parsed = JSON.parse(raw); } catch { toast('Invalid JSON format', 'error'); return; }
  if (!Array.isArray(parsed)) { toast('JSON must be an array of objects', 'error'); return; }
  toast(`Inserting ${parsed.length} rows into ${table}...`, 'info');
  try {
    const res = await apiPost(`/insert/${table}`, JSON.stringify(parsed));
    if (res.error) toast('Insert failed: ' + res.error, 'error');
    else toast(res.message, 'success');
  } catch (e) { toast('Request failed: ' + e.message, 'error'); }
}

// ── Init ──────────────────────────────────────────────────────
loadDashboard();
