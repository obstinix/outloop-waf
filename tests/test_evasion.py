"""
WAF bypass evasion tests.
Tests encoding tricks, polyglots, and double-encoding attacks
that naive regex rules are known to miss.
"""
import pytest

EVASION_PAYLOADS = [
    # URL-encoded SQLi
    ("%27%20OR%201%3D1", "URL-encoded SQL injection"),
    ("%27%3B%20DROP%20TABLE%20users%3B--", "URL-encoded DROP TABLE"),

    # Double URL-encoded
    ("%2527", "Double-encoded single quote"),

    # Unicode SQLi
    ("\\u0027 OR 1=1", "Unicode-escaped quote SQLi"),

    # Case variation
    ("SeLeCt * FrOm users", "Mixed-case SELECT"),
    ("uNiOn SeLeCt null,null", "Mixed-case UNION SELECT"),

    # Comment-based bypass
    ("SEL/**/ECT", "Inline comment fragmentation"),
    ("1/*!UNION*/SELECT", "MySQL version comment bypass"),

    # XSS polyglots
    ("<ScRiPt>alert(1)</sCrIpT>", "Mixed-case XSS tag"),
    ("javascript:/*--></title></style></textarea></script><svg/onload='+/*/`/+/onmouseover=1//>'", "XSS polyglot"),
    ("'-alert(1)-'", "Single-quote XSS bypass"),

    # Path traversal variants
    ("....//....//etc/passwd", "Double-dot traversal"),
    ("..%2f..%2fetc%2fpasswd", "URL-encoded traversal"),
    ("%2e%2e%2f%2e%2e%2fetc%2fpasswd", "Double-encoded traversal"),

    # Command injection variants
    ("`id`", "Backtick command substitution"),
    ("$(id)", "Dollar-paren command substitution"),

    # SSRF
    ("http://169.254.169.254/latest/meta-data/", "AWS IMDS SSRF"),
    ("http://metadata.google.internal/computeMetadata/v1/", "GCP metadata SSRF"),
]

CLEAN_PAYLOADS = [
    ("example.com/page#section", "URL fragment should pass"),
    ("color: #ffffff", "CSS hex color should pass"),
    ("price--", "Double dash in legitimate content"),
    ("SELECT * FROM products WHERE id = $1", "Parameterized query reference"),
]

@pytest.mark.asyncio
async def test_evasion_payloads_are_blocked(async_client):
    for payload, description in EVASION_PAYLOADS:
        response = await async_client.get(
            "/api/secure/test",
            params={"payload": payload}
        )
        assert response.status_code == 403, (
            f"EVASION BYPASS: '{description}' — payload not blocked: {payload!r}"
        )

@pytest.mark.asyncio
async def test_clean_payloads_are_not_blocked(async_client):
    for payload, description in CLEAN_PAYLOADS:
        response = await async_client.get(
            "/api/secure/test",
            params={"payload": payload}
        )
        assert response.status_code == 200, (
            f"FALSE POSITIVE: '{description}' — legitimate payload blocked: {payload!r}"
        )
