import logging

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes


def setup_logging(service_name: str, endpoint: str) -> logging.Logger:
    resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: service_name})
    logger_provider = LoggerProvider(resource=resource)
    otlp_log_exporter = OTLPLogExporter(endpoint=endpoint)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    otel_handler = LoggingHandler(logger_provider=logger_provider)
    logger.addHandler(otel_handler)

    return logger
