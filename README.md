# Web Application Firewall

A production-grade Web Application Firewall (WAF) built with FastAPI, featuring middleware-based request inspection, real-time threat detection, and serverless deployment architecture.

## Overview

This project implements a comprehensive WAF solution that protects web applications from common attack vectors including SQL injection, cross-site scripting (XSS), path traversal, and command injection attacks.

The WAF operates as middleware, intercepting and analyzing all incoming HTTP requests before they reach application logic. Threats are detected using pattern-based rules with multi-pass decoding to catch obfuscated attacks.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Request   │────▶│  WAF Middleware  │────▶│ Analysis Engine │────▶│ Allow/Block  │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
                            │                         │
                            ▼                         ▼
                    ┌──────────────┐          ┌──────────────┐
                    │   Headers    │          │ Security     │
                    │  Validation  │          │ Rules        │
                    └──────────────┘          └──────────────┘
```

### Components

- **WAF Middleware** (`api/waf/middleware.py`): FastAPI middleware that intercepts all requests
- **Security Rules** (`api/waf/rules.py`): Pattern-based detection rules for various attack types
- **Analysis Engine** (`api/waf/engine.py`): Core processing engine that evaluates requests
- **Routes**: API endpoints including health checks, secure endpoints, and system status

## Security Features

### SQL Injection Protection
- Detects SQL keywords and dangerous combinations
- Catches UNION-based, time-based, and error-based injection attempts
- Protects against schema enumeration

### XSS Prevention
- Script tag detection
- Event handler attribute filtering
- JavaScript protocol blocking
- SVG/IMG onload injection prevention

### Path Traversal Detection
- Directory traversal pattern matching
- URL-encoded attack detection
- Null byte injection prevention

### Header Validation
- CRLF injection detection
- Header overflow protection
- Content-type validation

## Project Structure

```
├── api/
│   ├── index.py              # FastAPI entry point
│   ├── waf/
│   │   ├── middleware.py     # WAF request inspection
│   │   ├── rules.py          # Security rule definitions
│   │   └── engine.py         # Analysis engine
│   ├── core/
│   │   └── logic.py          # Business logic
│   ├── routes/
│   │   ├── health.py         # Health check endpoints
│   │   ├── secure.py         # WAF-protected endpoints
│   │   └── gravity.py        # System status
│   └── utils/
│       └── logger.py         # Logging utilities
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── index.astro   # Landing page
│   │   └── components/
│   │       └── GravityStatus.jsx
│   └── astro.config.mjs
├── tests/
│   ├── test_health.py
│   ├── test_waf.py
│   └── test_antigravity.py
├── vercel.json
├── requirements.txt
└── README.md
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api.index:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api

# Run specific test file
pytest tests/test_waf.py -v
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Basic health check |
| `/api/health/detailed` | GET | Detailed component status |
| `/api/ready` | GET | Kubernetes readiness probe |
| `/api/live` | GET | Kubernetes liveness probe |
| `/api/secure/info` | GET | WAF protection info |
| `/api/secure/process` | POST | WAF-protected data processing |
| `/api/secure/test` | GET | Test WAF blocking |
| `/api/gravity` | GET | System gravitational status |
| `/api/gravity/constants` | GET | Physical constants reference |
| `/api/docs` | GET | OpenAPI documentation |

## Deployment

### Vercel

This project is configured for deployment on Vercel's serverless platform.

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

The `vercel.json` configuration handles:
- Python serverless functions for `/api/*` routes
- Static site generation for the frontend
- Security headers on API responses

### Environment Variables

No environment variables are required for basic deployment. The application is stateless by design.

## Configuration

### WAF Bypass Paths

Certain paths bypass WAF inspection for performance:
- `/api/docs` - API documentation
- `/api/health` - Health checks
- `/favicon.ico` - Static assets

Configure in `api/waf/middleware.py`:

```python
BYPASS_PATHS = {
    "/api/docs",
    "/api/redoc",
    "/api/health",
    # Add custom paths
}
```

### Threat Level Handling

The WAF categorizes threats into levels:
- **CRITICAL/HIGH**: Request blocked with 403
- **MEDIUM/LOW**: Logged but allowed (configurable)

## Testing WAF

Send malicious payloads to test blocking:

```bash
# SQL Injection (blocked)
curl "http://localhost:8000/api/secure/test?payload='; DROP TABLE users; --"

# XSS (blocked)
curl "http://localhost:8000/api/secure/test?payload=<script>alert(1)</script>"

# Clean request (allowed)
curl "http://localhost:8000/api/secure/test?payload=Hello%20World"
```

## Performance

- **Stateless Design**: No database required, zero cold-start database connections
- **Efficient Pattern Matching**: Compiled regex patterns for fast evaluation
- **Request Tracking**: Each request receives a unique ID for auditing
- **Minimal Overhead**: Typically < 5ms added latency per request

## Security Considerations

- WAF provides defense-in-depth, not a complete security solution
- Regularly update security rules for new attack patterns
- Monitor logs for blocked requests and false positives
- Consider rate limiting for production deployments

---

There may be behavior in this system that only reveals itself under specific conditions.

## License

MIT License - See LICENSE file for details.
