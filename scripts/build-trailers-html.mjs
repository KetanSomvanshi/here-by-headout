import fs from "node:fs";
import path from "node:path";
import { renderPage } from "./md-to-html.mjs";

const root = process.cwd();

const pages = [
  {
    input: "flow-trailer-prompts.md",
    output: "trailer-guest.html",
    tocTitle: "Guest Trailer",
    navHref: "trailer-guest.html",
  },
  {
    input: "flow-trailer-prompts-partner.md",
    output: "trailer-partner.html",
    tocTitle: "Partner Trailer",
    navHref: "trailer-partner.html",
  },
];

const baseNav = [
  { label: "📋 Master Doc", href: "index.html" },
  { label: "🎬 Demo", href: "demo.html" },
  { label: "🧭 Architecture", href: "architecture.html" },
];

for (const page of pages) {
  const markdown = fs.readFileSync(path.join(root, page.input), "utf8");
  const siteNav = baseNav.map((link) => ({
    ...link,
    active: link.href === page.navHref,
  }));
  const html = renderPage({
    markdown,
    kicker: "Here by Headout",
    tocTitle: page.tocTitle,
    siteNav,
  });
  fs.writeFileSync(path.join(root, page.output), html, "utf8");
  console.log(`Wrote ${path.join(root, page.output)}`);
}
