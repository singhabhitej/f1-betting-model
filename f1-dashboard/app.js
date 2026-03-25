/* ============================================
   F1 PREDICTOR — Dashboard Logic & Charts
   ============================================ */

// --- THEME TOGGLE ---
(function () {
  const toggle = document.querySelector('[data-theme-toggle]');
  const root = document.documentElement;
  let theme = root.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  root.setAttribute('data-theme', theme);
  updateToggleIcon();

  toggle && toggle.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', theme);
    toggle.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
    updateToggleIcon();
    updateChartColors();
  });

  function updateToggleIcon() {
    if (!toggle) return;
    toggle.innerHTML = theme === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
})();

// --- DATA ---
const TEAM_COLORS = {
  'Mercedes': '#00D2BE',
  'Ferrari': '#DC143C',
  'McLaren': '#FF8700',
  'Red Bull': '#0600EF',
  'Haas': '#B6BABD',
  'Racing Bulls': '#6692FF',
  'Alpine': '#0090FF',
  'Audi': '#00827E',
  'Williams': '#005AFF',
  'Aston Martin': '#006F62',
  'Cadillac': '#FFD700'
};

const PREDICTIONS = [
  { pos: 1, driver: 'Russell', team: 'Mercedes', composite: 96.14, win: 50.5, podium: 90.8, top6: 93.7 },
  { pos: 2, driver: 'Antonelli', team: 'Mercedes', composite: 94.61, win: 42.0, podium: 89.7, top6: 93.7 },
  { pos: 3, driver: 'Leclerc', team: 'Ferrari', composite: 84.20, win: 3.9, podium: 56.8, top6: 92.7 },
  { pos: 4, driver: 'Hamilton', team: 'Ferrari', composite: 83.85, win: 3.6, podium: 54.0, top6: 92.8 },
  { pos: 5, driver: 'Bearman', team: 'Haas', composite: 72.35, win: 0.0, podium: 4.5, top6: 60.2 },
  { pos: 6, driver: 'Norris', team: 'McLaren', composite: 69.75, win: 0.0, podium: 2.2, top6: 59.0 },
  { pos: 7, driver: 'Verstappen', team: 'Red Bull', composite: 66.77, win: 0.0, podium: 0.7, top6: 31.8 },
  { pos: 8, driver: 'Piastri', team: 'McLaren', composite: 65.04, win: 0.0, podium: 0.5, top6: 30.9 },
  { pos: 9, driver: 'Lawson', team: 'Racing Bulls', composite: 63.74, win: 0.0, podium: 0.2, top6: 11.6 },
  { pos: 10, driver: 'Lindblad', team: 'Racing Bulls', composite: 63.21, win: 0.0, podium: 0.1, top6: 10.1 },
  { pos: 11, driver: 'Gasly', team: 'Alpine', composite: 63.00, win: 0.0, podium: 0.1, top6: 8.9 },
  { pos: 12, driver: 'Ocon', team: 'Haas', composite: 61.76, win: 0.0, podium: 0.1, top6: 6.3 },
  { pos: 13, driver: 'Hadjar', team: 'Red Bull', composite: 61.53, win: 0.0, podium: 0.0, top6: 7.1 },
  { pos: 14, driver: 'Colapinto', team: 'Alpine', composite: 57.41, win: 0.0, podium: 0.0, top6: 0.7 },
  { pos: 15, driver: 'Hulkenberg', team: 'Audi', composite: 54.90, win: 0.0, podium: 0.0, top6: 0.2 },
  { pos: 16, driver: 'Bortoleto', team: 'Audi', composite: 54.84, win: 0.0, podium: 0.0, top6: 0.1 },
  { pos: 17, driver: 'Sainz', team: 'Williams', composite: 54.46, win: 0.0, podium: 0.0, top6: 0.2 },
  { pos: 18, driver: 'Albon', team: 'Williams', composite: 52.35, win: 0.0, podium: 0.0, top6: 0.0 },
  { pos: 19, driver: 'Alonso', team: 'Aston Martin', composite: 46.40, win: 0.0, podium: 0.0, top6: 0.0 },
  { pos: 20, driver: 'Bottas', team: 'Cadillac', composite: 45.47, win: 0.0, podium: 0.0, top6: 0.0 },
  { pos: 21, driver: 'Perez', team: 'Cadillac', composite: 44.94, win: 0.0, podium: 0.0, top6: 0.0 },
  { pos: 22, driver: 'Stroll', team: 'Aston Martin', composite: 44.58, win: 0.0, podium: 0.0, top6: 0.0 },
];

