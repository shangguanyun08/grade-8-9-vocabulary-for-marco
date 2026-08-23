"use strict";

const STORAGE_KEY = "marco-grade-8-9-vocabulary-checked-v1";
const numberFormat = new Intl.NumberFormat("en-US");

const elements = {
  bandFilters: document.querySelector("#band-filters"),
  checkedCount: document.querySelector("#checked-count"),
  clearFilters: document.querySelector("#clear-filters"),
  clearSearch: document.querySelector("#clear-search"),
  completion: document.querySelector("#completion"),
  emptyState: document.querySelector("#empty-state"),
  footerTotal: document.querySelector("#footer-total"),
  heroTotal: document.querySelector("#hero-total"),
  listHeading: document.querySelector("#word-list-heading"),
  listTotal: document.querySelector("#list-total"),
  progressBar: document.querySelector("#progress-bar"),
  progressTotal: document.querySelector("#progress-total"),
  rows: document.querySelector("#word-rows"),
  saveState: document.querySelector("#save-state"),
  search: document.querySelector("#search"),
  sortControls: document.querySelector("#sort-controls"),
  source: document.querySelector("#source-filter"),
  statusFilters: document.querySelector("#status-filters"),
  tableShell: document.querySelector("#table-shell"),
  visibleCount: document.querySelector("#visible-count"),
};

const state = {
  band: "all",
  checked: loadChecked(),
  query: "",
  sort: "rank-asc",
  source: "all",
  status: "all",
  words: [],
};

function loadChecked() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return new Set(Array.isArray(value) ? value : []);
  } catch {
    return new Set();
  }
}

function saveChecked() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.checked]));
    elements.saveState.className = "save-state save-state-ready";
    elements.saveState.lastChild.textContent = "Saved in this browser";
  } catch {
    elements.saveState.className = "save-state save-state-error";
    elements.saveState.lastChild.textContent = "Browser saving unavailable";
  }
}

