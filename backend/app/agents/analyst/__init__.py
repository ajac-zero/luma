from __future__ import annotations

from typing import Any, Iterable, List

from app.agents.form_auditor.models import ExtractedIrsForm990PfDataSchema

from .agent import agent
from .metrics import SnapshotBundle, build_key_metrics, build_snapshots
from .models import AnalystReport, AnalystState

__all__ = ["build_performance_report"]


def _resolve_year(
    entry: dict[str, Any], extraction: ExtractedIrsForm990PfDataSchema
) -> int:
    candidates: Iterable[Any] = (
        entry.get("calendar_year"),
        entry.get("year"),
        entry.get("tax_year"),
        entry.get("return_year"),
        entry.get("metadata", {}).get("return_year")
        if isinstance(entry.get("metadata"), dict)
        else None,
        entry.get("metadata", {}).get("tax_year")
        if isinstance(entry.get("metadata"), dict)
        else None,
        extraction.core_organization_metadata.calendar_year,
    )
    for candidate in candidates:
        if candidate in (None, ""):
            continue
        try:
            return int(candidate)
        except (TypeError, ValueError):
            continue
    raise ValueError("Unable to determine filing year for one of the payload entries.")


async def build_performance_report(payloads: List[dict[str, Any]]) -> AnalystReport:
    if not payloads:
        raise ValueError("At least one payload is required for performance analysis.")

    bundles: List[SnapshotBundle] = []

    organisation_name = ""
    organisation_ein = ""

    for entry in payloads:
        if not isinstance(entry, dict):
            raise TypeError("Each payload entry must be a dict.")

        extraction_payload = entry.get("extraction") if "extraction" in entry else entry
        extraction = ExtractedIrsForm990PfDataSchema.model_validate(extraction_payload)
        year = _resolve_year(entry, extraction)

        if not organisation_ein:
            organisation_ein = extraction.core_organization_metadata.ein
            organisation_name = extraction.core_organization_metadata.legal_name
        else:
            if extraction.core_organization_metadata.ein != organisation_ein:
                raise ValueError(
                    "All payload entries must belong to the same organization."
                )

        bundles.append(SnapshotBundle(year=year, extraction=extraction))

    bundles.sort(key=lambda bundle: bundle.year)
    snapshots = build_snapshots(bundles)
    metrics = build_key_metrics(snapshots)

    notes = []
    if metrics:
        revenue_metric = metrics[0]
        expense_metric = metrics[1] if len(metrics) > 1 else None
        if revenue_metric.cagr is not None:
            notes.append(f"Revenue CAGR: {revenue_metric.cagr:.2%}")
        if expense_metric and expense_metric.cagr is not None:
            notes.append(f"Expense CAGR: {expense_metric.cagr:.2%}")
        surplus_metric = next(
            (m for m in metrics if m.name == "Operating Surplus"), None
        )
        if surplus_metric:
            last_value = surplus_metric.points[-1].value if surplus_metric.points else 0
            notes.append(f"Latest operating surplus: {last_value:,.0f}")

    state = AnalystState(
        organisation_name=organisation_name,
        organisation_ein=organisation_ein,
        series=snapshots,
        key_metrics=metrics,
        notes=notes,
    )

    prompt = (
        "Analyze the provided multi-year financial context. Quantify notable trends, "
        "call out risks or strengths, and supply actionable recommendations. "
        "Capture both positive momentum and areas requiring attention."
    )
    result = await agent.run(prompt, deps=state)
    report = result.output

    years = [snapshot.year for snapshot in snapshots]

    return report.model_copy(
        update={
            "organisation_name": organisation_name,
            "organisation_ein": organisation_ein,
            "years_analyzed": years,
            "key_metrics": metrics,
        }
    )
