from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import logging


class OtelSetup:
    def __init__(self, name: str, otlp_collector_endpoint: str):
        if not otlp_collector_endpoint:
            raise ValueError("OTLP collector endpoint is required.")
          
        self.name = name
        self.otlp_collector_endpoint = otlp_collector_endpoint
        self.resource = Resource(attributes={SERVICE_NAME: name})

    def init_tracing(self):
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        provider = TracerProvider(resource=self.resource)

        # Console logging for debugging
        console_processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(console_processor)

        # OTLP exporter for sending spans
        span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=self.otlp_collector_endpoint))
        provider.add_span_processor(span_processor)

        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(self.name)
        return [trace, tracer]
    
    def init_metrics(self):
        from opentelemetry import metrics
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

        # Console and OTLP metric readers
        console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
        otlp_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=self.otlp_collector_endpoint))

        # Initialize MeterProvider
        meter_provider = MeterProvider(metric_readers=[console_reader, otlp_reader], resource=self.resource)
        metrics.set_meter_provider(meter_provider)

        return meter_provider.get_meter(self.name)

    def get_logger(self, scope_name: str = '', formatter: logging.Formatter = None):
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

        # Standard logger setup
        if not scope_name:
            scope_name = self.name
            
        logger = logging.getLogger(scope_name)
        logger.setLevel(logging.INFO)

        # Console handler, prevent adding multiple instances if same scope_name is used.
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
        
            if formatter is None:
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # OTLP handler
        if not any(isinstance(h, LoggingHandler) for h in logger.handlers):
            logger_provider = LoggerProvider(resource=self.resource)
            set_logger_provider(logger_provider)
            log_exporter = OTLPLogExporter(endpoint=self.otlp_collector_endpoint, insecure=True)
            logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

            otlp_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
            logger.addHandler(otlp_handler)

        return logger

    def get_request_instrumentor(self):
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        return RequestsInstrumentor