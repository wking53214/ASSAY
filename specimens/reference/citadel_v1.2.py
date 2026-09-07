# =============================================================================
# VENDORED COPY - not a reconstruction. Copied verbatim 2026-09-03 from
# https://github.com/wking53214/citadel, commit 81f0b817e864e5fdf73743e859d23321d355119e,
# file citadel_v1.2.py. That repo already runs; nothing below this header is
# changed. Wired into sovereign_kernel.py's step-2 linguistic scrub.
#
# Vendored rather than kept as a live dependency: GSA-GATEWAY has no packaging
# infrastructure anywhere (no requirements.txt/pyproject.toml), and every other
# governance-stack layer is already loaded the same way, as a local sibling
# file. CITADEL stays its own repo deliberately (a general-purpose LLM-output
# enforcer, not GSA-specific) - this copy will go stale if CITADEL changes
# upstream; re-sync by diffing against the commit above.
# =============================================================================
import re 
import time 
from enum import Enum 
from typing import Dict, List, Any # ============================================================ # CITADEL v1.2 # Deterministic LLM Output Enforcement Engine # Reconstructed from flattened source (artifact_1.py, copy 1 of 2) 2026-08-20; # v1.2 adds the prohibited_verbs check salvaged from the STRIDE repo before its deletion. 
# ============================================================ 
# ============================================================ # REGEX DETECTION LAYERS 
# ============================================================ 
REGEX = {
    "identity": re.compile(
        r"\b(i|me|my|mine|myself|we|us|our|ours|ourselves)\b",
        re.I
    ),
    "hedging": re.compile(
        r"\b(may|might|could|seems|generally|potentially|likely|perhaps|probably|i think)\b",
        re.I
    ),
    "passive": re.compile(
        r"\b(am|is|are|was|were|be|been|being)\b\s+\w+(ed|en)\b",
        re.I
    ),
    "metric": re.compile(
        r"\b\d+(\.\d+)?%|\b\d+\b"
    ),
    "causal": re.compile(
        r"\b(because|due to|driven by|resulting from|caused by|therefore|consequently)\b",
        re.I
    ),
    # PUNCTUATION CONTROL LAYER
    "emdash": re.compile(r"—"),
    # VAGUE-VERB CONTROL LAYER (salvaged from STRIDE/CLIP's PROHIBITED_VERBS,
    # confirmed not present in the original v1.1 pull; added v1.2)
    "prohibited_verbs": re.compile(
        r"\b(improve|optimize|enhance|enable|support|strengthen|utilize|leverage)\b",
        re.I
    )
} # ============================================================ # ENFORCEMENT PROFILES 
# ============================================================ 
PROFILES = {
    "default": {
        "identity": True,
        "hedging": True,
        "passive": False,
        "causality": False,
        "punctuation": True,
        "prohibited_verbs": False
    },
    "ops": {
        "identity": True,
        "hedging": True,
        "passive": True,
        "causality": True,
        "punctuation": True,
        "prohibited_verbs": True
    },
    "exec": {
        "identity": True,
        "hedging": True,
        "passive": True,
        "causality": False,
        "punctuation": True,
        "prohibited_verbs": True
    },
    "legal": {
        "identity": True,
        "hedging": True,
        "passive": True,
        "causality": True,
        "punctuation": True,
        "prohibited_verbs": False
    } } # ============================================================ # CONSTRAINT MODEL 
# ============================================================ 
class Constraint(Enum):
    IDENTITY = "identity"
    HEDGING = "hedging"
    PASSIVE = "passive"
    CAUSALITY = "causality"
    PUNCTUATION = "punctuation"
    PROHIBITED_VERBS = "prohibited_verbs" # ============================================================ # DETECTOR ENGINE 
# ============================================================ 
class CitadelDetector:
    def detect(self, text: str, profile: Dict[str, bool]) -> List[Dict[str, str]]:
        violations = []
        if profile["identity"] and REGEX["identity"].search(text):
            violations.append({
                "type": Constraint.IDENTITY.value,
                "snippet": self._extract(REGEX["identity"], text)
            })
        if profile["hedging"] and REGEX["hedging"].search(text):
            violations.append({
                "type": Constraint.HEDGING.value,
                "snippet": self._extract(REGEX["hedging"], text)
            })
        if profile["passive"] and REGEX["passive"].search(text):
            violations.append({
                "type": Constraint.PASSIVE.value,
                "snippet": self._extract(REGEX["passive"], text)
            })
        if profile["causality"] and self._needs_causality(text):
            if not (
                REGEX["causal"].search(text)
                or REGEX["metric"].search(text)
            ):
                violations.append({
                    "type": Constraint.CAUSALITY.value,
                    "snippet": "missing causal support"
                })
        # PUNCTUATION ENFORCEMENT
        if profile["punctuation"] and REGEX["emdash"].search(text):
            violations.append({
                "type": Constraint.PUNCTUATION.value,
                "snippet": "emdash detected"
            })
        # VAGUE-VERB ENFORCEMENT
        if profile["prohibited_verbs"] and REGEX["prohibited_verbs"].search(text):
            violations.append({
                "type": Constraint.PROHIBITED_VERBS.value,
                "snippet": self._extract(REGEX["prohibited_verbs"], text)
            })
        return violations
    def _needs_causality(self, text: str) -> bool:
        triggers = ["increase", "decrease", "improve", "impact", "result"]
        return any(t in text.lower() for t in triggers)
    def _extract(self, pattern, text):
        m = pattern.search(text)
        return m.group(0) if m else "" # ============================================================ # TRANSFORMER ENGINE 
