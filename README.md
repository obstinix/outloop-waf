<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Tests-39%2F39%20Passing-success?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/Vercel-Deployed-black?style=for-the-badge&logo=vercel" alt="Vercel">
</p>

<h1 align="center">OUTERLOOP WAF</h1>

<p align="center">
  <strong>Perimeter-Grade Web Attack Protection</strong><br>
  Real-time threat detection | Middleware-based inspection | Serverless architecture
</p>

<p align="center">
  <a href="https://outerloop-waf.vercel.app">🌐 Live Demo</a> •
  <a href="https://outerloop-waf.vercel.app/api/docs">📚 API Docs</a> •
  <a href="#quick-start">🚀 Quick Start</a>
</p>

---

## 🌐 Live Deployment

**Production URL:** https://outerloop-waf.vercel.app

| Endpoint | URL |
|----------|-----|
| Dashboard | https://outerloop-waf.vercel.app |
| API Documentation | https://outerloop-waf.vercel.app/api/docs |
| Health Check | https://outerloop-waf.vercel.app/api/health |
| WAF Test | https://outerloop-waf.vercel.app/api/secure/test |

---

## Problem Statement

Modern web applications face constant threats from automated attacks, injection attempts, and malicious payloads. Traditional security approaches require expensive hardware appliances or complex configurations. **OUTERLOOP WAF** solves this by providing:

- **Edge-ready security** configured for instant cloud deployment
- **Low-latency request filtering** with minimal overhead
- **Pattern-based detection** against major OWASP Top 10 threat patterns
- **Serverless-native** stateless design with optional Redis persistence

---

## How It Works

OUTERLOOP operates as **middleware** that intercepts every HTTP request before it reaches your application, running sliding-window rate limit checks, header validations, multi-pass decoding, and regex rule matching:

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

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.9+ / FastAPI | High-performance async API |
| **Persistence** | Upstash Redis | Edge-compatible persistent IP blocklists and statistics |
| **WAF Engine** | Custom regex engine | Pattern-based threat detection with 43 security patterns |
| **Frontend** | HTML/CSS/JS + Three.js | Dashboard with 3D attack globe and SSE live threat stream |
| **Deployment** | Vercel Serverless | Edge-distributed, auto-scaling |
| **Testing** | Pytest | Evasion and validation test suites |

---

## 🔒 Admin API Reference

All admin API endpoints require the `X-Admin-Key` header with the value matching your configured `WAF_ADMIN_KEY`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/blocklist` | Manually block an IP address. Expects JSON: `{"ip": "1.2.3.4", "reason": "abusive behaviour"}`. |
| `DELETE` | `/api/admin/blocklist/{ip}` | Unblock an IP address. |
| `GET` | `/api/admin/blocklist` | List all blocked IP addresses. |
| `GET` | `/api/admin/stats` | Retrieve persistent global WAF metrics. |
| `GET` | `/api/admin/rules` | Retrieve list of compiled WAF regex rule definitions. |

---

## ⚙️ Environment Variables

Copy the `.env.example` file to `.env` and configure the following variables:

- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: `https://outerloop-waf.vercel.app,http://localhost:3000`).
- `WAF_ADMIN_KEY`: API token required to authorize `/api/admin/*` endpoints.
- `UPSTASH_REDIS_REST_URL`: Upstash Redis REST URL for persistent IP blocklists, rate limiting, and global request statistics.
- `UPSTASH_REDIS_REST_TOKEN`: Upstash Redis REST authentication token.
- `RATE_BURST_REQUESTS`: Max requests allowed within the burst window per IP (default: `20`).
- `RATE_BURST_SECONDS`: Duration of the burst rate limit window in seconds (default: `1`).
- `RATE_GLOBAL_REQUESTS`: Max requests allowed within the global window per IP (default: `300`).
- `RATE_GLOBAL_SECONDS`: Duration of the global rate limit window in seconds (default: `60`).
- `ENVIRONMENT`: App environment mode (`development` or `production`). Production enables JSON structured logging.

---

## Attack Vectors Protected

### SQL Injection
```bash
# Returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload='; DROP TABLE users;--"
```

