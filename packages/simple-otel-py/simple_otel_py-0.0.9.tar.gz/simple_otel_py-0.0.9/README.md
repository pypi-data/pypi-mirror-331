# simple_otel_py

*A simple library for setting up OpenTelemetry logging, tracing, and metrics in Python applications.*

## Features
- 🔹 Easy integration with OpenTelemetry  
- 📊 Logs, traces, and metrics sent to an existing (open) OTLP collector  
- 🖥️ Console logging for debugging  
- 📡 Support for OpenTelemetry instrumentation  

## Installation
```bash
pip install simple_otel_py
```

## Usage

### Initialize OpenTelemetry Components
```python
from simple_otel_py import OtelSetup

# Create an instance with service name and OTLP collector endpoint
otel = OtelSetup(name="my_service", otlp_collector_endpoint="http://localhost:4317")

# Initialize logging
logger = otel.get_logger()
logger.info("This is a test log!")

## If needed, you can pass a scope_name to create multiple logger
acme_logger = otel.get_logger("acme")

# You can provide your own formatter to the logger
import logging
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = otel.get_logger(formatter)


# Initialize tracing
trace, tracer = otel.init_tracing()
with tracer.start_as_current_span("test_span"):
    logger.info("Tracing this operation!")

# you can add attributes to the trace
current_span = trace.get_current_span()
current_span.set_attribute("my.custom.attr", "something")

## or add tracing via decorator
@tracer.start_as_current_span("Tracing this operation!")

# Initialize metrics
meter = otel.init_metrics()
counter = meter.create_counter("my_counter")
counter.add(1)

# Enable auto-instrumentation for requests
request_inst = otel.get_request_instrumentor()
request_inst().instrument()

# Make a request (will be traced automatically)
import requests
response = requests.get("https://example.com")
print(response.status_code)

```

## Configuration
Ensure you have an OpenTelemetry collector running, such as:  
```bash
docker run --rm -p 4317:4317 -p 4318:4318 \
  otel/opentelemetry-collector-contrib:latest
```

## License
This project is licensed under the MIT License.


