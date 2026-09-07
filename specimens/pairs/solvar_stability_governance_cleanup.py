from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol

import matplotlib.pyplot as plt
import numpy as np

# ==============================================================================
# NUMERICAL CONSTANTS (SSOT ARCHITECTURAL SPECIFICATIONS)
# ==============================================================================

AXIS_HANDLE_TIME_FRICTION_SCALE = 25.0
ABANDONMENT_THRESHOLD_BASE_SCALE = 1.2
ABANDONMENT_FRICTION_BASE_SCALE = 0.9
CONFUSION_REENTRY_BASE_SCALE = 1.5
CONFUSION_REPEAT_AUTH_BASE_SCALE = 1.0
TRANSFER_PROPENSITY_BASE_SCALE = 1.3
CALLBACK_ABANDON_BASE_SCALE = 2.0
BACKOFFICE_REENTRY_BASE_SCALE = 0.5
SHORT_DISCONNECT_BASE_SCALE = 0.4
MINIMUM_DETERMINISM_INDEX = 0.01
REGIME_HYSTERESIS_WEIGHT = 0.15

EXPECTED_REGIME_FEATURES = ("stable", "surge", "confusion", "panic")


# ==============================================================================
# PROGRAMMATIC DATA TYPES & MODELS
# ==============================================================================

@dataclass(frozen=True)
class OperationalRate:
   """Tracks raw numeric metrics along with stabilized values."""
   raw_value: float
   stabilized_value: float


@dataclass(frozen=True, slots=True)
class OperationalMetrics:
   """Unified system performance indices used across simulation layers."""
   containment_rate: float = 0.0
   average_handle_time: float = 0.0
   callback_rate: float = 0.0
   abandon_rate: float = 0.0
   backoffice_trigger_rate: float = 0.0
   determinism_index: float = 1.0
   repeat_authentication_rate: float = 0.0
   ivr_reentry_rate: float = 0.0
   transfer_rate: float = 0.0
   short_disconnect_rate: float = 0.0
   queue_depth_index: float = 0.0


@dataclass
class MetricDiagnostics:
   """Telemetry capture for non-stabilized raw metric definitions."""
   abandon_rate_raw: Optional[float] = None
   callback_rate_raw: Optional[float] = None
   ivr_reentry_rate_raw: Optional[float] = None


@dataclass
class ProjectedMetrics:
   """Combines core metric indices with standard diagnostic data."""
   metrics: OperationalMetrics
   diagnostics: MetricDiagnostics


@dataclass
class EvaluationResult:
   """Result details emitted by policy governance models."""
   population_type: str
   verdict_status: str
   rationale_text: str


@dataclass
class EvaluationContext:
   """Execution context and metadata for unique evaluation steps."""
   run_uuid: str
   execution_timestamp: datetime
   dominant_regime_type: str
   regime_confidence_score: float
   regime_profile_scores: Dict[str, float]


@dataclass
class OperationalEvaluation:
   """Consolidated wrapper encapsulating an evaluation outcome and its context."""
   outcome: EvaluationResult
   context: EvaluationContext


@dataclass
class SyntheticAgent:
   """Fine-grained behavioral parameters tracking an individual interaction node."""
   agent_id: str
   account_segment: str
   delinquency_status: str
   repayment_shock_index: float
   confusion_tolerance_index: float
   emotional_state_index: float
   trust_state_index: float
   retry_propensity_index: float
   escalation_propensity_index: float
   abandonment_threshold_index: float
   prior_contact_count: int
   fraud_risk_index: float
   demographic_weight_factor: float = 1.0


@dataclass
class CohortParameterSummary:
   """Aggregated population summaries parsed by the behavior engines."""
   total_records_count: int = 0
   total_weighted_population: float = 0.0
   average_repayment_shock: float = 0.5
   average_confusion_tolerance: float = 0.5
   average_escalation_propensity: float = 0.5
   average_abandonment_threshold: float = 0.5
   maximum_repayment_shock: float = 0.0
   minimum_confusion_tolerance: float = 1.0


@dataclass
class TouchpointModification:
   """Tracks contextual alterations applied to workflow channels."""
   channel_type: str
   exposure_duration_seconds: float
   friction_coefficient: float
   clarity_coefficient: float
   randomize_verification_protocol: bool = False


# ==============================================================================
# RESERVOIR STATE SPACE ESTIMATOR (ECHO STATE MECHANICS)
# ==============================================================================

