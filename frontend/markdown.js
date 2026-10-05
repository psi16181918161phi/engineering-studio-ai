/**
 * WHAT: Minimal, dependency-free Markdown -> DOM renderer.
 * WHY: Pipeline artifacts are full Markdown documents (headings, tables,
 * lists, code fences) but were previously dumped as literal text in a
 * <pre>, showing raw '#'/'|'/'-' characters. This renders them properly
 * while preserving the app's core XSS rule (see app.js's own header
 * comment): LLM-produced text is NEVER passed to innerHTML. Every DOM
 * node here is built with createElement/createTextNode; the only place a
 * source string becomes an attribute is an <a href>, and only after
 * isSafeUrl() confirms it's a plain http(s) URL — markup embedded in the
 * source is never interpreted as HTML.
 * HOW: A block-level pass (headings, fenced code, tables, lists,
 * blockquotes, hr, paragraphs) followed by an inline pass (bold, italic,
 * inline code, strikethrough, links) within each block's text.
 */
(function (global) {
  "use strict";

  function isSafeUrl(url) {
    return /^https?:\/\/\S+$/i.test(url);
  }

  function renderInline(parent, text) {
    const pattern = /(\*\*(.+?)\*\*|__(.+?)__|`([^`]+?)`|~~(.+?)~~|\*(.+?)\*|_(.+?)_|\[([^\]]+)\]\(([^)\s]+)\))/;
    let rest = text;
    let guard = 0;
    while (rest.length && guard < 2000) {
      guard++;
      const match = pattern.exec(rest);
      if (!match) {
        parent.appendChild(document.createTextNode(rest));
        break;
      }
      if (match.index > 0) {
        parent.appendChild(document.createTextNode(rest.slice(0, match.index)));
      }
      if (match[2] !== undefined || match[3] !== undefined) {
        const strong = document.createElement("strong");
        strong.className = "md-strong";
        renderInline(strong, match[2] !== undefined ? match[2] : match[3]);
        parent.appendChild(strong);
      } else if (match[4] !== undefined) {
        const code = document.createElement("code");
        code.className = "md-code";
        code.textContent = match[4];
        parent.appendChild(code);
      } else if (match[5] !== undefined) {
        const del = document.createElement("del");
        del.className = "md-strike";
        renderInline(del, match[5]);
        parent.appendChild(del);
      } else if (match[6] !== undefined || match[7] !== undefined) {
        const em = document.createElement("em");
        em.className = "md-em";
        renderInline(em, match[6] !== undefined ? match[6] : match[7]);
        parent.appendChild(em);
      } else if (match[8] !== undefined) {
        const label = match[8];
        const url = match[9];
        if (isSafeUrl(url)) {
          const a = document.createElement("a");
          a.className = "md-a";
          a.href = url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          renderInline(a, label);
          parent.appendChild(a);
        } else {
          parent.appendChild(document.createTextNode(`${label} (${url})`));
        }
      }
      rest = rest.slice(match.index + match[0].length);
    }
  }

  function splitTableRow(line) {
    let trimmed = line.trim();
    if (trimmed.startsWith("|")) trimmed = trimmed.slice(1);
    if (trimmed.endsWith("|")) trimmed = trimmed.slice(0, -1);
    return trimmed.split("|").map((cell) => cell.trim());
  }

  function isTableSeparator(line) {
    return /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/.test(line) && line.includes("-");
  }

  function renderTable(container, lines) {
    const table = document.createElement("table");
    table.className = "md-table";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    splitTableRow(lines[0]).forEach((cell) => {
      const th = document.createElement("th");
      renderInline(th, cell);
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (let i = 2; i < lines.length; i++) {
      const cells = splitTableRow(lines[i]);
      if (!cells.length || (cells.length === 1 && !cells[0])) continue;
      const tr = document.createElement("tr");
      cells.forEach((cell) => {
        const td = document.createElement("td");
        renderInline(td, cell);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    container.appendChild(table);
  }

  /** WHAT: Renders a Markdown string into `container` (cleared first).
   * ARGS: container (Element), text (string). */
  function render(container, text) {
    container.textContent = "";
    const lines = String(text).replace(/\r\n/g, "\n").split("\n");
    let i = 0;
    let list = null; // {el, type: "ul"|"ol"}

    function closeList() {
      list = null;
    }

    while (i < lines.length) {
      const line = lines[i];

      if (!line.trim()) {
        closeList();
        i++;
        continue;
      }

      const fence = /^```(\w*)\s*$/.exec(line);
      if (fence) {
        closeList();
        const codeLines = [];
        i++;
        while (i < lines.length && !/^```\s*$/.test(lines[i])) {
          codeLines.push(lines[i]);
          i++;
        }
        i++; // skip closing fence (or end of input if unterminated)
        const pre = document.createElement("pre");
        pre.className = "md-pre";
        const code = document.createElement("code");
        code.textContent = codeLines.join("\n");
        pre.appendChild(code);
        container.appendChild(pre);
        continue;
      }

      const heading = /^(#{1,6})\s+(.*)$/.exec(line);
      if (heading) {
        closeList();
        const level = heading[1].length;
        const h = document.createElement(`h${Math.min(level + 2, 6)}`);
        h.className = `md-h${level}`;
        renderInline(h, heading[2]);
        container.appendChild(h);
        i++;
        continue;
      }

      if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(line.trim())) {
        closeList();
        const hr = document.createElement("hr");
        hr.className = "md-hr";
        container.appendChild(hr);
        i++;
        continue;
      }

      if (line.includes("|") && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
        closeList();
        const tableLines = [line, lines[i + 1]];
        let j = i + 2;
        while (j < lines.length && lines[j].includes("|") && lines[j].trim()) {
          tableLines.push(lines[j]);
          j++;
        }
        renderTable(container, tableLines);
        i = j;
        continue;
      }

      if (/^>\s?/.test(line)) {
        closeList();
        const quoteLines = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) {
          quoteLines.push(lines[i].replace(/^>\s?/, ""));
          i++;
        }
        const bq = document.createElement("blockquote");
        bq.className = "md-blockquote";
        renderInline(bq, quoteLines.join(" "));
        container.appendChild(bq);
        continue;
      }

      const ulItem = /^(\s*)[-*+]\s+(.*)$/.exec(line);
      const olItem = !ulItem ? /^(\s*)\d+[.)]\s+(.*)$/.exec(line) : null;
      if (ulItem || olItem) {
        const isOrdered = !!olItem;
        const contentText = (ulItem || olItem)[2];
        if (!list || list.type !== (isOrdered ? "ol" : "ul")) {
          list = { el: document.createElement(isOrdered ? "ol" : "ul"), type: isOrdered ? "ol" : "ul" };
          list.el.className = isOrdered ? "md-ol" : "md-ul";
          container.appendChild(list.el);
        }
        const li = document.createElement("li");
        li.className = "md-li";
        const task = /^\[( |x|X)\]\s+(.*)$/.exec(contentText);
        if (task) {
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.disabled = true;
          checkbox.checked = task[1].toLowerCase() === "x";
          checkbox.className = "md-task-checkbox";
          li.appendChild(checkbox);
          renderInline(li, " " + task[2]);
        } else {
          renderInline(li, contentText);
        }
        list.el.appendChild(li);
        i++;
        continue;
      }

      closeList();
      const paraLines = [line];
      i++;
      while (
        i < lines.length &&
        lines[i].trim() &&
        !/^```/.test(lines[i]) &&
        !/^#{1,6}\s/.test(lines[i]) &&
        !/^>\s?/.test(lines[i]) &&
        !/^\s*[-*+]\s+/.test(lines[i]) &&
        !/^\s*\d+[.)]\s+/.test(lines[i]) &&
        !(lines[i].includes("|") && i + 1 < lines.length && isTableSeparator(lines[i + 1]))
      ) {
        paraLines.push(lines[i]);
        i++;
      }
      const p = document.createElement("p");
      p.className = "md-p";
      renderInline(p, paraLines.join(" "));
      container.appendChild(p);
    }
  }

  global.EngineeringStudioMarkdown = { render };
})(window);
