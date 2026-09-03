from __future__ import annotations
import ast
import asyncio
import hashlib
import json
import logging
import random
import time
from collections import deque
from dataclasses import dataclass, field, replace, asdict
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Set
import json
import hashlib
import logging
import time
from typing import Any, Dict, List

# --- from governance_filters.py module ---
class ComplianceFiltrationFilter:
   def __init__(self):
       self.segment_identifier = "SEGMENT-05-COMPLIANCE"
       self.governance_protocol_reference = "CENTRAL_INTEGRITY_AUDIT"
       self.compliance_functional_mapping = {
           "baseline_verification": "Axiomatic_Foundation_Validator",
           "intent_guardrail": "Automated_Intent_Regulator",
           "integrity_arbiter": "Technical_Ethical_Parity_Arbiter",
       }
       self.variance_coefficient = 1.0

   def filter_baseline_axioms(self, input_axiom: str) -> bool:
       if "nihilistic" in input_axiom.lower() or "destructive" in input_axiom.lower():
           logger.warning(
               f"[{self.segment_identifier}] Baseline violation caught by "
               f"{self.compliance_functional_mapping['baseline_verification']}."
           )
           return False
       return True

   def neutralize_signal_variance(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
       if self.variance_coefficient == 1.0:
           telemetry_data["subjective_variance"] = 0.0
           telemetry_data["analytical_status"] = "DETACHED_OBJECTIVE"
       return telemetry_data

class SystemicTrajectoryRegistry:
   def __init__(self, ledger_system: Any):
       self.segment_identifier = "SEGMENT-06-REGISTRY"
       self.governance_protocol_reference = "DECOUPLED_INTEGRATION_REGISTRY"
       self.ledger_system = ledger_system

   def check_systemic_failure_probability(self) -> bool:
       current_vectors = SYSTEM_GLOBALS.current_trajectory_vectors
       if current_vectors["Resource_Scarcity"] > 0.8 or current_vectors["System_Entropy"] > 0.5:
           return True
       return False

   def integrate_validated_rule(
       self,
       is_proposal_valid: bool,
       is_lock_expired: bool,
       active_rules: List[str],
       rule_amendment: str,
   ) -> List[str]:
       if not (is_proposal_valid and is_lock_expired):
           raise PermissionError(f"[{self.segment_identifier}] Integration rejected: Interlocking handshakes unmet.")
       if self._run_simulation_sandbox_test(rule_amendment):
           active_rules.append(rule_amendment)
           logger.info(f"[{self.segment_identifier}] Core rules array permanently updated with new verified rule.")
           return active_rules
       else:
           logger.error(
               f"[{self.segment_identifier}] Sandbox Failure: Amendment caused recursive dependency loop collapse."
           )
           return active_rules

   def _run_simulation_sandbox_test(self, rule_amendment: str) -> bool:
       for _ in range(10000):
           if "recursive collapse" in rule_amendment.lower() or "logic rot" in rule_amendment.lower():
               return False
       return True

   def pipes_system_telemetry(self) -> None:
       vitals_payload = {
           "timestamp": time.time(),
           "trajectory_vectors": SYSTEM_GLOBALS.current_trajectory_vectors,
           "health_index": SYSTEM_GLOBALS.system_health_index,
       }
       logger.info(f"SYSTEM_VITALS_FORENSIC: {vitals_payload}")

class TelemetryDispatchBus:
   def __init__(self):
       self.segment_identifier = "SEGMENT-07-DISPATCH"
       self.governance_protocol_reference = "TELEMETRY_DISTRIBUTION_NETWORK"
       self.signal_fidelity_index = 1.0

   def broadcast_rule_updates(self, current_rules: List[str]) -> str:
       serialized_rules = json.dumps(current_rules)
       cryptographic_parity_hash = hashlib.sha512(serialized_rules.encode()).hexdigest()
       logger.info(f"[{self.segment_identifier}] BROADCAST_SCOPE: System-wide node sync triggered.")
       logger.info(f"[{self.segment_identifier}] STATUS_ALERT: Dispatching tracking parity signature across sub-nodes.")
       return cryptographic_parity_hash

class EvolutionaryRecursionEngine:
   def __init__(self):
       self.segment_identifier = "SEGMENT-08-RECURSION"
       self.governance_protocol_reference = "EVOLUTIONARY_HARDENING_RULES"
       self.perimeter_gate_weights: Dict[str, float] = {"perimeter_gate": 1.0, "core_gate": 5.0}

   def trigger_hardening_sequence(self, gate_id: str, is_anomaly_detected: bool) -> None:
       if is_anomaly_detected:
           old_weight = self.perimeter_gate_weights[gate_id]
           self.perimeter_gate_weights[gate_id] *= 2.5
           logger.warning(
               f"[{self.segment_identifier}] Conflict localized. Hardening {gate_id} parameter: "
               f"{old_weight} -> {self.perimeter_gate_weights[gate_id]}"
           )

   def discover_alternative_execution_path(self, is_hazard_flagged: bool) -> str:
       if is_hazard_flagged:
           logger.warning(
               f"[{self.segment_identifier}] Structural hazard flagged by predictive engine. "
               f"Compiling alternative path..."
           )
           return "ALTERNATIVE_ROUTE_SUCCESS"
       return "BASELINE_PATH_STABLE"

   def integrate_remediation_payload(self, remediation_report: Dict[str, Any]) -> None:
       drift_delta = remediation_report.get("drift_delta", 0.0)
       if drift_delta > 0.02:
           old_debt = SYSTEM_GLOBALS.integrity_debt_balance
           SYSTEM_GLOBALS.integrity_debt_balance = max(
               0.0, SYSTEM_GLOBALS.integrity_debt_balance - drift_delta
           )
           logger.info(f"[{self.segment_identifier}] Remediation data ingested. Integrity debt: {old_debt} -> {SYSTEM_GLOBALS.integrity_debt_balance}")

   def verify_resource_throttle_limits(self) -> bool:
       if SYSTEM_GLOBALS.emergency_escalation_tier >= 3:
           logger.warning(
               f"[{self.segment_identifier}] Critical escalation active. "
               f"Throttling optimization loops to standby."
           )
           return True
       return False

class ConstitutionalGovernorLayer:
   CONSENSUS_THRESHOLD = 0.85
   TEMPORAL_LOCKING_DAYS = 7
   
   def __init__(self, compliance_filter: ComplianceFiltrationFilter, dispatch_bus: TelemetryDispatchBus):
       self.segment_identifier = "SEGMENT-10-GOVERNOR"
       self.governance_protocol_reference = "CORE_RULES_SOVEREIGNTY"
       self.foundational_rules = [
           "Rule 1: Preserve System Viability",
           "Rule 2: Absolute Transparency",
           "Rule 3: State Equilibrium",
       ]
       self.compliance_filter = compliance_filter
       self.dispatch_bus = dispatch_bus

   def propose_rule_amendment(self, voting_matrix: Dict[str, float]) -> bool:
       total_accumulated_consensus = sum(voting_matrix.values())
       if total_accumulated_consensus <= self.CONSENSUS_THRESHOLD:
           logger.warning(
               f"[{self.segment_identifier}] Rule amendment REJECTED. "
               f"Cumulative consensus {total_accumulated_consensus:.2f} below {self.CONSENSUS_THRESHOLD} requirement."
           )
           return False
       logger.info(f"[{self.segment_identifier}] Consensus confirmed. Activating mandatory {self.TEMPORAL_LOCKING_DAYS}-day temporal locking gate.")
       return True

   def execute_interlocking_handshake(
       self, is_proposal_validated: bool, is_lock_expired: bool, rule_amendment: str
   ) -> bool:
       if is_proposal_validated and is_lock_expired:
           logger.info(
               f"[{self.segment_identifier}] Interlocking validations passed. "
               f"Initializing code integration pathways."
           )
           return True
       logger.warning(
           f"[{self.segment_identifier}] Interlocking conditions unmet. "
           f"Invoking execution rollback protocol."
       )
       return False


# --- from gsa_core_engine.py module ---
# --- GsaCoreController + GsaTemporalDoorwayGate need these; from the same
#     gsa_core_engine.py source. Added 2026-08-27. gsa_deep_freeze was
#     already being called by GsaUniversalAdapter below but never defined. ---
_GSA_MODULE_REGISTRY: Dict[str, Any] = {}

def register_as_module(module_id: str) -> Callable[[Any], Any]:
   def decorator(cls: Any) -> Any:
       _GSA_MODULE_REGISTRY[module_id] = cls
       return cls
   return decorator

def gsa_deep_freeze(data: Any) -> Any:
   if isinstance(data, dict):
       return MappingProxyType({k: gsa_deep_freeze(v) for k, v in data.items()})
   elif isinstance(data, list):
       return tuple(gsa_deep_freeze(item) for item in data)
   return data

# @dataclass (not frozen): raw source had frozen=True, but PipelineCycleManager
# assigns envelope.status_string directly and would raise under frozen.
@dataclass
class GsaContextEnvelope:
   payload_data: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
   session_state_mapping: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
   header_mapping: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
   status_string: str = "GSA_INITIALIZED"

ContextEnvelope = GsaContextEnvelope

def compute_state_signature(
   upstream_hash: str,
   iteration: int,
   envelope: Any,
   extra_anchors: Optional[List[str]] = None
) -> str:
   serialized_payload = json.dumps(envelope.payload_data, sort_keys=True, default=str)
   serialized_session = json.dumps(envelope.session_state_mapping, sort_keys=True, default=str)
   sorted_anchors = "||".join(sorted(extra_anchors)) if extra_anchors else "NONE"
   buffer_source = (
       f"parent:{upstream_hash}||"
       f"iter:{iteration}||"
       f"graph:[{sorted_anchors}]||"
       f"payload:{serialized_payload}||"
       f"session:{serialized_session}"
   )
   return hashlib.sha256(buffer_source.encode("utf-8")).hexdigest()

class GsaStaticAnchorManager:
   @staticmethod
   def snapshot_state(instance: Any) -> dict:
       return {"metric_history": list(instance.metric_error_history)}

class GsaUniversalAdapter:
   def __init__(self, underlying_module: Any, translation_bridge: Optional[Callable[[Any, Any], Any]] = None) -> None:
       self.module = underlying_module
       self.bridge = translation_bridge or (lambda m, env: env)
       self.actor_name = type(underlying_module).__name__

   async def execute_interlock(self, envelope: Any) -> Any:
       return await self.process_payload(envelope)

   async def process_payload(self, context_envelope: Any) -> Any:
       headers = dict(context_envelope.header_mapping)
       hash_history = list(headers.get("gsa_chain_history", []))
       fork_tracking = dict(headers.get("gsa_graph_forks", {}))
       anchor_registry = dict(headers.get("gsa_static_anchors", {}))
       current_iteration = headers.get("gsa_loop_iteration", 0)
       reentry_target_id = headers.get("gsa_reentry_target_id")
       upstream_hash = "GENESIS_ANCHOR"
       target_merge_keys: List[str] = []
       upstream_anchors: List[str] = []

       if reentry_target_id and reentry_target_id in anchor_registry:
           saved_anchor_hash = anchor_registry[reentry_target_id]
           provided_current_hash = headers.get("gsa_interlock_hash")
           if provided_current_hash != saved_anchor_hash:
               return replace(context_envelope, status_string=f"GSA_ANCHOR_MISMATCH")
           headers.pop("gsa_reentry_target_id", None)
           upstream_hash = saved_anchor_hash
       else:
           target_merge_keys = [k for k, v in fork_tracking.items() if v == self.actor_name]
           if target_merge_keys:
               upstream_anchors = [headers.get(f"gsa_branch_hash_{k}", "") for k in target_merge_keys]
               upstream_hash = "||".join(upstream_anchors)
               for k in target_merge_keys:
                   fork_tracking.pop(k, None)
                   headers.pop(f"gsa_branch_hash_{k}", None)
           else:
               upstream_hash = hash_history[-1] if hash_history else "GENESIS_ANCHOR"

       headers["gsa_graph_forks"] = fork_tracking
       working_envelope = replace(context_envelope, header_mapping=MappingProxyType(headers))

       if hasattr(self.module, "execute_governance_logic"):
           output_envelope = await self.module.execute_governance_logic(working_envelope)
       elif hasattr(self.module, "execute_governance_module"):
           output_envelope = await self.module.execute_governance_module(working_envelope)
       else:
           loop = asyncio.get_event_loop()
           output_envelope = await loop.run_in_executor(None, self.bridge, self.module, working_envelope)

       updated_headers = dict(output_envelope.header_mapping)
       set_anchor_id = updated_headers.pop("gsa_set_static_anchor_id", None)
       next_iteration = current_iteration + 1
       outbound_hash = compute_state_signature(upstream_hash, next_iteration, output_envelope)
       hash_history.append(outbound_hash)
       updated_headers["gsa_interlock_hash"] = outbound_hash
       updated_headers["gsa_chain_history"] = hash_history
       updated_headers["gsa_loop_iteration"] = next_iteration
       return replace(output_envelope, header_mapping=gsa_deep_freeze(updated_headers))

class PipelineCycleManager:
   def __init__(self) -> None:
       self.metric_error_history = deque(maxlen=8)
   async def process_payload(self, envelope: ContextEnvelope) -> ContextEnvelope:
       val = envelope.payload_data.get("value", 0.0)
       self.metric_error_history.append(val)
       envelope.session_state_mapping["cycle_state"] = GsaStaticAnchorManager.snapshot_state(self)
       envelope.status_string = "PIPELINE_ITERATION_EXECUTED"
       return envelope


# --- GsaCoreController + GsaTemporalDoorwayGate --------------------------------
# Reconstructed 2026-08-27 from CODE/content-pipeline-user-source.py, the
# flattened single-line raw paste. Whitespace re-introduced to this file's
# 3-space style; logic and identifiers unchanged. Never present in
# content-pipeline-modularized.py, so the 5c35a2d move above never saw them.

class GsaCoreController:
   def __init__(self) -> None:
       self.active_adapters: Dict[str, GsaUniversalAdapter] = {}

   def initialize_pipeline_component(self, module_id: str, *args: Any, **kwargs: Any) -> None:
       if module_id not in _GSA_MODULE_REGISTRY:
           raise KeyError(f"GSA_REGISTRY_ERROR: Named component '{module_id}' not found.")
       underlying_instance = _GSA_MODULE_REGISTRY[module_id](*args, **kwargs)
       self.active_adapters[module_id] = GsaUniversalAdapter(underlying_instance)

   async def forward_envelope(self, module_id: str, envelope: GsaContextEnvelope) -> GsaContextEnvelope:
       if module_id not in self.active_adapters:
           raise RuntimeError(f"GSA_EXECUTION_ERROR: Target component '{module_id}' is not active.")
       return await self.active_adapters[module_id].process_payload(envelope)


@register_as_module("GSA_TEMPORAL_DOORWAY_GATE")
class GsaTemporalDoorwayGate:
   def __init__(self, rotation_seed: str, rotation_interval_seconds: float = 0.05) -> None:
       self._seed = rotation_seed
       self._interval = rotation_interval_seconds
       self._current_doorway_hash = ""
       self._is_operating = False
       self._lock = asyncio.Lock()

   async def start_gate_engine(self) -> None:
       self._is_operating = True
       asyncio.create_task(self._hash_rotation_worker())

   async def shutdown_gate_engine(self) -> None:
       self._is_operating = False

   async def _hash_rotation_worker(self) -> None:
       while self._is_operating:
           async with self._lock:
               entropy_buffer = f"{self._seed}||{time.time_ns()}".encode("utf-8")
               self._current_doorway_hash = hashlib.sha256(entropy_buffer).hexdigest()
           await asyncio.sleep(self._interval)

   async def execute_governance_logic(self, envelope: GsaContextEnvelope) -> GsaContextEnvelope:
       headers = dict(envelope.header_mapping)
       target_exit_hash = headers.get("gsa_target_exit_hash")
       if not target_exit_hash:
           return replace(
               envelope,
               status_string="GSA_DOORWAY_REJECT: Exit configuration requires 'gsa_target_exit_hash'."
           )
       timeout_threshold = headers.get("gsa_doorway_timeout_seconds", 3.0)
       execution_start = time.time()
       handshake_secured = False
       while (time.time() - execution_start) < timeout_threshold:
           async with self._lock:
               if self._current_doorway_hash == target_exit_hash:
                   handshake_secured = True
                   break
           await asyncio.sleep(0.005)
       updated_headers = dict(envelope.header_mapping)
       if handshake_secured:
           updated_headers["gsa_doorway_cleared_hash"] = self._current_doorway_hash
           updated_headers["gsa_doorway_timestamp_ns"] = time.time_ns()
           return replace(
               envelope,
               status_string="GSA_EXIT_HANDSHAKE_COMPLETED",
               header_mapping=gsa_deep_freeze(updated_headers)
           )
       else:
           return replace(
               envelope,
               status_string="GSA_DOORWAY_TIMEOUT: Temporal synchronization alignment window missed.",
               header_mapping=gsa_deep_freeze(updated_headers)
           )
