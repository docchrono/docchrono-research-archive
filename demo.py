"""Build, inspect, save, and reload a synthetic historical archive."""

from __future__ import annotations

from pathlib import Path

from generate_data import DATA_DIR, generate

from docchrono import Case
from docchrono.domain import Event

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
CASE_PATH = OUTPUT_DIR / "lantern.case.json"


def build_archive(data_dir: Path = DATA_DIR) -> Case:
    if not data_dir.exists():
        generate(data_dir)
    return Case.build(data_dir, strict=True)


def event_date(event: Event) -> str:
    temporal_values = event.temporal
    starts = sorted(
        temporal.start
        for temporal in temporal_values
        if temporal.resolved and temporal.start is not None
    )
    return starts[0] if starts else "Undated"


def event_sources(case: Case, event: Event) -> tuple[str, ...]:
    documents = {document.id: document for document in case.documents}
    sources = {source.id: source for source in case.source_references}
    names: set[str] = set()
    for span in case.evidence(event):
        document = documents[span.document_id]
        names.update(
            sources[source_id].filename
            for source_id in document.source_reference_ids
            if source_id in sources
        )
    return tuple(sorted(names))


def evidence_round_trips(case: Case) -> bool:
    documents = {document.id: document for document in case.documents}
    return all(
        documents[span.document_id].raw_text[span.raw_start : span.raw_end] == span.quote
        for span in case.evidence_spans
    )


def render_archive(case: Case, *, save_load_identical: bool, saved_path: str) -> str:
    """Render a stable summary suitable for humans and a golden regression test."""

    lines = [
        "DocChrono research archive",
        f"Documents: {len(case.documents)}",
        f"Entities: {len(case.entities)}",
        f"Events: {len(case.events)}",
        "Timeline:",
    ]
    for event in case.timeline:
        sources = ", ".join(event_sources(case, event))
        lines.append(f"  {event_date(event)} | {event.title} | {sources}")
    lines.extend(
        (
            f"Evidence round-trips: {evidence_round_trips(case)}",
            f"Save/load identical: {save_load_identical}",
            f"Saved case: {saved_path}",
        )
    )
    return "\n".join(lines) + "\n"


def run_demo(data_dir: Path = DATA_DIR, case_path: Path = CASE_PATH) -> Case:
    case = build_archive(data_dir)
    case_path.parent.mkdir(parents=True, exist_ok=True)
    case.save(case_path)
    reloaded = Case.load(case_path)
    saved_path = (
        case_path.relative_to(ROOT).as_posix() if case_path.is_relative_to(ROOT) else str(case_path)
    )
    print(
        render_archive(
            case,
            save_load_identical=reloaded.data == case.data,
            saved_path=saved_path,
        ),
        end="",
    )
    return case


if __name__ == "__main__":
    run_demo()