class EchoStateReservoir:
   """Echo State Network execution layer for multi-step trajectory projection."""

   def __init__(
       self,
       random_seed: str = "sentinel_fixed_seed",
       network_size: int = 128,
       input_dimensions: int = 4,
   ) -> None:
       hash_value = int(hashlib.sha256(random_seed.encode()).hexdigest(), 16) % (2**32)
       generator = np.random.default_rng(hash_value)

       self.network_size = network_size
       self.input_dimensions = input_dimensions
       self.internal_weight_matrix = generator.standard_normal((network_size, network_size)) * 0.05
       self.input_weight_matrix = generator.standard_normal((network_size, input_dimensions)) * 0.1
       self.current_state_vector = np.zeros(network_size)
       self.output_weight_matrix: Optional[np.ndarray] = None
       self._normalize_spectral_radius(spectral_radius_target=0.90)

   def _normalize_spectral_radius(self, spectral_radius_target: float) -> None:
       eigenvalues = np.linalg.eigvals(self.internal_weight_matrix)
       maximum_radius = max(abs(eigenvalues)) if len(eigenvalues) else 1.0
       if maximum_radius > 0:
           self.internal_weight_matrix = (self.internal_weight_matrix / maximum_radius) * spectral_radius_target

   def validate_matrix_stability(self) -> None:
       eigenvalues = np.linalg.eigvals(self.internal_weight_matrix)
       maximum_radius = max(abs(eigenvalues)) if len(eigenvalues) else 0.0
       if maximum_radius > 1.0:
           raise ValueError(f"Unstable reservoir state configuration. Spectral radius = {maximum_radius}")

   def transition_step(self, input_vector: np.ndarray) -> np.ndarray:
       self.current_state_vector = np.tanh(
           self.internal_weight_matrix @ self.current_state_vector + self.input_weight_matrix @ input_vector
       )
       return self.current_state_vector

   def project_trajectory(self, input_vector: np.ndarray, prediction_steps: int = 3) -> np.ndarray:
       state_copy = self.current_state_vector.copy()
       output_trajectories = []

       for _ in range(prediction_steps):
           state_copy = np.tanh(
               self.internal_weight_matrix @ state_copy + self.input_weight_matrix @ input_vector
           )
           if self.output_weight_matrix is not None:
               augmented_vector = np.concatenate([state_copy, input_vector, [1.0]])
               prediction_output = self.output_weight_matrix @ augmented_vector
               extracted_output = prediction_output[:self.input_dimensions]
               output_trajectories.append(extracted_output)
               input_vector = extracted_output
           else:
               output_trajectories.append(input_vector)

       return np.array(output_trajectories)


# ==============================================================================
# HISTORICAL WINDOW MANAGEMENT BUFFER
# ==============================================================================

class DynamicDelayBuffer:
   """Maintains a bounded historical sliding timeline of system execution states."""

   def __init__(self, allocation_capacity: int = 3) -> None:
       self.allocation_capacity = allocation_capacity
       self.internal_buffer: List[OperationalEvaluation] = []

   def append_state(self, evaluation_node: OperationalEvaluation) -> Optional[OperationalEvaluation]:
       self.internal_buffer.append(evaluation_node)
       if len(self.internal_buffer) > self.allocation_capacity:
           return self.internal_buffer.pop(0)
       return None


# ==============================================================================
# EXCEPTIONS & SECURITY CONTRACTS (ETHICS VALIDATION GATE)
# ==============================================================================

class EthicsViolation(Exception):
   """Raised when operational metrics exceed critical survival thresholds."""
   pass


class EthicsValidationEngine:
   """Enforces mathematical boundaries to block runaway system collapse or toxic delays."""

   def autopoietic_check(self, operational_state: OperationalMetrics) -> bool:
       if operational_state.queue_depth_index > 5000.0 or operational_state.abandon_rate > 0.95:
           return False
       return True


# ==============================================================================
# NUMERICAL UTILITIES
# ==============================================================================

def stabilize_logit(probability_value: float) -> float:
   """Transforms a raw probability value into log-odds space with boundary defense."""
   p_bounded = min(max(probability_value, 1e-9), 1.0 - 1e-9)
   return math.log(p_bounded / (1.0 - p_bounded))


def stabilize_inverse_logit(log_odds_value: float) -> float:
   """Transforms a log-odds value back into standard probability space."""
   return 1.0 / (1.0 + math.exp(-log_odds_value))


# ==============================================================================
# COHORT AGGREGATION
# ==============================================================================

