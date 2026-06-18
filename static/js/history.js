/** 历史记录：列表、编辑、删除 */

const editDialog = document.getElementById("edit-dialog");
const editMood = setupMoodPicker("edit-mood-picker", "edit-mood");
const editLifeAreas = setupChipGroup("edit-life-areas");
const editSaveBtn = document.querySelector("#edit-form .btn-primary");

function renderRecord(item) {
  const mood = MOOD_EMOJI[item.mood] || "—";
  const keywords = (item.keywords || [])
    .map((k) => `<span class="tag">${escapeHtml(k)}</span>`)
    .join("");
  const areas = (item.life_areas || [])
    .map((a) => `<span class="tag">${escapeHtml(a)}</span>`)
    .join("");

  const hasMetric = item.weight != null && item.weight !== "";
  const metricLine = hasMetric
    ? `<div>数值：<strong>${displayValue(item.weight)}</strong></div>`
    : "";

  return `
    <article class="history-item" data-id="${item.id}">
      <header>
        <span class="history-date">${escapeHtml(item.date)}</span>
        <div class="history-actions">
          <button type="button" class="btn-secondary btn-edit">编辑</button>
          <button type="button" class="btn-danger btn-delete">删除</button>
        </div>
      </header>
      <div class="history-meta">
        <div>心情：<strong>${mood}</strong></div>
        <div>睡眠：<strong>${displayValue(item.sleep_hours)}</strong> h</div>
        <div>运动：<strong>${displayValue(item.exercise_minutes)}</strong> min</div>
        ${metricLine}
      </div>
      ${areas ? `<div class="history-tags">${areas}</div>` : ""}
      ${keywords ? `<div class="history-tags">${keywords}</div>` : ""}
      ${item.diary ? `<p class="history-diary">${escapeHtml(item.diary)}</p>` : ""}
    </article>
  `;
}

async function loadHistory() {
  const list = document.getElementById("history-list");
  try {
    const records = await api("/api/records");
    // 后端已 date DESC；前端再稳一层排序
    records.sort((a, b) => {
      const d = b.date.localeCompare(a.date);
      return d !== 0 ? d : (b.id || 0) - (a.id || 0);
    });
    list.innerHTML = records.length
      ? records.map(renderRecord).join("")
      : `<p class="hint">还没有记录，去首页写下第一条吧。</p>`;
  } catch (e) {
    list.innerHTML = `<p class="hint">加载失败：${escapeHtml(e.message)}</p>`;
  }
}

document.getElementById("history-list").addEventListener("click", async (e) => {
  const item = e.target.closest(".history-item");
  if (!item) return;
  const id = item.dataset.id;

  if (e.target.classList.contains("btn-delete")) {
    if (!confirm("确定删除这条记录吗？")) return;
    try {
      await api(`/api/records/${id}`, { method: "DELETE" });
      showToast("已删除", "success");
      loadHistory();
    } catch (err) {
      showToast(err.message, "error");
    }
    return;
  }

  if (e.target.classList.contains("btn-edit")) {
    const records = await api("/api/records");
    const record = records.find((r) => String(r.id) === id);
    if (!record) return;

    document.getElementById("edit-id").value = record.id;
    document.getElementById("edit-date").value = record.date || "";
    document.getElementById("edit-weight").value = record.weight ?? "";
    editMood.setValue(record.mood);
    document.getElementById("edit-sleep").value = record.sleep_hours ?? "";
    document.getElementById("edit-exercise").value = record.exercise_minutes ?? "";
    document.getElementById("edit-keywords").value = (record.keywords || []).join(", ");
    document.getElementById("edit-diary").value = record.diary || "";
    editLifeAreas.setValues(record.life_areas || []);
    editDialog.showModal();
  }
});

document.getElementById("edit-cancel").addEventListener("click", () => editDialog.close());

document.getElementById("edit-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;

  const payload = buildRecordPayload({
    date: document.getElementById("edit-date").value,
    weight: document.getElementById("edit-weight").value,
    mood: editMood.getValue(),
    sleep_hours: document.getElementById("edit-sleep").value,
    exercise_minutes: document.getElementById("edit-exercise").value,
    keywords: document.getElementById("edit-keywords").value
      .split(/[,，]/).map((s) => s.trim()).filter(Boolean),
    diary: document.getElementById("edit-diary").value,
    life_areas: editLifeAreas.getValues(),
  });

  const errors = validateRecord(payload);
  if (errors.length) {
    showToast(errors[0], "error");
    return;
  }

  setButtonLoading(editSaveBtn, true);

  try {
    await api(`/api/records/${id}`, { method: "PUT", body: JSON.stringify(payload) });
    showToast("保存成功", "success");
    editDialog.close();
    loadHistory();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setButtonLoading(editSaveBtn, false);
  }
});

loadHistory();
