/**
 * WHAT: Client-side wiring for the artifact-download affordances added to
 * the dashboard (per-stage "Download output" link, run-level "Download
 * all (.zip)" link).
 * WHY: Kept as its own file (not merged into app.js) so this addition
 * stays strictly additive — teammates independently extending app.js's
 * stage-rendering logic never need to touch or merge-conflict with this
 * file, and vice versa.
 * HOW: app.js owns all run/stage state privately inside its own IIFE, so
 * this file never reads it directly — it instead observes the DOM
 * (data-state attribute changes on stage status pills, run-meta-id text)
 * via a single MutationObserver and derives download URLs purely from
 * already-rendered markup. No fetch/XHR here: downloads are plain <a
 * href> + download attribute, letting the browser handle the
 * Content-Disposition response from engineering_studio.api.downloads.
 */

(() => {
  "use strict";

  function apiUrl(path) {
    return path; // same-origin, mirrors app.js's own apiUrl() helper
  }

  function currentRunId() {
    const el = document.getElementById("run-meta-id");
    return el ? el.textContent.trim() : "";
  }

  function updateDownloadAllLink() {
    const link = document.getElementById("download-all-link");
    if (!link) return;
    const runId = currentRunId();
    const anyDone = Array.from(document.querySelectorAll(".stage-card__status")).some(
      (el) => el.dataset.state === "done"
    );
    if (!runId || !anyDone) {
      link.hidden = true;
      return;
    }
    link.href = apiUrl(`/api/runs/${encodeURIComponent(runId)}/download`);
    link.hidden = false;
  }

  function updateStageDownloadLink(card) {
    const stageId = card.dataset.stage;
    const statusEl = card.querySelector(".stage-card__status");
    const downloadLink = card.querySelector(".stage-card__download");
    if (!stageId || !statusEl || !downloadLink) return;
    const runId = currentRunId();
    if (statusEl.dataset.state === "done" && runId) {
      downloadLink.href = apiUrl(
        `/api/runs/${encodeURIComponent(runId)}/artifacts/${encodeURIComponent(stageId)}/download`
      );
      downloadLink.hidden = false;
    } else {
      downloadLink.hidden = true;
    }
  }

  function refreshAll() {
    updateDownloadAllLink();
    document.querySelectorAll(".stage-card").forEach(updateStageDownloadLink);
  }

  const observer = new MutationObserver(() => refreshAll());
  observer.observe(document.body, {
    subtree: true,
    attributes: true,
    attributeFilter: ["data-state"],
    childList: true,
    characterData: true,
  });

  document.addEventListener("DOMContentLoaded", refreshAll);
  refreshAll();
})();