class CohortParameterAggregator:
   """Compiles individual synthetic agent parameters into group baseline summaries."""

   def summarize_population(self, agent_iterable: Iterable[SyntheticAgent]) -> CohortParameterSummary:
       records_count = 0
       weight_sum = 0.0
       shock_sum = 0.0
       confusion_sum = 0.0
       escalation_sum = 0.0
       abandonment_sum = 0.0
       max_shock = 0.0
       min_confusion = 1.0

       for agent in agent_iterable:
           weight = agent.demographic_weight_factor
           records_count += 1
           weight_sum += weight
           shock_sum += agent.repayment_shock_index * weight
           confusion_sum += agent.confusion_tolerance_index * weight
           escalation_sum += agent.escalation_propensity_index * weight
           abandonment_sum += agent.abandonment_threshold_index * weight

           if agent.repayment_shock_index > max_shock:
               max_shock = agent.repayment_shock_index
           if agent.confusion_tolerance_index < min_confusion:
               min_confusion = agent.confusion_tolerance_index

       if weight_sum == 0.0:
           return CohortParameterSummary()

       return CohortParameterSummary(
           total_records_count=records_count,
           total_weighted_population=weight_sum,
           average_repayment_shock=round(shock_sum / weight_sum, 3),
           average_confusion_tolerance=round(confusion_sum / weight_sum, 3),
           average_escalation_propensity=round(escalation_sum / weight_sum, 3),
           average_abandonment_threshold=round(abandonment_sum / weight_sum, 3),
           maximum_repayment_shock=round(max_shock, 3),
           minimum_confusion_tolerance=round(min_confusion, 3),
       )


# ==============================================================================
# EVENT SYSTEM AUDITING
# ==============================================================================

@dataclass(frozen=True)
class OperationalEvent:
   """Programmatic transaction payload captured by the ledger loggers."""
   event_type: str
   run_uuid: str
   record_timestamp: datetime
   event_payload: Dict[str, Any]


class AuditEventStore:
   """Maintains an append-only in-memory sequential event ledger."""

   def __init__(self) -> None:
       self.historical_events: List[OperationalEvent] = []
       self.failure_log_history: List[str] = []

   def append_event(self, event_node: OperationalEvent) -> None:
       self.historical_events.append(event_node)

   def record_failure_message(self, runtime_message: str) -> None:
       self.failure_log_history.append(runtime_message)

   def extract_recent_failures(self) -> List[str]:
       """Returns the last 10 entries recorded in the verification logging timeline."""
       return list(itertools.islice(reversed(self.failure_log_history), 10))

   def fetch_all_events(self) -> List[OperationalEvent]:
       return list(self.historical_events)


class OperationalEventPublisher:
   """Manages publishing operations directed toward target event storages."""

   def __init__(self, target_store: AuditEventStore) -> None:
       self._target_store = target_store

   def publish_transaction(self, operational_event: OperationalEvent) -> None:
       self._target_store.append_event(operational_event)


# ==============================================================================
# REPLAY UTILITIES
# ==============================================================================

class OperationalReplayHasher:
   """Computes SHA-256 state signatures to audit historical ledger records."""

   def hash_event_node(self, event_node: OperationalEvent) -> str:
       serialized_payload = json.dumps(event_node.__dict__, default=str, sort_keys=True)
       return hashlib.sha256(serialized_payload.encode()).hexdigest()


class LedgerRebuildBuilder:
   """Reconstructs contextual execution structures by replaying historical events."""

   def __init__(self, target_store: AuditEventStore) -> None:
       self._target_store = target_store
       self._hasher = OperationalReplayHasher()
       self._action_handlers = {
           "EVAL_RESULT": self._process_eval_payload,
           "ADVISORY": self._process_advisory_payload,
       }

   def reconstruct_state(self) -> Dict[str, Any]:
       rebuilt_state = {"evaluations": [], "advisories": [], "audit_hashes": []}
       for event in self._target_store.fetch_all_events():
           rebuilt_state["audit_hashes"].append(self._hasher.hash_event_node(event))
           handler = self._action_handlers.get(event.event_type)
           if handler:
               handler(rebuilt_state, event)
       return rebuilt_state

   def _process_eval_payload(self, state_dict: Dict[str, Any], event_node: OperationalEvent) -> None:
       state_dict["evaluations"].append(event_node.event_payload)

   def _process_advisory_payload(self, state_dict: Dict[str, Any], event_node: OperationalEvent) -> None:
       state_dict["advisories"].append(event_node.event_payload)


# ==============================================================================
# BORROWER BEHAVIOR MODELING
# ==============================================================================

