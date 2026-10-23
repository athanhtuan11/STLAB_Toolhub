// Trang Sua anh: chon anh + kieu mau -> xem goc / da ap; do manh xem truc tiep bang opacity
// (anh "over" chong len "under" = cung phep tron ma develop.py dung khi xuat that).
const $ = (id) => document.getElementById(id);
const KIND = { base: "Preset STLab", lut: "LUT phim", xmp: "Preset Lightroom (XMP)" };
const S = { src: "", photos: [], looks: [], photo: null, look: "base", cache: {}, seq: 0, prefetchFor: "" };

async function api(url, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(url, opt);
  try { return await r.json(); } catch { return { ok: false, msg: `HTTP ${r.status}` }; }
}
const fileUrl = (rel) => `/anh/file?src=${encodeURIComponent(S.src)}&p=${encodeURIComponent(rel)}`;
const local = () => $("local").checked;
const strength = () => Number($("strength").value) / 100;
const key = (photo, look, loc) => `${photo}|${look}|${loc ? 1 : 0}`;

async function openSrc(src) {
  $("srcInfo").textContent = "Đang đọc thư mục và tạo ảnh nhỏ…";
  const r = await api("/api/anh/photos", { src });
  if (!r.ok) { $("srcInfo").textContent = ""; toast(false, r.msg); return; }
  Object.assign(S, { src, photos: r.photos, cache: {} });
  $("srcInfo").textContent = `${r.photos.length} ảnh (${r.origin === "cull/dat" ? "nhóm đạt đã duyệt: cull/dat" : "cả thư mục nguồn"}) · kết quả ghi vào ${r.edit}`;
  $("applyInfo").textContent = `Sẽ xuất ${r.photos.length} ảnh, cạnh dài 2048 px, sRGB, không EXIF/GPS.`;
  const th = $("thumbs");
  th.innerHTML = "";
  for (const p of r.photos) {
    const b = document.createElement("button");
    b.type = "button"; b.dataset.photo = p; b.title = p;
    b.innerHTML = `<img loading="lazy" src="${fileUrl(`lab/thumbs/${p}.jpg`)}" alt="${p}">`;
    th.append(b);
  }
  $("lab").hidden = false;
  history.replaceState(null, "", `?src=${encodeURIComponent(src)}`);
  selectPhoto(r.photos[0]);
  pollJob();
}

function renderLooks() {
  const box = $("looks");
  box.innerHTML = "";
  let group = "";
  for (const lk of S.looks) {
    if (lk.kind !== group) {
      group = lk.kind;
      const h = document.createElement("div"); h.className = "looks-group"; h.textContent = KIND[group] || group;
      box.append(h);
    }
    const l = document.createElement("label");
    l.className = "look"; l.dataset.look = lk.id;
    l.innerHTML = `<input type="radio" name="look" value="${lk.id}"${lk.id === S.look ? " checked" : ""}><span>${lk.label}</span><i class="ready" title="Đã có bản xem trước"></i>`;
    box.append(l);
  }
}

function markReady() {
  document.querySelectorAll(".look").forEach((el) => {
    el.classList.toggle("is-ready", !!S.cache[key(S.photo, el.dataset.look, local())]);
    el.classList.toggle("on", el.dataset.look === S.look);
  });
}

async function getPreview(photo, look, loc) {
  const k = key(photo, look, loc);
  if (!S.cache[k]) {
    const r = await api("/api/anh/preview", { src: S.src, photo, look, local: loc });
    if (!r.ok) throw new Error(r.msg);
    S.cache[k] = r;
  }
  return S.cache[k];
}

async function show() {
  const my = ++S.seq;
  const lk = S.looks.find((x) => x.id === S.look);
  $("afterCap").textContent = `Đã áp: ${lk ? lk.label : S.look}${local() ? " + nâng sáng người" : ""}`;
  $("busy").hidden = !!S.cache[key(S.photo, S.look, local())];
  try {
    const r = await getPreview(S.photo, S.look, local());
    if (my !== S.seq) return;
    $("orig").src = fileUrl(r.orig); $("origLink").href = fileUrl(r.orig);
    $("under").src = fileUrl(r.under); $("over").src = fileUrl(r.over); $("afterLink").href = fileUrl(r.over);
    applyStrength();
    markReady();
    prefetch(S.photo, local());
  } catch (e) { if (my === S.seq) toast(false, String(e.message || e)); }
  finally { if (my === S.seq) $("busy").hidden = true; }
}

// Tao truoc cac kieu con lai cua anh dang xem (lan luot) de bam la thay ngay
async function prefetch(photo, loc) {
  const tag = `${photo}|${loc}`;
  if (S.prefetchFor === tag) return;
  S.prefetchFor = tag;
  for (const lk of S.looks) {
    if (S.prefetchFor !== tag) return;
    try { await getPreview(photo, lk.id, loc); } catch { /* bao loi khi Tuan bam vao kieu do */ }
    if (photo === S.photo) markReady();
  }
}

function applyStrength() {
  $("strengthVal").textContent = `${Math.round(strength() * 100)}%`;
  $("over").style.opacity = strength();
}

