import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.provenance import ProvenanceStore


class TestProvenance(unittest.TestCase):
    def setUp(self):
        self.store = ProvenanceStore()

    def test_record_hash_determinism(self):
        rec1 = self.store.record(
            trace_id="t1",
            operation="COMBINE",
            relation="ADD",
            inputs=[1, 2],
            result=3,
        )
        self.assertTrue(len(rec1.hash) == 64)
        # Fetching back
        rec_fetched = self.store.get("t1")
        self.assertEqual(rec_fetched.hash, rec1.hash)

    def test_causal_ancestry_tracking(self):
        self.store.record("t0", "SOURCE", "INIT", [10], 10)
        self.store.record("t1", "TRANSFORM", "DOUBLE", [10], 20, causal_parents=["t0"])
        self.store.record("t2", "CANCEL", "ZERO", [20, -20], 0, causal_parents=["t1"])

        ancestry = self.store.trace_ancestry("t2")
        self.assertEqual(len(ancestry), 3)
        ids = [r.trace_id for r in ancestry]
        self.assertEqual(ids, ["t0", "t1", "t2"])
        # Null cancellation in t2 still points to its causal ancestry
        self.assertEqual(ancestry[-1].result, 0)
        self.assertEqual(ancestry[-1].inputs, [20, -20])


if __name__ == "__main__":
    unittest.main()
