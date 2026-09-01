(() => {
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const panels = [...document.querySelectorAll(".tab-panel")];

  function activateTab(id, updateHash = true) {
    const target = document.getElementById(id);
    if (!target) return;

    tabs.forEach((tab) => {
      const isActive = tab.dataset.tab === id;
      tab.setAttribute("aria-selected", String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
    });
    panels.forEach((panel) => { panel.hidden = panel.id !== id; });

    target.scrollTo(0, 0);
    window.scrollTo(0, 0);
    if (updateHash) history.replaceState(null, "", `#${id}`);
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activateTab(tab.dataset.tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      tabs[next].focus();
      activateTab(tabs[next].dataset.tab);
    });
  });

  document.querySelectorAll("[data-tab-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      activateTab(link.dataset.tabLink);
    });
  });

  window.addEventListener("hashchange", () => activateTab(location.hash.slice(1) || "overview", false));

  const evidenceButtons = [...document.querySelectorAll("[data-evidence]")];
  const evidenceViews = [...document.querySelectorAll("[data-evidence-view]")];

  evidenceButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = button.dataset.evidence;
      evidenceButtons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      evidenceViews.forEach((view) => { view.hidden = view.dataset.evidenceView !== selected; });
    });
  });

  activateTab(location.hash.slice(1) || "overview", false);
})();
