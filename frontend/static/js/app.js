const WS_URL = "ws://localhost:8000/ws/telemetry";
const API_BASE = "http://localhost:8000/api";

let map;
let marker;
let pathLine;
const pathCoords = [];

let altitudeChart;
let speedChart;

const timeLabels = [];
const altitudeData = [];
const speedData = [];

const MAX_POINTS = 100;
let alertsVisible = false;

function initMap() {
  map = L.map("map").setView([19.0760, 72.8777], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  marker = L.marker([19.0760, 72.8777]).addTo(map);
  pathLine = L.polyline([], { color: '#3b82f6', weight: 3 }).addTo(map);
}

function initCharts() {
  const altCtx = document.getElementById("altitudeChart").getContext("2d");
  altitudeChart = new Chart(altCtx, {
    type: "line",
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: "Altitude (m)",
          data: altitudeData,
          fill: false,
          borderColor: '#10b981',
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: {
          ticks: { maxTicksLimit: 5 },
        },
      },
    },
  });

  const speedCtx = document.getElementById("speedChart").getContext("2d");
  speedChart = new Chart(speedCtx, {
    type: "line",
    data: {
      labels: timeLabels,
      datasets: [
        {
          label: "Ground Speed (m/s)",
          data: speedData,
          fill: false,
          borderColor: '#f59e0b',
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: {
          ticks: { maxTicksLimit: 5 },
        },
      },
    },
  });
}

function setConnectionStatus(text, ok) {
  const el = document.getElementById("connection-status");
  el.textContent = text;
  if (ok) {
    el.classList.remove("bg-slate-700");
    el.classList.remove("bg-red-700");
    el.classList.add("bg-emerald-600");
  } else {
    el.classList.remove("bg-emerald-600");
    el.classList.add("bg-red-700");
  }
}

function updateStatusCards(data) {
  document.getElementById("mode").textContent = data.mode || "--";
  document.getElementById("battery").textContent =
    (data.battery_percent ?? "--") + " %";
  document.getElementById("speed").textContent =
    (data.ground_speed_ms ?? "--") + " m/s";
  document.getElementById("altitude").textContent =
    (data.altitude_m ?? "--") + " m";

  const batteryEl = document.getElementById("battery");
  const batteryPercent = data.battery_percent ?? 100;
  if (batteryPercent < 20) {
    batteryEl.classList.add("text-red-400");
  } else if (batteryPercent < 50) {
    batteryEl.classList.add("text-yellow-400");
  } else {
    batteryEl.classList.remove("text-red-400", "text-yellow-400");
  }
}

function updateMap(data) {
  if (!map || !marker) return;
  if (typeof data.lat !== "number" || typeof data.lon !== "number") return;

  const latlng = [data.lat, data.lon];

  marker.setLatLng(latlng);
  pathCoords.push(latlng);
  if (pathCoords.length > 200) {
    pathCoords.shift();
  }
  pathLine.setLatLngs(pathCoords);

  map.panTo(latlng, { animate: true });
}

function updateCharts(data) {
  const ts = data.timestamp ? new Date(data.timestamp * 1000) : new Date();
  const label = ts.toLocaleTimeString();

  timeLabels.push(label);
  altitudeData.push(data.altitude_m ?? 0);
  speedData.push(data.ground_speed_ms ?? 0);

  if (timeLabels.length > MAX_POINTS) {
    timeLabels.shift();
    altitudeData.shift();
    speedData.shift();
  }

  altitudeChart.update();
  speedChart.update();
}

function updateRaw(data) {
  document.getElementById("raw-data").textContent = JSON.stringify(
    data,
    null,
    2
  );
}

function updateAlerts(alerts) {
  const container = document.getElementById("alerts-container");
  const badge = document.getElementById("alerts-badge");

  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<p class="text-slate-400 text-sm">No active alerts</p>';
    badge.textContent = '0';
    badge.classList.add('hidden');
    return;
  }

  badge.textContent = alerts.length;
  badge.classList.remove('hidden');

  container.innerHTML = alerts.map(alert => {
    const severityColors = {
      HIGH: 'bg-red-900/50 border-red-500',
      MEDIUM: 'bg-orange-900/50 border-orange-500',
      LOW: 'bg-yellow-900/50 border-yellow-500'
    };

    return `
      <div class="border-l-4 p-2 mb-2 text-sm ${severityColors[alert.severity] || 'bg-slate-700'}">
        <div class="font-semibold">${alert.type.replace(/_/g, ' ')}</div>
        <div class="text-slate-300">${alert.message}</div>
        <div class="text-xs text-slate-400 mt-1">${new Date(alert.timestamp).toLocaleTimeString()}</div>
      </div>
    `;
  }).join('');
}

function toggleAlerts() {
  const panel = document.getElementById("alerts-panel");
  alertsVisible = !alertsVisible;

  if (alertsVisible) {
    panel.classList.remove('hidden');
  } else {
    panel.classList.add('hidden');
  }
}

async function clearAlerts() {
  try {
    await fetch(`${API_BASE}/alerts/clear`, { method: 'POST' });
    document.getElementById("alerts-container").innerHTML =
      '<p class="text-slate-400 text-sm">No active alerts</p>';
    document.getElementById("alerts-badge").classList.add('hidden');
  } catch (err) {
    console.error('Failed to clear alerts:', err);
  }
}

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/stats`);
    const stats = await response.json();

    if (stats.message) {
      document.getElementById("stats-content").innerHTML =
        `<p class="text-slate-400">${stats.message}</p>`;
      return;
    }

    document.getElementById("stats-content").innerHTML = `
      <div class="grid grid-cols-2 gap-3">
        <div>
          <div class="text-xs text-slate-400">Flight Duration</div>
          <div class="text-lg font-semibold">${(stats.flight_duration_seconds / 60).toFixed(1)} min</div>
        </div>
        <div>
          <div class="text-xs text-slate-400">Data Points</div>
          <div class="text-lg font-semibold">${stats.data_points}</div>
        </div>
        <div>
          <div class="text-xs text-slate-400">Max Altitude</div>
          <div class="text-lg font-semibold">${stats.max_altitude.toFixed(1)} m</div>
        </div>
        <div>
          <div class="text-xs text-slate-400">Avg Speed</div>
          <div class="text-lg font-semibold">${stats.avg_speed.toFixed(1)} m/s</div>
        </div>
      </div>
    `;
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

function connectWebSocket() {
  setConnectionStatus("Connecting...", false);
  const ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    setConnectionStatus("Connected", true);
  };

  ws.onclose = () => {
    setConnectionStatus("Disconnected – retrying...", false);
    setTimeout(connectWebSocket, 2000);
  };

  ws.onerror = () => {
    setConnectionStatus("Error – retrying...", false);
  };

  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      const data = payload.telemetry || payload;

      updateStatusCards(data);
      updateMap(data);
      updateCharts(data);
      updateRaw(data);

      if (payload.alerts) {
        updateAlerts(payload.alerts);
      }
    } catch (err) {
      console.error("Failed to parse telemetry:", err);
    }
  };
}

window.addEventListener("DOMContentLoaded", () => {
  initMap();
  initCharts();
  connectWebSocket();

  setInterval(loadStats, 5000);
  loadStats();

  document.getElementById("alerts-button").addEventListener("click", toggleAlerts);
  document.getElementById("clear-alerts").addEventListener("click", clearAlerts);
});
