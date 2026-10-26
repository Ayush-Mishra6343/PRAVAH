// PRAVAHA EOC Operations Logic (Multilingual 10-Language Edition)

let selectedIncidentId = null;
let currentSummaryOriginal = "";
let map = null;
let incidentMarkers = [];
let isDemoRunning = false;
let allIncidents = [];
let currentFilter = 'ALL';

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadData();
  setInterval(loadData, 4000);
});

// Initialize Leaflet Map
function initMap() {
  try {
    const lat = 25.5941;
    const lng = 85.1376;
    map = L.map('map', {
      center: [lat, lng],
      zoom: 13,
      zoomControl: true,
      attributionControl: false
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(map);

    const depotIcon = L.divIcon({
      className: 'custom-div-icon',
      html: "<div style='background-color:#0284C7; color:white; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; border:2px solid #38BDF8; font-size:11px;'><i class='fa-solid fa-warehouse'></i></div>",
      iconSize: [24, 24]
    });

    L.marker([lat + 0.015, lng - 0.012], { icon: depotIcon })
      .addTo(map)
      .bindPopup("<b>Depot A - Central Logistics</b><br>Drinking Water & Food Stock");

    L.marker([lat - 0.018, lng + 0.02], { icon: depotIcon })
      .addTo(map)
      .bindPopup("<b>NDRF Base Sector 9</b><br>Inflatable Rescue Boats");

  } catch (err) {
    console.error("Map initialization failed:", err);
  }
}

// Fetch all system data
async function loadData() {
  try {
    const [statusRes, incRes, invRes, recRes, actRes] = await Promise.all([
      fetch('/api/status').then(r => r.json()),
      fetch('/api/incidents').then(r => r.json()),
      fetch('/api/inventory').then(r => r.json()),
      fetch('/api/recommendations').then(r => r.json()),
      fetch('/api/activity').then(r => r.json())
    ]);

    renderStatus(statusRes);
    allIncidents = incRes || [];
    applyIncidentFilters();
    renderInventory(invRes);
    renderRecommendations(recRes);
    renderActivity(actRes);

    if (selectedIncidentId) {
      loadIncidentDetail(selectedIncidentId);
    } else if (allIncidents.length > 0) {
      selectIncident(allIncidents[0].id);
    }

  } catch (err) {
    console.warn("Polling error:", err);
  }
}

// Render status & multilingual distribution pills
function renderStatus(data) {
  if (!data) return;
  const pName = document.getElementById('provider-name');
  const pPulse = document.getElementById('provider-pulse');

  if (data.provider) {
    pName.innerText = data.provider.active_provider;
    if (data.provider.is_fallback) {
      pName.className = "font-mono font-bold text-amber-400 ml-1";
      pPulse.className = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse";
    } else {
      pName.className = "font-mono font-bold text-emerald-400 ml-1";
      pPulse.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse";
    }
  }

  // Update KPIs
  if (data.metrics) {
    document.getElementById('kpi-reports').innerText = data.metrics.total_reports || 0;
    document.getElementById('kpi-incidents').innerText = data.metrics.active_incidents || 0;
    document.getElementById('kpi-contradictions').innerText = data.metrics.contradictions || 0;
    document.getElementById('kpi-recommendations').innerText = data.metrics.pending_recommendations || 0;
  }

  // Language Distribution
  const langContainer = document.getElementById('language-pills');
  if (data.language_distribution && Object.keys(data.language_distribution).length > 0) {
    langContainer.innerHTML = Object.entries(data.language_distribution).map(([lang, count]) => `
      <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-300 text-[11px] font-mono">
        ${lang}: <b class="text-white">${count}</b>
      </span>
    `).join('');
  } else {
    langContainer.innerHTML = `<span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">None yet</span>`;
  }
}

// Toggle Provider Mode
async function toggleProviderMode() {
  try {
    const res = await fetch('/api/toggle-provider', { method: 'POST' });
    const data = await res.json();
    loadData();
    showToast(`Provider switched: ${data.active_provider}`);
  } catch (err) {
    console.error(err);
  }
}

// Incident Filtering & Search Controls
function setIncidentFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.incident-filter-btn').forEach(b => {
    b.className = "incident-filter-btn px-2 py-0.5 rounded bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800";
  });
  const activeBtn = document.getElementById(`filter-btn-${filter}`);
  if (activeBtn) {
    if (filter === 'ALL') activeBtn.className = "incident-filter-btn px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-medium";
    if (filter === 'CRITICAL') activeBtn.className = "incident-filter-btn px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-medium";
    if (filter === 'CORROBORATED') activeBtn.className = "incident-filter-btn px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-medium";
    if (filter === 'CONFLICTING') activeBtn.className = "incident-filter-btn px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-medium";
  }
  applyIncidentFilters();
}

