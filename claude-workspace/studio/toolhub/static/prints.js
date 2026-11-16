function normalizePrintText(value) {
  return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
}

function printDuration(minutes) {
  if (minutes === null || minutes === undefined) return "";
  return minutes >= 60 ? `${Math.floor(minutes / 60)} g ${minutes % 60} ph` : `${minutes} ph`;
}

function printCard(item) {
  const card = document.createElement("article");
  card.className = "card print-card";

  if (item.image_url) {
    const image = document.createElement("img");
    image.className = "print-image";
    image.src = item.image_url;
    image.alt = `Bản xem trước ${item.plate}`;
    image.loading = "lazy";
    card.append(image);
  } else {
    const placeholder = document.createElement("div");
    placeholder.className = "print-image print-placeholder";
    placeholder.textContent = "In 3D";
    card.append(placeholder);
  }

  const name = document.createElement("div");
  name.className = "print-name";
  name.textContent = item.project;
  card.append(name);
  if (item.title) {
    const title = document.createElement("div");
    title.className = "muted print-title";
    title.textContent = item.title;
    card.append(title);
  }
  if (item.source === "linh-kien") {
    const source = document.createElement("span");
    source.className = "badge plain print-source";
    source.textContent = "Linh kiện";
    card.append(source);
  }

  const plate = document.createElement("h2");
  plate.className = "print-plate";
  plate.textContent = item.plate;
  card.append(plate);

  const metrics = document.createElement("div");
  metrics.className = "print-metrics";
  const values = [printDuration(item.minutes)];
  if (item.grams !== null && item.grams !== undefined) {
    values.push(`${Number(item.grams).toFixed(1).replace(".", ",")} g`);
  }
  metrics.textContent = values.filter(Boolean).join(" · ");
  card.append(metrics);

  const actions = document.createElement("div");
  actions.className = "actions print-actions";
  for (const [what, label] of [["3mf", "In"], ["cad", "CAD"], ["folder", "Thư mức"]]) {
    const button = document.createElement("button");
    button.textContent = label;
    if (what === "3mf") button.className = "primary";
    button.dataset.printOpen = "";
    button.dataset.project = item.project;
    button.dataset.plate = item.plate;
    button.dataset.what = what;
    if (what === "cad" && !item.cad.length) {
      button.disabled = true;
      button.title = "Chưa có file CAD";
    }
    actions.append(button);
  }
  card.append(actions);
  card.dataset.search = normalizePrintText([item.project, item.title, item.plate,
    item.source === "linh-kien" ? "linh kien sg90" : ""].join(" "));
  return card;
}

function projectCard(project) {
  const article = document.createElement("article");
  article.className = "card print-card print-project";
  article.role = "button";
  article.tabIndex = 0;

  if (project.image_url) {
    const image = document.createElement("img");
    image.className = "print-image";
    image.src = project.image_url;
    image.alt = `Bản xem trước ${project.project}`;
    image.loading = "lazy";
    article.append(image);
  } else {
    const placeholder = document.createElement("div");
    placeholder.className = "print-image print-placeholder";
    placeholder.textContent = "In 3D";
    article.append(placeholder);
  }

  const name = document.createElement("div");
  name.className = "print-name";
  name.textContent = project.project;
  article.append(name);
  if (project.title) {
    const title = document.createElement("div");
    title.className = "muted print-title";
    title.textContent = project.title;
    article.append(title);
  }
  if (project.source === "linh-kien") {
    const badge = document.createElement("span");
    badge.className = "badge plain print-source";
    badge.textContent = "Linh kiện";
    article.append(badge);
  }

  const metrics = document.createElement("div");
  metrics.className = "print-metrics";
  const values = [`${project.plate_count} bàn in`];
  if (project.minutes !== null && project.minutes !== undefined) {
    values.push(printDuration(project.minutes));
  }
  if (project.grams !== null && project.grams !== undefined) {
    values.push(`${Number(project.grams).toFixed(1).replace(".", ",")} g`);
  }
  metrics.textContent = values.join(" · ");
  article.append(metrics);

  article.dataset.search = normalizePrintText([project.project, project.title,
    ...(project.plates || []).map(p => p.plate)].join(" "));
  article.dataset.source = project.source;
  article.dataset.folder = project.folder;

  const open = () => { location.hash = "#p=" + encodeURIComponent(project.source + ":" + project.folder); };
  article.addEventListener("click", open);
  article.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      open();
    }
  });
  return article;
}