class SyntheticAgentModel:
   """Updates fine-grained agent parameter states against step variations."""

   def apply_modifications(
       self, agent: SyntheticAgent, modification: TouchpointModification
   ) -> SyntheticAgent:
       confusion = agent.confusion_tolerance_index
       emotion = agent.emotional_state_index
       trust = agent.trust_state_index

       if modification.clarity_coefficient < 0.5:
           confusion = max(0.0, confusion - (0.5 - modification.clarity_coefficient) * 0.5)
           emotion = min(1.0, emotion + (0.5 - modification.clarity_coefficient) * 0.3)
       else:
           confusion = min(1.0, confusion + (modification.clarity_coefficient - 0.5) * 0.2)
           trust = min(1.0, trust + (modification.clarity_coefficient - 0.5) * 0.1)

       if modification.friction_coefficient > 0.4:
           excess_friction = modification.friction_coefficient - 0.4
           confusion = max(0.0, confusion - excess_friction * 0.4)
           emotion = min(1.0, emotion + excess_friction * 0.4)

       return SyntheticAgent(
           agent_id=agent.agent_id,
           account_segment=agent.account_segment,
           delinquency_status=agent.delinquency_status,
           repayment_shock_index=agent.repayment_shock_index,
           confusion_tolerance_index=round(confusion, 3),
           emotional_state_index=round(emotion, 3),
           trust_state_index=round(trust, 3),
           retry_propensity_index=round(
               min(1.0, agent.retry_propensity_index + (1.0 - confusion) * 0.2), 3
           ),
           escalation_propensity_index=round(
               min(1.0, (1.0 - trust) * 0.7 + emotion * 0.3), 3
           ),
           abandonment_threshold_index=round(
               max(0.05, agent.abandonment_threshold_index - emotion * 0.2), 3
           ),
           prior_contact_count=agent.prior_contact_count,
           fraud_risk_index=agent.fraud_risk_index,
           demographic_weight_factor=agent.demographic_weight_factor,
       )


# ==============================================================================
# BEHAVIOR PROJECTION PATTERNS
# ==============================================================================

class PredictiveBehaviorModel(Protocol):
   def project_metrics_degradation(
       self,
       baseline: OperationalMetrics,
       cohort: CohortParameterSummary,
       modification: TouchpointModification,
   ) -> ProjectedMetrics:
       ...


