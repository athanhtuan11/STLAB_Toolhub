// Giao trinh Cu Bong: tab cap, bang chon may, ghim/bo ghim. Khong thu vien ngoai.
(function () {
  "use strict";
  function post(path, data) {
    return fetch(path, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { j.status = r.status; return j; });
    });
  }

  document.querySelectorAll(".tab[data-level]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var lv = tab.getAttribute("data-level");
      document.querySelectorAll(".tab[data-level]").forEach(function (t) { t.classList.toggle("on", t === tab); });
      document.querySelectorAll(".panel[data-panel]").forEach(function (p) {
        p.hidden = p.getAttribute("data-panel") !== lv;
      });
    });
  });

  var sheet = document.getElementById("pick");
  var dim = document.getElementById("dim");
  var pickTitle = document.getElementById("pick-title");
  var defaultTitle = pickTitle ? pickTitle.textContent : "";
  var currentSession = null;

  function show(on) {
    if (sheet) { sheet.hidden = !on; }
    if (dim) { dim.hidden = !on; }
  }

  var pinBtn = document.querySelector("[data-pin]");
  if (pinBtn && sheet) {
    pinBtn.addEventListener("click", function () {
      currentSession = null;
      if (pickTitle) { pickTitle.textContent = defaultTitle; }
      show(true);
    });
  }

  document.querySelectorAll("[data-pin-session]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var s = parseInt(btn.getAttribute("data-pin-session"), 10);
      currentSession = s;
      if (pickTitle) {
        pickTitle.textContent = defaultTitle.replace(/\?$/, "") + " · Buổi " + s + "?";
      }
      show(true);
    });
  });

  if (sheet) {
    if (dim) { dim.addEventListener("click", function () { show(false); }); }
    var cancelBtn = sheet.querySelector("[data-cancel]");
    if (cancelBtn) { cancelBtn.addEventListener("click", function () { show(false); }); }
    var confirmBtn = sheet.querySelector("[data-confirm]");
    if (confirmBtn) {
      confirmBtn.addEventListener("click", function () {
        var msg = document.getElementById("pick-msg");
        var sel = sheet.querySelector("input[name=device]:checked");
        msg.hidden = true;
        if (!sel) { msg.textContent = "Hãy chọn một máy."; msg.hidden = false; return; }
        var payload = { device: sel.value, lesson: sheet.getAttribute("data-lesson") };
        if (currentSession !== null && !isNaN(currentSession)) {
          payload.session = currentSession;
        }
        post("/curriculum/api/pin", payload).then(function (j) {
          if (j.ok) { window.location.reload(); return; }   // 2026-11-17: o lai trang bai de thay nut buoi doi trang thai
          msg.textContent = j.status === 401 ? "Hết phiên đăng nhập, tải lại trang." : "Không ghim được (mã " + j.status + ").";
          msg.hidden = false;
        }).catch(function () { msg.textContent = "Không kết nối được máy chủ."; msg.hidden = false; });
      });
    }
  }

  document.querySelectorAll("[data-unpin]").forEach(function (b) {
    b.addEventListener("click", function () {
      post("/curriculum/api/unpin", { device: b.getAttribute("data-unpin") }).then(function (j) {
        if (j.ok) { window.location.reload(); } else { window.alert("Không bỏ ghim được (mã " + j.status + ")."); }
      });
    });
  });
})();