function selectPhoto(p) {
  if (!p) return;
  S.photo = p;
  document.querySelectorAll("#thumbs button").forEach((b) => b.classList.toggle("on", b.dataset.photo === p));
  // Chi cuon dai anh nho (scrollIntoView cuon ca trang -> mat cho dang so sanh)
  const b = document.querySelector(`#thumbs button[data-photo="${p}"]`), box = $("thumbs");
  if (b && (b.offsetTop < box.scrollTop || b.offsetTop + b.offsetHeight > box.scrollTop + box.clientHeight)) {
    box.scrollTop = b.offsetTop - box.clientHeight / 2;
  }
  $("photoName").textContent = p;
  $("photoCount").textContent = `${S.photos.indexOf(p) + 1}/${S.photos.length}`;
  show();
}

function selectLook(id) {
  S.look = id;
  const input = document.querySelector(`input[name=look][value="${id}"]`);
  if (input) input.checked = true;
  markReady();
  show();
}

// ---------- Ap dung cho tat ca ----------
let pollTimer = null;
async function pollJob() {
  clearTimeout(pollTimer);
  const j = await api("/api/anh/job");
  if (j.state === "none" || (j.src && j.src !== S.src)) return;
  const pct = j.n ? Math.round((100 * j.i) / j.n) : 0;
  $("progress").hidden = false;
  $("progress").firstElementChild.style.width = `${j.state === "running" ? pct : 100}%`;
  $("applyBtn").disabled = j.state === "running";
  if (j.state === "running") {
    $("jobInfo").textContent = `Đang xuất ${j.i}/${j.n || "?"} ảnh · ${j.secs} s → ${j.out_name}`;
    pollTimer = setTimeout(pollJob, 1500);
    return;
  }
  $("jobInfo").textContent = j.state === "done" ? `Xong → ${j.out} · ${j.qa}` : "Lỗi khi áp dụng";
  const res = $("jobResult");
  res.innerHTML = "";
  if (j.state === "error") { res.textContent = j.msg || ""; res.className = "err-text"; return; }
  res.className = "";
  for (const s of j.sheets || []) {
    const a = document.createElement("a");
    a.href = fileUrl(`${j.out_name}/${s}`); a.target = "_blank"; a.className = "sheet";
    a.innerHTML = `<img src="${fileUrl(`${j.out_name}/${s}`)}" alt="${s}"><span>${s}</span>`;
    res.append(a);
  }
  if ((j.warn || []).length) {
    const w = document.createElement("div"); w.className = "err-text";
    w.textContent = "Cảnh báo QA: " + j.warn.join(" · ");
    res.append(w);
  }
  const b = document.createElement("button");
  b.type = "button"; b.textContent = "Mở thư mục kết quả";
  b.onclick = async () => { const r = await api("/api/anh/open-output", {}); toast(r.ok, r.msg); };
  res.append(b);
}

$("applyBtn").addEventListener("click", async () => {
  const lk = S.looks.find((x) => x.id === S.look);
  const msg = `Áp "${lk.label}"${local() ? " + nâng sáng người" : ""}, độ mạnh ${Math.round(strength() * 100)}% cho ${S.photos.length} ảnh?`;
  if (!confirm(msg)) return;
  const r = await api("/api/anh/apply", { src: S.src, look: S.look, strength: strength(), local: local() });
  toast(r.ok, r.msg);
  if (r.ok) { $("jobResult").innerHTML = ""; pollJob(); }
});

// ---------- Su kien ----------
$("srcForm").addEventListener("submit", (e) => { e.preventDefault(); openSrc($("src").value.trim()); });
$("thumbs").addEventListener("click", (e) => { const b = e.target.closest("button[data-photo]"); if (b) selectPhoto(b.dataset.photo); });
$("looks").addEventListener("change", (e) => { if (e.target.name === "look") selectLook(e.target.value); });
$("local").addEventListener("change", () => { markReady(); show(); });
$("strength").addEventListener("input", applyStrength);
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input[type=text], input:not([type]), textarea") || $("lab").hidden) return;
  const ids = S.looks.map((x) => x.id), i = ids.indexOf(S.look), j = S.photos.indexOf(S.photo);
  if (e.key === "ArrowDown") { e.preventDefault(); selectLook(ids[Math.min(i + 1, ids.length - 1)]); }
  else if (e.key === "ArrowUp") { e.preventDefault(); selectLook(ids[Math.max(i - 1, 0)]); }
  else if (e.key === "ArrowRight") { e.preventDefault(); selectPhoto(S.photos[Math.min(j + 1, S.photos.length - 1)]); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); selectPhoto(S.photos[Math.max(j - 1, 0)]); }
  else if (e.code === "Space" && !e.repeat) {
    // Giu Space: o ben phai tam hien anh goc (cung vi tri -> de thay khac biet)
    e.preventDefault();
    S.peek = $("over").src;
    $("over").src = $("orig").src; $("over").style.opacity = 1; $("afterLink").classList.add("peek");
  }
});
document.addEventListener("keyup", (e) => {
  if (e.code === "Space" && S.peek) { $("over").src = S.peek; S.peek = null; $("afterLink").classList.remove("peek"); applyStrength(); }
});

(async () => {
  const r = await api("/api/anh/looks");
  if (!r.ok) { toast(false, r.msg); return; }
  S.looks = r.looks;
  renderLooks();
  const src = $("src").value.trim();
  if (src) openSrc(src);
})();