async function openPrint(button) {
  button.disabled = true;
  try {
    const response = await fetch("/api/prints/open", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Studio": "1" },
      body: JSON.stringify({
        project: button.dataset.project,
        plate: button.dataset.plate,
        what: button.dataset.what
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.msg || `HTTP ${response.status}`);
    toast(result.ok, result.msg || (result.dry ? `Chế độ kiên tra: ${result.path}` : "Đã mò"));
  } catch (error) {
    toast(false, String(error));
  } finally {
    button.disabled = false;
  }
}

document.addEventListener("click", event => {
  const button = event.target.closest("button[data-print-open]");
  if (button) openPrint(button);
});

const printSearch = document.getElementById("print-search");
const printGrid = document.getElementById("print-grid");
const printCount = document.getElementById("print-count");
let projects = [];
let mode = "projects";
let backBar = null;

function showProjects() {
  mode = "projects";
  if (backBar) { backBar.remove(); backBar = null; }
  delete printGrid.dataset.view;
  printGrid.replaceChildren();
  projects.forEach(project => printGrid.append(projectCard(project)));
  applySearch();
}

function showProject(project) {
  mode = "project";
  if (backBar) backBar.remove();
  printGrid.dataset.view = "project";
  backBar = document.createElement("div");
  backBar.className = "print-back-bar";
  const back = document.createElement("button");
  back.className = "print-back";
  back.textContent = "← Tất cả dự án";
  back.addEventListener("click", () => { location.hash = ""; });
  const title = document.createElement("h2");
  title.className = "print-project-title";
  title.textContent = project.title || project.project;
  backBar.append(back, title);
  printGrid.before(backBar);
  printGrid.replaceChildren();
  (project.plates || []).forEach(plate => printGrid.append(printCard(plate)));
  applySearch();
}

function onHashChange() {
  const hash = location.hash;
  if (hash.startsWith("#p=")) {
    const key = decodeURIComponent(hash.slice(3));
    const sep = key.indexOf(":");
    const source = key.slice(0, sep);
    const folder = key.slice(sep + 1);
    const project = projects.find(p => p.source === source && p.folder === folder);
    if (project) {
      showProject(project);
      return;
    }
  }
  showProjects();
}

function applySearch() {
  const query = normalizePrintText(printSearch.value.trim());
  let visible = 0;
  printGrid.querySelectorAll(".print-card").forEach(card => {
    card.hidden = !!query && !card.dataset.search.includes(query);
    if (!card.hidden) visible++;
  });
  printCount.textContent = mode === "project"
    ? `${visible} bàn in`
    : `${visible} dự án`;
}

if (printGrid) {
  fetch("/api/prints").then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then(data => {
    projects = data.projects || [];
    const items = data.prints || [];
    window.addEventListener("hashchange", onHashChange);
    onHashChange();
    printSearch.addEventListener("input", applySearch);
    applySearch();
    if (!projects.length) printGrid.textContent = "Chưa có dự án.";
  }).catch(error => {
    printGrid.textContent = "Không tải được danh sách dự án.";
    toast(false, String(error));
  });
}

const health = document.getElementById("health");
if (health) {
  fetch("/api/health").then(response => response.json()).then(issues => {
    if (!issues.length) return;
    health.className = "note-box";
    const label = document.createElement("strong");
    label.textContent = "Cán chú ý: ";
    health.append(label);
    issues.forEach((issue, index) => {
      const link = document.createElement("a");
      link.href = issue.url;
      link.textContent = issue.text;
      health.append(link);
      if (index < issues.length - 1) health.append(" · ");
    });
  }).catch(() => {});
}
