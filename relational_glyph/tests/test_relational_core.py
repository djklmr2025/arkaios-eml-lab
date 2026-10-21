import unittest
import sys
import os

# Add eml-lab to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.core import RelationalCore
from relational_glyph.provenance import ProvenanceStore


class TestRelationalCore(unittest.TestCase):
    def setUp(self):
        self.store = ProvenanceStore()
        self.core = RelationalCore(provenance_store=self.store)

    def test_combine_positive(self):
        res = self.core.combine([10, 20, 30], operation="ADD")
        self.assertEqual(res.value, 60)
        self.assertEqual(res.relation, "COMBINATION")
        self.assertFalse(res.is_null)
        self.assertEqual(len(res.inputs), 3)

    def test_combine_null_cancellation_invariant(self):
        # Mandatory invariant: combine([5, -5]) -> 0
        res = self.core.combine([5, -5], operation="ADD")
        self.assertEqual(res.value, 0)
        self.assertEqual(res.relation, "CANCELLATION")
        self.assertTrue(res.is_null)
        # Verify inputs and provenance are NOT deleted or destroyed
        self.assertEqual(res.inputs, [5, -5])
        trace_data = self.core.trace(res.result_id)
        self.assertIsNotNone(trace_data)
        self.assertEqual(trace_data["record"]["inputs"], [5, -5])
        self.assertEqual(trace_data["record"]["relation"], "CANCELLATION")

    def test_reinforce(self):
        res = self.core.reinforce([2, 3], factor=2.0)
        self.assertEqual(res.value, 10.0)
        self.assertEqual(res.operation, "REINFORCE")
        self.assertEqual(res.relation, "REINFORCEMENT")

    def test_cancel(self):
        res = self.core.cancel([100, -100])
        self.assertEqual(res.value, 0)
        self.assertTrue(res.is_null)
        self.assertEqual(res.inputs, [100, -100])

    def test_transform_with_precondition(self):
        # Valid transformation
        res = self.core.transform(
            expression=4.0,
            rule_name="SQRT_RULE",
            transform_fn=lambda x: x ** 0.5,
            precondition=lambda x: x >= 0,
        )
        self.assertEqual(res.value, 2.0)

        # Invalid transformation violating precondition
        with self.assertRaises(ValueError):
            self.core.transform(
                expression=-4.0,
                rule_name="SQRT_RULE",
                transform_fn=lambda x: x ** 0.5,
                precondition=lambda x: x >= 0,
            )

    def test_five_inputs_convergence(self):
        inputs = [1.0, 2.0, 3.0, 4.0, 5.0]
        res = self.core.process_five_inputs(inputs)
        self.assertEqual(res.value, 15.0)
        self.assertEqual(res.inputs, inputs)
        self.assertEqual(res.operation, "FIVE_SIGNAL_CONVERGENCE")


if __name__ == "__main__":
    unittest.main()
