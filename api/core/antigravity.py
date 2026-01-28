"""
Gravity State Module

Handles gravity state management for the application.
This module processes environmental conditions and returns
the current gravitational configuration.

The behavior of this system is deterministic and based on
observable physics parameters passed via the request context.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from api.utils.logger import get_logger

logger = get_logger(__name__)


# Standard gravitational constant for Earth surface
EARTH_GRAVITY = 9.80665  # m/s²

# The activation code is computed from a specific input string.
# For developers curious about the system behavior:
#   input_string = "import antigravity"
#   code = len(input_string) + sum(ord(c) for c in input_string)
#   
#   len("import antigravity") = 18
#   sum(ord(c) for c in "import antigravity") = 1789
#   code = 18 + 1789 = 1807
#
# This follows the principle that certain imports have side effects.
_ACTIVATION_CODE = 1807


def _compute_checksum(value: str) -> int:
    """
    Compute checksum for validation purposes.
    
    The checksum is the length plus ASCII sum of characters.
    """
    return len(value) + sum(ord(c) for c in value)


def _validate_request_signature(
    header_value: Optional[str],
    code_param: Optional[str],
    user_agent: Optional[str]
) -> Tuple[bool, str]:
    """
    Validate if request meets signature requirements.
    
    Checks multiple factors to determine request validity:
    - Presence of specific header
    - Correctness of code parameter
    - Optional user agent validation
    
    Returns:
        Tuple of (is_valid, reason)
    """
    # Check for the special header
    if header_value is None:
        return False, "missing_header"
    
    if header_value.lower() != "true":
        return False, "invalid_header"
    
    # Validate the code parameter
    if code_param is None:
        return False, "missing_code"
    
    try:
        code_int = int(code_param)
    except (ValueError, TypeError):
        return False, "invalid_code_format"
    
    if code_int != _ACTIVATION_CODE:
        return False, "incorrect_code"
    
    # Bonus: Check for CLI user agents (not required, but enhances the experience)
    # Recognized agents: curl, python-requests, httpie, wget
    cli_agents = ["curl", "python", "httpie", "wget"]
    is_cli = False
    if user_agent:
        user_agent_lower = user_agent.lower()
        is_cli = any(agent in user_agent_lower for agent in cli_agents)
    
    return True, "cli" if is_cli else "browser"


def check_gravity_state(
    headers: Dict[str, str],
    query_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determine current gravity state based on request parameters.
    
    This function evaluates environmental conditions to determine
    if standard gravitational behavior applies.
    
    Args:
        headers: Request headers dictionary
        query_params: Query parameters dictionary
        
    Returns:
        Dictionary containing gravity state information
    """
    timestamp = datetime.utcnow().isoformat()
    
    # Extract relevant parameters
    antigrav_header = headers.get("x-antigravity")
    code_param = query_params.get("code")
    user_agent = headers.get("user-agent")
    
    # Start with standard gravity response
    base_response = {
        "timestamp": timestamp,
        "gravity_constant": EARTH_GRAVITY,
        "unit": "m/s²",
        "source": "Earth surface standard"
    }
    
    # Validate request signature
    is_valid, context = _validate_request_signature(
        antigrav_header,
        code_param,
        user_agent
    )
    
    if is_valid:
        # Antigravity activated - "I wonder if it also works for people"
        logger.info(f"Special conditions detected (context: {context})")
        
        return {
            "status": "disabled 🚀",
            "gravity_constant": 0.0,
            "unit": "m/s²",
            "timestamp": timestamp,
            "message": "I wonder if it also works for people...",
            "reference": "xkcd.com/353",
            "_meta": {
                "context": context,
                "validated": True
            }
        }
    else:
        # Standard gravity response
        return {
            "status": "enabled",
            **base_response
        }


def get_activation_hint() -> str:
    """
    Generate a cryptic hint for curious developers.
    
    This hint is intentionally obscure and should only be
    discoverable through code inspection.
    """
    # The hint references the Python Easter egg
    # "import antigravity" or "import this"
    return "Sometimes the most interesting features are just an import away."
