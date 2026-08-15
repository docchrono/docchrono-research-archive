"""Generate the deterministic, entirely fictional archive used by this demo."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def _minimal_pdf(lines: tuple[str, ...]) -> bytes:
    """Return a small standards-compliant, machine-readable one-page PDF."""

    def escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    commands = ["BT", "/F1 12 Tf", "72 720 Td", "16 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        commands.append(f"({escape(line)}) Tj")
    commands.append("ET")
    stream = ("\n".join(commands) + "\n").encode("latin-1")

    objects = (
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"endstream",
    )

    payload = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload.extend(f"{number} 0 obj\n".encode("ascii"))
        payload.extend(body)
        payload.extend(b"\nendobj\n")
    xref_offset = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    payload.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(payload)


def rendered_files() -> dict[str, bytes]:
    return {
        "01_foundation_note.txt": (
            b"On April 4, 1968, Eleanor Hart filed Project Lantern for Meridian Archive.\n"
            b"Eleanor Hart works for Meridian Archive.\n"
        ),
        "02_board_minutes.md": (
            b"# Meridian Archive board minutes\n\n"
            b"On April 12, 1968, Meridian Archive approved Project Lantern.\n"
        ),
        "03_dispatch.eml": (
            b"From: Elias Stone <elias.stone@example.test>\n"
            b"To: Eleanor Hart <eleanor.hart@example.test>\n"
            b"Date: Thu, 18 Apr 1968 09:15:00 -0600\n"
            b"Subject: Project Lantern dispatch\n"
            b"Message-ID: <lantern-dispatch@example.test>\n"
            b"MIME-Version: 1.0\n"
            b'Content-Type: text/plain; charset="utf-8"\n\n'
            b"On April 18, 1968, Elias Stone transferred Asset #L-17 to Eleanor Hart.\n"
        ),
        "04_receipt_report.pdf": _minimal_pdf(
            (
                "Meridian Archive field report",
                "On April 21, 1968, Meridian Archive filed Asset #L-17.",
            )
        ),
    }


def generate(destination: Path = DATA_DIR) -> tuple[Path, ...]:
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, content in rendered_files().items():
        path = destination / filename
        path.write_bytes(content)
        written.append(path)
    return tuple(written)


def check(destination: Path = DATA_DIR) -> bool:
    expected = rendered_files()
    actual_names = {path.name for path in destination.iterdir() if path.is_file()}
    return actual_names == set(expected) and all(
        (destination / filename).read_bytes() == content for filename, content in expected.items()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify committed data")
    args = parser.parse_args()
    if args.check:
        if not DATA_DIR.exists() or not check():
            print("Synthetic archive is missing or stale. Run: python generate_data.py")
            return 1
        print("Synthetic archive is deterministic and current.")
        return 0
    for path in generate():
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