function filterIncidents() {
  applyIncidentFilters();
}

function applyIncidentFilters() {
  const searchTerm = (document.getElementById('incident-search-input')?.value || '').toLowerCase().trim();
  
  let filtered = allIncidents.filter(inc => {
    // Status filter
    if (currentFilter === 'CRITICAL' && inc.severity !== 'CRITICAL') return false;
    if (currentFilter === 'CORROBORATED' && inc.status !== 'corroborated') return false;
    if (currentFilter === 'CONFLICTING' && (!inc.has_contradiction && inc.status !== 'conflicting')) return false;

    // Search term filter
    if (searchTerm) {
      const matchId = inc.id.toLowerCase().includes(searchTerm);
      const matchTitle = (inc.title || '').toLowerCase().includes(searchTerm);
      const matchLoc = (inc.location || '').toLowerCase().includes(searchTerm);
      const matchLangs = (inc.languages || []).join(' ').toLowerCase().includes(searchTerm);
      return matchId || matchTitle || matchLoc || matchLangs;
    }
    return true;
  });

  renderIncidents(filtered);
}

// Render Incident Feed
function renderIncidents(incidents) {
  const container = document.getElementById('incident-list');
  const countBadge = document.getElementById('incident-count-badge');
  countBadge.innerText = `${incidents.length} / ${allIncidents.length} Incidents`;

  if (!incidents || incidents.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 text-slate-500 text-xs">
        <i class="fa-solid fa-radar text-2xl mb-2 text-slate-600 block"></i>
        ${allIncidents.length === 0 ? 'No active incidents detected.<br>Click "Multilingual Test (4+1)" or Ingest a Report.' : 'No incidents match current filter criteria.'}
      </div>
    `;
    clearMapMarkers();
    return;
  }

  container.innerHTML = incidents.map(inc => {
    const isSelected = inc.id === selectedIncidentId;
    const hasConflict = inc.has_contradiction;
    
    let statusClass = "bg-slate-800 text-slate-300 border-slate-700";
    if (inc.status === "corroborated") statusClass = "bg-blue-950 text-blue-300 border-blue-800";
    if (inc.status === "conflicting") statusClass = "bg-amber-950 text-amber-300 border-amber-700 animate-pulse";
    if (inc.status === "human_reviewed") statusClass = "bg-emerald-950 text-emerald-300 border-emerald-800";

    const langs = inc.languages || [];

    return `
      <div onclick="selectIncident('${inc.id}')" 
           class="cursor-pointer p-3 rounded-lg border transition ${
             isSelected ? 'bg-slate-900 border-cyan-500 shadow-md shadow-cyan-950/40' : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
           } ${hasConflict ? 'border-l-4 border-l-amber-500' : ''}">
        
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center gap-1.5">
            <span class="font-mono font-bold text-xs text-white">${inc.id}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-mono border ${statusClass}">${inc.status.toUpperCase()}</span>
          </div>
          <span class="text-[10px] text-slate-500 font-mono">${inc.report_ids ? inc.report_ids.length : 1} Reports</span>
        </div>

        <h3 class="font-semibold text-xs text-slate-200 line-clamp-1 mb-1">${inc.title}</h3>

        <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1.5">
          <span class="flex items-center gap-1"><i class="fa-solid fa-location-dot text-rose-400 text-[10px]"></i> ${inc.location}</span>
          <span class="text-[10px] font-mono ${inc.severity === 'CRITICAL' ? 'text-rose-400 font-bold' : 'text-amber-400'}">${inc.severity}</span>
        </div>

        <div class="flex items-center gap-1 flex-wrap pt-1 border-t border-slate-900">
          <span class="text-[9px] text-slate-500">Langs:</span>
          ${langs.map(l => `<span class="px-1.5 py-0.2 rounded bg-slate-900 border border-slate-800 text-[10px] text-cyan-300 font-mono">${l}</span>`).join('')}
        </div>

        ${hasConflict ? `
          <div class="mt-2 text-[10px] bg-amber-950/80 border border-amber-800/80 rounded px-2 py-1 text-amber-300 flex items-center gap-1.5">
            <i class="fa-solid fa-triangle-exclamation text-amber-400"></i>
            <span>Contradiction: Conflicting road passability</span>
          </div>
        ` : ''}

      </div>
    `;
  }).join('');

  updateMapMarkers(incidents);
}

// Update Map Markers with Hazard Zone Buffers
function updateMapMarkers(incidents) {
  if (!map) return;
  clearMapMarkers();

  incidents.forEach((inc, idx) => {
    let lat = 25.5941;
    let lng = 85.1376;
    if (inc.normalized_location_id && inc.normalized_location_id.includes("RAMPUR")) {
      lat = 25.6250;
      lng = 85.1850;
    } else {
      lat = 25.5941 + (idx * 0.003);
      lng = 85.1376 + (idx * 0.003);
    }

    const isConflict = inc.has_contradiction;
    const markerColor = isConflict ? "#F59E0B" : (inc.severity === "CRITICAL" ? "#EF4444" : "#0284C7");

    // Tactical Hazard Radius Circle
    const hazardRadius = isConflict ? 450 : (inc.severity === "CRITICAL" ? 550 : 350);
    const circle = L.circle([lat, lng], {
      radius: hazardRadius,
      color: markerColor,
      fillColor: markerColor,
      fillOpacity: 0.12,
      weight: 1.5,
      dashArray: isConflict ? '4, 4' : null
    }).addTo(map);
    incidentMarkers.push(circle);

    const icon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="background-color:${markerColor}; color:white; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; border:2px solid white; font-size:12px; box-shadow:0 0 10px ${markerColor}99;"><i class="fa-solid fa-triangle-exclamation"></i></div>`,
      iconSize: [28, 28]
    });

    const marker = L.marker([lat, lng], { icon })
      .addTo(map)
      .bindPopup(`
        <div style="font-size:11px; color:#F1F5F9;">
          <b>${inc.id}: ${inc.title}</b><br>
          <span>Status: <b>${inc.status}</b></span><br>
          <span>Location: ${inc.location}</span><br>
          <span style="color:${markerColor};">Hazard Zone: ${hazardRadius}m</span>
        </div>
      `);

    incidentMarkers.push(marker);
  });
}

