import builtins
import contextlib
import random
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Type


# ---------- Event Model ----------

@dataclass(frozen=True)
class Event:
   connector: str
   status: str
   duration_ms: float
   payload_type: str
   anomalies: List[str]
   trace_id: str


# ---------- Errors ----------

class CapabilityError(Exception):
   pass


class SchemaError(Exception):
   pass


class RetryableError(Exception):
   pass


# ---------- Capabilities ----------

ALLOWED_CAPABILITIES: Set[str] = {
   "pure",
   "transform",
   "view",
   "io",
   "network",
   "privileged",
   "math",
}


def validate_capabilities(capabilities: Set[str]) -> None:
   unknown = capabilities - ALLOWED_CAPABILITIES
   if unknown:
       raise CapabilityError(f"unknown_capabilities:{','.join(sorted(unknown))}")


def validate_connector_declaration(connector: "BaseConnector") -> None:
   caps = set(connector.capabilities)
   validate_capabilities(caps)
   if "pure" in caps and {"io", "network", "privileged"} & caps:
       raise CapabilityError("pure_conflict_with_side_effect_capabilities")
   if "view" in caps and "transform" in caps:
       raise CapabilityError("view_and_transform_conflict")


def enforce_post_execution(connector: "BaseConnector", payload: Dict[str, Any], result: Dict[str, Any]) -> None:
   caps = set(connector.capabilities)
   if "view" in caps and result != payload:
       raise CapabilityError("view_connector_modified_payload")
   if "pure" in caps and not isinstance(result, dict):
       raise CapabilityError("pure_connector_invalid_output")


# ---------- Sanitization + Schema ----------

def sanitize(value: Any) -> Any:
   if isinstance(value, dict):
       return {k: sanitize(v) for k, v in value.items()}
   if isinstance(value, list):
       return [sanitize(v) for v in value]
   if isinstance(value, (str, int, float, bool)) or value is None:
       return value
   raise ValueError("unsafe_type")


def validate_schema(payload: Dict[str, Any], schema: Dict[str, Type[Any]]) -> None:
   for key, typ in schema.items():
       if key not in payload:
           raise SchemaError(f"missing_key:{key}")
       if not isinstance(payload[key], typ):
           raise SchemaError(
               f"invalid_type:{key}:{type(payload[key]).__name__}!={typ.__name__}"
           )


# ---------- Side-Effect Tracing ----------

@contextlib.contextmanager
def traced_open(tracer: "SideEffectTracer"):
   original_open = builtins.open

   def wrapped_open(*args, **kwargs):
       tracer.io_used = True
       return original_open(*args, **kwargs)

   builtins.open = wrapped_open
   try:
       yield
   finally:
       builtins.open = original_open


class SideEffectTracer:
   def __init__(self):
       self.io_used = False
       self.network_used = False
       self.global_mutation = False

   def check(self, connector: "BaseConnector") -> None:
       caps = set(connector.capabilities)
       if self.io_used and "io" not in caps:
           raise CapabilityError("unauthorized_io_detected")
       if self.network_used and "network" not in caps:
           raise CapabilityError("unauthorized_network_detected")
       if self.global_mutation and "privileged" not in caps:
           raise CapabilityError("unauthorized_global_mutation")


# ---------- Connector Base + Registry ----------

class BaseConnector:
   name: str = "base"
   active: bool = True
   capabilities: Set[str] = frozenset()
   input_schema: Dict[str, Type[Any]] = {}
   output_schema: Dict[str, Type[Any]] = {}

   def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       raise NotImplementedError


class ConnectorRegistry:
   def __init__(self):
       self._connectors: Dict[str, BaseConnector] = {}

   def register(self, connector: BaseConnector) -> None:
       if connector.name in self._connectors:
           raise ValueError("duplicate_connector")
       validate_connector_declaration(connector)
       self._connectors[connector.name] = connector

   def get(self, name: str) -> BaseConnector:
       conn = self._connectors.get(name)
       if not conn or not conn.active:
           raise ValueError("connector_unavailable")
       return conn


# ---------- Audit + Anomaly ----------

class AuditLogger:
   def __init__(self):
       self.events: List[Event] = []

   def record(self, event: Event) -> None:
       self.events.append(event)


