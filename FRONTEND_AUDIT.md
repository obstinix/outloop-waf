# Frontend Audit — OUTLOOP WAF

This document analyzes the architecture, user experience, design system, and technical constraints of the current OUTLOOP WAF frontend as of June 2026.

---

## 1. UX Problems

1. **Intrusive Boot Screen:** The startup animation uses low-fidelity ASCII art and slow sequential text loads. While attempting a "terminal feel," it blocks the user from viewing dashboard data for ~2 seconds on every refresh.
2. **Actionable Insights Deficit:** When the sandbox blocks a request, the output is listed as a raw list of rule violations. It does not guide the user on *why* it matched or *what* the mitigation steps are.
3. **Passive Threat Stream:** The threat operations list updates in real-time, but lacks detail (e.g., source region, HTTP method, user-agent details). It is not possible to inspect an individual threat row or block/allow it directly from the stream.
4. **Disconnected Admin Area:** The administration pane is hidden under a drawer at the bottom of the page, separating configuration actions (like blocking an IP or setting keys) from the live stream.
5. **No Rule Relationships:** The rules database is shown as a flat table without grouping by threat level, category, or mapping rules to actual attack payload matches.

---

## 2. Design Debt

1. **"Hacker Movie" Aesthetic:** The green-on-black, monospaced-heavy, bracket-bound UI (`[→ Try the Sandbox]`) looks like a hobby project or developer demo rather than enterprise-grade security software.
2. **Inconsistent Color Contrast:** Semantic colors (green, amber, red) are applied as glowing borders or text tags that lack structural consistency and make the page feel busy.
3. **Typography Misalignment:** Monospace fonts are overused for body text, reading labels, and table content, reducing readability. Headings lack clear optical weights.
4. **Arbitrary Box Model Values:** Borders, padding, and border-radius are inconsistent (`4px` on buttons, `6px` on panels, `3px` on badges) creating a disjointed grid alignment.
5. **Lack of Visual Depth:** The interface lacks layered grays, crisp borders, and subtle focus states characteristic of modern tools like Linear or Warp.

---

## 3. Technical Debt

1. **Monolithic Single-File codebase:** The entire frontend is packed into `api/static/index.html` (2,800+ lines), mixing structure, styling, SVG diagrams, and API logic. This prevents caching, parallel loads, and modular code ownership.
2. **Direct DOM-Style Mutation:** State is managed via a mutable global object (`WAF_STATE`). DOM elements are queried and overwritten directly (e.g., `document.getElementById("sb-req").textContent = ...`).
3. **Inline Event Handlers:** Code uses obsolete `onclick="..."` and inline attributes rather than modern event delegation or programmatic listeners.
4. **No API Client Layer:** Fetch calls are written ad-hoc inside various UI click handlers, using duplicated headers and credentials.
5. **Brittle SSE Stream Lifespan:** The EventSource stream does not handle reconnection back-off cleanly and uses a basic interval to check for "silent periods."

---

## 4. Accessibility Failures (WCAG 2.1 AA)

1. **Contrast Violation:** Base text styles like `--text-3: #5A5A6A` against `--bg-panel: #0F0F13` yield a contrast ratio of `1.9:1`, failing the required `4.5:1` ratio for readable text.
2. **Keyboard Inoperability:** Custom interactive cards (like rule category panels) are marked as `div` elements and cannot be focused or triggered via keyboard navigation (`Tab` + `Enter`).
3. **Missing Screen Reader Landmarks:** Interactive states (like the payload analysis result loading and blocking) lack `aria-live` regions, meaning screen readers are not notified of WAF block events.

---

## 5. Performance Bottlenecks

1. **Blocking External Resources:** Fonts, GSAP, and ScrollTrigger scripts are loaded from external CDNs, making the app dependent on network speed and rendering blocking frames.
2. **Layout Shifts (CLS):** Count-up animations and asynchronous stats updates cause text expansions, shifting adjacent panels.
3. **Lack of Cache Headers for Assets:** The FastAPI server explicitly sends `Cache-Control: no-store` headers on index.html, forcing the browser to redownload all assets and scripts on every page load.

---

## 6. Competitive Analysis

| Competitor / Inspiration | Typography | Layout Density | Spacing & Borders | Interactive Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **Linear** | Space Grotesk/Inter, crisp hierarchy | Moderate-High, command bar driven | Strict 8px grid, subtle 1px border lines | High micro-animations, keyboard-first |
| **Datadog** | Sans-serif metrics, Mono values | High, metric grid, widget-based | Solid background layering, high contrast | Actionable click-throughs to logs |
| **Cloudflare** | Clean Sans, Mono for code elements | High, multi-column data views | Light/dark grays, thin borders | Instant filters, clear warning banners |
| **Ghostty / Warp** | JetBrains Mono | Dense terminal layout | Ultra-thin borders, minimal padding | Prompt-focused, immediate execution |
| **OUTLOOP WAF (Current)** | Overused Monospace, inconsistent | Low-Moderate, single column stack | Cyberpunk glowing borders, neon accents | Delayed fake boot loader, raw text outputs |

### Identified Gaps:
* **Density:** We need to transition from a single-column layout into a dense, multi-column dashboard dashboard.
* **Control Center:** We need a keyboard-centric command palette or a dense control panel.
* **Playground:** The payload simulator must show a step-by-step visual pipeline (timeline) rather than a simple text output.
