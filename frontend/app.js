/**
 * WHAT: Client-side logic for the Engineering Studio AI command-and-control
 * dashboard — launches runs, subscribes to live stage updates over SSE, and
 * renders per-agent artifacts on demand.
 * WHY: A "command and control center" for the agent team means an operator
 * can (a) trigger a run, (b) see every agent's live status at a glance, and
 * (c) inspect what each agent actually produced — this file is the only
 * thing that talks to the backend API defined in
 * src/engineering_studio/api/.
 * HOW: No build step, no framework — plain fetch() + EventSource. All
 * agent-produced text is inserted via textContent only, never innerHTML,
 * since artifact content originates from an LLM and must never be treated
 * as trusted markup (XSS hygiene, AGENTS.md SS5 prompt-injection rule
 * extended to the browser).
 */

(() => {
  "use strict";

  /** WHAT: Display metadata for every stage, in dispatch order.
   * WHY: Mirrors engineering_studio.agents.orchestrator.STAGE_ORDER — kept
   * as a small hand-maintained table here since the frontend has no build
   * step to import the Python constant directly. */
  const STAGES = [
    { id: "research", label: "Research", role: "Problem framing & feasibility", lane: "sequential" },
    { id: "mechanical", label: "Mechanical", role: "Domain Specialist", lane: "parallel" },
    { id: "electrical", label: "Electrical", role: "Domain Specialist", lane: "parallel" },
    { id: "firmware", label: "Firmware", role: "Domain Specialist", lane: "parallel" },
    { id: "simulation", label: "Simulation", role: "Domain Specialist", lane: "parallel" },
    { id: "business", label: "Cost / Business / Legal", role: "Domain Specialist", lane: "sequential" },
    { id: "challenge", label: "Challenge Division", role: "Adversarial reviewer", lane: "sequential" },
    { id: "quality_gate", label: "Quality Gate", role: "Sole certifying authority", lane: "sequential" },
  ];

  const STATUS_ICON = {
    pending: "○",
    running: "◐",
    done: "✓",
    error: "✕",
    skipped: "–",
  };

  const STATUS_LABEL = {
    pending: "Idle",
    running: "Running…",
    done: "Done",
    error: "Error",
    skipped: "Skipped",
  };

  const els = {
    serverStatus: document.getElementById("server-status"),
    serverStatusText: document.getElementById("server-status-text"),
    themeToggle: document.getElementById("theme-toggle"),
    themeToggleText: document.getElementById("theme-toggle-text"),
    launchForm: document.getElementById("launch-form"),
    briefInput: document.getElementById("brief-input"),
    launchButton: document.getElementById("launch-button"),
    launchError: document.getElementById("launch-error"),
    runHistory: document.getElementById("run-history"),
    runMeta: document.getElementById("run-meta"),
    runMetaId: document.getElementById("run-meta-id"),
    runMetaStatus: document.getElementById("run-meta-status"),
    gateBanner: document.getElementById("gate-banner"),
    pipelineEmpty: document.getElementById("pipeline-empty"),
    stageGrid: document.getElementById("stage-grid"),
    stageCardTemplate: document.getElementById("stage-card-template"),
  };

  /** WHAT: Mutable client state for whichever run is currently displayed. */
  const state = {
    currentRunId: null,
    eventSource: null,
    cards: new Map(), // stage id -> { root, statusEl, iconEl, textEl, toggleBtn, outputEl, loaded }
    history: [], // [{run_id, product_brief, status}], newest first
  };

  function apiUrl(path) {
    return path; // same-origin: served by the FastAPI app under "/"
  }

  /** WHAT: Light Mode / Dark Mode theme toggle (promotional poster pair:
   * `promotions/X_STUDIO_X.png` = light, `promotions/X_STUDIO_X_ALT.png`
   * = dark).
   * WHY: `docs/TEAM_QA.md` §4 defines exactly these 2 supported themes;
   * `theme.css` implements both purely via a `data-theme` attribute on
   * `<html>`, so this function only needs to flip that attribute and
   * remember the choice — no other visual code changes between themes.
   * NOTE: unrelated to `engineering_studio.utils.palette`'s Python-side
   * "Variant A/B" (Plot Surface vs Interface Surface, both black-bg) —
   * different axis, intentionally different name (Light/Dark here).
   * HOW: Defaults to Dark Mode to match the pre-existing behavior for
   * anyone with no stored preference; persists the choice in
   * localStorage so a reload keeps the operator's last selection. */
  const THEME_STORAGE_KEY = "engineering-studio-theme";

  function applyTheme(theme) {
    const isLight = theme === "light";
    document.documentElement.dataset.theme = isLight ? "light" : "dark";
    els.themeToggle.setAttribute("aria-pressed", String(isLight));
    els.themeToggleText.textContent = isLight ? "Light mode" : "Dark mode";
  }

  function initTheme() {
    let stored = null;
    try {
      stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    } catch (err) {
      stored = null; // localStorage unavailable (e.g. private browsing) — fall back to default.
    }
    applyTheme(stored === "light" ? "light" : "dark");
  }

  els.themeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    applyTheme(next);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch (err) {
      /* localStorage unavailable — theme still applies for this page view. */
    }
  });

  async function checkHealth() {
    try {
      const res = await fetch(apiUrl("/api/health"));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setServerStatus("ok", "Backend online");
    } catch (err) {
      setServerStatus("down", "Backend unreachable — is uvicorn running?");
    }
  }

  function setServerStatus(kind, text) {
    els.serverStatus.dataset.state = kind;
    els.serverStatusText.textContent = text;
  }

  function buildStageGrid() {
    els.stageGrid.innerHTML = "";
    state.cards.clear();
    for (const stage of STAGES) {
      const fragment = els.stageCardTemplate.content.cloneNode(true);
      const root = fragment.querySelector(".stage-card");
      root.dataset.stage = stage.id;
      root.dataset.lane = stage.lane;
      root.querySelector(".stage-card__title").textContent = stage.label;
      root.querySelector(".stage-card__role").textContent = stage.role;

      const statusEl = root.querySelector(".stage-card__status");
      const iconEl = root.querySelector(".stage-card__status-icon");
      const textEl = root.querySelector(".stage-card__status-text");
      const toggleBtn = root.querySelector(".stage-card__toggle");
      const outputEl = root.querySelector(".stage-card__output");

      toggleBtn.addEventListener("click", () => toggleArtifact(stage.id));

      els.stageGrid.appendChild(fragment);
      state.cards.set(stage.id, {
        root, statusEl, iconEl, textEl, toggleBtn, outputEl, loaded: false,
      });
    }
    els.stageGrid.hidden = false;
    els.pipelineEmpty.hidden = true;
  }

  function setStageStatus(stageId, status, detail) {
    const card = state.cards.get(stageId);
    if (!card) return;
    card.statusEl.dataset.state = status;
    card.iconEl.textContent = STATUS_ICON[status] || "?";
    card.textEl.textContent = STATUS_LABEL[status] || status;

    if (status === "done") {
      card.toggleBtn.hidden = false;
    } else if (status === "error") {
      card.toggleBtn.hidden = true;
      card.outputEl.hidden = false;
      card.outputEl.textContent = detail ? `Error: ${detail}` : "Error: stage failed.";
    } else {
      card.toggleBtn.hidden = true;
      card.outputEl.hidden = true;
    }
  }

  function markRemainingPendingAsSkipped() {
    for (const [stageId, card] of state.cards.entries()) {
      if (card.statusEl.dataset.state === "pending") {
        setStageStatus(stageId, "skipped");
      }
    }
  }

  async function toggleArtifact(stageId) {
    const card = state.cards.get(stageId);
    if (!card) return;
    if (!card.outputEl.hidden) {
      card.outputEl.hidden = true;
      card.toggleBtn.textContent = "View output";
      return;
    }
    card.outputEl.hidden = false;
    card.toggleBtn.textContent = "Hide output";
    if (card.loaded) return;

    card.outputEl.textContent = "Loading…";
    try {
      const res = await fetch(
        apiUrl(`/api/runs/${encodeURIComponent(state.currentRunId)}/artifacts/${encodeURIComponent(stageId)}`)
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = await res.json();
      card.outputEl.textContent = payload.content;
      card.loaded = true;
    } catch (err) {
      card.outputEl.textContent = `Could not load artifact: ${err.message}`;
    }
  }

  function setRunMeta(runId, status) {
    els.runMeta.hidden = false;
    els.runMetaId.textContent = runId;
    els.runMetaStatus.dataset.state = status;
    els.runMetaStatus.textContent = STATUS_LABEL[status] || status;
  }

  function updateGateBanner(status, detail) {
    if (status !== "done" && status !== "error") {
      els.gateBanner.hidden = true;
      return;
    }
    els.gateBanner.hidden = false;
    els.gateBanner.dataset.state = status;
    if (status === "error") {
      els.gateBanner.textContent = `Run halted before completion: ${detail || "see stage that shows Error."}`;
      return;
    }
    els.gateBanner.textContent =
      "Run complete — expand “Quality Gate” below for the certifying agent's verdict.";
  }

  function applySnapshot(snapshot) {
    setRunMeta(snapshot.run_id, snapshot.status);
    const order = snapshot.stage_order || STAGES.map((s) => s.id);
    for (const stageId of order) {
      const stage = snapshot.stages[stageId];
      if (stage) setStageStatus(stageId, stage.status, stage.detail);
    }
    if (snapshot.status === "done" || snapshot.status === "error") {
      markRemainingPendingAsSkipped();
      updateGateBanner(snapshot.status, snapshot.status === "error" ? findFirstError(snapshot) : null);
    }
  }

  function findFirstError(snapshot) {
    for (const stageId of snapshot.stage_order || []) {
      const stage = snapshot.stages[stageId];
      if (stage && stage.status === "error") return `${stageId}: ${stage.detail || "unknown error"}`;
    }
    return null;
  }

  function applyEvent(event) {
    if (event.type === "stage") {
      setStageStatus(event.stage, event.status, event.detail);
    } else if (event.type === "run") {
      setRunMeta(state.currentRunId, event.status);
      markRemainingPendingAsSkipped();
      updateGateBanner(event.status, event.detail);
      refreshHistory();
    }
  }

  function openStream(runId) {
    if (state.eventSource) {
      state.eventSource.close();
      state.eventSource = null;
    }
    const source = new EventSource(apiUrl(`/api/runs/${encodeURIComponent(runId)}/stream`));
    state.eventSource = source;
    source.onmessage = (message) => {
      let payload;
      try {
        payload = JSON.parse(message.data);
      } catch (err) {
        return;
      }
      if (payload.stages && payload.stage_order) {
        applySnapshot(payload);
      } else {
        applyEvent(payload);
      }
    };
    source.onerror = () => {
      // WHAT: EventSource retries by default; nothing to do here beyond
      // leaving the last-known status visible rather than clearing the UI.
    };
  }

  function selectRun(runId) {
    state.currentRunId = runId;
    buildStageGrid();
    els.gateBanner.hidden = true;
    openStream(runId);
  }

  function renderHistory() {
    if (state.history.length === 0) {
      els.runHistory.innerHTML = '<li class="run-history__empty">No runs yet.</li>';
      return;
    }
    els.runHistory.innerHTML = "";
    for (const run of state.history) {
      const isActive = run.run_id === state.currentRunId;
      const item = document.createElement("li");
      item.className = "run-history__item";
      if (isActive) item.classList.add("is-active");

      const button = document.createElement("button");
      button.type = "button";
      button.className = "run-history__button";
      if (isActive) button.setAttribute("aria-current", "true");
      button.addEventListener("click", () => selectRun(run.run_id));

      const brief = document.createElement("span");
      brief.className = "run-history__brief";
      brief.textContent = run.product_brief;

      const badge = document.createElement("span");
      badge.className = "run-history__badge";
      badge.dataset.state = run.status;
      badge.textContent = STATUS_LABEL[run.status] || run.status;

      button.appendChild(brief);
      button.appendChild(badge);
      item.appendChild(button);
      els.runHistory.appendChild(item);
    }
  }

  async function refreshHistory() {
    try {
      const res = await fetch(apiUrl("/api/runs"));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const runs = await res.json();
      state.history = runs.map((r) => ({
        run_id: r.run_id,
        product_brief: r.product_brief,
        status: r.status,
      }));
      renderHistory();
    } catch (err) {
      // WHAT: History is a convenience panel; a transient failure here
      // must not disturb the live run view.
    }
  }

  async function launchRun(productBrief) {
    els.launchError.hidden = true;
    els.launchButton.disabled = true;
    try {
      const res = await fetch(apiUrl("/api/runs"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_brief: productBrief }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      const payload = await res.json();
      await refreshHistory();
      selectRun(payload.run_id);
    } catch (err) {
      els.launchError.hidden = false;
      els.launchError.textContent = `Could not launch run: ${err.message}`;
    } finally {
      els.launchButton.disabled = false;
    }
  }

  els.launchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const brief = els.briefInput.value.trim();
    if (!brief) return;
    launchRun(brief);
  });

  initTheme();
  checkHealth();
  refreshHistory();
})();
