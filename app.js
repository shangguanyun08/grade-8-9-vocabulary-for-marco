"use strict";

const STORAGE_KEY = "marco-grade-8-9-vocabulary-checked-v1";
const numberFormat = new Intl.NumberFormat("en-US");

const elements = {
  chapter: document.querySelector("#chapter-filter"),
  checkedCount: document.querySelector("#checked-count"),
  clearFilters: document.querySelector("#clear-filters"),
  clearSearch: document.querySelector("#clear-search"),
  completion: document.querySelector("#completion"),
  emptyState: document.querySelector("#empty-state"),
  listTotal: document.querySelector("#list-total"),
  progressBar: document.querySelector("#progress-bar"),
  progressTotal: document.querySelector("#progress-total"),
  rows: document.querySelector("#word-rows"),
  saveState: document.querySelector("#save-state"),
  search: document.querySelector("#search"),
  sortControls: document.querySelector("#sort-controls"),
  statusFilters: document.querySelector("#status-filters"),
  tableShell: document.querySelector("#table-shell"),
  visibleCount: document.querySelector("#visible-count"),
};

const state = {
  chapter: "all",
  checked: loadChecked(),
  query: "",
  sort: "rank-asc",
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

function getGradeLevel(word) {
  const grade8Limit = Math.ceil(state.words.length / 2);
  return word.rank <= grade8Limit ? "Grade 8" : "Grade 9";
}

function getVisibleWords() {
  const query = state.query.trim().toLocaleLowerCase();
  const filtered = state.words.filter((word) => {
    if (state.chapter !== "all" && !word.sources.includes(state.chapter)) return false;
    const checked = state.checked.has(word.id);
    if (state.status === "checked" && !checked) return false;
    if (state.status === "unchecked" && checked) return false;
    if (!query) return true;
    return `${word.word} ${word.meaning} ${word.sources.join(" ")} ${getGradeLevel(word)}`
      .toLocaleLowerCase()
      .includes(query);
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
  term.textContent = word.word;

  const meaning = document.createElement("td");
  meaning.className = "meaning-cell";
  meaning.textContent = word.meaning;

  const chapters = document.createElement("td");
  chapters.className = "chapters-cell";
  word.sources.forEach((source) => {
    const badge = document.createElement("span");
    badge.textContent = source.replace("Chapter ", "Ch. ");
    chapters.append(badge);
  });

  const gradeLevel = getGradeLevel(word);
  const grade = document.createElement("td");
  grade.className = "grade-cell";
  const gradeBadge = document.createElement("span");
  gradeBadge.className = gradeLevel === "Grade 8" ? "grade-eight" : "grade-nine";
  gradeBadge.textContent = gradeLevel;
  grade.append(gradeBadge);

  row.append(rank, term, meaning, chapters, grade);
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
  state.chapter = "all";
  state.status = "all";
  elements.search.value = "";
  elements.clearSearch.hidden = true;
  elements.chapter.value = "all";
  setActiveButton(elements.statusFilters, "data-status", "all");
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

elements.chapter.addEventListener("change", (event) => {
  state.chapter = event.target.value;
  render();
});

elements.statusFilters.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-status]");
  if (!button) return;
  state.status = button.dataset.status;
  setActiveButton(elements.statusFilters, "data-status", state.status);
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

fetch("words.json")
  .then((response) => {
    if (!response.ok) throw new Error("The vocabulary data could not be loaded.");
    return response.json();
  })
  .then((words) => {
    state.words = words;
    const validIds = new Set(words.map((word) => word.id));
    state.checked = new Set([...state.checked].filter((id) => validIds.has(id)));
    for (let chapter = 1; chapter <= 25; chapter += 1) {
      const option = document.createElement("option");
      option.value = `Chapter ${chapter}`;
      option.textContent = `Chapter ${chapter}`;
      elements.chapter.append(option);
    }
    const total = numberFormat.format(words.length);
    elements.listTotal.textContent = total;
    elements.progressTotal.textContent = total;
    updateProgress();
    render();
  })
  .catch((error) => {
    elements.tableShell.setAttribute("aria-busy", "false");
    elements.rows.innerHTML = `<tr><td class="loading-cell error-cell" colspan="6">${error.message}</td></tr>`;
  });

