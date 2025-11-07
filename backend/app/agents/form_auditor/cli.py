from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from . import build_audit_report

__all__ = ["build_audit_report", "main"]


def _load_payload(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def _print_report(report: dict) -> None:
    print(json.dumps(report, indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate a Form 990 extraction payload using the Form Auditor agent."
    )
    parser.add_argument(
        "payload",
        nargs="?",
        default="example_data.json",
        help="Path to a JSON file containing the extraction payload.",
    )
    args = parser.parse_args(argv)

    payload_path = Path(args.payload).expanduser()
    payload = _load_payload(payload_path)

    report = asyncio.run(build_audit_report(payload))
    _print_report(report.model_dump())