function clearMapMarkers() {
  incidentMarkers.forEach(m => map.removeLayer(m));
  incidentMarkers = [];
}

function selectIncident(id) {
  selectedIncidentId = id;
  loadIncidentDetail(id);
}

// Load Incident Detail into Evidence Ledger
async function loadIncidentDetail(id) {
  try {
    const res = await fetch(`/api/incidents/${id}`);
    if (!res.ok) return;
    const inc = await res.json();

    document.getElementById('evidence-empty').classList.add('hidden');
    document.getElementById('evidence-content').classList.remove('hidden');
    document.getElementById('selected-incident-badge').innerText = inc.id;

    document.getElementById('detail-title').innerText = inc.title;
    document.getElementById('detail-location').innerHTML = `<i class="fa-solid fa-location-dot text-rose-400"></i> ${inc.location} <span class="font-mono text-[10px] text-slate-500">(${inc.normalized_location_id})</span>`;
    
    const statusBadge = document.getElementById('detail-status');
    statusBadge.innerText = inc.status;
    statusBadge.className = `px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
      inc.status === 'conflicting' ? 'bg-amber-950 text-amber-300 border border-amber-700' :
      inc.status === 'corroborated' ? 'bg-blue-950 text-blue-300 border border-blue-700' :
      inc.status === 'human_reviewed' ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' :
      'bg-slate-800 text-slate-300'
    }`;

    // Contradiction banner
    const cBanner = document.getElementById('contradiction-banner');
    if (inc.has_contradiction) {
      cBanner.classList.remove('hidden');
      document.getElementById('contradiction-text').innerText = inc.contradiction_notes || "Conflicting claims detected between linked reports.";
    } else {
      cBanner.classList.add('hidden');
    }

    // Unified Summary
    currentSummaryOriginal = inc.unified_summary || "No summary generated yet.";
    document.getElementById('unified-summary-text').innerText = currentSummaryOriginal;
    document.getElementById('contributing-langs-text').innerText = (inc.languages || []).join(', ') || 'English';

    // Reset language selector to English
    document.getElementById('summary-lang-select').value = "English";

    // Linked reports
    document.getElementById('linked-report-count').innerText = inc.reports ? inc.reports.length : 0;
    const repList = document.getElementById('linked-reports-list');
    
    if (inc.reports && inc.reports.length > 0) {
      repList.innerHTML = inc.reports.map(r => `
        <div class="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 space-y-1.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-mono font-bold text-cyan-400">${r.id}</span>
            <div class="flex items-center gap-1.5 text-[10px]">
              <button onclick="speakReportText(this, '${encodeURIComponent(r.text)}', '${r.language}')" 
                      class="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-700 text-[10px] flex items-center gap-1 transition" 
                      title="Listen in Native Voice">
                <i class="fa-solid fa-volume-high"></i> <span>Listen</span>
              </button>
              <span class="px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 font-bold">${r.language}</span>
              <span class="text-slate-500">${new Date(r.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
          
          <!-- Exact Immutable Original Text -->
          <div>
            <span class="text-[9px] text-slate-500 font-mono uppercase block">Original Message (${r.language}):</span>
            <p class="text-slate-200 italic font-serif text-[11px] bg-slate-900/60 p-2 rounded border border-slate-800/80 mt-0.5">
              "${r.text}"
            </p>
          </div>

          <!-- Normalized English Text -->
          ${r.normalized_en_text && r.language !== 'English' ? `
            <div>
              <span class="text-[9px] text-cyan-400 font-mono uppercase block">Normalized / Translated (English):</span>
              <p class="text-slate-300 text-[10.5px] bg-slate-950 p-1.5 rounded border border-slate-900 mt-0.5">
                ${r.normalized_en_text}
              </p>
            </div>
          ` : ''}

          <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-900">
            <span>Source: <b class="text-slate-300">${r.source_type}</b></span>
            <span class="font-mono text-cyan-400">${r.provider_used}</span>
          </div>
        </div>
      `).join('');
    } else {
      repList.innerHTML = `<div class="text-xs text-slate-500">No reports linked.</div>`;
    }

    // Extracted claims matrix
    const claimsContainer = document.getElementById('claims-matrix');
    if (inc.evidence_claims && inc.evidence_claims.length > 0) {
      claimsContainer.innerHTML = inc.evidence_claims.map(cl => `
        <div class="p-2 rounded border text-xs flex items-start justify-between gap-2 ${
          cl.is_conflicting ? 'bg-amber-950/40 border-amber-800/60 text-amber-200' : 'bg-slate-950/60 border-slate-800 text-slate-300'
        }">
          <div>
            <div class="flex items-center gap-1.5">
              <span class="font-mono text-[10px] text-slate-500">${cl.report_id}</span>
              ${cl.is_conflicting ? '<span class="text-[9px] px-1 rounded bg-amber-500 text-black font-bold uppercase">Conflicting Claim</span>' : ''}
            </div>
            <p class="mt-0.5">${cl.claim_text}</p>
          </div>
          <span class="text-[10px] text-slate-500 font-mono">${new Date(cl.created_at).toLocaleTimeString()}</span>
        </div>
      `).join('');
    } else {
      claimsContainer.innerHTML = `<div class="text-xs text-slate-500">No claims extracted.</div>`;
    }

  } catch (err) {
    console.error("Failed to load incident detail:", err);
  }
}

