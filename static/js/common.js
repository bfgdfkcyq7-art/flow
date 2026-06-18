/** 通用工具：Toast、API 请求、校验、空值处理 */

function showToast(message, type = "default") {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.remove("hidden", "toast-error", "toast-success");
  if (type === "error") el.classList.add("toast-error");
  if (type === "success") el.classList.add("toast-success");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => el.classList.add("hidden"), 2800);
}

function parseApiError(data) {
  if (!data || !data.detail) return "请求失败";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((e) => {
        if (typeof e === "string") return e;
        const field = e.loc && e.loc.length > 1 ? e.loc.slice(1).join(".") : "";
        const msg = e.msg || "校验失败";
        return field ? `${field}: ${msg}` : msg;
      })
      .join("；");
  }
  return "请求失败";
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    credentials: "same-origin",
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) {
    window.location.href = "/login";
    throw new Error("请先登录");
  }
  if (!res.ok) throw new Error(parseApiError(data));
  return data;
}

const MOOD_EMOJI = { 5: "😀", 4: "🙂", 3: "😐", 2: "😔", 1: "😭" };

/** 解析可选数字：空字符串 / 无效输入 → null */
function parseOptionalNumber(raw, integer = false) {
  if (raw === null || raw === undefined || String(raw).trim() === "") return null;
  const n = integer ? parseInt(raw, 10) : parseFloat(raw);
  return Number.isFinite(n) ? n : null;
}

/** 前端提交前校验，与后端规则一致 */
function validateRecord(payload) {
  const errors = [];

  if (payload.weight != null) {
    if (payload.weight <= 0) errors.push("数值须大于 0");
    else if (payload.weight > 999999) errors.push("数值不能超过 999999");
  }
  if (payload.sleep_hours != null) {
    if (payload.sleep_hours < 0 || payload.sleep_hours > 24) {
      errors.push("睡眠时长须在 0–24 小时之间");
    }
  }
  if (payload.exercise_minutes != null) {
    if (payload.exercise_minutes < 0) errors.push("运动时间不能为负数");
    else if (payload.exercise_minutes > 1440) errors.push("运动时间不能超过 1440 分钟");
  }
  if (payload.mood != null && (payload.mood < 1 || payload.mood > 5)) {
    errors.push("请选择有效的心情");
  }

  return errors;
}

function escapeHtml(text) {
  if (text == null) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function displayValue(value, suffix = "") {
  if (value === null || value === undefined || value === "") return "—";
  return `${value}${suffix}`;
}

function setButtonLoading(btn, loading, loadingText = "保存中…") {
  if (!btn) return;
  if (loading) {
    btn.dataset.originalText = btn.textContent;
    btn.textContent = loadingText;
    btn.disabled = true;
    btn.classList.add("btn-loading");
  } else {
    btn.textContent = btn.dataset.originalText || btn.textContent;
    btn.disabled = false;
    btn.classList.remove("btn-loading");
  }
}

function setupMoodPicker(containerId, hiddenInputId) {
  const container = document.getElementById(containerId);
  const hidden = document.getElementById(hiddenInputId);
  if (!container || !hidden) {
    return { setValue() {}, getValue() { return null; } };
  }
  container.querySelectorAll(".mood-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      container.querySelectorAll(".mood-btn").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      hidden.value = btn.dataset.mood;
    });
  });
  return {
    setValue(val) {
      hidden.value = val ?? "";
      container.querySelectorAll(".mood-btn").forEach((b) => {
        b.classList.toggle("selected", b.dataset.mood === String(val));
      });
    },
    getValue() {
      return hidden.value ? Number(hidden.value) : null;
    },
  };
}

function setupChipGroup(containerId) {
  const container = document.getElementById(containerId);
  const selected = new Set();
  if (!container) {
    return { getValues() { return []; }, setValues() {}, clear() {} };
  }

  container.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const area = chip.dataset.area;
      if (selected.has(area)) {
        selected.delete(area);
        chip.classList.remove("selected");
      } else {
        selected.add(area);
        chip.classList.add("selected");
      }
    });
  });

  return {
    getValues() {
      return [...selected];
    },
    setValues(arr = []) {
      selected.clear();
      container.querySelectorAll(".chip").forEach((chip) => {
        const on = arr.includes(chip.dataset.area);
        chip.classList.toggle("selected", on);
        if (on) selected.add(chip.dataset.area);
      });
    },
    clear() {
      selected.clear();
      container.querySelectorAll(".chip").forEach((c) => c.classList.remove("selected"));
    },
  };
}

function buildRecordPayload(fields) {
  return {
    date: fields.date,
    weight: parseOptionalNumber(fields.weight),
    mood: fields.mood ?? null,
    sleep_hours: parseOptionalNumber(fields.sleep_hours),
    exercise_minutes: parseOptionalNumber(fields.exercise_minutes, true),
    keywords: fields.keywords,
    diary: (fields.diary || "").trim(),
    life_areas: fields.life_areas || [],
  };
}
