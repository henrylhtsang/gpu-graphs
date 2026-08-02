from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.validation import SpecError, validate_spec  # noqa: E402


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec(
            ROOT / "specs" / "kernels" / "flash-attention-4" / "forward-sm100.json"
        )

    def test_reference_spec_is_valid(self) -> None:
        validate_spec(self.spec)

    def test_unknown_role_is_rejected(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["operations"][0]["role"] = "missing"
        with self.assertRaisesRegex(SpecError, "unknown role"):
            validate_spec(broken)

    def test_exactly_one_view_is_primary(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["views"][0]["primary"] = False
        with self.assertRaisesRegex(SpecError, "exactly one view"):
            validate_spec(broken)

    def test_view_output_cannot_escape_topic(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["views"][0]["output"] = "graphs/other-topic/overview.svg"
        with self.assertRaisesRegex(SpecError, "must stay inside"):
            validate_spec(broken)

    def test_overlapping_alias_lifetimes_are_rejected(self) -> None:
        broken = copy.deepcopy(self.spec)
        resource = next(item for item in broken["resources"] if item["id"] == "svj1")
        resource["lifetime"]["from"] = {"operation": "load-k-next", "edge": "start"}
        with self.assertRaisesRegex(SpecError, "overlap"):
            validate_spec(broken)

    def test_loop_resident_q_cannot_end_after_first_qk(self) -> None:
        broken = copy.deepcopy(self.spec)
        resource = next(item for item in broken["resources"] if item["id"] == "sq0")
        resource["lifetime"]["until"] = {"operation": "mma-qk0", "edge": "end"}
        with self.assertRaisesRegex(SpecError, "loop-resident resource"):
            validate_spec(broken)

    def test_unknown_resource_access_is_rejected(self) -> None:
        broken = copy.deepcopy(self.spec)
        operation = next(item for item in broken["operations"] if item["id"] == "mma-qk0")
        operation["reads"].append("missing-resource")
        with self.assertRaisesRegex(SpecError, "unknown resource"):
            validate_spec(broken)

    def test_resource_access_must_fit_lifetime(self) -> None:
        broken = copy.deepcopy(self.spec)
        resource = next(item for item in broken["resources"] if item["id"] == "ts0")
        resource["lifetime"]["until"] = {"operation": "mma-qk0", "edge": "end"}
        with self.assertRaisesRegex(SpecError, "outside its lifetime"):
            validate_spec(broken)

    def test_multiple_resources_require_documented_reuse(self) -> None:
        broken = copy.deepcopy(self.spec)
        allocation = next(item for item in broken["allocations"] if item["id"] == "smem-kv-slot0")
        del allocation["reuse"]
        with self.assertRaisesRegex(SpecError, "explicit reuse policy"):
            validate_spec(broken)

    def test_storage_relation_must_match_physical_allocations(self) -> None:
        broken = copy.deepcopy(self.spec)
        relation = broken["storage_relations"][0]
        relation["kind"] = "alias"
        with self.assertRaisesRegex(SpecError, "alias assertion"):
            validate_spec(broken)

    def test_next_iteration_carry_reaches_loop_boundary(self) -> None:
        broken = copy.deepcopy(self.spec)
        resource = next(item for item in broken["resources"] if item["id"] == "skj1")
        resource["lifetime"]["until"] = {"operation": "load-k-next", "edge": "end"}
        with self.assertRaisesRegex(SpecError, "next-iteration carry"):
            validate_spec(broken)

    def test_storage_claims_require_registered_evidence(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["storage_relations"][0]["evidence"][0]["source"] = "missing-source"
        with self.assertRaisesRegex(SpecError, "unknown evidence source"):
            validate_spec(broken)

    def test_storage_relation_condition_must_match_configuration(self) -> None:
        broken = copy.deepcopy(self.spec)
        configuration = next(item for item in broken["configuration"] if item["id"] == "head-dim")
        configuration["value"] = 192
        with self.assertRaisesRegex(SpecError, "does not apply"):
            validate_spec(broken)

    def test_same_role_handoff_is_rejected(self) -> None:
        broken = copy.deepcopy(self.spec)
        broken["handoffs"][0]["to"] = "load-v"
        with self.assertRaisesRegex(SpecError, "cross role"):
            validate_spec(broken)

    def test_representative_loop_requires_indexing_contract(self) -> None:
        broken = copy.deepcopy(self.spec)
        del broken["loops"][0]["indexing"]
        with self.assertRaisesRegex(SpecError, "requires an indexing contract"):
            validate_spec(broken)

    def test_seed_operation_cannot_leak_into_mainloop(self) -> None:
        broken = copy.deepcopy(self.spec)
        operation = next(item for item in broken["operations"] if item["id"] == "load-k")
        operation["end"] = 2.5
        with self.assertRaisesRegex(SpecError, "seed operation must finish"):
            validate_spec(broken)

    def test_next_operation_must_stay_in_mainloop(self) -> None:
        broken = copy.deepcopy(self.spec)
        operation = next(item for item in broken["operations"] if item["id"] == "load-k-next")
        del operation["scope"]
        operation["frequency"] = "once"
        with self.assertRaisesRegex(SpecError, "next operation must stay inside"):
            validate_spec(broken)

    def test_current_operation_cannot_use_concrete_seed_label(self) -> None:
        broken = copy.deepcopy(self.spec)
        operation = next(item for item in broken["operations"] if item["id"] == "mma-qk0")
        operation["detail"] = "sQ[0] × sK₀ → TMEM S₀"
        with self.assertRaisesRegex(SpecError, "must contain Kⱼ"):
            validate_spec(broken)


if __name__ == "__main__":
    unittest.main()
