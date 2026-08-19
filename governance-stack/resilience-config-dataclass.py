from dataclasses import dataclass

@dataclass
class ResilienceConfig:
   """
   Centralized governance registry for the universal ecosystem.
   This configuration defines the 'Safety Envelopes' within which the 
   Orchestrator, Fortress, and Iceberg modules must operate.
   """
   
   # ===== Stability Verification Thresholds =====
   # Defines the granularity of stability monitoring
   stability_stable: float = 1e-4
   stability_marginal: float = 1e-2
   
   # ===== Lyapunov/Distortion Weights =====
   # Determines sensitivity to system energy variance and surprisal
   volatility_weight: float = 0.05
   surprisal_weight: float = 0.02
   
   # ===== Causal Divergence Constants =====
   # Caps and scaling factors for divergence detection
   causal_divergence_cap: float = 0.45
   causal_divergence_scale: float = 25.0
   
   # ===== Governance Gates (Hysteresis) =====
   # Prevents chattering by enforcing a dead-band between 
   # entering and exiting governed modes
   enter_threshold: float = 0.55
   exit_threshold: float = 0.35
   
   # ===== Autopoietic Survival Thresholds =====
   # Defines the limits of the system's operational queues
   queue_max: float = 5000.0
   abandon_max: float = 0.95
   
   # ===== Tuning Knobs (Alpha Slew) =====
   # Controls the speed of authority transition ('Slew Rate')
   nominal_slew: float = 0.20
   sensitivity: float = 15.0

   def validate(self):
       """
       Self-check consistency of the configuration.
       Ensures Hysteresis logic is mathematically valid.
       """
       if self.enter_threshold <= self.exit_threshold:
           raise ValueError(
               "Governance enter_threshold must exceed exit_threshold "
               "(Hysteresis violation detected)."
           )

# End of resilience_config.py