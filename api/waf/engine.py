"""
WAF Engine

Core analysis engine that processes requests through the security
rules pipeline and generates threat assessments.
"""

import asyncio
import ipaddress
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union
from urllib.parse import unquote_plus as unquote

from api.core.redis_client import redis as _redis
from api.utils.logger import get_logger
from api.waf.rules import SecurityRules, ThreatLevel

BLOCKED_IPS_KEY = "waf:blocked_ips"
REQUEST_COUNTER_KEY = "waf:request_counter"
BLOCKED_COUNTER_KEY = "waf:blocked_counter"

logger = get_logger(__name__)


@dataclass
class ThreatAssessment:
    """Result of a WAF analysis on a request."""
    is_threat: bool
    threat_level: Union[ThreatLevel, None]
    violations: list[dict[str, Any]]
    timestamp: datetime
    request_id: str
    analysis_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        """Convert assessment to dictionary format."""
        return {
            "is_threat": self.is_threat,
            "threat_level": self.threat_level.value if self.threat_level else None,
            "violations": self.violations,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "analysis_time_ms": self.analysis_time_ms
        }


@dataclass
class RequestContext:
    """Encapsulates all analyzable parts of an HTTP request."""
    method: str
    path: str
    query_string: str
    headers: dict[str, str]
    body: Union[str, None]
    client_ip: str

    def get_all_content(self) -> str:
        """Combine all request content for analysis."""
        parts = [
            self.path,
            unquote(self.query_string) if self.query_string else "",
            self.body if self.body else ""
        ]

        # Include relevant header values
        suspicious_headers = ["user-agent", "referer", "cookie", "x-forwarded-for"]
        for header in suspicious_headers:
            if header in self.headers:
                parts.append(self.headers[header])

        return " ".join(parts)


