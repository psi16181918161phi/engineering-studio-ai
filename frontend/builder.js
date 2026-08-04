(function () {
  const host = document.getElementById("builder-content");
  if (!host) return;

  const state = window.__BUILDER_BLOB__ || {};
  const apiKey = state.apiKey || state.publicApiKey || "";

  const renderMessage = (message) => {
    host.innerHTML = `<p class="builder-panel__empty">${message}</p>`;
  };

  const init = () => {
    if (!apiKey) {
      renderMessage("Add BUILDER_API_KEY to enable Builder.io content preview.");
      return;
    }

    renderMessage("Builder.io is configured. Replace this placeholder with a model or content entry.");
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
