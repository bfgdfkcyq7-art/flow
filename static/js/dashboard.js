/** Dashboard：Plotly 曲线 + 人生时间轴热度（含空值与极端值防护） */

const chartLayout = {
  margin: { t: 20, r: 20, b: 40, l: 50 },
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { family: "-apple-system, BlinkMacSystemFont, sans-serif", size: 12, color: "#6B7A90" },
  xaxis: { showgrid: false, zeroline: false },
  yaxis: { gridcolor: "#E6EEF8", zeroline: false },
  hovermode: "x unified",
};

const chartConfig = { responsive: true, displayModeBar: false };

/** 各指标合理范围：Y 轴仅据此计算，避免 999kg 等异常值压扁曲线 */
const CHART_LIMITS = {
  weight: { min: 0, max: 999999, pad: 1 },
  mood: { min: 1, max: 5, pad: 0.3 },
  sleep_hours: { min: 0, max: 24, pad: 0.5 },
  exercise_minutes: { min: 0, max: 300, pad: 10 },
};

function toChartValue(val) {
  if (val === null || val === undefined || val === "") return null;
  const n = Number(val);
  return Number.isFinite(n) ? n : null;
}

/** 从有效且落在合理区间内的点计算 Y 轴范围 */
function computeYRange(values, limits) {
  const valid = values.filter((v) => v != null && Number.isFinite(v));
  const inRange = valid.filter((v) => v >= limits.min && v <= limits.max);
  const data = inRange.length ? inRange : valid;
  if (!data.length) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const pad = limits.pad ?? (max - min) * 0.1 || 1;

  return [
    Math.max(limits.min, min - pad),
    Math.min(limits.max, max + pad),
  ];
}

function showChartEmpty(elId, message) {
  const el = document.getElementById(elId);
  if (el) {
    el.innerHTML = `<p class="hint chart-empty">${message}</p>`;
  }
}

function buildLineChart(elId, dates, rawValues, yTitle, color, limits) {
  const el = document.getElementById(elId);
  if (!el) return;

  const values = rawValues.map(toChartValue);
  const hasData = values.some((v) => v != null);

  if (!hasData) {
    showChartEmpty(elId, "暂无数据");
    return;
  }

  const yRange = computeYRange(values, limits);

  const trace = {
    x: dates,
    y: values,
    type: "scatter",
    mode: "lines+markers",
    connectgaps: false,
    line: { color, width: 2.5, shape: "spline" },
    marker: { size: 6 },
    hovertemplate: "%{x}<br>" + yTitle + ": %{y}<extra></extra>",
  };

  Plotly.newPlot(
    elId,
    [trace],
    {
      ...chartLayout,
      yaxis: {
        ...chartLayout.yaxis,
        title: yTitle,
        ...(yRange ? { range: yRange, autorange: false } : { autorange: true }),
      },
    },
    chartConfig
  );
}

function renderLifeHeatmap(stats) {
  const container = document.getElementById("life-heatmap");
  if (!container) return;

  const entries = Object.entries(stats || {});
  if (!entries.length) {
    container.innerHTML = `<p class="hint">暂无数据</p>`;
    return;
  }

  const counts = entries.map(([, c]) => Number(c) || 0);
  const max = Math.max(...counts, 1);

  container.innerHTML = entries
    .map(([label, count]) => {
      const n = Number(count) || 0;
      const intensity = 0.12 + (n / max) * 0.45;
      return `
        <div class="life-bar" style="background: rgba(127,183,255,${intensity})">
          <div class="count">${n}</div>
          <div class="label">${escapeHtml(label)}</div>
        </div>
      `;
    })
    .join("");
}

async function initDashboard() {
  const [chartData, timeline] = await Promise.all([
    api("/api/dashboard/charts"),
    api("/api/dashboard/life-timeline"),
  ]);

  renderLifeHeatmap(timeline.stats || {});

  if (!chartData || !chartData.length) {
    ["chart-mood", "chart-sleep", "chart-exercise", "chart-weight"].forEach((id) => {
      showChartEmpty(id, "暂无数据，先去首页记录吧");
    });
    return;
  }

  const dates = chartData.map((r) => r.date || "");

  buildLineChart(
    "chart-mood",
    dates,
    chartData.map((r) => r.mood),
    "1-5",
    "#A9D1FF",
    CHART_LIMITS.mood
  );

  buildLineChart(
    "chart-sleep",
    dates,
    chartData.map((r) => r.sleep_hours),
    "小时",
    "#8BA4C7",
    CHART_LIMITS.sleep_hours
  );

  buildLineChart(
    "chart-exercise",
    dates,
    chartData.map((r) => r.exercise_minutes),
    "分钟",
    "#6B9FD4",
    CHART_LIMITS.exercise_minutes
  );

  buildLineChart(
    "chart-weight",
    dates,
    chartData.map((r) => r.weight),
    "数值",
    "#7FB7FF",
    CHART_LIMITS.weight
  );

  window.addEventListener("resize", () => {
    ["chart-weight", "chart-mood", "chart-sleep", "chart-exercise"].forEach((id) => {
      const el = document.getElementById(id);
      if (el && el.querySelector(".js-plotly-plot")) {
        Plotly.Plots.resize(id);
      }
    });
  });
}

initDashboard().catch((e) => {
  console.error(e);
  showToast("图表加载失败", "error");
});