// Text-to-Speech Playback for Native Reports
function speakReportText(buttonElem, encodedText, language) {
  if (!('speechSynthesis' in window)) {
    alert("Speech synthesis is not supported in this browser.");
    return;
  }

  const text = decodeURIComponent(encodedText);
  window.speechSynthesis.cancel(); // Stop any previous speech

  const utterance = new SpeechSynthesisUtterance(text);
  const langMap = {
    'Hindi': 'hi-IN',
    'Bengali': 'bn-IN',
    'Tamil': 'ta-IN',
    'Telugu': 'te-IN',
    'Marathi': 'mr-IN',
    'Gujarati': 'gu-IN',
    'Kannada': 'kn-IN',
    'Malayalam': 'ml-IN',
    'Punjabi': 'pa-IN',
    'English': 'en-IN'
  };
  utterance.lang = langMap[language] || 'en-IN';
  utterance.rate = 0.95;

  const originalHtml = buttonElem.innerHTML;
  buttonElem.innerHTML = `<i class="fa-solid fa-volume-high text-emerald-400 animate-pulse"></i> <span class="text-emerald-400">Playing...</span>`;
  buttonElem.disabled = true;

  utterance.onend = () => {
    buttonElem.innerHTML = originalHtml;
    buttonElem.disabled = false;
  };
  utterance.onerror = () => {
    buttonElem.innerHTML = originalHtml;
    buttonElem.disabled = false;
  };

  window.speechSynthesis.speak(utterance);
}