class WAFEngine:
    """
    Web Application Firewall Analysis Engine

    Processes incoming requests through the security rules pipeline
    to detect and classify potential threats.
    """

    def __init__(self):
        """Initialize the WAF engine with security rules and state fallbacks."""
        self.rules = SecurityRules()
        # In-memory fallback (used when Redis is unavailable)
        self._local_blocked_ips: set = set()
        self._local_request_counter: int = 0
        self._local_blocked_counter: int = 0
        self._request_id_counter: int = 0
        self._event_queue: deque = deque(maxlen=100)
        self._event_listeners: list = []
        logger.info(f"WAF Engine initialized with {len(self.rules.get_all_rules())} rules")

    def emit_threat_event(self, event: dict):
        """Emit a threat event to all active SSE subscribers."""
        self._event_queue.append(event)
        for listener in self._event_listeners[:]:
            try:
                listener.put_nowait(event)
            except asyncio.QueueFull:
                pass

    def subscribe(self) -> asyncio.Queue:
        """Subscribe a new listener queue to threat events."""
        q: asyncio.Queue = asyncio.Queue(maxsize=50)
        self._event_listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        """Unsubscribe a listener queue."""
        try:
            self._event_listeners.remove(q)
        except ValueError:
            pass

    def _use_redis(self) -> bool:
        """Helper to check if Redis is configured and active."""
        return _redis is not None

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked."""
        if self._use_redis():
            return bool(_redis.sismember(BLOCKED_IPS_KEY, ip))
        return ip in self._local_blocked_ips

    def _generate_request_id(self) -> str:
        """Generate unique request identifier."""
        self._request_id_counter += 1
        return f"REQ-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self._request_id_counter:06d}"

    def _decode_content(self, content: str) -> str:
        """
        Apply multiple decoding passes to catch obfuscated attacks.

        Handles URL encoding, double encoding, and mixed encoding.
        """
        decoded = content

        # Multiple URL decode passes
        for _ in range(3):
            new_decoded = unquote(decoded)
            if new_decoded == decoded:
                break
            decoded = new_decoded

        return decoded

    def _validate_headers(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        """
        Validate request headers for anomalies.

        Checks for:
        - Malformed content-type
        - Suspicious header values
        - Header injection attempts
        """
        violations = []

        # Check for header injection (CRLF)
        for name, value in headers.items():
            if "\r" in value or "\n" in value:
                violations.append({
                    "rule_id": "HDR-001",
                    "rule_name": "Header Injection: CRLF",
                    "threat_level": ThreatLevel.HIGH.value,
                    "matched_content": f"{name}: [CRLF detected]"
                })

        # Check for excessively long header values
        max_header_length = 8192
        for name, value in headers.items():
            if len(value) > max_header_length:
                violations.append({
                    "rule_id": "HDR-002",
                    "rule_name": "Header Overflow",
                    "threat_level": ThreatLevel.MEDIUM.value,
                    "matched_content": f"{name}: [Length: {len(value)}]"
                })

        return violations

    def _validate_method(self, method: str, path: str) -> Union[dict[str, Any], None]:
        """Validate HTTP method is appropriate for the request."""
        dangerous_methods = ["TRACE", "TRACK", "DEBUG"]

        if method.upper() in dangerous_methods:
            return {
                "rule_id": "MTD-001",
                "rule_name": f"Dangerous HTTP Method: {method}",
                "threat_level": ThreatLevel.MEDIUM.value,
                "matched_content": f"{method} {path}"
            }

        return None

    def analyze(self, context: RequestContext) -> ThreatAssessment:
        """
        Perform comprehensive security analysis on a request.

        Args:
            context: The request context to analyze

        Returns:
            ThreatAssessment with detection results
        """
        start_time = datetime.utcnow()
        request_id = self._generate_request_id()
        violations: list[dict[str, Any]] = []

        logger.debug(f"Analyzing request {request_id}: {context.method} {context.path}")

        # Check if IP is blocked
        if self.is_ip_blocked(context.client_ip):
            violations.append({
                "rule_id": "IP-001",
                "rule_name": "Blocked IP",
                "threat_level": ThreatLevel.CRITICAL.value,
                "matched_content": context.client_ip
            })

        # Validate HTTP method
        method_violation = self._validate_method(context.method, context.path)
        if method_violation:
            violations.append(method_violation)

        # Validate headers
        header_violations = self._validate_headers(context.headers)
        violations.extend(header_violations)

        # Get and decode all content for analysis
        raw_content = context.get_all_content()
        decoded_content = self._decode_content(raw_content)

        # Run content through security rules
        rule_violations = self.rules.check_content(decoded_content)
        for rule, matched in rule_violations:
            violations.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "threat_level": rule.threat_level.value,
                "matched_content": matched[:100]  # Truncate for safety
            })

        # Also check raw content (some attacks rely on encoding)
        if raw_content != decoded_content:
            raw_violations = self.rules.check_content(raw_content)
            for rule, matched in raw_violations:
                # Avoid duplicates
                if not any(v["rule_id"] == rule.id for v in violations):
                    violations.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "threat_level": rule.threat_level.value,
                        "matched_content": matched[:100]
                    })

        # Calculate analysis time
        end_time = datetime.utcnow()
        analysis_time = (end_time - start_time).total_seconds() * 1000

        # Determine overall threat level
        is_threat = len(violations) > 0
        max_threat_level = None

        if is_threat:
            threat_priority = {
                ThreatLevel.CRITICAL.value: 4,
                ThreatLevel.HIGH.value: 3,
                ThreatLevel.MEDIUM.value: 2,
                ThreatLevel.LOW.value: 1
            }
            max_priority = max(threat_priority.get(v["threat_level"], 0) for v in violations)
            for level, priority in threat_priority.items():
                if priority == max_priority:
                    max_threat_level = ThreatLevel(level)
                    break

        if is_threat:
            logger.warning(
                f"Threat detected in {request_id}: "
                f"{len(violations)} violation(s), level: {max_threat_level}"
            )

        return ThreatAssessment(
            is_threat=is_threat,
            threat_level=max_threat_level,
            violations=violations,
            timestamp=start_time,
            request_id=request_id,
            analysis_time_ms=round(analysis_time, 3)
        )

    def block_ip(self, ip: str) -> bool:
        """Add an IP to the blocklist after validating its format."""
        try:
            ipaddress.ip_address(ip)  # raises ValueError for invalid input
        except ValueError:
            logger.warning(f"Attempted to block invalid IP: {ip!r}")
            return False

        if self._use_redis():
            _redis.sadd(BLOCKED_IPS_KEY, ip)
        else:
            self._local_blocked_ips.add(ip)
        logger.info(f"IP blocked: {ip}")
        return True

    def unblock_ip(self, ip: str) -> bool:
        """Remove an IP from the blocklist."""
        if self._use_redis():
            success = bool(_redis.srem(BLOCKED_IPS_KEY, ip))
            if success:
                logger.info(f"IP unblocked: {ip}")
            return success

        if ip in self._local_blocked_ips:
            self._local_blocked_ips.remove(ip)
            logger.info(f"IP unblocked: {ip}")
            return True
        return False

    def increment_request_counter(self) -> int:
        """Increment request analyzed counter."""
        if self._use_redis():
            return int(_redis.incr(REQUEST_COUNTER_KEY) or 0)
        self._local_request_counter += 1
        return self._local_request_counter

    def increment_blocked_counter(self) -> int:
        """Increment blocked requests counter."""
        if self._use_redis():
            return int(_redis.incr(BLOCKED_COUNTER_KEY) or 0)
        self._local_blocked_counter += 1
        return self._local_blocked_counter

    def get_stats(self) -> dict[str, Any]:
        """Return engine statistics."""
        rule_count = len(self.rules.get_all_rules())
        if self._use_redis():
            return {
                "requests_analyzed": int(_redis.get(REQUEST_COUNTER_KEY) or 0),
                "blocked_requests": int(_redis.get(BLOCKED_COUNTER_KEY) or 0),
                "blocked_ips": int(_redis.scard(BLOCKED_IPS_KEY) or 0),
                "backend": "redis",
                "total_rules": rule_count,
                "rule_count": rule_count,
                "rules_by_level": {
                    level.value: len(self.rules.get_rules_by_threat_level(level))
                    for level in ThreatLevel
                }
            }
        return {
            "requests_analyzed": self._local_request_counter,
            "blocked_requests": self._local_blocked_counter,
            "blocked_ips": len(self._local_blocked_ips),
            "backend": "memory",
            "total_rules": rule_count,
            "rule_count": rule_count,
            "rules_by_level": {
                level.value: len(self.rules.get_rules_by_threat_level(level))
                for level in ThreatLevel
            }
        }


# Module-level singleton — shared across the app within one process
waf_engine = WAFEngine()