class BasePredictiveBehaviorModel:
   """Transforms aggregated group states into logit-stabilized matrix metric predictions."""

   def project_metrics_degradation(
       self,
       baseline: OperationalMetrics,
       cohort: CohortParameterSummary,
       modification: TouchpointModification,
   ) -> ProjectedMetrics:

       handle_time = self._calculate_handle_time(baseline, modification)
       abandon = self._calculate_abandon_rate(baseline, cohort, modification)
       reentry = self._calculate_reentry_rate(cohort, modification)
       repeat_auth = self._calculate_repeat_auth_rate(cohort, modification)
       transfer = self._calculate_transfer_rate(cohort)
       callback = self._calculate_callback_rate(baseline, abandon)
       backoffice = self._calculate_backoffice_rate(baseline, reentry)
       determinism = self._calculate_determinism_index(baseline, modification)
       disconnect = self._calculate_disconnect_rate(baseline, abandon)

       containment = max(
           0.0, min(1.0, baseline.containment_rate - (0.05 * modification.friction_coefficient))
       )

       metrics_node = OperationalMetrics(
           containment_rate=round(containment, 3),
           average_handle_time=round(handle_time, 1),
           callback_rate=round(callback.stabilized_value, 3),
           abandon_rate=round(abandon.stabilized_value, 3),
           backoffice_trigger_rate=round(backoffice, 3),
           determinism_index=round(determinism, 3),
           repeat_authentication_rate=round(repeat_auth.stabilized_value, 3),
           ivr_reentry_rate=round(reentry.stabilized_value, 3),
           transfer_rate=round(transfer.stabilized_value, 3),
           short_disconnect_rate=round(disconnect, 3),
           queue_depth_index=max(0.0, baseline.queue_depth_index * (1.0 + transfer.stabilized_value)),
       )

       diagnostics_node = MetricDiagnostics(
           abandon_rate_raw=round(abandon.raw_value, 4),
           callback_rate_raw=round(callback.raw_value, 4),
           ivr_reentry_rate_raw=round(reentry.raw_value, 4),
       )

       return ProjectedMetrics(metrics=metrics_node, diagnostics=diagnostics_node)

   def _calculate_handle_time(
       self, baseline: OperationalMetrics, modification: TouchpointModification
   ) -> float:
       return max(
           0.0,
           baseline.average_handle_time
           + (modification.friction_coefficient * AXIS_HANDLE_TIME_FRICTION_SCALE),
       )

   def _calculate_abandon_rate(
       self,
       baseline: OperationalMetrics,
       cohort: CohortParameterSummary,
       modification: TouchpointModification,
   ) -> OperationalRate:
       raw_odds = (
           stabilize_logit(baseline.abandon_rate)
           + (modification.friction_coefficient * ABANDONMENT_FRICTION_BASE_SCALE)
           - (cohort.average_abandonment_threshold * ABANDONMENT_THRESHOLD_BASE_SCALE)
       )
       return OperationalRate(raw_value=raw_odds, stabilized_value=stabilize_inverse_logit(raw_odds))

   def _calculate_reentry_rate(
       self, cohort: CohortParameterSummary, modification: TouchpointModification
   ) -> OperationalRate:
       confusion_factor = max(0.0, 1.0 - cohort.average_confusion_tolerance)
       raw_odds = stabilize_logit(0.1) + (
           confusion_factor * modification.friction_coefficient * CONFUSION_REENTRY_BASE_SCALE
       )
       return OperationalRate(raw_value=raw_odds, stabilized_value=stabilize_inverse_logit(raw_odds))

   def _calculate_repeat_auth_rate(
       self, cohort: CohortParameterSummary, modification: TouchpointModification
   ) -> OperationalRate:
       confusion_factor = max(0.0, 1.0 - cohort.average_confusion_tolerance)
       raw_odds = stabilize_logit(0.05) + (
           confusion_factor * modification.friction_coefficient * CONFUSION_REPEAT_AUTH_BASE_SCALE
       )
       return OperationalRate(raw_value=raw_odds, stabilized_value=stabilize_inverse_logit(raw_odds))

   def _calculate_transfer_rate(self, cohort: CohortParameterSummary) -> OperationalRate:
       raw_odds = stabilize_logit(0.1) + (
           cohort.average_escalation_propensity * TRANSFER_PROPENSITY_BASE_SCALE
       )
       return OperationalRate(raw_value=raw_odds, stabilized_value=stabilize_inverse_logit(raw_odds))

   def _calculate_callback_rate(
       self, baseline: OperationalMetrics, abandon: OperationalRate
   ) -> OperationalRate:
       raw_odds = stabilize_logit(baseline.callback_rate) + (
           abandon.stabilized_value * CALLBACK_ABANDON_BASE_SCALE
       )
       return OperationalRate(raw_value=raw_odds, stabilized_value=stabilize_inverse_logit(raw_odds))

   def _calculate_backoffice_rate(
       self, baseline: OperationalMetrics, reentry: OperationalRate
   ) -> float:
       return stabilize_inverse_logit(
           stabilize_logit(baseline.backoffice_trigger_rate)
           + (reentry.stabilized_value * BACKOFFICE_REENTRY_BASE_SCALE)
       )

   def _calculate_determinism_index(
       self, baseline: OperationalMetrics, modification: TouchpointModification
   ) -> float:
       return max(
           MINIMUM_DETERMINISM_INDEX,
           baseline.determinism_index
           - (
               0.1 * modification.friction_coefficient
               if modification.randomize_verification_protocol
               else 0.0
           ),
       )

   def _calculate_disconnect_rate(
       self, baseline: OperationalMetrics, abandon: OperationalRate
   ) -> float:
       return stabilize_inverse_logit(
           stabilize_logit(baseline.short_disconnect_rate)
           + (abandon.stabilized_value * SHORT_DISCONNECT_BASE_SCALE)
       )


# ==============================================================================
# STABILITY MODEL & REGIME DETECTION
# ==============================================================================

LYAPUNOV_AXIS_WEIGHTS: Dict[str, float] = {
   "abandon_rate": 1.0,
   "ivr_reentry_rate": 1.0,
   "transfer_rate": 1.0,
   "normalized_handle_time": 1.0,
}


