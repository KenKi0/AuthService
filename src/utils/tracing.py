from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import Resource, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from core.config import settings


def configure_tracer(app: Flask) -> None:
    resource = Resource(attributes={'SERVICE_NAME': 'auth-service'})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger.AGENT_HOST,
                agent_port=settings.jaeger.AGENT_PORT,
            ),
        ),
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    FlaskInstrumentor().instrument_app(app)
