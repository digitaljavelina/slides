#!/usr/bin/env node
/**
 * bridge.js — load a branded-slides HTML deck in headless Chromium and
 * render every <section class="slide"> to native-shape PPTX via dom-to-pptx.
 *
 * dom-to-pptx is a browser-only library — it walks the live DOM via
 * getBoundingClientRect to capture computed layout, gradients, shadows, and
 * SVGs. We host it inside Playwright so all CSS resolves identically to a
 * real browser rendering.
 *
 * Why force-reveal: the deck's reveal-on-scroll animations leave content at
 * `opacity: 0; transform: translateY(28px)` until JS adds `.visible`. We
 * inject that class on every slide and disable transitions so dom-to-pptx
 * reads the *settled* visual state.
 *
 * Usage:
 *   node bridge.js --input <deck.html> --output <out.pptx>
 *
 * Options:
 *   --no-svg-vector       embed SVGs as images instead of editable vectors
 *   --viewport-width N    default 1920 (16:9 at 1080)
 *   --viewport-height N   default 1080
 *   --debug               stream page console output to this terminal
 */

import { chromium } from "playwright";
import { fileURLToPath } from "url";
import { dirname, resolve as pathResolve, extname, basename } from "path";
import { writeFile, mkdir, readFile } from "fs/promises";
import { parseArgs } from "node:util";
import { createServer } from "node:http";

// Minimal MIME map covering everything our brand template references.
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript",
  ".css": "text/css",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
};

// Serve the deck folder over a transient localhost HTTP server. Chromium
// blocks canvas readback on `file://` origins (the `null` origin trips CORS),
// so dom-to-pptx can't read the AI-generated PNGs. Hosting them on
// http://127.0.0.1 sidesteps the entire issue.
function serveDeckDir(rootDir) {
  return new Promise((resolve, reject) => {
    const server = createServer(async (req, res) => {
      try {
        const url = new URL(req.url, "http://127.0.0.1");
        const safe = pathResolve(rootDir, "." + url.pathname);
        if (!safe.startsWith(rootDir)) {
          res.writeHead(403);
          return res.end("Forbidden");
        }
        const data = await readFile(safe);
        const mime =
          MIME[extname(safe).toLowerCase()] || "application/octet-stream";
        res.writeHead(200, {
          "Content-Type": mime,
          "Cache-Control": "no-store",
          "Access-Control-Allow-Origin": "*",
        });
        res.end(data);
      } catch (err) {
        res.writeHead(404);
        res.end(`Not found: ${err.message}`);
      }
    });
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, port });
    });
  });
}