class LyapunovStabilityModel:
   """Calculates multidimensional operational energy variance across target baseline parameters."""

   @staticmethod
   def calculate_system_energy(
       baseline: OperationalMetrics, current: OperationalMetrics, export_breakdown: bool = False
   ) -> Any:
       delta_matrix = np.array([
           current.abandon_rate - baseline.abandon_rate,
           current.ivr_reentry_rate - baseline.ivr_reentry_rate,
           current.transfer_rate - baseline.transfer_rate,
           (current.average_handle_time - baseline.average_handle_time)
           / (abs(baseline.average_handle_time) + 1e-9),
       ])

       weight_matrix = np.array([
           max(LYAPUNOV_AXIS_WEIGHTS["abandon_rate"], 1e-9),
           max(LYAPUNOV_AXIS_WEIGHTS["ivr_reentry_rate"], 1e-9),
           max(LYAPUNOV_AXIS_WEIGHTS["transfer_rate"], 1e-9),
           max(LYAPUNOV_AXIS_WEIGHTS["normalized_handle_time"], 1e-9),
       ])

       calculated_terms = weight_matrix * (delta_matrix**2)
       total_energy = float(np.sum(calculated_terms))

       if not export_breakdown:
           return total_energy

       return total_energy, {
           "abandon_rate_term": float(calculated_terms[0]),
           "ivr_reentry_rate_term": float(calculated_terms[1]),
           "transfer_rate_term": float(calculated_terms[2]),
           "normalized_handle_time_term": float(calculated_terms[3]),
       }

   @staticmethod
   def classify_energy_state(
       total_energy_value: float,
       stable_threshold: float = 1e-4,
       marginal_threshold: float = 1e-2,
   ) -> str:
       if total_energy_value <= stable_threshold:
           return "stable"
       if total_energy_value <= marginal_threshold:
           return "marginal"
       return "unstable"


@dataclass
class MacroRegimeProfile:
   profile_scores: Dict[str, float]
   dominant_regime_type: str
   confidence_score: float


class MacroRegimeDetector:
   """Scans performance indexes to categorize current operational environments."""

   def detect_regime(
       self,
       metrics: OperationalMetrics,
       temporal_window: Any,
       prior_regime: Optional[str],
   ) -> MacroRegimeProfile:
       regime_weights = {
           "stable": 0.5 if metrics.abandon_rate < 0.1 else 0.0,
           "surge": (
               0.6
               if (metrics.queue_depth_index > 30.0 and metrics.abandon_rate <= 0.15)
               else 0.0
           ),
           "confusion": (
               0.7
               if (metrics.ivr_reentry_rate > 0.3 or metrics.repeat_authentication_rate > 0.2)
               else 0.0
           ),
           "panic": 0.6 if metrics.abandon_rate > 0.25 else 0.0,
       }

       if prior_regime and prior_regime in regime_weights:
           regime_weights[prior_regime] += REGIME_HYSTERESIS_WEIGHT

       summation_total = sum(regime_weights.values()) + 1e-9
       normalized_scores = {k: v / summation_total for k, v in regime_weights.items()}
       dominant_type = max(normalized_scores, key=normalized_scores.get)

       return MacroRegimeProfile(
           profile_scores=normalized_scores,
           dominant_regime_type=dominant_type,
           confidence_score=round(normalized_scores[dominant_type], 3),
       )


# ==============================================================================
# GOVERNANCE & POLICY SYSTEMS
# ==============================================================================

class PolicyGovernanceKernel:
   """Evaluates trajectory changes to issue authorization verdicts."""

   def evaluate_policy_constraints(
       self,
       baseline: OperationalMetrics,
       current: OperationalMetrics,
       forecast_matrix: np.ndarray,
   ) -> EvaluationResult:
       computed_energy = LyapunovStabilityModel.calculate_system_energy(baseline, current)
       trajectory_stress_detected = len(forecast_matrix) > 0 and (
           forecast_matrix[0, 0] > current.abandon_rate * 1.2
       )

       if computed_energy > 0.05 or trajectory_stress_detected:
           verdict = "REJECT"
           rationale = "Stability constraints breached or future trajectory lookahead stress observed."
       elif current.abandon_rate > baseline.abandon_rate:
           verdict = "CAUTION"
           rationale = "Synthetic agent operational stress indicators showing growth parameters."
       else:
           verdict = "APPROVE"
           rationale = "Operating metrics remaining inside baseline target values."

       return EvaluationResult(
           population_type="borrower", verdict_status=verdict, rationale_text=rationale
       )


class AdvisoryDirectiveEngine:
   """Maps recognized macro regime shifts into mitigation directives."""

   MITIGATION_DIRECTIVES = {
       "panic": ["minimize cognitive load", "protect queue", "stabilize messaging"],
       "confusion": ["reduce recursive traversal", "increase intent clarity", "accelerate routing"],
       "surge": ["prioritize informational consistency", "protect queue stability"],
   }

   def generate_advisory_payload(self, regime_profile: MacroRegimeProfile) -> Dict[str, Any]:
       return {
           "profile": regime_profile.dominant_regime_type,
           "directives": self.MITIGATION_DIRECTIVES.get(
               regime_profile.dominant_regime_type, ["standard operating conditions"]
           ),
       }


