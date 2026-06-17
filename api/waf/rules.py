"""
WAF Security Rules

Defines pattern-based rules for detecting common web attack vectors
including SQL injection, XSS, and malicious payloads.
"""

import re
from typing import List, Tuple, Pattern
from dataclasses import dataclass, field
from enum import Enum


class ThreatLevel(Enum):
    """Classification of threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityRule:
    """Represents a single security rule with pattern and metadata."""
    id: str
    name: str
    pattern: Pattern
    threat_level: ThreatLevel
    description: str
    enabled: bool = True


@dataclass
class SecurityRules:
    """
    Collection of security rules for WAF inspection.
    
    Implements detection patterns for:
    - SQL Injection attacks
    - Cross-Site Scripting (XSS)
    - Path traversal attempts
    - Command injection
    - Header manipulation
    """
    
    _sql_injection_patterns: List[SecurityRule] = field(default_factory=list)
    _xss_patterns: List[SecurityRule] = field(default_factory=list)
    _path_traversal_patterns: List[SecurityRule] = field(default_factory=list)
    _command_injection_patterns: List[SecurityRule] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize all security rule patterns."""
        self._initialize_sql_injection_rules()
        self._initialize_xss_rules()
        self._initialize_path_traversal_rules()
        self._initialize_command_injection_rules()
    
    def _initialize_sql_injection_rules(self) -> None:
        """Define SQL injection detection patterns."""
        patterns = [
            (r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b.*\b(FROM|INTO|TABLE|SET)\b)", 
             "SQL keyword combination"),
            (r"(\bOR\b\s+\d+\s*=\s*\d+)", "OR-based SQL injection"),
            (r"(\bAND\b\s+\d+\s*=\s*\d+)", "AND-based SQL injection"),
            (r"(?i)(\s--|;--|'\s*--|\"--|\s*/\*.*?\*/)", "SQL comment injection"),
            (r"(\bUNION\b\s+\bSELECT\b)", "UNION SELECT injection"),
            (r"(\bEXEC\b|\bEXECUTE\b)\s*\(", "SQL EXEC injection"),
            (r"(\bDECLARE\b\s+@)", "SQL variable declaration"),
            (r"(\bCAST\b\s*\(.*\bAS\b)", "SQL CAST injection"),
            (r"(\bCONVERT\b\s*\()", "SQL CONVERT injection"),
            (r"(\bWAITFOR\b\s+\bDELAY\b)", "SQL time-based injection"),
            (r"(\'|\")(\s*)(OR|AND)(\s*)(\'|\"|\d)", "Quote-based injection"),
            (r"(\bINFORMATION_SCHEMA\b)", "Schema enumeration"),
            (r"(\bSYSOBJECTS\b|\bSYSTABLES\b)", "System table access"),
            # SQL Injection — Enhanced
            (r"(?i)(0x[0-9a-f]+)", "Hex-encoded SQL payload"),
            (r"(?i)(\bchar\s*\(\s*\d+)", "SQL CHAR() encoding"),
            (r"(?i)(sleep\s*\(\s*\d+\s*\))", "SQL time-based blind injection"),
            (r"(?i)(benchmark\s*\()", "SQL benchmark injection"),
        ]
        
        for i, (pattern, desc) in enumerate(patterns):
            self._sql_injection_patterns.append(SecurityRule(
                id=f"SQLI-{i+1:03d}",
                name=f"SQL Injection: {desc}",
                pattern=re.compile(pattern, re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description=f"Detects {desc}"
            ))
    
    def _initialize_xss_rules(self) -> None:
        """Define XSS detection patterns."""
        patterns = [
            (r"<script[^>]*>", "Script tag"),
            (r"javascript\s*:", "JavaScript protocol"),
            (r"on\w+\s*=", "Event handler attribute"),
            (r"<iframe[^>]*>", "Iframe injection"),
            (r"<object[^>]*>", "Object tag injection"),
            (r"<embed[^>]*>", "Embed tag injection"),
            (r"<svg[^>]*onload", "SVG onload injection"),
            (r"<img[^>]*onerror", "Image onerror injection"),
            (r"<body[^>]*onload", "Body onload injection"),
            (r"expression\s*\(", "CSS expression injection"),
            (r"vbscript\s*:", "VBScript protocol"),
            (r"data\s*:\s*text\/html", "Data URL injection"),
            (r"<link[^>]*href\s*=\s*['\"]?javascript", "Link javascript injection"),
        ]
        
        for i, (pattern, desc) in enumerate(patterns):
            self._xss_patterns.append(SecurityRule(
                id=f"XSS-{i+1:03d}",
                name=f"XSS: {desc}",
                pattern=re.compile(pattern, re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description=f"Detects {desc}"
            ))
    
    def _initialize_path_traversal_rules(self) -> None:
        """Define path traversal detection patterns."""
        patterns = [
            (r"\.\.\/", "Directory traversal with forward slash"),
            (r"\.\.\\", "Directory traversal with backslash"),
            (r"%2e%2e%2f", "URL encoded traversal"),
            (r"%2e%2e\/", "Mixed encoded traversal"),
            (r"\.\.%2f", "Partial encoded traversal"),
            (r"\/etc\/passwd", "Unix passwd file access"),
            (r"\/etc\/shadow", "Unix shadow file access"),
            (r"c:\\windows", "Windows system path"),
            (r"%00", "Null byte injection"),
        ]
        
        for i, (pattern, desc) in enumerate(patterns):
            self._path_traversal_patterns.append(SecurityRule(
                id=f"PATH-{i+1:03d}",
                name=f"Path Traversal: {desc}",
                pattern=re.compile(pattern, re.IGNORECASE),
                threat_level=ThreatLevel.HIGH,
                description=f"Detects {desc}"
            ))
    
    def _initialize_command_injection_rules(self) -> None:
        """Define command injection detection patterns."""
        patterns = [
            (r";\s*(ls|cat|rm|wget|curl)\b", "Unix command chaining"),
            (r"\|\s*(ls|cat|rm|wget|curl)\b", "Unix pipe injection"),
            (r"`[^`]+`", "Backtick command execution"),
            (r"\$\([^)]+\)", "Subshell execution"),
            (r"&&\s*(ls|cat|rm|wget|curl)\b", "AND command chaining"),
            (r"\|\|\s*(ls|cat|rm|wget|curl)\b", "OR command chaining"),
            (r">\s*\/", "Output redirection to root"),
            (r"<\s*\/", "Input redirection from root"),
        ]
        
        for i, (pattern, desc) in enumerate(patterns):
            self._command_injection_patterns.append(SecurityRule(
                id=f"CMDI-{i+1:03d}",
                name=f"Command Injection: {desc}",
                pattern=re.compile(pattern, re.IGNORECASE),
                threat_level=ThreatLevel.CRITICAL,
                description=f"Detects {desc}"
            ))
    
    def get_all_rules(self) -> List[SecurityRule]:
        """Return all enabled security rules."""
        all_rules = (
            self._sql_injection_patterns +
            self._xss_patterns +
            self._path_traversal_patterns +
            self._command_injection_patterns
        )
        return [rule for rule in all_rules if rule.enabled]
    
    def get_rules_by_threat_level(self, level: ThreatLevel) -> List[SecurityRule]:
        """Return rules filtered by threat level."""
        return [rule for rule in self.get_all_rules() if rule.threat_level == level]
    
    def check_content(self, content: str) -> List[Tuple[SecurityRule, str]]:
        """
        Check content against all security rules.
        
        Args:
            content: The string content to analyze
            
        Returns:
            List of tuples containing matched rules and the matching substring
        """
        violations = []
        for rule in self.get_all_rules():
            match = rule.pattern.search(content)
            if match:
                violations.append((rule, match.group()))
        return violations