const WIN_BETS = [
  { verdict: 'BACK', driver: 'Antonelli', odds: 4.75, model: 42.0, implied: 21.1, edge: 20.9, kelly: 6.63 },
  { verdict: 'FADE', driver: 'Russell', odds: 1.70, model: 50.5, implied: 58.8, edge: -8.3, kelly: 0 },
  { verdict: 'FADE', driver: 'Leclerc', odds: 12.00, model: 3.9, implied: 8.3, edge: -4.4, kelly: 0 },
  { verdict: 'FADE', driver: 'Hamilton', odds: 11.00, model: 3.6, implied: 9.1, edge: -5.5, kelly: 0 },
  { verdict: 'FADE', driver: 'Verstappen', odds: 31.00, model: 0.0, implied: 3.2, edge: -3.2, kelly: 0 },
];

const PODIUM_BETS = [
  { verdict: 'BACK', driver: 'Antonelli', odds: 1.80, model: 89.7, implied: 55.6, edge: 34.1, kelly: 19.21 },
  { verdict: 'BACK', driver: 'Leclerc', odds: 3.50, model: 56.8, implied: 28.6, edge: 28.2, kelly: 9.88 },
  { verdict: 'BACK', driver: 'Hamilton', odds: 3.00, model: 54.0, implied: 33.3, edge: 20.7, kelly: 7.75 },
  { verdict: 'BACK', driver: 'Russell', odds: 1.20, model: 90.8, implied: 83.3, edge: 7.5, kelly: 11.20 },
  { verdict: 'FADE', driver: 'Norris', odds: 12.00, model: 2.2, implied: 8.3, edge: -6.1, kelly: 0 },
  { verdict: 'FADE', driver: 'Verstappen', odds: 8.00, model: 0.7, implied: 12.5, edge: -11.8, kelly: 0 },
];

const TEAM_PACE = [
  { team: 'Mercedes', power: 95, aero: 96, traction: 93, tyreDeg: 92, reliability: 97 },
  { team: 'Ferrari', power: 90, aero: 93, traction: 89, tyreDeg: 85, reliability: 88 },
  { team: 'McLaren', power: 88, aero: 88, traction: 84, tyreDeg: 82, reliability: 55 },
  { team: 'Red Bull', power: 82, aero: 82, traction: 80, tyreDeg: 76, reliability: 72 },
  { team: 'Haas', power: 80, aero: 80, traction: 78, tyreDeg: 74, reliability: 82 },
  { team: 'Racing Bulls', power: 78, aero: 76, traction: 74, tyreDeg: 72, reliability: 78 },
  { team: 'Alpine', power: 78, aero: 77, traction: 74, tyreDeg: 70, reliability: 76 },
  { team: 'Audi', power: 74, aero: 72, traction: 70, tyreDeg: 68, reliability: 72 },
  { team: 'Williams', power: 72, aero: 70, traction: 68, tyreDeg: 66, reliability: 68 },
  { team: 'Aston Martin', power: 70, aero: 66, traction: 64, tyreDeg: 62, reliability: 62 },
  { team: 'Cadillac', power: 65, aero: 62, traction: 60, tyreDeg: 60, reliability: 58 },
];

const CIRCUIT_PROFILE = { power: 75, aero: 92, traction: 85, tyreDeg: 70 };

