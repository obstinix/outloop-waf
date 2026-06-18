# Design System — OUTLOOP WAF

This document defines the typography, spacing, and color system to transform OUTLOOP WAF into an enterprise-ready security product.

---

## 1. Typography

### Primary Sans-Serif
* **Family:** `Space Grotesk`, `Inter`, sans-serif
* **Usage:** Dashboard metrics, titles, structural cards, navigation elements.
* **Weights:** `400` (Regular), `500` (Medium), `600` (Semi-Bold), `700` (Bold)

### Technical Mono
* **Family:** `JetBrains Mono`, monospace
* **Usage:** Code snippets, terminal logs, rule patterns, telemetry values, IP addresses.
* **Weights:** `400` (Regular), `500` (Medium), `600` (Semi-Bold)

### Font Scale

| Token | Size (rem) | Size (px) | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `fs-xs` | `0.75rem` | `12px` | `1.4` | Badges, small metadata, micro-metrics |
| `fs-sm` | `0.8125rem` | `13px` | `1.5` | Code, table values, utility buttons |
| `fs-base` | `0.875rem` | `14px` | `1.5` | Dashboard body text, default labels |
| `fs-md` | `1.0rem` | `16px` | `1.5` | Secondary card titles, interactive prompts |
| `fs-lg` | `1.25rem` | `20px` | `1.4` | Section subtitles, terminal title bars |
| `fs-xl` | `1.5rem` | `24px` | `1.3` | Hero subheaders, primary panel titles |
| `fs-2xl` | `2.25rem` | `36px` | `1.2` | Hero headlines, major count values |
| `fs-3xl` | `3.5rem` | `56px` | `1.1` | Main dashboard hero values, landing stats |

---

## 2. Spacing System
All spacing is relative to the `16px` root font-size using `rem` units to support native browser scaling and accessibility.

| Spacing Token | Value (rem) | Value (px) | Typical Application |
| :--- | :--- | :--- | :--- |
| `space-1` | `0.25rem` | `4px` | Inner badge padding, text-icon gaps |
| `space-2` | `0.5rem` | `8px` | Small buttons, card inner list items, table rows |
| `space-3` | `0.75rem` | `12px` | Standard button padding, input field padding |
| `space-4` | `1.0rem` | `16px` | Content panel padding, element card gaps |
| `space-6` | `1.5rem` | `24px` | Main grid gaps, large dashboard sections |
| `space-8` | `2.0rem` | `32px` | Main section layout outer margins |
| `space-12` | `3.0rem` | `48px` | Section separators |
| `space-16` | `4.0rem` | `64px` | Hero section top/bottom padding |

---

## 3. Color System
All color combinations conform to the WCAG 2.1 AA contrast requirements. The UI uses a sleek dark mode with high contrast elements.

### Base Palette & Grays

```css
:root {
  /* Neutral Grays */
  --gray-950: #060608; /* Canvas backdrop (very dark) */
  --gray-900: #0b0b0e; /* Component panels, cards */
  --gray-800: #121217; /* Toolbars, input fields, header background */
  --gray-700: #1a1a22; /* Hover states, raised buttons */
  --gray-600: #2b2b36; /* Subtle border outlines */
  --gray-500: #3f3f4e; /* Disabled states, grid lines */
  --gray-400: #717185; /* Muted text, label details */
  --gray-300: #a1a1b5; /* Secondary text */
  --gray-100: #e4e4e7; /* Primary high-contrast text */
  --gray-50:  #f4f4f7; /* High-contrast headers, active text */
}
```

### Semantic Alerts
Each semantic color provides a low-opacity fill, a high-contrast label, and a defined border color.

| State | Variable | Hex | Contrast Ratio (vs `--gray-900`) |
| :--- | :--- | :--- | :--- |
| **Healthy** | `--green-500` | `#10b981` | `5.6:1` (Passes AA) |
| **Informational**| `--blue-500` | `#3b82f6` | `4.8:1` (Passes AA) |
| **Medium Threat**| `--yellow-500`| `#f59e0b` | `6.1:1` (Passes AA) |
| **High Threat** | `--orange-500`| `#f97316` | `5.2:1` (Passes AA) |
| **Critical Threat**| `--red-500` | `#ef4444` | `4.7:1` (Passes AA) |

### Focus & Accents
* **Accent/Brand:** `--accent-500` (`#4f46e5` - Indigo Blue)
* **Focus Outline:** `2px solid #3b82f6` with `2px` offset.
* **Selection:** `background: rgba(79, 70, 229, 0.25)`

---

## 4. UI Borders & Radii
To deliver a crisp, Warp/Linear-class application, borders are solid and border radii are consistent:
* **Small Radii (`--radius-sm`):** `4px` — Used for badges, buttons, input fields.
* **Medium Radii (`--radius-md`):** `6px` — Used for metric cells, table headers, small modals.
* **Large Radii (`--radius-lg`):** `8px` — Used for primary content sections, consoles, panels.
* **Borders:** `1px solid var(--gray-600)` or `1px solid var(--gray-700)` for secondary items.
