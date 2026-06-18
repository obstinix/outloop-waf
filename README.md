<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.0.0-green?style=for-the-badge&logo=github" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Tests-44%2F44%20Passing-success?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/Vercel-Deployed-black?style=for-the-badge&logo=vercel" alt="Vercel">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
</p>

<h1 align="center">🛡️ OUTLOOP WAF</h1>

<p align="center">
  <strong>Perimeter-Grade Web Application Firewall & Security Operations Center (SOC)</strong><br>
  Real-Time Threat Detection | Serverless Edge Filtering | Sliding-Window Rate Limiting
</p>

---

## 🌐 Live Deployment & Workspace Links

Here are the live deployment urls and module-specific shortcuts:

| Module / View | Live URL |
|---|---|
| **Overview SOC Dashboard** | [https://outloop-waf.vercel.app/](https://outloop-waf.vercel.app/) |
| **Payload Sandbox Simulator** | [https://outloop-waf.vercel.app/#playground](https://outloop-waf.vercel.app/#playground) |
| **Threat Operations Stream** | [https://outloop-waf.vercel.app/#threats](https://outloop-waf.vercel.app/#threats) |
| **Signature Explorer** | [https://outloop-waf.vercel.app/#rules](https://outloop-waf.vercel.app/#rules) |
| **Request Validation Pipeline** | [https://outloop-waf.vercel.app/#pipeline](https://outloop-waf.vercel.app/#pipeline) |
| **WAF Administration Workspace** | [https://outloop-waf.vercel.app/#admin](https://outloop-waf.vercel.app/#admin) |
| **GitHub Repository** | [https://github.com/obstinix/outloop-waf](https://github.com/obstinix/outloop-waf) |

---

## 📢 Release Notes: Version 1.0.0 (New Release)

* **Current Status:** **Version 1.0.0** (Stable Production Release)
* **Previous Version:** **Version 0.x** (Initial terminal UI mockup prototype)

### What's New in v1.0.0:
* **High-Density SOC Theme:** Upgraded layout to a professional dark mode dashboard inspired by Linear and Cloudflare.
* **Serverless Static asset Fallbacks:** Configured robust fallback paths at `/static/...` and `/api/static/...` with explicit MIME-types to satisfy strict CDN/browser `X-Content-Type-Options: nosniff` headers under Vercel.
* **Python 3.9 Compatibility:** Resolved local ASGI connection thread crashes by updating threat streams to handle `asyncio.TimeoutError` correctly on Python 3.9+.
* **All Tests Passing:** 44/44 backend security test cases verified and passing.

---

## Problem Statement

Modern web applications face constant threats from automated scanners, injection scripts, and malicious inputs. **OUTLOOP WAF** addresses this by providing an edge-ready, extremely low-latency security layer that validates inbound requests before they reach downstream servers.

- **Low-latency request filtering** with minimal overhead (< 5ms)
- **Zero-Trust perimeter defense** blocking major OWASP Top 10 vulnerabilities
- **Serverless-native** stateless architecture with optional Upstash Redis state synchronization

---

## How It Works

OUTLOOP operates as **FastAPI Middleware** that intercepts every incoming request. It validates signatures, enforces rate limits, decodes content obfuscation, and determines access authorization:

```
                                 CLIENT REQUEST
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   WAF MIDDLEWARE ENTRY    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ Rate Limiter (IP Sliding) │◄──── (Redis / Memory)
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  Header & Method Checks   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    Multi-pass Decoding    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ Pattern Rule Inspection   │
                         └─────────────┬─────────────┘
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
                THREAT DETECTED                  CLEAN REQUEST
                       │                               │
                       ▼                               ▼
           ┌───────────────────────┐       ┌───────────────────────┐
           │  Block Request (403)  │       │  Forward to App Logic │
           │   + Increment Stats   │       │   + Increment Stats   │
           │   + Emit SSE Event    │       │     (Redis/Memory)    │
           │    (Redis/Memory)     │       └───────────────────────┘
           └───────────────────────┘
```

---

## ⚔️ Attack Vectors & Protection Mechanisms

### 1. SQL Injection (SQLi)
* **Description:** Attackers insert malicious SQL statements into input fields to view, edit, or delete database values.
* **WAF Protection:** Uses multi-pass decoding to catch hex or double-URL encoding bypasses. Scans query variables and bodies for SQL keywords (`SELECT`, `UNION`, `DROP`), tautologies (`OR 1=1`), comment markers (`--`, `/*`), schema tables (`INFORMATION_SCHEMA`), and stacked commands.
* **Test Payloads:**
  ```sql
  -- Auth Bypass
  ' OR '1'='1
  " OR 1=1 --
  
  -- UNION-Based Data Extraction
  ' UNION SELECT username, password FROM users --
  
  -- Time-based Blind SQLi
  '; WAITFOR DELAY '0:0:5' --
  
  -- Stacked command
  ; DROP TABLE users; --
  ```

### 2. Cross-Site Scripting (XSS)
* **Description:** Attackers inject malicious JavaScript scripts into pages viewed by other users.
* **WAF Protection:** Scans content for `<script>` tags, inline event handler attributes (`onload`, `onerror`), script protocols (`javascript:`), tag injections (`<iframe>`, `<object>`, `<embed>`), and typical execution functions (`alert()`, `eval()`).

### 3. Command Injection
* **Description:** Executing arbitrary shell commands on the hosting operating system.
* **WAF Protection:** Blocks system chaining characters (`;`, `|`, `&&`, `||`), backticks (`` `...` ``), subshell calls (`$(...)`), and standard system command signatures (`cat`, `wget`, `curl`, `whoami`, `id`, `uname`, `ps`).

### 4. Path Traversal
* **Description:** Navigating relative directory paths to access restricted files outside the web root.
* **WAF Protection:** Blocks sequence traversal operators (`../`, `..\`), hex-encoded traversal (`%2e%2e%2f`), and attempts to load sensitive operating system directories (like `/etc/passwd`, `/etc/shadow`, `c:\windows`).

### 5. Server-Side Request Forgery (SSRF)
* **Description:** Coerces the server into making unauthorized requests to internal network locations.
* **WAF Protection:** Blocks access queries pointing to cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`) and private IP ranges (`10.x.x.x`, `172.16.x.x`, `192.168.x.x`).

---

## 🚀 Live Testing Commands

You can verify threat detection instantly by firing these payloads at the secure test route:

```bash
# Test SQL Injection Protection (Expect 403 Forbidden)
curl -i "https://outloop-waf.vercel.app/api/secure/test?payload='%20UNION%20SELECT%20username,%20password%20FROM%20users%20--"

# Test XSS Protection (Expect 403 Forbidden)
curl -i "https://outloop-waf.vercel.app/api/secure/test?payload=<script>alert(document.cookie)</script>"

# Test Path Traversal Protection (Expect 403 Forbidden)
curl -i "https://outloop-waf.vercel.app/api/secure/test?payload=../../../../etc/passwd"

# Test Command Injection Protection (Expect 403 Forbidden)
curl -i "https://outloop-waf.vercel.app/api/secure/test?payload=\$(whoami)"

# Test Clean Request (Expect 200 OK)
curl -i "https://outloop-waf.vercel.app/api/secure/test?payload=HelloWAF"
```

---

## ⚙️ Core Configuration

### Environment Variables (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `WAF_ADMIN_KEY` | `your_secret_key` | Secret key required to access `/api/admin/*` routes. |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Allowed CORS client origins. |
| `UPSTASH_REDIS_REST_URL` | *Optional* | Upstash Redis connection endpoint for persistent statistics and IP blocklists. |
| `UPSTASH_REDIS_REST_TOKEN` | *Optional* | Upstash Redis auth token. |
| `RATE_BURST_REQUESTS` | `20` | Max requests allowed in the burst window. |
| `RATE_BURST_SECONDS` | `1` | Burst rate limiter window size. |

---

## 🔒 Administrative Endpoint Reference

Manage global WAF status and enforce IP blocks with the `X-Admin-Key` header.

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/admin/blocklist` | Block an IP address (`{"ip": "1.2.3.4", "reason": "abusive request patterns"}`). |
| `DELETE` | `/api/admin/blocklist/{ip}` | Remove an IP from the blocklist. |
| `GET` | `/api/admin/blocklist` | List all blocked IP addresses. |
| `GET` | `/api/admin/stats` | Retrieve detailed stats from the WAF assessment engine. |
| `GET` | `/api/admin/rules` | Fetch a list of all active security rules. |

---

## 🛠️ Local Development

### Prerequisites & Installation

```bash
# Clone the repository
git clone https://github.com/obstinix/outloop-waf.git
cd outloop-waf

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the backend locally
uvicorn api.index:app --reload --port 8080
```

Access the local dashboard at `http://localhost:8080/` and Swagger documentation at `http://localhost:8080/api/docs`.

### Docker Environment

Run the containerized application:
```bash
docker-compose up --build
```

---

## 🧪 Testing & Code Quality

Verify tests locally with `pytest`:
```bash
./venv/bin/pytest -v
```
All 44 test suites are verified:
* **`test_waf.py`** (23 checks): Validates SQLi, XSS, and command evasion blocks.
* **`test_health.py`** (6 checks): Verifies detailed and basic uptime checks.
* **`test_antigravity.py`** (3 checks): Validates Easter Egg constants and status logic.
* **`test_admin.py`** (3 checks): Verifies admin endpoint authentication.

---

## 🤝 Contributing & Issue Tracking

If you find a bug, have a feature request, or would like to submit a improvement:
1. **GitHub Issues:** Head over to our [Issues Section](https://github.com/obstinix/outloop-waf/issues) to report bugs or search for planned enhancements.
2. **Pull Requests:** 
   * Fork the repository.
   * Create a feature branch (`git checkout -b feature/cool-new-filter`).
   * Commit your work (`git commit -m "feat: add new WAF injection detection filter"`).
   * Open a Pull Request for review.

---

## 📄 License

This software is distributed under the **MIT License**. See [LICENSE](LICENSE) for the full license text.

Copyright (c) 2026 **obstinix**
