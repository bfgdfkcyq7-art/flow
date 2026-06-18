/** 登录 / 注册表单 */

(function () {
  function initAuthForm() {
    const mode = window.FLOW_AUTH_MODE;
    if (!mode) {
      console.error("FLOW_AUTH_MODE 未设置");
      return;
    }

    const formId = mode === "register" ? "register-form" : "login-form";
    const form = document.getElementById(formId);
    const submitBtn = document.getElementById("submit-btn");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      if (!username) {
        showToast("请输入用户名", "error");
        return;
      }

      let payload = { username, password };

      if (mode === "register") {
        const passwordConfirm = document.getElementById("password_confirm").value;
        if (password.length < 6) {
          showToast("密码至少 6 位", "error");
          return;
        }
        if (password !== passwordConfirm) {
          showToast("两次输入的密码不一致", "error");
          return;
        }
        payload = { username, password, password_confirm: passwordConfirm };
      }

      setButtonLoading(submitBtn, true, mode === "register" ? "注册中…" : "登录中…");

      try {
        const endpoint = mode === "register" ? "/api/auth/register" : "/api/auth/login";
        await api(endpoint, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showToast(mode === "register" ? "注册成功" : "登录成功", "success");
        setTimeout(() => {
          window.location.href = "/";
        }, 400);
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        setButtonLoading(submitBtn, false);
        submitBtn.textContent = mode === "register" ? "注册" : "登录";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAuthForm);
  } else {
    initAuthForm();
  }
})();