# ============================================================ 
class CitadelTransformer:
    HEDGE_REPLACEMENTS = {
        "might": "",
        "may": "",
        "could": "",
        "seems": "",
        "probably": "",
        "perhaps": "",
        "likely": "",
        "i think": ""
    }
    IDENTITY_REPLACEMENTS = {
        "i": "",
        "we": "",
        "my": "",
        "our": ""
    }
    def rewrite(self, text: str, violations: List[Dict[str, str]]) -> str:
        updated = text
        for v in violations:
            if v["type"] == Constraint.HEDGING.value:
                updated = self._remove_hedging(updated)
            elif v["type"] == Constraint.IDENTITY.value:
                updated = self._remove_identity(updated)
            elif v["type"] == Constraint.PASSIVE.value:
                updated = self._fix_passive(updated)
            elif v["type"] == Constraint.CAUSALITY.value:
                updated += " due to measurable operational impact."
            elif v["type"] == Constraint.PUNCTUATION.value:
                updated = self._normalize_punctuation(updated)
            elif v["type"] == Constraint.PROHIBITED_VERBS.value:
                updated = self._normalize_prohibited_verbs(updated)
        return re.sub(r"\s{2,}", " ", updated).strip()
    def _remove_hedging(self, text: str) -> str:
        for k, v in self.HEDGE_REPLACEMENTS.items():
            text = re.sub(rf"\b{k}\b", v, text, flags=re.I)
        return text
    def _remove_identity(self, text: str) -> str:
        for k, v in self.IDENTITY_REPLACEMENTS.items():
            text = re.sub(rf"\b{k}\b", v, text, flags=re.I)
        return text
    def _fix_passive(self, text: str) -> str:
        mapping = {
            "was improved": "improved",
            "is generated": "generates",
            "was completed": "completed"
        }
        for a, b in mapping.items():
            text = re.sub(a, b, text, flags=re.I)
        return text
    def _normalize_punctuation(self, text: str) -> str:
        # EN DASH ONLY POLICY
        return text.replace("—", "–")
    def _normalize_prohibited_verbs(self, text: str) -> str:
        # salvaged from STRIDE's InputNormalizer: collapse vague corporate
        # verbs to a single neutral word rather than deleting them outright
        return REGEX["prohibited_verbs"].sub("use", text) # ============================================================ # SCORER ENGINE 
# ============================================================ 
class CitadelScorer:
    PENALTY = {
        Constraint.IDENTITY.value: 10,
        Constraint.HEDGING.value: 5,
        Constraint.PASSIVE.value: 5,
        Constraint.CAUSALITY.value: 10,
        Constraint.PUNCTUATION.value: 3,
        Constraint.PROHIBITED_VERBS.value: 5
    }
    def score(self, violations: List[Dict[str, str]]) -> int:
        s = 100
        for v in violations:
            s -= self.PENALTY.get(v["type"], 0)
        return max(0, s) # ============================================================ # MAIN ENGINE 
# ============================================================ 
class Citadel:
    def __init__(self):
        self.detector = CitadelDetector()
        self.transformer = CitadelTransformer()
        self.scorer = CitadelScorer()
    def enforce(self, text: str, profile: str = "default") -> Dict[str, Any]:
        start = time.time()
        config = PROFILES.get(profile, PROFILES["default"])
        violations = self.detector.detect(text, config)
        score = self.scorer.score(violations)
        final = self.transformer.rewrite(text, violations)
        return {
            "original": text,
            "final": final,
            "changed": text != final,
            "score": score,
            "violations": violations,
            "profile_used": profile,
            "latency_ms": round((time.time() - start) * 1000, 2)
        } # ============================================================ # EXAMPLE 
# ============================================================ 
if __name__ == "__main__":
    engine = Citadel()
    sample = "I think this might improve performance — because workflow was improved."
    print(engine.enforce(sample, profile="ops"))
    verb_sample = "This will enable us to optimize and enhance throughput."
    print(engine.enforce(verb_sample, profile="ops"))
