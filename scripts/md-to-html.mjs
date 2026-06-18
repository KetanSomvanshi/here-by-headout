// Shared Markdown → HTML renderer for the Here by Headout GitHub Pages site.
// Used by build-master-html.mjs and build-trailers-html.mjs so every page
// shares one look. Lightweight on purpose (no deps) for Replit/CI simplicity.

export function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function slugify(value, usedIds) {
  const base =
    value
      .toLowerCase()
      .replace(/<[^>]+>/g, "")
      .replace(/[`*_~]/g, "")
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "") || "section";
  let id = base;
  let index = 2;
  while (usedIds.has(id)) {
    id = `${base}-${index}`;
    index += 1;
  }
  usedIds.add(id);
  return id;
}

function parseInline(value) {
  const placeholders = [];
  let text = escapeHtml(value);

  text = text.replace(/`([^`]+)`/g, (_, code) => {
    const key = `@@CODE${placeholders.length}@@`;
    placeholders.push(`<code>${code}</code>`);
    return key;
  });

  text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
  text = text.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noreferrer">$1</a>'
  );
  text = text.replace(/\*\*([\s\S]+?)\*\*/g, (_, inner) => {
    return `<strong>${inner.replace(/\*([^*]+)\*/g, "<em>$1</em>")}</strong>`;
  });
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  text = text.replace(/§(\d+)/g, '<a class="section-ref" href="#$1">$&</a>');

  for (let i = 0; i < placeholders.length; i += 1) {
    text = text.replace(`@@CODE${i}@@`, placeholders[i]);
  }

  return text;
}

function isTableStart(lines, index) {
  return (
    lines[index]?.trim().startsWith("|") &&
    lines[index + 1]?.trim().startsWith("|") &&
    /^\|?[\s:-]+\|[\s|:-]*$/.test(lines[index + 1].trim())
  );
}

function splitTableRow(row) {
  let value = row.trim();
  if (value.startsWith("|")) value = value.slice(1);
  if (value.endsWith("|")) value = value.slice(0, -1);
  return value.split("|").map((cell) => cell.trim());
}

function buildTable(lines, start) {
  const headers = splitTableRow(lines[start]);
  const aligns = splitTableRow(lines[start + 1]).map((cell) => {
    const left = cell.startsWith(":");
    const right = cell.endsWith(":");
    if (left && right) return "center";
    if (right) return "right";
    return "left";
  });

  let index = start + 2;
  const rows = [];
  while (index < lines.length && lines[index].trim().startsWith("|")) {
    rows.push(splitTableRow(lines[index]));
    index += 1;
  }

  const thead = `<thead><tr>${headers
    .map(
      (header, i) =>
        `<th style="text-align:${aligns[i] || "left"}">${parseInline(header)}</th>`
    )
    .join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map(
      (row) =>
        `<tr>${row
          .map(
            (cell, i) =>
              `<td style="text-align:${aligns[i] || "left"}">${parseInline(cell)}</td>`
          )
          .join("")}</tr>`
    )
    .join("")}</tbody>`;

  return {
    html: `<div class="table-wrap"><table>${thead}${tbody}</table></div>`,
    nextIndex: index,
  };
}

function parseMermaidEndpoint(value) {
  const trimmed = value.trim();
  const match = trimmed.match(/^([A-Za-z0-9_]+)(?:\["([\s\S]*)"\])?$/);
  if (!match) return null;
  return { id: match[1], label: match[2] || match[1] };
}

function renderDiagramLabel(value) {
  return parseInline(value).replace(/&lt;br\s*\/?&gt;/g, "<br>");
}

function renderMermaidLite(source) {
  const nodes = new Map();
  const edges = [];

  for (const rawLine of source.split("\n")) {
    const line = rawLine.trim();
    if (!line || line.startsWith("flowchart")) continue;

    const parts = line.split(/\s*-->\s*/);
    if (parts.length !== 2) continue;

    const sourceNode = parseMermaidEndpoint(parts[0]);
    const targetNode = parseMermaidEndpoint(parts[1]);
    if (!sourceNode || !targetNode) continue;

    if (!nodes.has(sourceNode.id) || sourceNode.label !== sourceNode.id) {
      nodes.set(sourceNode.id, sourceNode.label);
    }
    if (!nodes.has(targetNode.id) || targetNode.label !== targetNode.id) {
      nodes.set(targetNode.id, targetNode.label);
    }
    edges.push([sourceNode.id, targetNode.id]);
  }

  if (!edges.length) {
    return `<pre class="code-block"><code class="language-mermaid">${escapeHtml(source)}</code></pre>`;
  }

  const outgoing = new Map();
  const incoming = new Set();
  for (const [from, to] of edges) {
    if (!outgoing.has(from)) outgoing.set(from, []);
    outgoing.get(from).push(to);
    incoming.add(to);
  }

  const starts = [...nodes.keys()].filter((id) => !incoming.has(id));
  const rows = [];
  const usedEdgeKeys = new Set();

  for (const start of starts.length ? starts : [edges[0][0]]) {
    let current = start;
    const row = [current];
    const seenNodes = new Set([current]);

    while (outgoing.has(current)) {
      const next = outgoing
        .get(current)
        .find((target) => !usedEdgeKeys.has(`${current}->${target}`));
      if (!next) break;

      usedEdgeKeys.add(`${current}->${next}`);
      row.push(next);
      if (seenNodes.has(next)) break;
      seenNodes.add(next);
      current = next;
    }

    if (row.length > 1) rows.push(row);
  }

  for (const [from, to] of edges) {
    const key = `${from}->${to}`;
    if (!usedEdgeKeys.has(key)) {
      rows.push([from, to]);
      usedEdgeKeys.add(key);
    }
  }

  const rowHtml = rows
    .map((row) => {
      const pieces = row.map((id) => {
        const label = renderDiagramLabel(nodes.get(id) || id);
        return `<div class="flow-node">${label}</div>`;
      });
      return `<div class="flow-row">${pieces.join('<span class="flow-arrow">→</span>')}</div>`;
    })
    .join("");

  return `<div class="diagram-shell flow-diagram">${rowHtml}</div>`;
}

function parseBlocks(source) {
  const lines = source.split("\n");
  const usedIds = new Set();
  const headings = [];
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      i += 1;
      continue;
    }

    const fence = trimmed.match(/^```(\w+)?/);
    if (fence) {
      const lang = fence[1] || "";
      const codeLines = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i += 1;
      }
      i += 1;
      const code = escapeHtml(codeLines.join("\n"));
      if (lang === "mermaid") {
        blocks.push(renderMermaidLite(codeLines.join("\n")));
      } else {
        blocks.push(
          `<pre class="code-block"><code class="language-${escapeHtml(lang)}">${code}</code></pre>`
        );
      }
      continue;
    }

    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const text = heading[2].trim();
      const id = slugify(text, usedIds);
      headings.push({ id, level, text: text.replace(/[*_`]/g, "") });
      blocks.push(
        `<h${level} id="${id}"><a class="anchor" href="#${id}" aria-label="Link to section">#</a>${parseInline(text)}</h${level}>`
      );
      i += 1;
      continue;
    }

    if (trimmed === "---") {
      blocks.push("<hr>");
      i += 1;
      continue;
    }

    if (isTableStart(lines, i)) {
      const table = buildTable(lines, i);
      blocks.push(table.html);
      i = table.nextIndex;
      continue;
    }

    if (trimmed.startsWith(">")) {
      const quoteLines = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ""));
        i += 1;
      }
      blocks.push(
        `<blockquote>${quoteLines
          .map((quoteLine) => `<p>${parseInline(quoteLine)}</p>`)
          .join("")}</blockquote>`
      );
      continue;
    }

    const listMatch = trimmed.match(/^([-*]|\d+\.)\s+(.+)$/);
    if (listMatch) {
      const ordered = /\d+\./.test(listMatch[1]);
      const tag = ordered ? "ol" : "ul";
      const items = [];
      while (i < lines.length) {
        const item = lines[i].trim().match(/^([-*]|\d+\.)\s+(.+)$/);
        if (!item) break;
        items.push(`<li>${parseInline(item[2])}</li>`);
        i += 1;
      }
      blocks.push(`<${tag}>${items.join("")}</${tag}>`);
      continue;
    }

    const paragraph = [trimmed];
    i += 1;
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trim().startsWith("```") &&
      !lines[i].trim().startsWith(">") &&
      !lines[i].trim().match(/^(#{1,6})\s+/) &&
      !lines[i].trim().match(/^([-*]|\d+\.)\s+/) &&
      !isTableStart(lines, i)
    ) {
      paragraph.push(lines[i].trim());
      i += 1;
    }
    blocks.push(`<p>${parseInline(paragraph.join(" "))}</p>`);
  }

  return { content: blocks.join("\n"), headings };
}

