document.body.classList.add("has-js");

const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector("#site-nav");
if (toggle && nav) {
  toggle.hidden = false;
  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!open));
    nav.dataset.open = String(!open);
    toggle.textContent = open ? "Menu" : "Close";
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && nav.dataset.open === "true") {
      nav.dataset.open = "false";
      toggle.setAttribute("aria-expanded", "false");
      toggle.textContent = "Menu";
      toggle.focus();
    }
  });
}

const themeToggle = document.querySelector(".theme-toggle");
if (themeToggle) {
  const setTheme = theme => {
    document.documentElement.dataset.theme = theme;
    themeToggle.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    themeToggle.textContent = theme === "dark" ? "☀" : "◐";
  };
  let theme = "light";
  try { theme = localStorage.getItem("mosaic-theme") || "light"; } catch {}
  setTheme(theme === "dark" ? "dark" : "light");
  themeToggle.hidden = false;
  themeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    setTheme(next);
    try { localStorage.setItem("mosaic-theme", next); } catch {}
  });
}

const filters = document.querySelectorAll("[data-year-filter]");
const pubGroups = document.querySelectorAll("[data-publication-year]");
if (filters.length) {
  document.querySelector(".filter-bar").hidden = false;
  for (const button of filters) {
    button.addEventListener("click", () => {
      const year = button.dataset.yearFilter;
      for (const peer of filters) peer.setAttribute("aria-pressed", String(peer === button));
      let count = 0;
      for (const group of pubGroups) {
        group.hidden = year !== "all" && group.dataset.publicationYear !== year;
        if (!group.hidden) count += group.querySelectorAll(".publication").length;
      }
      document.querySelector("#publication-count").textContent = count + " publication" + (count === 1 ? "" : "s") + " shown";
    });
  }
}

function seminarDateInBuffalo(now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit"
  }).formatToParts(now);
  const value = type => parts.find(part => part.type === type).value;
  return value("year") + "-" + value("month") + "-" + value("day");
}

const programme = document.querySelector("#seminar-programme");
if (programme) {
  const today = seminarDateInBuffalo();
  const rows = Array.from(programme.querySelectorAll("[data-seminar-date]"));
  const upcomingBody = programme.querySelector("[data-upcoming-seminars]");
  const pastYears = programme.querySelector("[data-past-years]");
  const yearGroups = new Map(Array.from(pastYears.querySelectorAll("[data-seminar-year]")).map(group => [group.dataset.seminarYear, group]));
  for (const group of yearGroups.values()) group.querySelector("tbody").replaceChildren();
  upcomingBody.replaceChildren();

  const groupFor = year => {
    if (!yearGroups.has(year)) {
      const group = document.createElement("details");
      group.className = "seminar-year";
      group.dataset.seminarYear = year;
      const summary = document.createElement("summary");
      const label = document.createElement("span");
      label.className = "seminar-year-label";
      label.textContent = year;
      const count = document.createElement("span");
      count.className = "seminar-year-count";
      summary.append(label, count);
      const tableWrap = upcomingBody.closest(".seminar-table-wrap").cloneNode(true);
      const body = tableWrap.querySelector("tbody");
      body.removeAttribute("data-upcoming-seminars");
      body.setAttribute("data-past-seminars", "");
      body.replaceChildren();
      tableWrap.querySelector("caption").textContent = year + " past seminars";
      group.append(summary, tableWrap);
      group.open = true;
      yearGroups.set(year, group);
    }
    return yearGroups.get(year);
  };
  rows.sort((a, b) => a.dataset.seminarDate.localeCompare(b.dataset.seminarDate));
  for (const row of rows) {
    const isUpcoming = row.dataset.seminarDate >= today;
    if (isUpcoming) upcomingBody.append(row);
    else groupFor(row.dataset.seminarDate.slice(0, 4)).querySelector("tbody").prepend(row);
    if (row.dataset.topicKind === "unspecified") {
      row.querySelector("td:last-child .note").textContent = isUpcoming ? "To be announced" : "Topic not listed";
    }
  }
  for (const year of Array.from(yearGroups.keys()).sort().reverse()) pastYears.append(yearGroups.get(year));

  const normalize = value => value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const input = programme.querySelector("#seminar-search");
  const updateSearch = () => {
    const query = normalize(input.value.trim());
    for (const row of rows) row.hidden = !normalize(row.textContent + " " + row.dataset.seminarDate).includes(query);
    const upcomingCount = Array.from(upcomingBody.children).filter(row => !row.hidden).length;
    let pastCount = 0;
    for (const group of yearGroups.values()) {
      const count = Array.from(group.querySelector("tbody").children).filter(row => !row.hidden).length;
      group.hidden = count === 0;
      group.querySelector(".seminar-year-count").textContent = count + " seminar" + (count === 1 ? "" : "s");
      if (query && count) group.open = true;
      pastCount += count;
    }
    programme.querySelector("[data-upcoming-count]").textContent = upcomingCount;
    programme.querySelector("[data-past-count]").textContent = pastCount;
    programme.querySelector("#seminar-result-count").textContent = upcomingCount + " upcoming · " + pastCount + " past";
    upcomingBody.closest(".seminar-table-wrap").hidden = upcomingCount === 0;
    const empty = programme.querySelector("[data-upcoming-empty]");
    empty.hidden = upcomingCount > 0;
    empty.textContent = query ? "No upcoming seminars match your search." : "No upcoming seminars listed.";
    programme.querySelector("[data-seminar-no-results]").hidden = upcomingCount + pastCount > 0;
  };
  programme.querySelector(".seminar-search").hidden = false;
  input.addEventListener("input", updateSearch);
  updateSearch();
}