# ==============================================================================
# RUNTIME INTEGRATED SENTINEL ARCHITECTURE
# ==============================================================================

class SOLVARSystemKernel:
   """Central orchestration runtime coordinator for predictive behavior governance."""

   def __init__(
       self,
       publisher: OperationalEventPublisher,
       detector: MacroRegimeDetector,
       governance: PolicyGovernanceKernel,
       agent_model: SyntheticAgentModel,
       predictive_model: PredictiveBehaviorModel,
       aggregator: CohortParameterAggregator,
       advisory_engine: AdvisoryDirectiveEngine,
   ) -> None:
       self._publisher = publisher
       self._detector = detector
       self._governance = governance
       self._agent_model = agent_model
       self._predictive_model = predictive_model
       self._aggregator = aggregator
       self._advisory_engine = advisory_engine
       self._ethics_gate = EthicsValidationEngine()

       self.lookahead_reservoir = EchoStateReservoir()
       self.sliding_delay_buffer = DynamicDelayBuffer(3)

   def split_data_stream(
       self, tracking_stream: Iterable[Any]
   ) -> tuple[Iterable[Any], Iterable[Any]]:
       """Splits an incoming stream for multi-consumer processing without data re-reads."""
       return itertools.tee(tracking_stream)

   def execute_simulation(
       self,
       baseline: OperationalMetrics,
       agent_cohort: Iterable[SyntheticAgent],
       modification: TouchpointModification,
   ) -> ProjectedMetrics:
       modified_agents = (
           self._agent_model.apply_modifications(agent, modification) for agent in agent_cohort
       )
       summary_parameters = self._aggregator.summarize_population(modified_agents)
       projection_output = self._predictive_model.project_metrics_degradation(
           baseline, summary_parameters, modification
       )

       if not self._ethics_gate.autopoietic_check(projection_output.metrics):
           self._publisher._target_store.record_failure_message(
               "Ethics check boundary violation detected during execution loop."
           )
           raise EthicsViolation(
               "Ethics validation failed - Operational state contains unresolvable degradation."
           )

       return projection_output

   def process_execution_step(
       self, baseline: OperationalMetrics, current: OperationalMetrics
   ) -> Dict[str, Any]:
       vectorized_inputs = np.array([
           current.abandon_rate,
           current.ivr_reentry_rate,
           current.transfer_rate,
           current.queue_depth_index / 100.0,
       ])

       self.lookahead_reservoir.transition_step(vectorized_inputs)

       wrapped_projections = ProjectedMetrics(metrics=current, diagnostics=MetricDiagnostics())
       evaluation_node = self.evaluate_operational_state(
           baseline, wrapped_projections, temporal_window=None, prior_regime=None
       )

       delayed_evaluation = self.sliding_delay_buffer.append_state(evaluation_node)

       return {
           "current": evaluation_node,
           "delayed": delayed_evaluation,
       }

   def evaluate_operational_state(
       self,
       baseline: OperationalMetrics,
       projected_node: ProjectedMetrics,
       temporal_window: Any = None,
       prior_regime: Optional[str] = None,
   ) -> OperationalEvaluation:
       regime_profile = self._detector.detect_regime(
           projected_node.metrics, temporal_window, prior_regime
       )

       vectorized_current = np.array([
           projected_node.metrics.abandon_rate,
           projected_node.metrics.ivr_reentry_rate,
           projected_node.metrics.transfer_rate,
           projected_node.metrics.queue_depth_index / 100.0,
       ])
       forecast_matrix = self.lookahead_reservoir.project_trajectory(
           vectorized_current, prediction_steps=3
       )

       governance_verdict = self._governance.evaluate_policy_constraints(
           baseline, projected_node.metrics, forecast_matrix
       )

       context_node = EvaluationContext(
           run_uuid=str(random.randint(100000, 999999)),
           execution_timestamp=datetime.now(timezone.utc),
           dominant_regime_type=regime_profile.dominant_regime_type,
           regime_confidence_score=regime_profile.confidence_score,
           regime_profile_scores=regime_profile.profile_scores,
       )

       evaluation_record = OperationalEvaluation(
           outcome=governance_verdict, context=context_node
       )

       self._publisher.publish_transaction(
           OperationalEvent(
               event_type="EVAL_RESULT",
               run_uuid=context_node.run_uuid,
               record_timestamp=context_node.execution_timestamp,
               event_payload={
                   "verdict": governance_verdict.verdict_status,
                   "rationale": governance_verdict.rationale_text,
                   "regime": regime_profile.dominant_regime_type,
               },
           )
       )
       return evaluation_record

   def generate_system_advisory(self, regime_profile: MacroRegimeProfile) -> Dict[str, Any]:
       advisory_payload = self._advisory_engine.generate_advisory_payload(regime_profile)

       self._publisher.publish_transaction(
           OperationalEvent(
               event_type="ADVISORY",
               run_uuid=str(random.randint(100000, 999999)),
               record_timestamp=datetime.now(timezone.utc),
               event_payload=advisory_payload,
           )
       )
       return advisory_payload


