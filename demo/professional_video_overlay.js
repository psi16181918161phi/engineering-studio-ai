/**
 * WHAT: Browser-side caption/topbar/progress-bar/title-card overlay used
 * by `professional_video_demo.py`'s recorded walkthrough videos.
 * WHY: Kept in its own file (rather than embedded as a Python string) so
 * the Python driver script stays focused on orchestration/pacing only —
 * single-responsibility split between "what the browser renders" (this
 * file) and "when/what it's told to show" (the .py file). Also makes
 * each half far easier to review/edit independently without touching a
 * large embedded string literal.
 * HOW: Injected once per page via `page.evaluate()` reading this file's
 * text. An IIFE guarded by `window.__demoOverlayReady` so re-injection
 * (e.g. after a reload) is a safe no-op. Every element is
 * `pointer-events: none` — this overlay is purely a decorative status
 * display and must NEVER intercept clicks meant for the real app UI
 * underneath it (e.g. the theme toggle button in the page's own
 * header), regardless of z-index/stacking order.
 */
(() => {
  if (window.__demoOverlayReady) return;
  window.__demoOverlayReady = true;

  const style = document.createElement("style");
  style.id = "demo-overlay-style";
  style.textContent = `
    #demo-topbar {
      position: fixed; top: 0; left: 0; right: 0; height: 56px;
      background: rgba(0,0,0,0.85); color: #ffffff;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 28px; font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
      font-size: 17px; font-weight: 600; letter-spacing: 0.02em;
      z-index: 2147483000; pointer-events: none;
    }
    #demo-topbar .demo-title { color: #B76E79; }
    #demo-progress-track {
      position: fixed; top: 56px; left: 0; right: 0; height: 4px;
      background: rgba(255,255,255,0.15); z-index: 2147483000;
      pointer-events: none;
    }
    #demo-progress-fill {
      height: 100%; width: 0%; background: #B76E79;
      transition: width 0.6s ease;
    }
    #demo-caption {
      position: fixed; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.82); color: #ffffff;
      padding: 18px 32px 24px; font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
      opacity: 0; transform: translateY(12px);
      transition: opacity 0.5s ease, transform 0.5s ease;
      z-index: 2147483000; pointer-events: none;
    }
    #demo-caption.demo-caption--visible { opacity: 1; transform: translateY(0); }
    #demo-caption-heading { font-size: 23px; font-weight: 700; color: #B76E79; margin: 0 0 6px; }
    #demo-caption-body { font-size: 17px; line-height: 1.4; margin: 0; max-width: 1500px; }
    #demo-card {
      position: fixed; inset: 0; display: flex; flex-direction: column;
      align-items: center; justify-content: center; text-align: center;
      background: var(--brand-ink); color: var(--brand-primary);
      opacity: 0; pointer-events: none; transition: opacity 0.6s ease;
      z-index: 2147483647; padding: 48px;
      font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    }
    #demo-card.demo-card--visible { opacity: 1; }
    #demo-card-title { font-size: 52px; font-weight: 800; margin: 0 0 14px; }
    #demo-card-subtitle { font-size: 25px; font-weight: 500; margin: 0 0 26px; color: #B76E79; }
    #demo-card-extra { font-size: 16px; max-width: 1000px; opacity: 0.85; line-height: 1.5; }
  `;
  document.head.appendChild(style);

  const topbar = document.createElement("div");
  topbar.id = "demo-topbar";
  topbar.innerHTML = '<span class="demo-title"></span><span class="demo-stage-text"></span>';
  document.body.appendChild(topbar);

  const progressTrack = document.createElement("div");
  progressTrack.id = "demo-progress-track";
  const progressFill = document.createElement("div");
  progressFill.id = "demo-progress-fill";
  progressTrack.appendChild(progressFill);
  document.body.appendChild(progressTrack);

  const caption = document.createElement("div");
  caption.id = "demo-caption";
  caption.innerHTML = '<p id="demo-caption-heading"></p><p id="demo-caption-body"></p>';
  document.body.appendChild(caption);

  const card = document.createElement("div");
  card.id = "demo-card";
  card.innerHTML = '<h1 id="demo-card-title"></h1><p id="demo-card-subtitle"></p><p id="demo-card-extra"></p>';
  document.body.appendChild(card);

  window.__demoSetTopbar = (title, stageText) => {
    topbar.querySelector(".demo-title").textContent = title;
    topbar.querySelector(".demo-stage-text").textContent = stageText;
  };
  window.__demoSetProgress = (pct) => {
    progressFill.style.width = Math.max(0, Math.min(100, pct)) + "%";
  };
  window.__demoSetCaption = (heading, body) => {
    document.getElementById("demo-caption-heading").textContent = heading;
    document.getElementById("demo-caption-body").textContent = body;
    caption.classList.add("demo-caption--visible");
  };
  window.__demoClearCaption = () => {
    caption.classList.remove("demo-caption--visible");
  };
  window.__demoShowCard = (title, subtitle, extra) => {
    document.getElementById("demo-card-title").textContent = title;
    document.getElementById("demo-card-subtitle").textContent = subtitle;
    document.getElementById("demo-card-extra").textContent = extra;
    card.classList.add("demo-card--visible");
  };
  window.__demoHideCard = () => {
    card.classList.remove("demo-card--visible");
  };
})();
