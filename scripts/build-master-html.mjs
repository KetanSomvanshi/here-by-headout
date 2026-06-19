import fs from "node:fs";
import path from "node:path";
import { renderPage } from "./md-to-html.mjs";

const root = process.cwd();
const inputPath = path.join(root, "Headout Here - Hackin 2026 Master.md");
const outputPath = path.join(root, "Headout Here - Hackin 2026 Master.html");
const pagesPath = path.join(root, "index.html");

const siteNav = [
  { label: "📋 Master Doc", href: "index.html", active: true },
  { label: "🧭 Architecture", href: "architecture.html" },
];

const markdown = fs.readFileSync(inputPath, "utf8");
const html = renderPage({
  markdown,
  kicker: "Headout Here",
  tocTitle: "Master Doc",
  siteNav,
});

fs.writeFileSync(outputPath, html, "utf8");
fs.writeFileSync(pagesPath, html, "utf8");
console.log(`Wrote ${outputPath}`);
console.log(`Wrote ${pagesPath}`);