function setActiveButton(group, attribute, value) {
  group.querySelectorAll(`button[${attribute}]`).forEach((button) => {
    const active = button.getAttribute(attribute) === value;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function searchableText(word) {
  return [
    word.word,
    word.meaning,
    ...(word.aliases || []),
    ...(word.sources || []),
    ...(word.details || []),
    word.studyBand,
  ].join(" ").toLocaleLowerCase();
}

function getVisibleWords() {
  const query = state.query.trim().toLocaleLowerCase();
  const filtered = state.words.filter((word) => {
    if (state.source !== "all" && !word.sources.includes(state.source)) return false;
    if (state.band !== "all" && word.studyBand !== state.band) return false;
    const checked = state.checked.has(word.id);
    if (state.status === "checked" && !checked) return false;
    if (state.status === "unchecked" && checked) return false;
    return !query || searchableText(word).includes(query);
  });

  return filtered.sort((a, b) => {
    if (state.sort === "rank-asc") return a.rank - b.rank;
    if (state.sort === "rank-desc") return b.rank - a.rank;
    const alphabetical = a.word.localeCompare(b.word, "en", { sensitivity: "base" });
    return state.sort === "az" ? alphabetical : -alphabetical;
  });
}

function createCheckbox(word, checked) {
  const cell = document.createElement("td");
  cell.className = "check-cell";
  const label = document.createElement("label");
  const input = document.createElement("input");
  input.type = "checkbox";
  input.checked = checked;
  input.setAttribute("aria-label", `Mark ${word.word} as ${checked ? "not checked" : "checked"}`);
  input.addEventListener("change", () => {
    if (input.checked) state.checked.add(word.id);
    else state.checked.delete(word.id);
    saveChecked();
    updateProgress();
    if (state.status !== "all") render();
    else input.closest("tr")?.classList.toggle("checked-row", input.checked);
  });
  const mark = document.createElement("span");
  mark.setAttribute("aria-hidden", "true");
  mark.textContent = "✓";
  label.append(input, mark);
  cell.append(label);
  return cell;
}

function sourceClass(source) {
  if (source === "ISEE Test Samples") return "source-tested";
  if (source === "Piqosity Middle") return "source-middle";
  if (source === "Piqosity Upper") return "source-upper";
  if (source === "Zozeck Grade 8–9") return "source-zozeck";
  return "source-practice";
}

function bandClass(band) {
  return band.toLocaleLowerCase().replaceAll(" ", "-");
}

function createRow(word) {
  const checked = state.checked.has(word.id);
  const row = document.createElement("tr");
  row.classList.toggle("checked-row", checked);
  row.append(createCheckbox(word, checked));

  const rank = document.createElement("td");
  rank.className = "rank-cell";
  const rankBadge = document.createElement("span");
  rankBadge.textContent = numberFormat.format(word.rank);
  rank.append(rankBadge);

  const term = document.createElement("th");
  term.scope = "row";
  term.className = "word-cell";
  const headword = document.createElement("span");
  headword.textContent = word.word;
  term.append(headword);
  if (word.aliases?.length) {
    const aliases = document.createElement("small");
    aliases.textContent = `Forms: ${word.aliases.join(", ")}`;
    term.append(aliases);
  }

  const meaning = document.createElement("td");
  meaning.className = "meaning-cell";
  meaning.textContent = word.meaning;

  const sources = document.createElement("td");
  sources.className = "sources-cell";
  word.sources.forEach((source) => {
    const badge = document.createElement("span");
    badge.className = sourceClass(source);
    badge.textContent = source;
    sources.append(badge);
  });

  const band = document.createElement("td");
  band.className = "band-cell";
  const bandBadge = document.createElement("span");
  bandBadge.className = bandClass(word.studyBand);
  bandBadge.textContent = word.studyBand;
  band.append(bandBadge);

  row.append(rank, term, meaning, sources, band);
  return row;
}

function updateProgress() {
  const count = state.checked.size;
  const completion = state.words.length ? Math.round((count / state.words.length) * 100) : 0;
  elements.checkedCount.textContent = numberFormat.format(count);
  elements.completion.textContent = `${completion}%`;
  elements.progressBar.style.width = `${completion}%`;
}

function render() {
  const visible = getVisibleWords();
  const fragment = document.createDocumentFragment();
  visible.forEach((word) => fragment.append(createRow(word)));
  elements.rows.replaceChildren(fragment);
  elements.visibleCount.textContent = numberFormat.format(visible.length);
  elements.emptyState.hidden = visible.length !== 0;
  elements.rows.closest("table").hidden = visible.length === 0;
  elements.tableShell.setAttribute("aria-busy", "false");
}

function clearFilters() {
  state.query = "";
  state.source = "all";
  state.status = "all";
  state.band = "all";
  elements.search.value = "";
  elements.clearSearch.hidden = true;
  elements.source.value = "all";
  setActiveButton(elements.statusFilters, "data-status", "all");
  setActiveButton(elements.bandFilters, "data-band", "all");
  render();
}

elements.search.addEventListener("input", (event) => {
  state.query = event.target.value;
  elements.clearSearch.hidden = !state.query;
  render();
});

elements.clearSearch.addEventListener("click", () => {
  state.query = "";
  elements.search.value = "";
  elements.clearSearch.hidden = true;
  elements.search.focus();
  render();
});

elements.source.addEventListener("change", (event) => {
  state.source = event.target.value;
  render();
});

elements.statusFilters.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-status]");
  if (!button) return;
  state.status = button.dataset.status;
  setActiveButton(elements.statusFilters, "data-status", state.status);
  render();
});

elements.bandFilters.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-band]");
  if (!button) return;
  state.band = button.dataset.band;
  setActiveButton(elements.bandFilters, "data-band", state.band);
  render();
});

elements.sortControls.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-sort]");
  if (!button) return;
  state.sort = button.dataset.sort;
  setActiveButton(elements.sortControls, "data-sort", state.sort);
  render();
});

elements.clearFilters.addEventListener("click", clearFilters);

fetch("words.json?v=3")
  .then((response) => {
    if (!response.ok) throw new Error("The vocabulary data could not be loaded.");
    return response.json();
  })
  .then((words) => {
    state.words = words;
    const validIds = new Set(words.map((word) => word.id));
    state.checked = new Set([...state.checked].filter((id) => validIds.has(id)));
    const sources = [...new Set(words.flatMap((word) => word.sources))];
    sources.forEach((source) => {
      const option = document.createElement("option");
      option.value = source;
      option.textContent = source;
      elements.source.append(option);
    });
    const total = numberFormat.format(words.length);
    elements.listTotal.textContent = total;
    elements.progressTotal.textContent = total;
    elements.heroTotal.textContent = total;
    elements.footerTotal.textContent = total;
    elements.listHeading.textContent = `${total} unique words & phrases`;
    updateProgress();
    render();
  })
  .catch((error) => {
    elements.tableShell.setAttribute("aria-busy", "false");
    elements.rows.innerHTML = `<tr><td class="loading-cell error-cell" colspan="6">${error.message}</td></tr>`;
  });
