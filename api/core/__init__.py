"""
Core Module

Contains primary business logic and internal utilities.
"""

from api.core.logic import CoreService
from api.core.antigravity import check_gravity_state

__all__ = ["CoreService", "check_gravity_state"]