// Copy Unified Incident Summary to Clipboard
function copyUnifiedSummary() {
  const text = document.getElementById('unified-summary-text')?.innerText || '';
  if (!text) return;

  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('copy-summary-btn');
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> <span class="text-emerald-400">Copied!</span>`;
      setTimeout(() => { btn.innerHTML = orig; }, 2000);
    }
    showToast("Incident summary copied to clipboard.");
  }).catch(err => {
    console.error("Copy failed:", err);
    showToast("Could not access clipboard.");
  });
}

// Translate Unified Summary on Language Switch
async function translateUnifiedSummary() {
  const targetLang = document.getElementById('summary-lang-select').value;
  if (!selectedIncidentId) return;

  if (targetLang === "English") {
    document.getElementById('unified-summary-text').innerText = currentSummaryOriginal;
    return;
  }

  try {
    document.getElementById('unified-summary-text').innerText = `Translating into ${targetLang} via Sarvam Mayura:v1...`;
    const res = await fetch(`/api/incidents/${selectedIncidentId}/translate-summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: currentSummaryOriginal, target_language: targetLang })
    });
    const data = await res.json();
    document.getElementById('unified-summary-text').innerText = data.translated_summary;
    showToast(`Summary translated to ${targetLang}`);
  } catch (err) {
    console.error(err);
    document.getElementById('unified-summary-text').innerText = currentSummaryOriginal;
  }
}

// Human Operator Verification
async function verifyIncident() {
  if (!selectedIncidentId) return;
  try {
    await fetch(`/api/incidents/${selectedIncidentId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'verify', note: 'Ground survey confirmed by operator.' })
    });
    loadData();
    showToast("Incident marked as Human-Reviewed.");
  } catch (err) {
    console.error(err);
  }
}

// Contradiction Resolution
async function resolveContradiction() {
  if (!selectedIncidentId) return;
  const note = prompt("Enter Operator Resolution Note (e.g. Drone scout confirmed road is partially flooded, 4x4 vehicles only):", "Drone scout confirmed road is partially flooded, 4x4 vehicles only");
  if (!note) return;

  try {
    await fetch(`/api/incidents/${selectedIncidentId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'resolve_contradiction', note })
    });
    loadData();
    showToast("Contradiction marked as resolved.");
  } catch (err) {
    console.error(err);
  }
}

// Render Inventory
function renderInventory(items) {
  const container = document.getElementById('inventory-meters');
  if (!items || items.length === 0) return;

  container.innerHTML = items.map(it => {
    const pct = Math.round((it.available_qty / it.total_qty) * 100);
    return `
      <div class="bg-slate-900 border border-slate-800 rounded p-2 text-xs">
        <div class="flex items-center justify-between text-[11px] mb-1">
          <span class="font-bold text-slate-200 line-clamp-1">${it.item_name}</span>
          <span class="font-mono text-cyan-400 font-bold">${it.available_qty}/${it.total_qty}</span>
        </div>
        <div class="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
          <div class="bg-cyan-500 h-1.5 rounded-full" style="width: ${pct}%"></div>
        </div>
        <span class="text-[9px] text-slate-500 block mt-1 line-clamp-1">${it.depot_name}</span>
      </div>
    `;
  }).join('');
}