const PAGE_STYLE = `
    :root {
      color-scheme: light;
      --bg: #f7f4ef;
      --paper: #fffdf8;
      --ink: #17201b;
      --muted: #637069;
      --line: #ded8ce;
      --accent: #e8552f;
      --accent-dark: #aa321f;
      --teal: #0f766e;
      --green-soft: #e7f4ec;
      --blue-soft: #e8f0fb;
      --shadow: 0 18px 50px rgba(27, 32, 29, 0.11);
      --radius: 8px;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      background:
        linear-gradient(135deg, rgba(232, 85, 47, 0.10), transparent 32rem),
        linear-gradient(225deg, rgba(15, 118, 110, 0.10), transparent 34rem),
        var(--bg);
      color: var(--ink);
      line-height: 1.65;
      font-size: 16px;
    }

    a {
      color: var(--accent-dark);
      text-decoration-thickness: 0.08em;
      text-underline-offset: 0.18em;
    }

    .page-shell {
      display: grid;
      grid-template-columns: minmax(220px, 300px) minmax(0, 1fr);
      min-height: 100vh;
    }

    aside {
      border-right: 1px solid var(--line);
      background: rgba(255, 253, 248, 0.82);
      backdrop-filter: blur(18px);
      padding: 28px 22px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
    }

    .brand-kicker {
      color: var(--accent-dark);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin: 0 0 8px;
    }

    .toc-title { font-size: 1rem; font-weight: 800; margin: 0 0 18px; }

    .site-nav {
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin: 0 0 18px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
    }

    .site-nav a {
      border-radius: 8px;
      color: var(--muted);
      display: block;
      font-size: 0.9rem;
      font-weight: 700;
      padding: 8px 10px;
      text-decoration: none;
    }

    .site-nav a:hover { background: var(--blue-soft); color: var(--ink); }
    .site-nav a.active {
      background: var(--accent);
      color: #fff;
    }

    .toc { display: flex; flex-direction: column; gap: 2px; }

    .toc-link {
      border-radius: 8px;
      color: var(--muted);
      display: block;
      font-size: 0.9rem;
      line-height: 1.3;
      padding: 8px 10px;
      text-decoration: none;
    }

    .toc-link:hover { background: var(--green-soft); color: var(--ink); }
    .toc-level-1 { color: var(--ink); font-weight: 800; margin-top: 10px; }
    .toc-level-2 { padding-left: 22px; }

    main { padding: 42px min(6vw, 72px) 72px; }

    article {
      background: var(--paper);
      border: 1px solid rgba(222, 216, 206, 0.82);
      border-radius: 8px;
      box-shadow: var(--shadow);
      margin: 0 auto;
      max-width: 980px;
      padding: clamp(28px, 5vw, 68px);
    }

    h1, h2, h3, h4 {
      color: var(--ink);
      letter-spacing: 0;
      line-height: 1.12;
      margin: 2.2rem 0 1rem;
      scroll-margin-top: 28px;
    }

    h1:first-child { margin-top: 0; }
    h1 { font-size: clamp(2rem, 5vw, 4.4rem); max-width: 13ch; }
    h2 {
      border-top: 1px solid var(--line);
      font-size: clamp(1.5rem, 3vw, 2.35rem);
      padding-top: 2.1rem;
    }
    h3 { color: var(--teal); font-size: 1.18rem; margin-top: 1.8rem; }
    h4 { font-size: 1rem; }

    .anchor {
      color: var(--accent);
      float: left;
      font-size: 0.8em;
      margin-left: -1.05em;
      opacity: 0;
      text-decoration: none;
      transition: opacity 0.16s ease;
    }

    h1:hover .anchor, h2:hover .anchor, h3:hover .anchor, h4:hover .anchor { opacity: 1; }

    p { margin: 0.9rem 0; }
    strong { color: #0f241c; font-weight: 800; }

    blockquote {
      background: linear-gradient(90deg, rgba(232, 85, 47, 0.10), rgba(15, 118, 110, 0.07));
      border-left: 5px solid var(--accent);
      border-radius: 0 8px 8px 0;
      margin: 1.5rem 0;
      padding: 1rem 1.2rem;
    }

    blockquote p { font-size: 1.02rem; margin: 0.25rem 0; }

    ul, ol { padding-left: 1.35rem; }
    li { margin: 0.45rem 0; padding-left: 0.12rem; }

    hr { border: 0; border-top: 1px solid var(--line); margin: 2.4rem 0; }

    code {
      background: #f0ebe2;
      border: 1px solid #e3dccf;
      border-radius: 6px;
      color: #8f2b1d;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.88em;
      padding: 0.12em 0.36em;
    }

    .code-block {
      background: #151b18;
      border-radius: var(--radius);
      color: #e9f0eb;
      overflow: auto;
      padding: 1.1rem;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .code-block code { background: transparent; border: 0; color: inherit; padding: 0; }

    .table-wrap {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      margin: 1.4rem 0;
      overflow-x: auto;
    }

    table { border-collapse: collapse; min-width: 720px; width: 100%; }

    th, td {
      border-bottom: 1px solid var(--line);
      padding: 0.78rem 0.9rem;
      vertical-align: top;
    }

    th {
      background: #efe9df;
      color: #20251f;
      font-size: 0.82rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    tr:nth-child(even) td { background: rgba(232, 240, 251, 0.45); }
    tr:last-child td { border-bottom: 0; }

    .diagram-shell {
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      margin: 1.5rem 0;
      overflow-x: auto;
      padding: 1rem;
    }

    .flow-diagram { display: flex; flex-direction: column; gap: 0.75rem; }
    .flow-row { align-items: center; display: flex; gap: 0.7rem; min-width: max-content; }

    .flow-node {
      background: var(--green-soft);
      border: 1px solid rgba(15, 118, 110, 0.34);
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(27, 32, 29, 0.06);
      color: #12352f;
      font-size: 0.9rem;
      font-weight: 750;
      line-height: 1.25;
      max-width: 190px;
      min-height: 64px;
      min-width: 150px;
      padding: 0.75rem;
      text-align: center;
    }

    .flow-arrow { color: var(--accent); font-weight: 900; }
    .section-ref { color: inherit; text-decoration: none; }

    @media (max-width: 900px) {
      .page-shell { display: block; }
      aside {
        border-bottom: 1px solid var(--line);
        border-right: 0;
        height: auto;
        max-height: 46vh;
        position: relative;
      }
      main { padding: 18px; }
      article { padding: 24px; }
      .anchor { display: none; }
      h1 { max-width: none; }
    }

    @media print {
      body { background: #fff; }
      .page-shell { display: block; }
      aside { display: none; }
      main, article { box-shadow: none; margin: 0; max-width: none; padding: 0; }
    }
`;