# ==============================================================================
# SYSTEM VISUALIZATION DIAGNOSTICS & TELEMETRY
# ==============================================================================

class TelemetryDashboardVisualizer:

   @staticmethod
   def output_energy_plot(
       energy_value_list: List[float], output_filename: str = "energy_plot.png"
   ) -> None:
       plt.figure(figsize=(10, 4))
       plt.plot(energy_value_list, label="Operational Variance Energy")
       plt.title("Lyapunov Energy Stability Matrix Metrics")
       plt.xlabel("Simulation Steps")
       plt.ylabel("Computed Energy")
       plt.legend()
       plt.tight_layout()
       plt.savefig(output_filename)
       plt.close()

   @staticmethod
   def output_classification_plot(
       classification_string_list: List[str], output_filename: str = "classification_plot.png"
   ) -> None:
       state_mapping = {"stable": 0, "marginal": 1, "unstable": 2}
       mapped_y_values = [state_mapping.get(c, 1) for c in classification_string_list]

       plt.figure(figsize=(10, 4))
       plt.step(range(len(mapped_y_values)), mapped_y_values, where="mid")
       plt.yticks([0, 1, 2], ["stable", "marginal", "unstable"])
       plt.title("Stability Interval Categorizations")
       plt.xlabel("Simulation Steps")
       plt.ylabel("Interval Classification")
       plt.tight_layout()
       plt.savefig(output_filename)
       plt.close()


# ==============================================================================
# HORIZON FORECASTING ENGINE
# ==============================================================================

class HorizonForecastingEngine:

   def __init__(
       self, baseline_metrics: OperationalMetrics, behavior_model: PredictiveBehaviorModel
   ) -> None:
       self._baseline_metrics = baseline_metrics
       self._behavior_model = behavior_model

   def generate_horizon_forecast(
       self,
       tracking_horizon: int,
       parameter_summary: CohortParameterSummary,
       touchpoint_schedule: Callable[[int], TouchpointModification],
   ) -> Dict[str, Any]:
       predicted_metrics_timeline: List[OperationalMetrics] = []

       for step in range(tracking_horizon):
           active_modification = touchpoint_schedule(step)
           step_projection = self._behavior_model.project_metrics_degradation(
               self._baseline_metrics, parameter_summary, active_modification
           )
           predicted_metrics_timeline.append(step_projection.metrics)

       calculated_energies = [
           LyapunovStabilityModel.calculate_system_energy(self._baseline_metrics, metric_step)
           for metric_step in predicted_metrics_timeline
       ]

       state_classifications = [
           LyapunovStabilityModel.classify_energy_state(energy_value)
           for energy_value in calculated_energies
       ]

       return {
           "projections": predicted_metrics_timeline,
           "energies": calculated_energies,
           "classifications": state_classifications,
       }


# ==============================================================================
# OPERATIONAL VERIFICATION BENCHMARKS
# ==============================================================================

class SystemPerformanceBenchmark:
   COMPARED_FIELDS = [
       "average_handle_time",
       "abandon_rate",
       "callback_rate",
       "containment_rate",
       "transfer_rate",
       "ivr_reentry_rate",
       "repeat_authentication_rate",
       "backoffice_trigger_rate",
       "short_disconnect_rate",
       "determinism_index",
   ]

   def execute_comparison(
       self, left_metrics: OperationalMetrics, right_metrics: OperationalMetrics
   ) -> List[str]:
       comparison_rows = []
       for field in self.COMPARED_FIELDS:
           left_value = getattr(left_metrics, field)
           right_value = getattr(right_metrics, field)
           comparison_rows.append(f"{field:28s} | left={left_value:.4f} | right={right_value:.4f}")
       return comparison_rows