// --- PIT CREW DATA ---
const PIT_CREW_DATA = [
  { team: 'Ferrari', avgTime: 2.31, bestTime: 2.00, consistency: 97, xpt: 2.50, errorRate: 1.3, dhl2025: 559, dhl2024: 364, trend: 'improving' },
  { team: 'Red Bull', avgTime: 2.42, bestTime: 1.95, consistency: 88, xpt: 2.65, errorRate: 4.5, dhl2025: 362, dhl2024: 552, trend: 'declining' },
  { team: 'Racing Bulls', avgTime: 2.50, bestTime: 2.18, consistency: 82, xpt: 2.68, errorRate: 5.0, dhl2025: 353, dhl2024: 253, trend: 'improving' },
  { team: 'Mercedes', avgTime: 2.53, bestTime: 2.12, consistency: 80, xpt: 2.72, errorRate: 5.5, dhl2025: 253, dhl2024: 284, trend: 'stable' },
  { team: 'Sauber', avgTime: 2.63, bestTime: 2.13, consistency: 72, xpt: 2.81, errorRate: 7.0, dhl2025: 195, dhl2024: 144, trend: 'improving' },
  { team: 'McLaren', avgTime: 2.75, bestTime: 1.91, consistency: 65, xpt: 2.85, errorRate: 16.0, dhl2025: 410, dhl2024: 433, trend: 'stable' },
  { team: 'Alpine', avgTime: 2.85, bestTime: 2.30, consistency: 60, xpt: 2.88, errorRate: 9.0, dhl2025: 99, dhl2024: 177, trend: 'declining' },
  { team: 'Williams', avgTime: 2.80, bestTime: 2.35, consistency: 55, xpt: 3.00, errorRate: 11.0, dhl2025: 84, dhl2024: 38, trend: 'improving' },
  { team: 'Aston Martin', avgTime: 2.78, bestTime: 2.40, consistency: 52, xpt: 2.97, errorRate: 12.0, dhl2025: 56, dhl2024: 117, trend: 'declining' },
  { team: 'Haas', avgTime: 2.92, bestTime: 2.50, consistency: 50, xpt: 3.05, errorRate: 14.0, dhl2025: 53, dhl2024: 49, trend: 'stable' },
  { team: 'Cadillac', avgTime: 3.10, bestTime: 2.80, consistency: 45, xpt: 3.15, errorRate: 18.0, dhl2025: 0, dhl2024: 0, trend: 'stable' },
];

// --- FASTEST LAP DATA ---
const FL_PROPENSITY = [
  { driver: 'Russell', propensity: 90 },
  { driver: 'Antonelli', propensity: 88 },
  { driver: 'Leclerc', propensity: 75 },
  { driver: 'Hamilton', propensity: 72 },
  { driver: 'Norris', propensity: 65 },
  { driver: 'Verstappen', propensity: 55 },
  { driver: 'Bearman', propensity: 50 },
  { driver: 'Piastri', propensity: 40 },
  { driver: 'Gasly', propensity: 38 },
  { driver: 'Lawson', propensity: 35 },
];

const RACE_FL_2026 = [
  { round: 1, race: 'Australian GP', driver: 'Verstappen', team: 'Red Bull', time: '1:22.091' },
  { round: 2, race: 'Chinese GP', driver: 'Antonelli', team: 'Mercedes', time: '1:35.275' },
];

const ELO_DATA = [
  { driver: 'Russell', team: 'Mercedes', elo: 2170 },
  { driver: 'Antonelli', team: 'Mercedes', elo: 2130 },
  { driver: 'Leclerc', team: 'Ferrari', elo: 2040 },
  { driver: 'Hamilton', team: 'Ferrari', elo: 2020 },
  { driver: 'Norris', team: 'McLaren', elo: 1980 },
  { driver: 'Verstappen', team: 'Red Bull', elo: 1950 },
  { driver: 'Piastri', team: 'McLaren', elo: 1920 },
  { driver: 'Bearman', team: 'Haas', elo: 1870 },
  { driver: 'Gasly', team: 'Alpine', elo: 1820 },
  { driver: 'Lawson', team: 'Racing Bulls', elo: 1800 },
  { driver: 'Lindblad', team: 'Racing Bulls', elo: 1790 },
  { driver: 'Hadjar', team: 'Red Bull', elo: 1780 },
  { driver: 'Sainz', team: 'Williams', elo: 1760 },
  { driver: 'Hulkenberg', team: 'Audi', elo: 1750 },
  { driver: 'Albon', team: 'Williams', elo: 1740 },
  { driver: 'Ocon', team: 'Haas', elo: 1730 },
  { driver: 'Bortoleto', team: 'Audi', elo: 1720 },
  { driver: 'Colapinto', team: 'Alpine', elo: 1710 },
  { driver: 'Alonso', team: 'Aston Martin', elo: 1700 },
  { driver: 'Bottas', team: 'Cadillac', elo: 1680 },
  { driver: 'Perez', team: 'Cadillac', elo: 1670 },
  { driver: 'Stroll', team: 'Aston Martin', elo: 1650 },
];

