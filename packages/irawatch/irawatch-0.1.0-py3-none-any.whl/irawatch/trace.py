import os
import time
from enum import Enum
from typing import Union, Type
from nats.aio.client import Client as NATS
from irawatch.converter import convert_dict_to_key_values
from irawatch.trace_pb2 import TracesData, ResourceSpans, Resource, ScopeSpans, InstrumentationScope, Span as Spanpb, KeyValue, AnyValue


class SpanKind(Enum):
    UNSPECIFIED = 0
    INTERNAL = 1
    SERVER = 2
    CLIENT = 3
    PRODUCER = 4
    CONSUMER = 5


class _Span:
    service_name: Union[None, str] = None
    nc: Union[None, NATS] = None
    collector_subject: str = "irawatch.trace"

    def __init__(self, name: str, trace_id: bytes, parent_span_id=b"", kind = SpanKind.UNSPECIFIED):
        self.name = name
        self.trace_id = trace_id
        self.parent_span_id = parent_span_id
        self.span_kind = kind
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time.time_ns()
        return self
    
    async def stop(self, attributes: dict = {}):
        if self.start_time == 0:
            return
        self.end_time = time.time_ns()

        message = TracesData(
            resource_spans=[ResourceSpans(
                resource=Resource(
                    attributes=[KeyValue(key="service.name", value=AnyValue(string_value=self.service_name))]
                ),
                scope_spans=[ScopeSpans(
                    scope = InstrumentationScope(),
                    spans = [Spanpb(
                        trace_id=self.trace_id,
                        span_id=os.urandom(8),
                        parent_span_id=self.parent_span_id,
                        name=self.name,
                        kind=self.span_kind.value,
                        start_time_unix_nano=self.start_time,
                        end_time_unix_nano=self.end_time,
                        attributes=convert_dict_to_key_values(attributes)
                    )]
                )]
            )]
        )
        
        if self.nc:
            await self.nc.publish(self.collector_subject, message.SerializeToString())


class _NoOpSpan:
    def __init__(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        return self
    
    async def stop(self, *args, **kwargs):
        pass


Span: Union[Type[_Span], Type[_NoOpSpan]] = _NoOpSpan


def Tracer(service_name: str, nats_conn: NATS):
    """
    Initialize IraWatch Tracer. This function must be called when initializing the app.
    If not initialized, all other Tracer related classes and functions will be NoOp.

    Args:
        service_name (str): name of the app or service
        nc (nats.aio.client.Client): nats connection object
    """
    global Span
    Span = _Span
    Span.service_name = service_name
    Span.nc = nats_conn