// Render Recommendations
function renderRecommendations(recs) {
  const container = document.getElementById('recommendations-list');
  if (!recs || recs.length === 0) {
    container.innerHTML = `<div class="text-center py-6 text-slate-500 text-xs">No active recommendations pending.</div>`;
    return;
  }

  container.innerHTML = recs.map(rec => {
    const isApproved = rec.status === "APPROVED";
    const isHeld = rec.status === "HELD_FOR_RECON";

    return `
      <div class="bg-slate-950 border border-slate-800 rounded-lg p-3 space-y-2 text-xs">
        <div class="flex items-center justify-between">
          <span class="font-bold text-cyan-300">${rec.item_name}</span>
          <span class="font-mono text-xs text-white bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">
            ${rec.recommended_qty} ${rec.unit}
          </span>
        </div>

        <p class="text-slate-300 text-[11px] leading-relaxed">
          <b class="text-slate-400">Rationale:</b> ${rec.rationale}
        </p>

        ${rec.route_warning ? `
          <div class="bg-amber-950/70 border border-amber-800 rounded p-2 text-[10px] text-amber-200 space-y-1">
            <div class="font-bold flex items-center gap-1 text-amber-400">
              <i class="fa-solid fa-triangle-exclamation"></i> ROUTE SAFETY WARNING
            </div>
            <div>${rec.route_warning}</div>
          </div>
        ` : ''}

        <div class="flex items-center justify-between pt-1 border-t border-slate-900 text-[10px]">
          <span class="text-slate-500 font-mono">${rec.depot_name}</span>
          <div class="flex items-center gap-1.5">
            ${isApproved ? `
              <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-800">
                <i class="fa-solid fa-check mr-1"></i>DISPATCH AUTHORIZED
              </span>
            ` : isHeld ? `
              <span class="px-2 py-0.5 rounded bg-amber-950 text-amber-300 font-bold border border-amber-800">
                <i class="fa-solid fa-hand mr-1"></i>HELD FOR RECON
              </span>
            ` : `
              <button onclick="updateRecStatus('${rec.id}', 'HELD_FOR_RECON')" class="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
                Hold
              </button>
              <button onclick="updateRecStatus('${rec.id}', 'APPROVED')" class="px-2.5 py-0.5 rounded bg-emerald-700 hover:bg-emerald-600 text-white font-bold transition">
                Approve Dispatch
              </button>
            `}
          </div>
        </div>

      </div>
    `;
  }).join('');
}