const { values } = parseArgs({
  options: {
    input: { type: "string", short: "i" },
    output: { type: "string", short: "o" },
    "svg-vector": { type: "boolean", default: true },
    "no-svg-vector": { type: "boolean", default: false },
    // Default viewport matches PPTX widescreen at 96 DPI (13.333" × 7.5"
    // = 1280 × 720). Keeps dom-to-pptx's scale factor at 1.0 so font
    // sizes don't get downscaled — at 1920 viewport the brand's body
    // font (22px) was rendering as 11pt in PPTX, too small for slides.
    "viewport-width": { type: "string", default: "1280" },
    "viewport-height": { type: "string", default: "720" },
    debug: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
});

if (values.help || !values.input || !values.output) {
  console.error(
    "Usage: node bridge.js --input <deck.html> --output <out.pptx>\n" +
      "       [--no-svg-vector] [--viewport-width N] [--viewport-height N] [--debug]",
  );
  process.exit(values.help ? 0 : 2);
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const bundlePath = pathResolve(
  __dirname,
  "node_modules/dom-to-pptx/dist/dom-to-pptx.bundle.js",
);

const inputPath = pathResolve(values.input);
const outputPath = pathResolve(values.output);
const deckDir = dirname(inputPath);
const deckFilename = basename(inputPath);
const svgVector = values["svg-vector"] && !values["no-svg-vector"];
const viewport = {
  width: parseInt(values["viewport-width"], 10),
  height: parseInt(values["viewport-height"], 10),
};

await mkdir(dirname(outputPath), { recursive: true });

const { server, port } = await serveDeckDir(deckDir);
const inputUrl = `http://127.0.0.1:${port}/${deckFilename}`;

const browser = await chromium.launch({ headless: true });
let exitCode = 0;
try {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 2 });
  const page = await context.newPage();

  if (values.debug) {
    page.on("console", (msg) => console.log("[page]", msg.type(), msg.text()));
    page.on("pageerror", (err) => console.error("[page error]", err.message));
  }

  await page.goto(inputUrl, { waitUntil: "networkidle" });

  // Wait for web fonts (Space Grotesk, Inter) — without this dom-to-pptx
  // captures fallback typefaces.
  await page.evaluate(() => document.fonts && document.fonts.ready);

  // Force-reveal + freeze: every .slide gets `.visible`, all animations and
  // transitions are disabled so the captured state is fully settled.
  await page.addStyleTag({
    content: `*, *::before, *::after {
      animation: none !important;
      transition: none !important;
    }`,
  });
  await page.evaluate(() => {
    document
      .querySelectorAll(".slide")
      .forEach((s) => s.classList.add("visible"));
  });

  // Slide-background propagation: the brand puts `background: #0a0a0a` (or
  // light) on `<body>`, and `.slide` is transparent. In a browser this looks
  // fine because the body shines through; dom-to-pptx walks each slide
  // independently and sees no per-slide bg, leaving every slide white in
  // the rendered PPTX. Copy the body's computed background-color onto every
  // .slide before export so each slide carries its own settled bg.
  //
  // Image-fill fixup: dom-to-pptx places <img> elements at their intrinsic
  // dimensions or computed-style dimensions, but the brand's image asides
  // use width:100%; height:100% inside a parent with aspect-ratio. The img
  // ends up rendered at its natural ratio, leaving empty bands inside the
  // aside box. Force explicit pixel width/height attributes from the
  // parent's bounding rect so dom-to-pptx writes the img at the box bounds.
  await page.evaluate(() => {
    const bodyBg = getComputedStyle(document.body).backgroundColor;
    const bodyColor = getComputedStyle(document.body).color;
    document.querySelectorAll(".slide").forEach((s) => {
      s.style.backgroundColor = bodyBg;
      s.style.color = bodyColor;
    });
    // Force img dimensions inside slide-image asides and slide-bg img tags
    // to fill their parent box exactly (matches the visual browser behavior
    // of width:100%/height:100% + object-fit:cover).
    document
      .querySelectorAll("aside.slide-image img, img.slide-bg")
      .forEach((img) => {
        const parent = img.parentElement;
        if (!parent) return;
        const r = parent.getBoundingClientRect();
        img.setAttribute("width", String(Math.round(r.width)));
        img.setAttribute("height", String(Math.round(r.height)));
        img.style.width = `${r.width}px`;
        img.style.height = `${r.height}px`;
        img.style.objectFit = "cover";
      });
  });

  // Inject dom-to-pptx browser bundle (UMD: attaches to window.domToPptx).
  await page.addScriptTag({ path: bundlePath });

  // Render. dom-to-pptx returns a Blob when skipDownload is true.
  const blobBytes = await page.evaluate(
    async ({ svgAsVector }) => {
      const slides = Array.from(document.querySelectorAll(".slide"));
      if (slides.length === 0) {
        throw new Error('No <section class="slide"> elements found in deck.');
      }
      // dom-to-pptx attaches its API as a UMD global. Naming differs by
      // version: try both common shapes.
      const api = window.domToPptx || window["dom-to-pptx"] || {};
      const exporter = api.exportToPptx || api.default?.exportToPptx;
      if (typeof exporter !== "function") {
        throw new Error(
          "dom-to-pptx exportToPptx not found on window. Bundle may have failed to load.",
        );
      }
      const blob = await exporter(slides, {
        fileName: "export.pptx",
        skipDownload: true,
        svgAsVector,
        autoEmbedFonts: true,
        // Modern widescreen 16:9 (13.333" x 7.5"). dom-to-pptx defaults to
        // the legacy 10" x 5.625" frame, which makes 1920px-wide HTML
        // content render small inside the PPTX. The `width`/`height`
        // options are accepted publicly but not documented in USAGE.md;
        // they map to pptxgen's defineLayout internally.
        width: 13.333,
        height: 7.5,
      });
      if (!(blob instanceof Blob)) {
        throw new Error(`exportToPptx returned ${typeof blob}, not a Blob.`);
      }
      const buf = await blob.arrayBuffer();
      return Array.from(new Uint8Array(buf));
    },
    { svgAsVector: svgVector },
  );

  await writeFile(outputPath, Buffer.from(blobBytes));
  const kb = (blobBytes.length / 1024).toFixed(1);
  console.log(`✓ wrote ${outputPath} (${kb} KB)`);
} catch (err) {
  console.error("✗ render failed:", err.message);
  if (values.debug && err.stack) console.error(err.stack);
  exitCode = 1;
} finally {
  await browser.close();
  server.close();
}

process.exit(exitCode);
