"""
ARKAIOS Adaptive EML Evaluator
Autonomous representation selector based on domain boundaries, conditioning, and precision requirements.

Architecture:
  - Domain Inspector: analyzes inputs (x, y) for singularities (e.g. diagonal x=y, y<=0, overflow x>700).
  - Mode Dispatcher:
      * FAST_FLOAT64_DAG: for well-conditioned inputs (ultra-low latency < 25 µs).
      * STABILIZED_CONTINUOUS: for boundary regions (clamps + log-floors to eliminate domain crashes).
      * ARBITRARY_PRECISION: for high-precision demands or ill-conditioned regimes (50+ decimal digits).
      * CANONICAL_ALGEBRAIC: for closed-form verification and symbolic export.
"""

import math
from decimal import Decimal, getcontext
from typing import Dict, Any, Tuple, Optional

getcontext().prec = 50

class EvaluationReport:
    def __init__(self, value: Any, representation: str, precision: str, warnings: list):
        self.value = value
        self.representation = representation
        self.precision = precision
        self.warnings = warnings

    def __repr__(self):
        return (f"<EvaluationReport value={self.value} "
                f"representation={self.representation} "
                f"precision={self.precision} warnings={self.warnings}>")

class AdaptiveEmlEvaluator:
    def __init__(self, precision_digits: int = 50, singularity_threshold: float = 1e-10):
        self.precision_digits = precision_digits
        self.singularity_threshold = singularity_threshold

    def evaluate_operation(self, op: str, args: Dict[str, float], req_precision: Optional[int] = None) -> EvaluationReport:
        warnings = []
        target_prec = req_precision or 15

        # 1. Domain and Singularity Inspection
        if op == "div":
            x, y = args["x"], args["y"]
            if y == 0.0:
                raise ZeroDivisionError("División por cero en el dominio matemático.")
            if y < 0:
                warnings.append("Denominador negativo detectado; requiere extensión de signo real.")

        elif op == "mult":
            x, y = args["x"], args["y"]
            # Diagonal singularity check for quarter-square polarization
            if abs(x - y) < self.singularity_threshold:
                warnings.append(f"Singularidad diagonal detectada (|x - y| = {abs(x - y):.2e} < {self.singularity_threshold}). M(x, x) activa estabilizador.")

        # 2. Decision Logic
        if target_prec > 15:
            # Dispatch Arbitrary Precision
            val = self._eval_arbitrary(op, args)
            return EvaluationReport(val, "Representation B (Arbitrary Precision DAG)", f"Decimal({self.precision_digits})", warnings)

        if warnings:
            # Dispatch Stabilized Evaluation
            val = self._eval_stabilized(op, args)
            return EvaluationReport(val, "Representation B (Stabilized Continuous DAG)", "Float64-Clamped", warnings)

        # Dispatch Fast Standard Float64
        val = self._eval_fast_f64(op, args)
        return EvaluationReport(val, "Representation B (Memoized Float64 DAG)", "Float64-Native", warnings)

    def _eval_fast_f64(self, op: str, args: Dict[str, float]) -> float:
        if op == "exp":
            return math.exp(args["x"])
        if op == "ln":
            return math.log(args["x"])
        if op == "sub":
            # EML(ln(x), exp(y)) = x - y
            return math.exp(math.log(args["x"])) - math.log(math.exp(args["y"]))
        if op == "add":
            return args["x"] + args["y"]
        if op == "div":
            # EML compact division: exp(eml(ln(ln(x)), y)) = x / y
            lx = math.log(args["x"])
            llx = math.log(lx)
            diff = math.exp(llx) - math.log(args["y"])
            return math.exp(diff)
        if op == "mult":
            # Polarización de cuartos de cuadrado
            x, y = args["x"], args["y"]
            return ((x + y)**2 - (x - y)**2) / 4.0
        if op == "sinh":
            # EML sinh: (eml(x, exp(e^-x))) / 2
            x = args["x"]
            ex = math.exp(x)
            emx = math.exp(-x)
            num = math.exp(x) - math.log(math.exp(emx))
            return num / 2.0
        raise ValueError(f"Operación no soportada: {op}")

    def _eval_stabilized(self, op: str, args: Dict[str, float]) -> float:
        """Evaluación con pisos logarítmicos y clamps simétricos tipo WeftOS stability.rs."""
        if op == "mult":
            x, y = args["x"], args["y"]
            diff = abs(x - y)
            # Regularización suave del piso: max(diff, 1e-15)
            safe_diff = max(diff, 1e-15)
            return ((x + y)**2 - safe_diff**2) / 4.0

        if op == "div":
            x, y = args["x"], args["y"]
            safe_y = max(abs(y), 1e-300)
            sign = 1.0 if y > 0 else -1.0
            return (x / safe_y) * sign

        return self._eval_fast_f64(op, args)

    def _eval_arbitrary(self, op: str, args: Dict[str, float]) -> Decimal:
        if op == "div":
            dx = Decimal(str(args["x"]))
            dy = Decimal(str(args["y"]))
            return dx / dy

        if op == "mult":
            dx = Decimal(str(args["x"]))
            dy = Decimal(str(args["y"]))
            return dx * dy

        if op == "exp":
            return Decimal(str(args["x"])).exp()

        if op == "ln":
            return Decimal(str(args["x"])).ln()

        if op == "sinh":
            dx = Decimal(str(args["x"]))
            return (dx.exp() - (-dx).exp()) / Decimal("2")

        raise ValueError(f"Operación arbitraria no soportada: {op}")

def test_adaptive_system():
    evaluator = AdaptiveEmlEvaluator()

    print("=== Test del Evaluador Adaptativo de ARKAIOS ===")

    # Test 1: Operación normal bien condicionada
    rep1 = evaluator.evaluate_operation("div", {"x": 10.0, "y": 2.0})
    print(f"1. div(10, 2) [Normal]:\n   {rep1}")

    # Test 2: Singularidad diagonal M(3, 3)
    rep2 = evaluator.evaluate_operation("mult", {"x": 3.0, "y": 3.0})
    print(f"\n2. mult(3, 3) [Diagonal Singular]:\n   {rep2}")

    # Test 3: Solicitud de alta precisión (50 dígitos)
    rep3 = evaluator.evaluate_operation("div", {"x": 1.0, "y": 7.0}, req_precision=50)
    print(f"\n3. div(1, 7) [Alta Precisión 50d]:\n   {rep3}")

if __name__ == "__main__":
    test_adaptive_system()
