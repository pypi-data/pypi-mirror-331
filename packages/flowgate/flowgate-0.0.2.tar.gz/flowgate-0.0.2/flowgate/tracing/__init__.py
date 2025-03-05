from . import datadog
from .opentelemetry import OpenTelemetryBackend

tracer = OpenTelemetryBackend("flowgate")

__all__ = ['tracer', 'OpenTelemetryBackend', 'datadog']
