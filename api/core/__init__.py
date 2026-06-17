"""
Core Module

Contains primary business logic and internal utilities.
"""

from api.core.antigravity import check_gravity_state
from api.core.logic import CoreService

__all__ = ["CoreService", "check_gravity_state"]
