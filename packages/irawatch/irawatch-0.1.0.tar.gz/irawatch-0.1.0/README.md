# IraWatch

This is a client library which sends traces to IraWatch collector.

Install 

```bash
pip install setuptools
pip install git+ssh://git@github.com/darylac/irawatch.git
```

```py
import nats

# It is important to have a import statement like this. `from irawatch.trace import Tracer, Span` won't work due to design considerations.
from irawatch import trace

nc = await nats.connect()

# Initialise tracer when application starts up
trace.Tracer(service_name="App A", nats_conn=nc)

# The trace ID must be 16 bytes. UUID4 is 16 bytes, so can be used.
trace_id = uuid.uuid4().bytes

# Every time you want to send a trace, you do the following
span = trace.Span(name="Task A", trace_id=trace_id).start()
time.sleep(2) # some task
await span.stop() # when you invoke stop, it will send the trace to the collector.

span = trace.Span("Task B", trace_id).start()
time.sleep(3)
await span.stop(attributes={"attr1": "val1"}) # the attributes argument takes dict where key is string and value is any valid JSON value
```