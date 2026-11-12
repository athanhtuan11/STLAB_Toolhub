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
  for (const [what, label] of [["3mf", "In"], ["cad", "CAD"], ["folder", "Thư mục"]]) {
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
    toast(result.ok, result.msg || (result.dry ? `Chế độ kiểm tra: ${result.path}` : "Đã mở"));
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
if (printGrid) {
  const count = document.getElementById("print-count");
  fetch("/api/prints").then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then(data => {
    const items = data.prints || [];
    printGrid.replaceChildren();
    items.forEach(item => printGrid.append(printCard(item)));
    const apply = () => {
      const query = normalizePrintText(printSearch.value.trim());
      let visible = 0;
      printGrid.querySelectorAll(".print-card").forEach(card => {
        card.hidden = !!query && !card.dataset.search.includes(query);
        if (!card.hidden) visible++;
      });
      count.textContent = `${visible} bàn in`;
    };
    printSearch.addEventListener("input", apply);
    apply();
    if (!items.length) printGrid.textContent = "Chưa có bàn in.";
  }).catch(error => {
    printGrid.textContent = "Không tải được danh sách bàn in.";
    toast(false, String(error));
  });
}

const health = document.getElementById("health");
if (health) {
  fetch("/api/health").then(response => response.json()).then(issues => {
    if (!issues.length) return;
    health.className = "note-box";
    const label = document.createElement("strong");
    label.textContent = "Cần chú ý: ";
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
