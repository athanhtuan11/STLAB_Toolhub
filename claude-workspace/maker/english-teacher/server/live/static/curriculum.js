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
  function show(on) {
    if (sheet) { sheet.hidden = !on; }
    if (dim) { dim.hidden = !on; }
  }
  var pinBtn = document.querySelector("[data-pin]");
  if (pinBtn && sheet) {
    pinBtn.addEventListener("click", function () { show(true); });
    if (dim) { dim.addEventListener("click", function () { show(false); }); }
    sheet.querySelector("[data-cancel]").addEventListener("click", function () { show(false); });
    sheet.querySelector("[data-confirm]").addEventListener("click", function () {
      var msg = document.getElementById("pick-msg");
      var sel = sheet.querySelector("input[name=device]:checked");
      msg.hidden = true;
      if (!sel) { msg.textContent = "Hãy chọn một máy."; msg.hidden = false; return; }
      post("/curriculum/api/pin", { device: sel.value, lesson: sheet.getAttribute("data-lesson") }).then(function (j) {
        if (j.ok) { window.location.href = "/curriculum"; return; }
        msg.textContent = j.status === 401 ? "Hết phiên đăng nhập, tải lại trang." : "Không ghim được (mã " + j.status + ").";
        msg.hidden = false;
      }).catch(function () { msg.textContent = "Không kết nối được máy chủ."; msg.hidden = false; });
    });
  }

  document.querySelectorAll("[data-unpin]").forEach(function (b) {
    b.addEventListener("click", function () {
      post("/curriculum/api/unpin", { device: b.getAttribute("data-unpin") }).then(function (j) {
        if (j.ok) { window.location.reload(); } else { window.alert("Không bỏ ghim được (mã " + j.status + ")."); }
      });
    });
  });
})();