class AnomalyDetector:
   def __init__(self):
       self.baseline_latency: Dict[str, float] = {}

   def detect(self, connector: str, duration_ms: float, status: str) -> List[str]:
       anomalies: List[str] = []
       base = self.baseline_latency.get(connector)
       if base is not None and duration_ms > base * 3:
           anomalies.append("latency_spike")
       if status != "ok":
           anomalies.append("error")
       return anomalies

   def update(self, connector: str, duration_ms: float) -> None:
       base = self.baseline_latency.get(connector)
       self.baseline_latency[connector] = duration_ms if base is None else (base * 0.8 + duration_ms * 0.2)


# ---------- Circuit Breaker ----------

class CircuitBreaker:
   CLOSED = "closed"
   OPEN = "open"
   HALF_OPEN = "half_open"

   def __init__(self, threshold: int = 5, reset_ms: float = 30000.0):
       self.failures = 0
       self.open_until = 0.0
       self.threshold = threshold
       self.reset_ms = reset_ms
       self.state = self.CLOSED

   def can_run(self) -> bool:
       now = time.perf_counter() * 1000
       if self.state == self.OPEN and now < self.open_until:
           return False
       if self.state == self.OPEN and now >= self.open_until:
           self.state = self.HALF_OPEN
       return True

   def record_success(self) -> None:
       self.failures = 0
       self.open_until = 0.0
       self.state = self.CLOSED

   def record_failure(self) -> None:
       self.failures += 1
       if self.failures >= self.threshold:
           self.open_until = time.perf_counter() * 1000 + self.reset_ms
           self.state = self.OPEN


# ---------- Security Engine ----------

