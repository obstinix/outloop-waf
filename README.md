<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Tests-40%2F40%20Passing-success?style=for-the-badge" alt="Tests">
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

- **Zero-config security** that activates on deployment
- **Sub-5ms latency** with no performance degradation
- **Pattern-based detection** against OWASP Top 10 threats
- **Serverless-native** design for cloud-first architectures

---

## How It Works

OUTERLOOP operates as **middleware** that intercepts every HTTP request before it reaches your application:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT REQUEST                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTERLOOP MIDDLEWARE                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Header    │  │   Content   │  │      Multi-pass        │  │
│  │ Validation  │──│  Decoding   │──│   Pattern Matching     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
                  ▼                               ▼
         ┌─────────────┐                 ┌─────────────────┐
         │   THREAT    │                 │   CLEAN         │
         │  DETECTED   │                 │   REQUEST       │
         └──────┬──────┘                 └────────┬────────┘
                │                                 │
                ▼                                 ▼
         ┌─────────────┐                 ┌─────────────────┐
         │ 403 BLOCKED │                 │  APPLICATION    │
         │  + Logged   │                 │    LOGIC        │
         └─────────────┘                 └─────────────────┘
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.11+ / FastAPI | High-performance async API |
| **WAF Engine** | Custom regex engine | Pattern-based threat detection |
| **Frontend** | HTML/CSS/JS + Three.js | Dashboard with 3D attack globe |
| **Deployment** | Vercel Serverless | Edge-distributed, auto-scaling |
| **Testing** | Pytest | 40 tests covering all vectors |

---

## Attack Vectors Protected

### SQL Injection (13 patterns)
```bash
# Try on live site - returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload='; DROP TABLE users;--"
```

### Cross-Site Scripting (13 patterns)
```bash
# Try on live site - returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=<script>alert(1)</script>"
```

### Path Traversal (9 patterns)
```bash
# Try on live site - returns 403 BLOCKED
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=../../etc/passwd"
```

### Clean Request
```bash
# Returns 200 OK - safe request passes through
curl "https://outerloop-waf.vercel.app/api/secure/test?payload=hello"
```

---

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/obstinix/Web-Application-Firewall-WAF-.git
cd Web-Application-Firewall-WAF-

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn api.index:app --reload --port 8000

# Access locally
# Dashboard: http://localhost:8000
# API Docs:  http://localhost:8000/api/docs
```

### Deploy to Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

---

## Testing Results

All 40 tests pass:

```
tests/test_health.py        ✓ 6 passed
tests/test_waf.py           ✓ 21 passed  
tests/test_antigravity.py   ✓ 13 passed
────────────────────────────────────────
TOTAL:                      ✓ 40 passed
```

Run tests locally:
```bash
pytest -v
```

---

## Project Structure

```
Web-Application-Firewall-WAF-/
├── api/
│   ├── index.py              # FastAPI entry point
│   ├── static/index.html     # Dashboard with 3D globe
│   ├── waf/
│   │   ├── middleware.py     # Request interception
│   │   ├── rules.py          # 35+ security patterns
│   │   └── engine.py         # Threat analysis engine
│   ├── routes/
│   │   ├── health.py         # Health endpoints
│   │   ├── secure.py         # Protected endpoints
│   │   └── gravity.py        # Status endpoints
│   └── utils/logger.py       # Structured logging
├── tests/                    # 40 test cases
├── vercel.json               # Serverless config
└── requirements.txt          # Python dependencies
```

---

## Features

- ✅ **SQL Injection Protection** - 13 detection patterns
- ✅ **XSS Prevention** - Script tags, event handlers, protocols
- ✅ **Path Traversal Detection** - Multi-pass URL decoding
- ✅ **Header Validation** - CRLF injection, overflow protection
- ✅ **Request Tracking** - Unique IDs for audit logging
- ✅ **3D Attack Globe** - Animated cyber attack visualization
- ✅ **Real-time Demo** - Live terminal showing WAF in action

---

## License

MIT License - See [LICENSE](LICENSE)

---

<p align="center">
  <strong>OUTERLOOP WAF</strong> | Perimeter-Grade Web Attack Protection<br>
  <a href="https://outerloop-waf.vercel.app">https://outerloop-waf.vercel.app</a>
</p>
