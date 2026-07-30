from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)
_configured = False


def configure_application_insights() -> None:
    global _configured
    if _configured or not settings.insights_configured:
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=settings.applicationinsights_connection_string)
        _configured = True
        logger.info("Application Insights telemetry enabled")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to configure Application Insights: %s", exc)
