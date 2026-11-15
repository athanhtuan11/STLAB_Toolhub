// Trang Du an + huong dan: chip loc nhom, loc day theo nhom, o tich luu bo nho trinh duyet (moi truy cap trong try/catch).
(function () {
  function store(key) {
    try { return JSON.parse(localStorage.getItem(key) || "{}") || {}; } catch (e) { return {}; }
  }
  function save(key, obj) {
    try { localStorage.setItem(key, JSON.stringify(obj)); } catch (e) { /* bi chan: bo qua */ }
  }

  // --- Chip loc nhom ---
  var grid = document.querySelector("[data-active-filter]");
  if (grid) {
    var chips = document.querySelectorAll("[data-filter]");
    var apply = function (g) {
      grid.setAttribute("data-active-filter", g);
      grid.querySelectorAll("[data-group]").forEach(function (card) {
        card.hidden = !(g === "all" || card.getAttribute("data-group") === g);
      });
      chips.forEach(function (c) { c.classList.toggle("current", c.getAttribute("data-filter") === g); });
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var g = c.getAttribute("data-filter");
        apply(g);
        try { history.replaceState(null, "", g === "all" ? location.pathname : "?nhom=" + encodeURIComponent(g)); } catch (e) { /* bo qua */ }
      });
    });
    apply(grid.getAttribute("data-active-filter") || "all");
  }

  // --- Trang huong dan ---
  var guide = document.querySelector("[data-guide]");
  if (!guide) return;
  var slug = guide.getAttribute("data-guide");
  var key = "stlab-guide:" + slug;
  var state = store(key);

  // loc day theo nhom
  document.querySelectorAll("[data-wire-group]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var g = btn.getAttribute("data-wire-group");
      document.querySelectorAll("[data-wire-group]").forEach(function (b) { b.classList.toggle("current", b === btn); });
      document.querySelectorAll("[data-wire-svg]").forEach(function (el) {
        el.hidden = el.getAttribute("data-wire-svg") !== g;
      });
      document.querySelectorAll("[data-wire]").forEach(function (tr) {
        tr.hidden = !(g === "all" || tr.getAttribute("data-group") === g);
      });
    });
  });

  // o tich day + o tich buoc
  document.querySelectorAll("[data-wire] input[type=checkbox]").forEach(function (cb) {
    var id = "w" + cb.closest("[data-wire]").getAttribute("data-wire");
    cb.checked = !!state[id];
    cb.closest("tr").classList.toggle("wiring-done", cb.checked);
    cb.addEventListener("change", function () {
      state[id] = cb.checked;
      cb.closest("tr").classList.toggle("wiring-done", cb.checked);
      save(key, state);
    });
  });
  document.querySelectorAll("[data-step-done]").forEach(function (cb) {
    var id = "s" + cb.getAttribute("data-step-done");
    cb.checked = !!state[id];
    cb.addEventListener("change", function () {
      state[id] = cb.checked;
      save(key, state);
    });
  });
})();
