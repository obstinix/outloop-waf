"""
Core Logic

Primary business logic for the WAF application including
service layer operations and internal utilities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

from api.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ServiceStatus:
    """Represents the current status of a service component."""
    name: str
    healthy: bool
    latency_ms: float
    last_check: datetime
    details: Union[dict[str, Any], None] = None


class CoreService:
    """
    Core service layer for WAF application.

    Manages internal state, health checks, and service orchestration.
    """

    def __init__(self):
        """Initialize core service."""
        self._start_time = datetime.utcnow()
        self._components: dict[str, ServiceStatus] = {}
        logger.info("Core service initialized")

    @property
    def uptime_seconds(self) -> float:
        """Calculate service uptime in seconds."""
        return float((datetime.utcnow() - self._start_time).total_seconds())

    def register_component(self, name: str, status: ServiceStatus) -> None:
        """Register a component's health status."""
        self._components[name] = status
        logger.debug(f"Component registered: {name}")

    def get_component_status(self, name: str) -> Union[ServiceStatus, None]:
        """Retrieve status of a specific component."""
        return self._components.get(name)

    def get_health_summary(self) -> dict[str, Any]:
        """
        Generate comprehensive health summary.

        Returns:
            Dictionary containing health status of all components
        """
        all_healthy = all(c.healthy for c in self._components.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "uptime_seconds": round(self.uptime_seconds, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                name: {
                    "healthy": status.healthy,
                    "latency_ms": status.latency_ms,
                    "last_check": status.last_check.isoformat()
                }
                for name, status in self._components.items()
            }
        }

    def process_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a generic request through the core service layer.

        Args:
            data: Request data to process

        Returns:
            Processed response data
        """
        logger.debug(f"Processing request with {len(data)} fields")

        # Simulate processing
        result = {
            "processed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "input_fields": len(data)
        }

        return result


# Global service instance
_service_instance: Union[CoreService, None] = None


def get_service() -> CoreService:
    """Get or create the global service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CoreService()
    return _service_instance
