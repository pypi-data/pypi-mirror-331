from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, TypedDict


@dataclass
class TelemetryConfig:
    service_name: str
    environment: str
    version: Optional[str] = "1.0.0"
    otlp_endpoint: Optional[str] = "http://localhost:4317"
    metric_interval_ms: Optional[int] = 5000
    log_level: Optional[str] = "INFO"
    resource_attributes: Optional[Dict[str, str]] = None


@dataclass
class MetricOptions:
    name: str
    description: str
    unit: str = ""
    tags: Optional[Dict[str, str]] = None


@dataclass
class LogAttributes:
    attributes: Dict[str, Any] = field(default_factory=dict)


class TelemetryService(Protocol):
    async def start(self) -> None:
        ...

    async def shutdown(self) -> None:
        ...


class TraceCarrier(TypedDict, total=False):
    """Carrier for trace context propagation headers"""

    traceparent: str
    tracestate: str