// --- HELPERS ---
function getTheme() {
  return document.documentElement.getAttribute('data-theme') || 'dark';
}

function chartTextColor() {
  return getTheme() === 'dark' ? '#888888' : '#52525b';
}

function chartGridColor() {
  return getTheme() === 'dark' ? '#2a2a2a' : '#d4d4d8';
}

function chartBgColor() {
  return getTheme() === 'dark' ? '#1c1c1c' : '#ffffff';
}

function driverTeamColor(driver) {
  const found = PREDICTIONS.find(p => p.driver === driver) || ELO_DATA.find(e => e.driver === driver);
  return found ? TEAM_COLORS[found.team] : '#888';
}

// --- PREDICTIONS TABLE ---
function renderPredictionsTable() {
  const tbody = document.getElementById('predictionsBody');
  tbody.innerHTML = '';
  PREDICTIONS.forEach(p => {
    const tc = TEAM_COLORS[p.team] || '#888';
    const maxWin = 50.5;
    const maxPodium = 90.8;
    const maxTop6 = 93.7;
    const tr = document.createElement('tr');
    tr.style.setProperty('--row-team-color', tc);
    tr.innerHTML = `
      <td class="col-pos team-border-cell mono" style="font-weight:600">${p.pos}</td>
      <td style="font-weight:600">${p.driver}</td>
      <td class="col-team"><span class="team-dot" style="background:${tc}"></span>${p.team}</td>
      <td class="col-num mono" style="font-weight:600">${p.composite.toFixed(2)}</td>
      <td class="col-bar">
        <div class="bar-cell">
          <div class="bar-track"><div class="bar-fill" style="width:${(p.win / maxWin * 100).toFixed(1)}%; background:${tc}"></div></div>
          <span class="bar-value">${p.win.toFixed(1)}%</span>
        </div>
      </td>
      <td class="col-bar">
        <div class="bar-cell">
          <div class="bar-track"><div class="bar-fill" style="width:${(p.podium / maxPodium * 100).toFixed(1)}%; background:${tc}"></div></div>
          <span class="bar-value">${p.podium.toFixed(1)}%</span>
        </div>
      </td>
      <td class="col-bar">
        <div class="bar-cell">
          <div class="bar-track"><div class="bar-fill" style="width:${(p.top6 / maxTop6 * 100).toFixed(1)}%; background:${tc}"></div></div>
          <span class="bar-value">${p.top6.toFixed(1)}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// --- VALUE BETS ---
function renderBetCard(bet) {
  const verdictClass = bet.verdict === 'BACK' ? 'back' : bet.verdict === 'FADE' ? 'fade' : 'neutral';
  const edgeClass = bet.edge > 0 ? 'edge-positive' : 'edge-negative';
  return `
    <div class="bet-card bet-card--${verdictClass}">
      <span class="bet-driver">${bet.driver}</span>
      <span class="bet-verdict bet-verdict--${verdictClass}">${bet.verdict}</span>
      <div class="bet-details">
        <div class="bet-detail">
          <span class="bet-detail-value">${bet.odds.toFixed(2)}</span>
          <span class="bet-detail-label">Odds</span>
        </div>
        <div class="bet-detail">
          <span class="bet-detail-value">${bet.model.toFixed(1)}%</span>
          <span class="bet-detail-label">Model</span>
        </div>
        <div class="bet-detail">
          <span class="bet-detail-value">${bet.implied.toFixed(1)}%</span>
          <span class="bet-detail-label">Implied</span>
        </div>
        <div class="bet-detail">
          <span class="bet-detail-value ${edgeClass}">${bet.edge > 0 ? '+' : ''}${bet.edge.toFixed(1)}pp</span>
          <span class="bet-detail-label">Edge</span>
        </div>
        <div class="bet-detail">
          <span class="bet-detail-value">${bet.kelly.toFixed(2)}%</span>
          <span class="bet-detail-label">Kelly</span>
        </div>
      </div>
    </div>
  `;
}

function renderBets() {
  document.getElementById('winBets').innerHTML = WIN_BETS.map(renderBetCard).join('');
  document.getElementById('podiumBets').innerHTML = PODIUM_BETS.map(renderBetCard).join('');
}

// --- CHARTS ---
const chartInstances = {};

function getChartDefaults() {
  return {
    color: chartTextColor(),
    borderColor: chartGridColor(),
    font: { family: "'General Sans', sans-serif", size: 11 }
  };
}

function createRadarChart() {
  const ctx = document.getElementById('radarChart').getContext('2d');
  const top6 = TEAM_PACE.slice(0, 6);
  const labels = ['Power', 'Aero', 'Traction', 'Tyre Deg', 'Reliability'];

  if (chartInstances.radar) chartInstances.radar.destroy();

  chartInstances.radar = new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: top6.map(t => ({
        label: t.team,
        data: [t.power, t.aero, t.traction, t.tyreDeg, t.reliability],
        borderColor: TEAM_COLORS[t.team],
        backgroundColor: TEAM_COLORS[t.team] + '18',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: TEAM_COLORS[t.team],
        pointBorderColor: 'transparent',
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: false,
          min: 50,
          max: 100,
          ticks: { stepSize: 10, color: chartTextColor(), backdropColor: 'transparent', font: { size: 10, family: "'JetBrains Mono', monospace" } },
          grid: { color: chartGridColor() },
          angleLines: { color: chartGridColor() },
          pointLabels: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif", weight: 600 } }
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif" }, boxWidth: 12, padding: 16, usePointStyle: true, pointStyle: 'circle' }
        }
      }
    }
  });
}

function createCircuitChart() {
  const ctx = document.getElementById('circuitChart').getContext('2d');
  const labels = ['Power', 'Aero', 'Traction', 'Tyre Deg'];
  const data = [CIRCUIT_PROFILE.power, CIRCUIT_PROFILE.aero, CIRCUIT_PROFILE.traction, CIRCUIT_PROFILE.tyreDeg];
  const colors = ['#E10600', '#E10600CC', '#E1060099', '#E1060066'];

  if (chartInstances.circuit) chartInstances.circuit.destroy();

  chartInstances.circuit = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderRadius: 4, barThickness: 36 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: { min: 0, max: 100, ticks: { color: chartTextColor(), font: { size: 10, family: "'JetBrains Mono', monospace" } }, grid: { color: chartGridColor() }, border: { color: chartGridColor() } },
        y: { ticks: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif", weight: 600 } }, grid: { display: false }, border: { display: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => ctx.parsed.x + '/100' }
        }
      }
    }
  });
}

function createTeamCompareChart() {
  const ctx = document.getElementById('teamCompareChart').getContext('2d');
  const labels = TEAM_PACE.map(t => t.team);
  const dims = ['power', 'aero', 'traction', 'tyreDeg', 'reliability'];
  const dimLabels = ['Power', 'Aero', 'Traction', 'Tyre Deg', 'Reliability'];
  const dimColors = ['#E10600', '#00D2BE', '#FF8700', '#0090FF', '#B6BABD'];

  if (chartInstances.teamCompare) chartInstances.teamCompare.destroy();

  chartInstances.teamCompare = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: dims.map((dim, i) => ({
        label: dimLabels[i],
        data: TEAM_PACE.map(t => t[dim]),
        backgroundColor: dimColors[i] + 'CC',
        borderRadius: 2,
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: chartTextColor(), font: { size: 10, family: "'General Sans', sans-serif" }, maxRotation: 45 }, grid: { display: false }, border: { color: chartGridColor() } },
        y: { min: 50, max: 100, ticks: { color: chartTextColor(), stepSize: 10, font: { size: 10, family: "'JetBrains Mono', monospace" } }, grid: { color: chartGridColor() }, border: { color: chartGridColor() } }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif" }, boxWidth: 12, padding: 16, usePointStyle: true, pointStyle: 'rect' }
        }
      }
    }
  });
}

function createEloChart() {
  const ctx = document.getElementById('eloChart').getContext('2d');
  const sorted = [...ELO_DATA].reverse();
  const labels = sorted.map(d => d.driver);
  const data = sorted.map(d => d.elo);
  const colors = sorted.map(d => TEAM_COLORS[d.team] || '#888');

  if (chartInstances.elo) chartInstances.elo.destroy();

  chartInstances.elo = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.map(c => c + 'CC'),
        borderColor: colors,
        borderWidth: 1,
        borderRadius: 3,
        barThickness: 18,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: { min: 1600, max: 2250, ticks: { color: chartTextColor(), stepSize: 100, font: { size: 10, family: "'JetBrains Mono', monospace" } }, grid: { color: chartGridColor() }, border: { color: chartGridColor() } },
        y: { ticks: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif", weight: 500 } }, grid: { display: false }, border: { display: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => 'Elo: ' + ctx.parsed.x,
            afterLabel: (ctx) => {
              const d = sorted[ctx.dataIndex];
              return d.team;
            }
          }
        }
      }
    },
    plugins: [{
      id: 'eloLabels',
      afterDatasetsDraw(chart) {
        const { ctx: c, scales: { x } } = chart;
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
          c.fillStyle = chartTextColor();
          c.font = "600 11px 'JetBrains Mono', monospace";
          c.textAlign = 'left';
          c.textBaseline = 'middle';
          c.fillText(data[i], bar.x + 6, bar.y);
        });
      }
    }]
  });
}

function createCalibrationChart() {
  const ctx = document.getElementById('calibrationChart').getContext('2d');
  const buckets = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+'];
  const predicted = [5, 15, 25, 35, 45, 55];
  const actual = [4.2, 13.8, 22.1, 31.5, 44.0, 52.3];

  if (chartInstances.calibration) chartInstances.calibration.destroy();

  chartInstances.calibration = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: buckets,
      datasets: [
        {
          label: 'Predicted (midpoint)',
          data: predicted,
          backgroundColor: '#E10600AA',
          borderRadius: 3,
        },
        {
          label: 'Actual',
          data: actual,
          backgroundColor: '#00D2BEAA',
          borderRadius: 3,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: chartTextColor(), font: { size: 11 } }, grid: { display: false }, border: { color: chartGridColor() } },
        y: { min: 0, max: 60, ticks: { color: chartTextColor(), callback: v => v + '%', font: { size: 10, family: "'JetBrains Mono', monospace" } }, grid: { color: chartGridColor() }, border: { color: chartGridColor() } }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: chartTextColor(), font: { size: 11 }, boxWidth: 12, padding: 16, usePointStyle: true, pointStyle: 'rect' }
        }
      }
    }
  });
}

function createWeightsChart() {
  const ctx = document.getElementById('weightsChart').getContext('2d');
  const weights = [
    { label: 'Elo', value: 20, color: '#E10600' },
    { label: 'Circuit Fit', value: 20, color: '#00D2BE' },
    { label: 'Team Form', value: 15, color: '#FF8700' },
    { label: 'Grid Pos.', value: 15, color: '#0600EF' },
    { label: 'Weather', value: 10, color: '#0090FF' },
    { label: 'Reliability', value: 10, color: '#B6BABD' },
    { label: 'Momentum', value: 10, color: '#FFD700' },
  ];

  if (chartInstances.weights) chartInstances.weights.destroy();

  chartInstances.weights = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [''],
      datasets: weights.map(w => ({
        label: w.label + ' (' + w.value + '%)',
        data: [w.value],
        backgroundColor: w.color + 'CC',
        borderColor: w.color,
        borderWidth: 1,
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: { stacked: true, display: false, max: 100 },
        y: { stacked: true, display: false }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif" }, boxWidth: 12, padding: 12, usePointStyle: true, pointStyle: 'rect' }
        },
        tooltip: {
          callbacks: { label: (ctx) => ctx.dataset.label }
        }
      }
    }
  });
}

// --- PIT CREW SECTION ---
function createPitStopChart() {
  const ctx = document.getElementById('pitStopChart').getContext('2d');
  const sorted = [...PIT_CREW_DATA].sort((a, b) => a.avgTime - b.avgTime);
  const labels = sorted.map(t => t.team);
  const data = sorted.map(t => t.avgTime);
  const colors = sorted.map(t => {
    const tc = TEAM_COLORS[t.team] || TEAM_COLORS['Audi'] || '#888';
    return t.team === 'Ferrari' ? tc : tc + 'AA';
  });
  const borders = sorted.map(t => {
    const tc = TEAM_COLORS[t.team] || TEAM_COLORS['Audi'] || '#888';
    return tc;
  });

  if (chartInstances.pitStop) chartInstances.pitStop.destroy();

  chartInstances.pitStop = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: borders,
        borderWidth: sorted.map(t => t.team === 'Ferrari' ? 2 : 1),
        borderRadius: 3,
        barThickness: 22,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          min: 2.0, max: 3.3,
          ticks: { color: chartTextColor(), callback: v => v.toFixed(2) + 's', font: { size: 10, family: "'JetBrains Mono', monospace" } },
          grid: { color: chartGridColor() },
          border: { color: chartGridColor() },
        },
        y: {
          ticks: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif", weight: 500 } },
          grid: { display: false },
          border: { display: false },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const team = sorted[ctx.dataIndex];
              return `Avg: ${team.avgTime}s | Best: ${team.bestTime}s | Errors: ${team.errorRate}%`;
            }
          }
        }
      }
    },
    plugins: [{
      id: 'pitLabels',
      afterDatasetsDraw(chart) {
        const { ctx: c } = chart;
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
          c.fillStyle = chartTextColor();
          c.font = "600 11px 'JetBrains Mono', monospace";
          c.textAlign = 'left';
          c.textBaseline = 'middle';
          c.fillText(data[i].toFixed(2) + 's', bar.x + 6, bar.y);
        });
      }
    }]
  });
}

function renderConsistencyBadges() {
  const container = document.getElementById('consistencyBadges');
  const sorted = [...PIT_CREW_DATA].sort((a, b) => b.consistency - a.consistency);
  container.innerHTML = sorted.map((t, i) => {
    const tc = TEAM_COLORS[t.team] || TEAM_COLORS['Audi'] || '#888';
    const leaderClass = i === 0 ? ' consistency-badge--leader' : '';
    const trendClass = `trend-${t.trend}`;
    return `
      <div class="consistency-badge${leaderClass}" style="--badge-team-color: ${tc}">
        <span class="consistency-score">${t.consistency}</span>
        <span class="consistency-team"><span class="team-dot" style="background:${tc}"></span>${t.team}</span>
        <span class="consistency-trend ${trendClass}">${t.trend}</span>
      </div>
    `;
  }).join('');
}

function renderDHLTable() {
  const tbody = document.getElementById('dhlTableBody');
  const sorted = [...PIT_CREW_DATA].sort((a, b) => b.dhl2025 - a.dhl2025);
  tbody.innerHTML = sorted.map((t, i) => {
    const tc = TEAM_COLORS[t.team] || TEAM_COLORS['Audi'] || '#888';
    const diff = t.dhl2025 - t.dhl2024;
    let changeClass, changeText;
    if (diff > 0) { changeClass = 'dhl-change-up'; changeText = '+' + diff; }
    else if (diff < 0) { changeClass = 'dhl-change-down'; changeText = String(diff); }
    else { changeClass = 'dhl-change-same'; changeText = '—'; }
    return `<tr>
      <td class="mono" style="font-weight:600">${i + 1}</td>
      <td><span class="team-dot" style="background:${tc}"></span>${t.team}</td>
      <td class="mono">${t.dhl2025}</td>
      <td class="mono">${t.dhl2024}</td>
      <td class="mono ${changeClass}">${changeText}</td>
    </tr>`;
  }).join('');
}

// --- FASTEST LAP SECTION ---
function createFLPropensityChart() {
  const ctx = document.getElementById('flPropensityChart').getContext('2d');
  const top10 = FL_PROPENSITY.slice(0, 10);
  const labels = top10.map(d => d.driver);
  const data = top10.map(d => d.propensity);
  const colors = top10.map(d => {
    const tc = driverTeamColor(d.driver);
    return tc + 'CC';
  });
  const borders = top10.map(d => driverTeamColor(d.driver));

  if (chartInstances.flPropensity) chartInstances.flPropensity.destroy();

  chartInstances.flPropensity = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: borders,
        borderWidth: 1,
        borderRadius: 3,
        barThickness: 22,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          min: 0, max: 100,
          ticks: { color: chartTextColor(), font: { size: 10, family: "'JetBrains Mono', monospace" } },
          grid: { color: chartGridColor() },
          border: { color: chartGridColor() },
        },
        y: {
          ticks: { color: chartTextColor(), font: { size: 11, family: "'General Sans', sans-serif", weight: 500 } },
          grid: { display: false },
          border: { display: false },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => 'Propensity: ' + ctx.parsed.x + '/100'
          }
        }
      }
    },
    plugins: [{
      id: 'flLabels',
      afterDatasetsDraw(chart) {
        const { ctx: c } = chart;
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
          c.fillStyle = chartTextColor();
          c.font = "600 11px 'JetBrains Mono', monospace";
          c.textAlign = 'left';
          c.textBaseline = 'middle';
          c.fillText(data[i], bar.x + 6, bar.y);
        });
      }
    }]
  });
}

function renderFLRaceTable() {
  const tbody = document.getElementById('flRaceTableBody');
  tbody.innerHTML = RACE_FL_2026.map(r => {
    const tc = TEAM_COLORS[r.team] || '#888';
    return `<tr>
      <td class="mono" style="font-weight:600">R${r.round}</td>
      <td>${r.race}</td>
      <td style="font-weight:600">${r.driver}</td>
      <td><span class="team-dot" style="background:${tc}"></span>${r.team}</td>
      <td class="mono" style="font-weight:600">${r.time}</td>
    </tr>`;
  }).join('');
}

// --- CHART THEME UPDATE ---
function updateChartColors() {
  Object.keys(chartInstances).forEach(key => {
    if (chartInstances[key]) chartInstances[key].destroy();
  });
  createRadarChart();
  createCircuitChart();
  createTeamCompareChart();
  createPitStopChart();
  createFLPropensityChart();
  createEloChart();
  createCalibrationChart();
  createWeightsChart();
}

// --- NAV SCROLL EFFECT ---
(function () {
  const nav = document.getElementById('topNav');
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    if (scrollY > 100) {
      nav.style.borderBottomColor = 'var(--color-border)';
    }
    lastScroll = scrollY;
  }, { passive: true });
})();

// --- INIT ---
document.addEventListener('DOMContentLoaded', () => {
  renderPredictionsTable();
  renderBets();
  createRadarChart();
  createCircuitChart();
  createTeamCompareChart();
  // Pit Crew section
  createPitStopChart();
  renderConsistencyBadges();
  renderDHLTable();
  // Fastest Lap section
  createFLPropensityChart();
  renderFLRaceTable();
  // Elo + Backtest + Model
  createEloChart();
  createCalibrationChart();
  createWeightsChart();
});