/**
 * Render a Markdown string into a full standalone HTML page.
 * @param {object} opts
 * @param {string} opts.markdown   raw markdown
 * @param {string} opts.kicker     small uppercase brand label in the sidebar
 * @param {string} opts.tocTitle   sidebar section title
 * @param {Array<{label:string, href:string, active?:boolean}>} [opts.siteNav]
 *        cross-page links rendered above the outline
 */
export function renderPage({ markdown, kicker, tocTitle, siteNav = [] }) {
  const normalized = markdown.replace(/\r\n/g, "\n");
  const parsed = parseBlocks(normalized);
  const headings = parsed.headings;

  const sectionLinks = new Map(
    headings
      .map((heading) => {
        const match = heading.text.match(/^(\d+)\./);
        return match ? [match[1], heading.id] : null;
      })
      .filter(Boolean)
  );
  const content = parsed.content.replace(/href="#(\d+)"/g, (_, section) => {
    return `href="#${sectionLinks.get(section) || section}"`;
  });
  const title = headings[0]?.text || tocTitle || "Here by Headout";

  const nav = headings
    .filter((heading) => heading.level <= 2)
    .map(
      (heading) =>
        `<a class="toc-link toc-level-${heading.level}" href="#${heading.id}">${parseInline(heading.text)}</a>`
    )
    .join("\n");

  const siteNavHtml = siteNav.length
    ? `<nav class="site-nav" aria-label="Site">
        ${siteNav
          .map(
            (link) =>
              `<a href="${link.href}"${link.active ? ' class="active"' : ""}>${escapeHtml(link.label)}</a>`
          )
          .join("\n        ")}
      </nav>`
    : "";

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <style>${PAGE_STYLE}</style>
</head>
<body>
  <div class="page-shell">
    <aside>
      <p class="brand-kicker">${escapeHtml(kicker)}</p>
      <p class="toc-title">${escapeHtml(tocTitle)}</p>
      ${siteNavHtml}
      <nav class="toc" aria-label="Document outline">
        ${nav}
      </nav>
    </aside>
    <main>
      <article>
${content}
      </article>
    </main>
  </div>
</body>
</html>
`;
}
