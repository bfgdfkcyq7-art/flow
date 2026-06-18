/** 首页：加载今日记录 + 保存 */

const moodPicker = setupMoodPicker("mood-picker", "mood");
const lifeAreas = setupChipGroup("life-areas");
const diaryEl = document.getElementById("diary");
const diaryCount = document.getElementById("diary-count");
const saveBtn = document.getElementById("save-btn");

diaryEl.addEventListener("input", () => {
  diaryCount.textContent = diaryEl.value.length;
});

function parseKeywords(raw) {
  if (!raw || !String(raw).trim()) return [];
  return String(raw).split(/[,，]/).map((s) => s.trim()).filter(Boolean);
}

function fillForm(record) {
  if (!record || !record.id) {
    document.getElementById("record-id").value = "";
    saveBtn.textContent = "保存记录";
    return;
  }
  document.getElementById("record-id").value = record.id;
  document.getElementById("weight").value = record.weight ?? "";
  if (record.weight != null && record.weight !== "") {
    const details = document.getElementById("metric-details");
    if (details) details.open = true;
  }
  moodPicker.setValue(record.mood);
  document.getElementById("sleep_hours").value = record.sleep_hours ?? "";
  document.getElementById("exercise_minutes").value = record.exercise_minutes ?? "";
  document.getElementById("keywords").value = (record.keywords || []).join(", ");
  diaryEl.value = record.diary || "";
  diaryCount.textContent = diaryEl.value.length;
  lifeAreas.setValues(record.life_areas || []);
  saveBtn.textContent = "更新今日记录";
}

async function loadToday() {
  try {
    const record = await api(`/api/records/today/${window.FLOW_TODAY}`);
    fillForm(record.id ? record : null);
  } catch (e) {
    console.error(e);
    showToast("加载今日记录失败", "error");
  }
}

document.getElementById("record-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = buildRecordPayload({
    date: window.FLOW_TODAY,
    weight: document.getElementById("weight").value,
    mood: moodPicker.getValue(),
    sleep_hours: document.getElementById("sleep_hours").value,
    exercise_minutes: document.getElementById("exercise_minutes").value,
    keywords: parseKeywords(document.getElementById("keywords").value),
    diary: diaryEl.value,
    life_areas: lifeAreas.getValues(),
  });

  const errors = validateRecord(payload);
  if (errors.length) {
    showToast(errors[0], "error");
    return;
  }

  setButtonLoading(saveBtn, true);

  try {
    const id = document.getElementById("record-id").value;
    if (id) {
      await api(`/api/records/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("保存成功", "success");
    } else {
      await api("/api/records", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("保存成功", "success");
      await loadToday();
    }
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setButtonLoading(saveBtn, false);
    saveBtn.textContent = document.getElementById("record-id").value
      ? "更新今日记录"
      : "保存记录";
  }
});

loadToday();
