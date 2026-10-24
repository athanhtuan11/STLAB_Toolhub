// Nut co data-post="/api/..." -> POST (kem header X-Studio), hien ket qua dang thong bao.
const H = { "X-Studio": "1" };

function toast(ok, msg) {
  const box = document.getElementById("log");
  const t = document.createElement("div");
  t.className = "toast" + (ok ? "" : " err");
  t.textContent = (ok ? "✓ " : "✗ ") + msg;
  box.prepend(t);
  setTimeout(() => t.remove(), ok ? 7000 : 15000);
}

async function post(url) {
  const r = await fetch(url, { method: "POST", headers: H });
  try { return await r.json(); } catch { return { ok: false, msg: `HTTP ${r.status}` }; }
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-post]");
  if (btn) {
    btn.disabled = true;
    const old = btn.textContent;
    if (btn.dataset.busy) btn.textContent = btn.dataset.busy;
    try {
      for (const url of btn.dataset.post.split(" ")) {
        const r = await post(url);
        toast(r.ok, r.msg);
      }
      if (btn.dataset.reload) setTimeout(() => location.reload(), 800);
    } catch (err) { toast(false, String(err)); }
    finally { btn.disabled = false; btn.textContent = old; refreshApps(); }
    return;
  }
  const copy = e.target.closest("button[data-copy]");
  if (copy) {
    try { await navigator.clipboard.writeText(copy.dataset.copy); toast(true, "Đã chép lệnh"); }
    catch { toast(false, "Không chép được, hãy bôi đen để chép"); }
  }
});

// Cap nhat den trang thai ung dung (phan tu co data-app).
async function refreshApps() {
  const els = document.querySelectorAll("[data-app]");
  if (!els.length) return;
  const rows = await (await fetch("/api/status")).json();
  for (const s of rows) {
    document.querySelectorAll(`[data-app="${s.id}"]`).forEach(el => {
      const dot = el.querySelector(".dot"), st = el.querySelector(".state");
      if (dot) dot.className = "dot " + (!s.installed ? "missing" : s.listening ? "ready" : s.running ? "half" : "");
      const text = !s.installed ? "Chưa cài trên máy" : s.listening ? "Sẵn sàng cho MCP"
        : s.running ? "Đang mở, cổng MCP chưa bật" : "Đang tắt";
      if (st) st.textContent = text;
      if (el.classList.contains("app")) el.title = `${s.name}: ${text}`;
    });
  }
}
refreshApps();
setInterval(refreshApps, 5000);

// Menu "Them": dong khi bam ra ngoai
document.addEventListener("click", (e) => {
  document.querySelectorAll("details.more[open]").forEach(d => { if (!d.contains(e.target)) d.open = false; });
});
