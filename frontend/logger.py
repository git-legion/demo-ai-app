import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger("app_logger")


def configure_logging(otlp_endpoint: str) -> None:
    """
    Attach an OTel LoggingHandler so every log record is correlated with
    the active trace/span IDs and exported to the OTel Collector.
    """
    resource = Resource.create({"service.name": "llamaops-ai"})

    log_provider = LoggerProvider(resource=resource)
    set_logger_provider(log_provider)

    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
        )
    )

    otel_handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=log_provider,
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] "
               "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s",
        handlers=[logging.StreamHandler(), otel_handler],
    )
