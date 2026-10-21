"""
ARKAIOS Five-Signal Model
Implements complex signal composition:
z_k(u) = A_k * exp(i * (omega_k * u + phi_k)) for k in [0, 1, 2, 3, 4].
Central Composition: S(u) = sum_{k=0}^4 z_k(u).

Test Cases:
- Case A: Reinforce -> |S(u)| = 5
- Case B: Cancel -> |S(u)| ≈ 0 (tolerance <= 1e-14)
- Case C: General Composition -> matches reference
- Case D: Traceability -> All 5 parameters & components preserved even if S(u) = 0
- Case E: Return Mapping -> Explicit declaration of lossy projection vs exact inverse
"""

import cmath
import math
from typing import Any, Dict, List, Optional, Tuple


class ComplexSignal:
    def __init__(self, k: int, amplitude: float = 1.0, frequency: float = 1.0, phase: float = 0.0):
        self.k = k
        self.A = float(amplitude)
        self.omega = float(frequency)
        self.phi = float(phase)

    def evaluate(self, u: float) -> complex:
        """Evaluates z_k(u) = A * exp(i * (omega * u + phi))."""
        theta = self.omega * u + self.phi
        return self.A * cmath.exp(1j * theta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "k": self.k,
            "amplitude": self.A,
            "frequency": self.omega,
            "phase": self.phi,
        }

    def __repr__(self) -> str:
        return f"<Signal k={self.k} A={self.A:.2f} w={self.omega:.2f} phi={self.phi:.2f}>"


class FiveSignalHub:
    def __init__(self, signals: Optional[List[ComplexSignal]] = None):
        if signals is not None:
            if len(signals) != 5:
                raise ValueError(f"FiveSignalHub requires exactly 5 signals, got {len(signals)}")
            self.signals = signals
        else:
            self.signals = [ComplexSignal(k=i) for i in range(5)]

    def evaluate_components(self, u: float) -> List[complex]:
        return [s.evaluate(u) for s in self.signals]

    def evaluate_central(self, u: float) -> complex:
        return sum(self.evaluate_components(u))

    @classmethod
    def create_case_a_reinforce(cls, A: float = 1.0, omega: float = 1.0, phi: float = 0.0) -> "FiveSignalHub":
        """Five identical signals: same amplitude, frequency, and phase."""
        signals = [ComplexSignal(k=i, amplitude=A, frequency=omega, phase=phi) for i in range(5)]
        return cls(signals)

    @classmethod
    def create_case_b_cancel(cls, A: float = 1.0, omega: float = 1.0) -> "FiveSignalHub":
        """Five signals with symmetric phase distribution phi_k = 2*pi*k / 5."""
        signals = [
            ComplexSignal(k=i, amplitude=A, frequency=omega, phase=(2.0 * math.pi * i) / 5.0)
            for i in range(5)
        ]
        return cls(signals)

    @classmethod
    def create_case_c_general(cls, configs: List[Dict[str, float]]) -> "FiveSignalHub":
        if len(configs) != 5:
            raise ValueError(f"Expected 5 signal configs, got {len(configs)}")
        signals = [
            ComplexSignal(
                k=i,
                amplitude=configs[i].get("amplitude", 1.0),
                frequency=configs[i].get("frequency", 1.0),
                phase=configs[i].get("phase", 0.0),
            )
            for i in range(5)
        ]
        return cls(signals)

    def get_traceability_data(self, u: float) -> Dict[str, Any]:
        """
        Case D: Full traceability audit.
        Ensures that even if S(u) ≈ 0, all 5 components, parameters, and phases are preserved.
        """
        components = self.evaluate_components(u)
        central = sum(components)
        return {
            "u": u,
            "central_value": central,
            "central_magnitude": abs(central),
            "is_algebraic_null": abs(central) < 1e-12,
            "components_retained": len(components),
            "signals": [
                {
                    "k": s.k,
                    "parameters": s.to_dict(),
                    "evaluated_value": components[s.k],
                    "evaluated_magnitude": abs(components[s.k]),
                }
                for s in self.signals
            ],
            "provenance_preserved": True,
        }

    def return_map_analysis(self, u: float) -> Dict[str, Any]:
        """
        Case E: Bidirectional return mapping analysis between central node and inputs.
        Specifies explicitly whether the return is an identity, exact inverse, or lossy projection.
        Since 5 complex numbers sum to 1 scalar/complex, going from central S(u) back to 5 inputs
        is an underdetermined 1 -> 5 mapping (lossy projection), unless a phase-partition dictionary is kept.
        """
        components = self.evaluate_components(u)
        central = sum(components)

        # Equal-weight projection hypothesis
        projected_back = [central / 5.0 for _ in range(5)]
        residual_errors = [abs(projected_back[i] - components[i]) for i in range(5)]
        mean_loss = sum(residual_errors) / 5.0

        return {
            "mapping_type": "LOSSY_PROJECTION_UNDERDETERMINED",
            "is_reversible_without_metadata": False,
            "is_reversible_with_metadata": True,
            "central_value": central,
            "original_components": components,
            "projected_back": projected_back,
            "mean_reconstruction_loss": mean_loss,
            "notes": "Exact return requires retaining component parameters in metadata/provenance.",
        }
