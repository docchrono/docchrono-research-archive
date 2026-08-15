from __future__ import annotations

from pathlib import Path

import pytest
from demo import (
    build_archive,
    event_date,
    event_sources,
    evidence_round_trips,
    render_archive,
    run_demo,
)
from generate_data import check, generate

from docchrono import Case


def test_generated_archive_builds_with_exact_provenance(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    generate(data_dir)
    assert check(data_dir)

    case = build_archive(data_dir)
    assert case.report.complete
    assert len(case.documents) == 4
    assert case.entities
    assert len(case.events) == 5
    assert tuple(case.timeline)
    assert [event_date(event) for event in case.timeline] == sorted(
        event_date(event) for event in case.timeline
    )
    assert evidence_round_trips(case)
    assert any(span.page == 1 and span.boxes for span in case.evidence_spans)
    timeline_sources = {source for event in case.timeline for source in event_sources(case, event)}
    assert timeline_sources == {
        "01_foundation_note.txt",
        "02_board_minutes.md",
        "03_dispatch.eml",
        "04_receipt_report.pdf",
    }


def test_demo_saves_a_lossless_case(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_dir = tmp_path / "data"
    generate(data_dir)
    case_path = tmp_path / "archive.case.json"

    case = run_demo(data_dir, case_path)
    loaded = Case.load(case_path)

    assert loaded.data == case.data
    output = capsys.readouterr().out
    assert "Evidence round-trips: True" in output
    assert "Save/load identical: True" in output


def test_rendered_demo_matches_committed_expected_output() -> None:
    case = build_archive()
    actual = render_archive(
        case,
        save_load_identical=True,
        saved_path="output/lantern.case.json",
    )
    expected = (Path(__file__).parents[1] / "expected_output.txt").read_text(encoding="utf-8")
    assert actual == expected