// Update Recommendation Status
async function updateRecStatus(recId, status) {
  try {
    const res = await fetch(`/api/recommendations/${recId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Action failed");
      return;
    }
    loadData();
    showToast(`Dispatch recommendation updated: ${status}`);
  } catch (err) {
    console.error(err);
  }
}

// Render Activity Log
function renderActivity(logs) {
  const container = document.getElementById('activity-log');
  if (!logs || logs.length === 0) {
    container.innerHTML = `<div class="text-slate-500 text-center py-4">No activity logged yet.</div>`;
    return;
  }

  container.innerHTML = logs.map(l => {
    let icon = "fa-circle-info text-cyan-400";
    if (l.severity === "WARNING") icon = "fa-triangle-exclamation text-amber-400";
    if (l.severity === "ERROR") icon = "fa-circle-xmark text-rose-400";

    return `
      <div class="border-b border-slate-900 pb-1.5 last:border-0">
        <div class="flex items-center justify-between text-[10px] text-slate-500">
          <span class="font-bold text-slate-400 flex items-center gap-1.5">
            <i class="fa-solid ${icon}"></i> ${l.title}
          </span>
          <span>${new Date(l.timestamp).toLocaleTimeString()}</span>
        </div>
        <p class="text-slate-400 text-[11px] mt-0.5 font-sans">${l.description}</p>
      </div>
    `;
  }).join('');
}

// MULTILINGUAL ACCEPTANCE TEST RUNNER (4 same school + 1 distinct village)
async function runMultilingualAcceptanceTest() {
  showToast("Executing Multilingual Acceptance Test (Hindi, Bengali, Tamil, English + Rampur Village)...");
  try {
    const res = await fetch('/api/demo/multilingual', { method: 'POST' });
    const data = await res.json();
    await loadData();
    
    if (data.distinct_village_separated) {
      showToast("SUCCESS! 4 Reports grouped at Govt School; Rampur Village preserved as separate incident!");
    } else {
      showToast("Multilingual test complete.");
    }
  } catch (err) {
    console.error(err);
  }
}

// STEP RUNNER
async function runStep(stepNumber) {
  try {
    document.querySelectorAll('.demo-step-btn').forEach(btn => btn.classList.remove('border-cyan-500', 'bg-cyan-950'));
    const activeBtn = document.getElementById(`step-btn-${stepNumber}`);
    if (activeBtn) activeBtn.classList.add('border-cyan-500', 'bg-cyan-950');

    const statusText = document.getElementById('demo-status-text');
    statusText.innerText = `Step ${stepNumber}...`;

    const res = await fetch(`/api/demo/step/${stepNumber}`, { method: 'POST' });
    const result = await res.json();

    statusText.innerText = `Step ${stepNumber}: ${result.title}`;
    await loadData();
    showToast(`Step ${stepNumber}: ${result.title}`);

  } catch (err) {
    console.error(`Step ${stepNumber} failed:`, err);
  }
}

async function runFullDemoScenario() {
  if (isDemoRunning) return;
  isDemoRunning = true;
  showToast("Starting 5-Step Crisis Scenario Tour...");

  await fetch('/api/demo/reset', { method: 'POST' });
  await loadData();

  for (let s = 1; s <= 5; s++) {
    await runStep(s);
    await new Promise(r => setTimeout(r, 2200));
  }

  isDemoRunning = false;
  showToast("Scenario Complete!");
}

async function resetSystem() {
  if (confirm("Reset PRAVAHA system to clean initial state?")) {
    await fetch('/api/demo/reset', { method: 'POST' });
    selectedIncidentId = null;
    loadData();
    showToast("System reset successfully.");
  }
}

// VOICE INPUT / SPEECH-TO-TEXT
let recognition = null;
let isRecording = false;

function toggleVoiceRecording() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Please type your message.");
    return;
  }

  const voiceBtn = document.getElementById('voice-btn');
  const voiceLabel = document.getElementById('voice-btn-label');
  const indicator = document.getElementById('voice-indicator');

  if (isRecording) {
    if (recognition) recognition.stop();
    isRecording = false;
    voiceBtn.classList.remove('bg-rose-950', 'border-rose-700', 'text-rose-300');
    voiceLabel.innerText = "Voice Input";
    indicator.classList.add('hidden');
    return;
  }

  recognition = new SpeechRecognition();
  const selectedLang = document.getElementById('modal-language').value;
  const langMap = {
    'Hindi': 'hi-IN',
    'Bengali': 'bn-IN',
    'Tamil': 'ta-IN',
    'Telugu': 'te-IN',
    'Marathi': 'mr-IN',
    'Gujarati': 'gu-IN',
    'Kannada': 'kn-IN',
    'Malayalam': 'ml-IN',
    'Punjabi': 'pa-IN',
    'English': 'en-IN',
    'Auto': 'en-IN'
  };
  recognition.lang = langMap[selectedLang] || 'en-IN';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isRecording = true;
    voiceBtn.classList.add('bg-rose-950', 'border-rose-700', 'text-rose-300');
    voiceLabel.innerText = "Stop Dictating";
    indicator.classList.remove('hidden');
    showToast(`Listening in ${selectedLang}... Speak now.`);
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const textArea = document.getElementById('modal-text');
    textArea.value = (textArea.value ? textArea.value + " " : "") + transcript;
    showToast("Voice transcribed successfully! Review before submitting.");
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    isRecording = false;
    voiceBtn.classList.remove('bg-rose-950', 'border-rose-700', 'text-rose-300');
    voiceLabel.innerText = "Voice Input";
    indicator.classList.add('hidden');
    if (event.error !== 'no-speech') {
      alert(`Voice recognition error: ${event.error}. Please type your message.`);
    }
  };

  recognition.onend = () => {
    isRecording = false;
    voiceBtn.classList.remove('bg-rose-950', 'border-rose-700', 'text-rose-300');
    voiceLabel.innerText = "Voice Input";
    indicator.classList.add('hidden');
  };

  try {
    recognition.start();
  } catch (err) {
    console.error("Failed to start voice recognition:", err);
  }
}

// MODAL CONTROLS
function openSubmitModal() {
  document.getElementById('submit-modal').classList.remove('hidden');
}
function closeSubmitModal() {
  document.getElementById('submit-modal').classList.add('hidden');
}

function applySample(type) {
  const textElem = document.getElementById('modal-text');
  const locElem = document.getElementById('modal-location');
  const langElem = document.getElementById('modal-language');
  const srcElem = document.getElementById('modal-source');

  if (type === 1) {
    textElem.value = "पानी तेजी से बढ़ रहा है। सरकारी स्कूल के पास परिवार फंसे हुए हैं। पीने का पानी चाहिए।";
    locElem.value = "Near Government Primary School, Sector 4";
    langElem.value = "Hindi";
    srcElem.value = "Citizen SMS";
  } else if (type === 2) {
    textElem.value = "জল দ্রুত বাড়ছে। সরকারি প্রাথমিক বিদ্যালয়ের কাছে পরিবারগুলি আটকে রয়েছে। পানীয় জলের তীব্র সংকট।";
    locElem.value = "Government Primary School, Sector 4";
    langElem.value = "Bengali";
    srcElem.value = "Field Volunteer";
  } else if (type === 4) {
    textElem.value = "தண்ணீர் வேகமாக உயர்ந்து வருகிறது. அரசு தொடக்கப் பள்ளி அருகே குடும்பங்கள் சிக்கித் தவிக்கின்றனர். குடிநீர் தேவை.";
    locElem.value = "Near Primary School, Sector 4";
    langElem.value = "Tamil";
    srcElem.value = "Emergency Helpline";
  } else if (type === 5) {
    textElem.value = "Floodwaters entered Rampur village. Farmlands and houses submerged near the riverbank.";
    locElem.value = "Rampur Village, Riverside Sector";
    langElem.value = "English";
    srcElem.value = "Field Volunteer";
  }
}

async function submitModalReport() {
  const text = document.getElementById('modal-text').value.trim();
  const location = document.getElementById('modal-location').value.trim();
  const language = document.getElementById('modal-language').value;
  const source_type = document.getElementById('modal-source').value;

  if (!text) {
    alert("Please provide the emergency report message.");
    return;
  }

  const submitBtn = document.getElementById('modal-submit-btn');
  const submitIcon = document.getElementById('submit-icon');
  const submitText = document.getElementById('submit-btn-text');

  if (submitBtn) {
    submitBtn.disabled = true;
    if (submitIcon) submitIcon.className = "fa-solid fa-circle-notch fa-spin";
    if (submitText) submitText.innerText = "Extracting via Sarvam AI...";
  }

  try {
    const res = await fetch('/api/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, location, language, source_type })
    });
    const result = await res.json();
    closeSubmitModal();
    document.getElementById('modal-text').value = '';
    document.getElementById('modal-location').value = '';
    loadData();
    showToast(`Report ${result.report_id} ingested in ${result.extraction.language}!`);
  } catch (err) {
    console.error(err);
    alert("Failed to ingest report.");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      if (submitIcon) submitIcon.className = "fa-solid fa-paper-plane";
      if (submitText) submitText.innerText = "Process & Ingest";
    }
  }
}

function showToast(message) {
  const existing = document.getElementById('toast-msg');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'toast-msg';
  toast.className = 'fixed bottom-4 right-4 bg-slate-900 border border-cyan-500/80 text-white text-xs px-4 py-2.5 rounded-lg shadow-2xl z-50 flex items-center gap-2 font-mono';
  toast.innerHTML = `<i class="fa-solid fa-satellite-dish text-cyan-400"></i> ${message}`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4500);
}
