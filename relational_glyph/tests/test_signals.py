import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.signals import ComplexSignal, FiveSignalHub


class TestSignals(unittest.TestCase):
    def test_case_a_reinforce(self):
        """Case A: Five unit signals, same frequency and phase -> |S(u)| = 5."""
        hub = FiveSignalHub.create_case_a_reinforce(A=1.0, omega=2.0, phi=0.5)
        for u in [0.0, 1.0, 3.1415, 10.0]:
            s_val = hub.evaluate_central(u)
            mag = abs(s_val)
            self.assertAlmostEqual(mag, 5.0, places=12, msg=f"Failed reinforcement at u={u}")

    def test_case_b_cancel(self):
        """Case B: Five unit signals, same frequency, phi_k = 2*pi*k / 5 -> |S(u)| ≈ 0."""
        hub = FiveSignalHub.create_case_b_cancel(A=1.0, omega=3.0)
        for u in [0.0, 0.5, 2.0, 7.7]:
            s_val = hub.evaluate_central(u)
            mag = abs(s_val)
            self.assertLess(mag, 1e-14, msg=f"Failed cancellation at u={u}: |S(u)| = {mag}")

    def test_case_c_general(self):
        """Case C: Heterogeneous frequencies, amplitudes, and phases."""
        configs = [
            {"amplitude": 1.5, "frequency": 1.0, "phase": 0.0},
            {"amplitude": 2.0, "frequency": 2.5, "phase": 0.4},
            {"amplitude": 0.8, "frequency": 0.5, "phase": 1.2},
            {"amplitude": 1.2, "frequency": 3.0, "phase": 2.1},
            {"amplitude": 2.5, "frequency": 1.8, "phase": 0.7},
        ]
        hub = FiveSignalHub.create_case_c_general(configs)
        u = 2.5
        s_val = hub.evaluate_central(u)
        # Compute reference sum directly
        ref_sum = sum(
            cfg["amplitude"] * (math.cos(cfg["frequency"] * u + cfg["phase"]) + 1j * math.sin(cfg["frequency"] * u + cfg["phase"]))
            for cfg in configs
        )
        self.assertAlmostEqual(s_val.real, ref_sum.real, places=12)
        self.assertAlmostEqual(s_val.imag, ref_sum.imag, places=12)

    def test_case_d_traceability_under_cancellation(self):
        """Case D: Traceability is 100% preserved even when S(u) cancels to 0."""
        hub = FiveSignalHub.create_case_b_cancel(A=1.0, omega=1.0)
        trace_data = hub.get_traceability_data(u=1.234)

        self.assertTrue(trace_data["is_algebraic_null"])
        self.assertEqual(trace_data["components_retained"], 5)
        self.assertEqual(len(trace_data["signals"]), 5)
        # Verify that each of the 5 signals still has unit amplitude and distinct phases
        for s in trace_data["signals"]:
            self.assertAlmostEqual(s["parameters"]["amplitude"], 1.0)
            self.assertAlmostEqual(s["evaluated_magnitude"], 1.0)

    def test_case_e_return_map(self):
        """Case E: Return mapping analysis between central node and inputs."""
        hub = FiveSignalHub.create_case_b_cancel(A=1.0, omega=1.0)
        return_analysis = hub.return_map_analysis(u=0.5)

        self.assertEqual(return_analysis["mapping_type"], "LOSSY_PROJECTION_UNDERDETERMINED")
        self.assertFalse(return_analysis["is_reversible_without_metadata"])
        self.assertTrue(return_analysis["is_reversible_with_metadata"])
        self.assertEqual(len(return_analysis["original_components"]), 5)
        self.assertEqual(len(return_analysis["projected_back"]), 5)


if __name__ == "__main__":
    unittest.main()