### Cross-Site Scripting (XSS)
```bash
# Returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=<script>alert(1)</script>"
```

### Path Traversal
```bash
# Returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=../../etc/passwd"
```

### Command Injection
```bash
# Returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=\$(whoami)"
```

### Clean Request
```bash
# Returns 200 OK - safe request passes through
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=hello"
```

---

## Quick Start

### Local Development (Python)

```bash
# Clone repository
git clone https://github.com/obstinix/Web-Application-Firewall-WAF-.git
cd Web-Application-Firewall-WAF-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn api.index:app --reload --port 8000
```

Access the dashboard at http://localhost:8000 and the API docs at http://localhost:8000/api/docs.

### Local Development (Docker & Compose)

Start the WAF application and a local Redis container automatically:

```bash
# Start all services in detached mode
docker-compose up --build -d

# View real-time logs
docker-compose logs -f

# Shut down and clean up containers
docker-compose down
```

---

## Testing & Linting

All tests are verified and passing locally:

```
tests/test_admin.py         ✓ 3 passed
tests/test_antigravity.py   ✓ 3 passed
tests/test_evasion.py       ✓ 2 passed
tests/test_events.py        ✓ 1 passed
tests/test_health.py        ✓ 6 passed
tests/test_rate_limiter.py  ✓ 1 passed
tests/test_waf.py           ✓ 23 passed
────────────────────────────────────────
TOTAL:                      ✓ 39 passed
```

### Run Tests Locally
```bash
pytest -v
```

### Lint & Type Check
```bash
# Lint code checks
ruff check api/

# Static type checking
mypy api/
```

---

## Project Structure

```
outloop-waf/
├── .github/workflows/ci.yml  # GitHub Actions CI pipeline
├── api/
│   ├── index.py              # FastAPI application root & CORS
│   ├── static/index.html     # Real HTML dashboard & SSE client
│   ├── waf/
│   │   ├── middleware.py     # Request interceptor & trusted proxy resolver
│   │   ├── rules.py          # Compiled regex security patterns
│   │   ├── rate_limiter.py   # Per-IP sliding-window rate limiter
│   │   └── engine.py         # Threat analysis & event emitter
│   ├── routes/
│   │   ├── health.py         # Detailed and basic health endpoints
│   │   ├── secure.py         # Request sandbox & mock database endpoints
│   │   ├── admin.py          # Authorized WAF management API
│   │   ├── events.py         # Server-Sent Events (SSE) stream endpoint
│   │   ├── metrics.py        # Prometheus monitoring metrics
│   │   └── gravity.py        # Easter egg activator
│   ├── core/
│   │   ├── logic.py          # Internal health checker
│   │   ├── redis_client.py   # Upstash Redis connection client
│   │   └── antigravity.py    # xkcd Easter egg module
│   └── utils/logger.py       # JSON production & colored dev logger
├── tests/                    # Integration and unit tests
├── Dockerfile                # Production Docker container definition
├── docker-compose.yml        # Development environment composer
├── vercel.json               # Vercel deployment routes and security headers
└── requirements.txt          # Python dependencies
```

---

## Features

- ✅ **SQL Injection Protection** - Context-aware patterns and evasion checks
- ✅ **XSS Prevention** - Mixed-case tags, events, and polyglot detection
- ✅ **SSRF & SSTI Defense** - Checks internal IP access and template interpolation
- ✅ **Sliding-Window Rate Limiting** - Burst and global per-IP throttling
- ✅ **Upstash Redis State** - Shared blocklist and metrics across serverless functions
- ✅ **Server-Sent Events (SSE)** - Real-time threat feed streamed directly to dashboard
- ✅ **Prometheus metrics** - `/api/metrics` export for system monitoring
- ✅ **Structured JSON logs** - production log shipping formatting

---

## License

MIT License - See [LICENSE](LICENSE)

---

<p align="center">
  <strong>OUTERLOOP WAF</strong> | Perimeter-Grade Web Attack Protection<br>
  <a href="https://outerloop-waf.vercel.app">https://outerloop-waf.vercel.app</a>
</p>