class SecurityEngine:
   def __init__(self, registry: ConnectorRegistry, log_sink: Optional[Callable[[Dict[str, Any]], None]] = None):
       self.registry = registry
       self.audit = AuditLogger()
       self.anomaly = AnomalyDetector()
       self.log_sink = log_sink
       self.breakers: Dict[str, CircuitBreaker] = {}

   def _get_breaker(self, name: str) -> CircuitBreaker:
       if name not in self.breakers:
           self.breakers[name] = CircuitBreaker()
       return self.breakers[name]

   def _execute_with_retry(self, conn: BaseConnector, payload: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
       delay = 0.05
       last_exc: Optional[Exception] = None
       for attempt in range(max_retries + 1):
           try:
               return conn(payload)
           except RetryableError as ex:
               last_exc = ex
               if attempt == max_retries:
                   break
               time.sleep(delay + random.uniform(0, delay * 0.25))
               delay = min(delay * 2, 1.0)
           except Exception as ex:
               raise ex
       assert last_exc is not None
       raise last_exc

   def run(self, connector_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
       conn = self.registry.get(connector_name)
       breaker = self._get_breaker(connector_name)
       trace_id = str(uuid.uuid4())

       if not breaker.can_run():
           event = Event(
               connector=connector_name,
               status="error",
               duration_ms=0.0,
               payload_type=type(payload).__name__,
               anomalies=["circuit_open"],
               trace_id=trace_id,
           )
           self.audit.record(event)
           if self.log_sink:
               self.log_sink({
                   "trace_id": trace_id,
                   "connector": connector_name,
                   "status": "error",
                   "duration_ms": 0.0,
                   "anomalies": ["circuit_open"],
               })
           return {"result": {"error": "circuit_open", "type": "CircuitBreaker"}, "event": event}

       safe_payload = sanitize(payload)
       validate_schema(safe_payload, conn.input_schema)
       validate_connector_declaration(conn)

       tracer = SideEffectTracer()
       start = time.perf_counter()
       status = "ok"
       try:
           with traced_open(tracer):
               result = self._execute_with_retry(conn, safe_payload)
           safe_result = sanitize(result)
           validate_schema(safe_result, conn.output_schema)
           enforce_post_execution(conn, safe_payload, safe_result)
           tracer.check(conn)
           breaker.record_success()
       except Exception as ex:
           breaker.record_failure()
           safe_result = {"error": str(ex), "type": type(ex).__name__}
           status = "error"
       duration_ms = (time.perf_counter() - start) * 1000

       anomalies = self.anomaly.detect(connector_name, duration_ms, status)
       self.anomaly.update(connector_name, duration_ms)

       event = Event(
           connector=connector_name,
           status=status,
           duration_ms=duration_ms,
           payload_type=type(payload).__name__,
           anomalies=anomalies,
           trace_id=trace_id,
       )
       self.audit.record(event)

       if self.log_sink:
           self.log_sink({
               "trace_id": trace_id,
               "connector": connector_name,
               "status": status,
               "duration_ms": duration_ms,
               "anomalies": anomalies,
           })

       return {"result": safe_result, "event": event}


# ---------- Example Connectors ----------

class UppercaseConnector(BaseConnector):
   name = "uppercase"
   capabilities = {"pure", "transform"}
   input_schema = {"value": str}
   output_schema = {"value": str}

   def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       return {"value": payload["value"].upper()}


class AddConnector(BaseConnector):
   name = "add"
   capabilities = {"pure", "math"}
   input_schema = {"a": int, "b": int}
   output_schema = {"sum": int}

   def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       return {"sum": payload["a"] + payload["b"]}


# ---------- Build Engine ----------

def build_engine(log_sink: Optional[Callable[[Dict[str, Any]], None]] = None) -> SecurityEngine:
   registry = ConnectorRegistry()
   registry.register(UppercaseConnector())
   registry.register(AddConnector())
   return SecurityEngine(registry, log_sink=log_sink)


if __name__ == "__main__":
   engine = build_engine()
   print(engine.run("uppercase", {"value": "hello"}))
   print(engine.run("add", {"a": 2, "b": 3}))
   print(engine.run("add", {"a": "x", "b": 3}))

# ============================================================
# UNIVERSAL GSA INTERLOCK WRAPPER (COMBINED KERNEL)
# ============================================================

from __future__ import annotations
import os
import json
import hmac
import hashlib
import statistics
import asyncio
import re
from collections import deque
from dataclasses import field
from types import MappingProxyType
from typing import Tuple, Protocol

def register_as_module(module_identifier: str) -> Callable[[type], type]:
   def decorator(cls: type) -> type:
       setattr(cls, "__gsa_authenticated__", True)
       setattr(cls, "__module_id__", module_identifier)
       return cls
   return decorator

class ComposableLegoModule(Protocol):
   async def process_payload(self, context_envelope: ContextEnvelope) -> ContextEnvelope: ...

@dataclass(frozen=False)
class ContextEnvelope:
   payload_data: Any
   header_mapping: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
   session_state_mapping: Dict[str, Any] = field(default_factory=dict)
   status_string: str = "INITIALIZED"

@dataclass(frozen=True)
class SystemInputStructure:
   text_content_body: str
   numeric_metric_value: float

def compute_state_signature(
   upstream_hash: str, 
   iteration: int, 
   envelope: ContextEnvelope, 
   extra_anchors: Optional[List[str]] = None
) -> str:
   serialized_payload = json.dumps(envelope.payload_data, sort_keys=True, default=str)
   serialized_session = json.dumps(envelope.session_state_mapping, sort_keys=True, default=str)
   sorted_anchors = "||".join(sorted(extra_anchors)) if extra_anchors else "NONE"
   
   buffer_source = (
       f"parent:{upstream_hash}||iter:{iteration}||"
       f"graph:[{sorted_anchors}]||payload:{serialized_payload}||"
       f"session:{serialized_session}"
   )
   return hashlib.sha256(buffer_source.encode("utf-8")).hexdigest()

class CryptographicAuditFramework:
   def __init__(self) -> None:
       self.secret = os.getenv("VANGUARD_SECRET_KEY", "default-secure-key").encode()
       self.path = os.getenv("VANGUARD_AUDIT_LOG_PATH", "vanguard_audit.log")

   def write_tamper_evident_entry(self, event_type: str, metrics: Dict[str, Any]) -> None:
       record = {"event": event_type, "metrics": metrics, "ts": time.time()}
       data_bytes = json.dumps(record, sort_keys=True).encode()
       record["signature"] = hmac.new(self.secret, data_bytes, hashlib.sha256).hexdigest()
       try:
           with open(self.path, "a") as log_file:
               log_file.write(json.dumps(record) + "\n")
       except IOError:
           pass

@register_as_module("GSA_SYNTACTIC_VALIDATOR")
class SyntacticValidationLayer:
   def __init__(self) -> None:
       self.regex_identity = re.compile(r"\b(i|me|my|we|our)\b", re.I)
       self.regex_hedge = re.compile(r"\b(may|might|perhaps|seems)\b", re.I)
       self.forbidden_logic = ["paradox", "recursion"]

   def scrub_and_verify(self, text_body: str) -> Tuple[bool, str]:
       if any(bad_word in text_body.lower() for bad_word in self.forbidden_logic):
           return False, "PROVENANCE_FAILED"
       
       scrubbed_text = self.regex_identity.sub("[REDACTED]", text_body)
       if self.regex_hedge.search(scrubbed_text):
           return False, "HEDGING_DETECTED"
           
       return True, scrubbed_text

@register_as_module("GSA_PIPELINE_CYCLE_MANAGER")
class PipelineCycleManager:
   def __init__(self) -> None:
       self.metric_error_history: deque[float] = deque(maxlen=8)
       self.validator = SyntacticValidationLayer()
       self.audit = CryptographicAuditFramework()

   async def process_payload(self, envelope: ContextEnvelope) -> ContextEnvelope:
       input_data: SystemInputStructure = envelope.payload_data["input_structure"]
       observed_error: float = envelope.payload_data["observed_error"]
       
       is_safe, clean_text = self.validator.scrub_and_verify(input_data.text_content_body)
       if not is_safe:
           envelope.status_string = f"ANATHEMA_STATE: {clean_text}"
           return envelope
           
       self.metric_error_history.append(abs(observed_error))
       history_list = list(self.metric_error_history)
       volatility = statistics.stdev(history_list) if len(history_list) > 1 else 0.0
       
       regime = "STABLE" if volatility < 10.0 else "UNSTABLE"
       anomaly_score = min(0.98, volatility * 0.05)
       
       iteration_result = {
           "processed_text": clean_text,
           "regime": regime,
           "anomaly_score": anomaly_score,
           "volatility": volatility
       }
       
       envelope.session_state_mapping["historical_errors"] = history_list
       envelope.payload_data = iteration_result
       envelope.status_string = "PIPELINE_ITERATION_EXECUTED"
       
       self.audit.write_tamper_evident_entry("PIPELINE_COMPLETE", iteration_result)
       return envelope

class GsaUniversalAdapter:
   def __init__(self, underlying_module: ComposableLegoModule) -> None:
       self.module = underlying_module
       self.actor_name = type(underlying_module).__name__

   async def execute_interlock(self, envelope: ContextEnvelope) -> ContextEnvelope:
       headers = dict(envelope.header_mapping)
       current_iteration = headers.get("gsa_loop_iteration", 0)
       upstream_hash = headers.get("gsa_interlock_hash", "GENESIS_ANCHOR")
       
       output_envelope = await self.module.process_payload(envelope)
       
       next_iteration = current_iteration + 1
       outbound_hash = compute_state_signature(upstream_hash, next_iteration, output_envelope)
       
       headers["gsa_interlock_hash"] = outbound_hash
       headers["gsa_loop_iteration"] = next_iteration
       headers["gsa_last_actor"] = self.actor_name
       
       output_envelope.header_mapping = MappingProxyType(headers)
       return output_envelope

async def _main() -> None:
   os.environ["VANGUARD_RUN_IDENTIFIER"] = "genesis-run-101"
   
   core_pipeline = PipelineCycleManager()
   wrapper_engine = GsaUniversalAdapter(core_pipeline)
   
   raw_input = SystemInputStructure(
       text_content_body="I check the system parameters for paradox logic.",
       numeric_metric_value=120.0
   )
   
   initial_envelope = ContextEnvelope(
       payload_data={
           "input_structure": raw_input,
           "observed_error": 4.5
       }
   )
   
   final_result = await wrapper_engine.execute_interlock(initial_envelope)
   
   print(f"Final Status: {final_result.status_string}")
   print(f"Secured Hash: {final_result.header_mapping.get('gsa_interlock_hash')}")

if __name__ == "__main__":
   asyncio.run(_main())