import json
import sys
from pathlib import Path

from app.domain.data_quality import DatasetValidator

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))
from seed_demo_data import SCENARIOS, generate  # noqa: E402


def test_demo_generation_is_deterministic_and_documents_truth(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate(first)
    generate(second)

    assert set(path.name for path in first.iterdir()) == set(SCENARIOS)
    for scenario in SCENARIOS:
        assert (first / scenario / "weekly_sales.csv").read_bytes() == (
            second / scenario / "weekly_sales.csv"
        ).read_bytes()
        truth = json.loads((first / scenario / "truth.json").read_text(encoding="utf-8"))
        assert truth["synthetic"] is True
        assert truth["seed"] == SCENARIOS[scenario].seed


def test_demo_scenarios_pass_schema_and_have_expected_viability(tmp_path: Path) -> None:
    generate(tmp_path)
    validator = DatasetValidator(minimum_history_weeks=12)

    for scenario in SCENARIOS:
        report = validator.validate(
            tmp_path / scenario / "weekly_sales.csv",
            currency="USD",
            gross_margin_representation="amount",
            stock_unit="units",
        )
        assert not report.has_critical_errors, scenario
        if scenario == "insufficient_evidence":
            assert not report.series_eligibility[0].eligible
        elif scenario != "cannibalization":
            assert all(item.eligible for item in report.series_eligibility), scenario
