# UI Changelog — OUTLOOP WAF

This document registers all visual, behavioral, and structural changes introduced during the OUTLOOP WAF frontend rebuild.

---

## [1.1.0] — 2026-06-18

### Architectural Refactoring
* **Decoupled Frontend Structure:** Extracted inline scripts and stylesheets from `index.html` into independent files: [app.js](file:///Users/apple/Documents/antigravity/goofy-heisenberg/api/static/app.js) and [style.css](file:///Users/apple/Documents/antigravity/goofy-heisenberg/api/static/style.css).
* **Static Assets Route:** Configured and mounted `/static` directory in [index.py](file:///Users/apple/Documents/antigravity/goofy-heisenberg/api/index.py) using FastAPI's `StaticFiles` middleware to serve external assets securely.

### Design System & Visuals
* **Premium Typography:** Bound `Space Grotesk` (sans-serif) for all headers, metrics, and structural titles. Bound `JetBrains Mono` (monospace) for telemetry elements, rule patterns, and console feeds.
* **Modern Grays:** Replaced the cyberpunk green-on-black neon theme with a professional layout using layered neutral grays (`#07070a` canvas base up to `#1e1e28` high-contrast borders).
* **WCAG 2.1 AA Semantic Colors:** Configured high-contrast semantic palettes for security levels:
  * **Critical:** Red (`#ef4444`)
  * **High:** Orange (`#f97316`)
  * **Medium:** Yellow (`#f59e0b`)
  * **Low/Info:** Blue (`#3b82f6`)
  * **Healthy/OK:** Green (`#10b981`)
* **Micro-Animations:** Implemented viewport reveal fade-ins and scale animations using GSAP and ScrollTrigger.
* **Custom Layout Controls:** Implemented consistent border-radii (`4px` for buttons/badges, `6px` for small grids, `8px` for primary panels) and thin solid border lines.

### Features & Layout Rebuild
1. **Startup Boot Sequence:** Replaced slow, decorative ASCII loader with a clean, fast connection verification sequence checking `/api/health`, `/api/version`, rules count, and SSE listener status.
2. **Command Center:** Redesigned hero section into a split operational panel:
  * **Left:** Protection shield status indicators, environment metadata, and main CTA actions.
  * **Right:** Terminal console showing live status checks of core, Redis, versioning, and live request metrics.
3. **Telemetry Overview:** Metrics grid upgraded with real-time count-up animations using GSAP, complete with status deltas computed every 15s.
4. **Interactive Attack Playground:**
  * Added preset buttons for SQLi, XSS, SSRF, RCE, LFI, Path Traversal, and Command Injection.
  * Integrated a 5-step **Detection Timeline** visualizing request progression (Inbound -> Decoder -> Match Engine -> Policy -> Verdict).
  * Added **Request Inspector** displaying raw HTTP headers on the left and WAF rule signature matches (Rule ID, description, severity, match snippet) on the right.
5. **Threat SOC Console:** Upgraded live threat feed to a dense table with timestamp, severity levels, rule ID, description, and source IP headers. Connected to real-time `/api/events/threats` with a 45s heartbeat timeout handler.
6. **Rule Intelligence Explorer:** Replaced simple HTML tables with a searchable rules index. Added input search (matching ID, name, regex pattern) and severity dropdown filters.
7. **SVG Pipeline Diagram:** Cleaned styling to match gray color tokens. Subtly highlighted flow pathways (Allow path in emerald, Block path in crimson).
8. **Administrative Workspace:** Revamped credentials manager panel (X-Admin-Key visibility toggle), system telemetry output, and perimeter ban/unban controls.
9. **Antigravity Diagnostics Toggle:** Added interactive gravity field in the status bar. Triggering the click calls the hidden `/api/gravity` signature endpoint, activating visual zero-g floating drift animations across all dashboard sections.
