from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from app.agents.form_auditor.models import ExtractedIrsForm990PfDataSchema

from .models import TrendDirection, TrendMetric, TrendMetricPoint, YearlySnapshot


@dataclass
class SnapshotBundle:
    year: int
    extraction: ExtractedIrsForm990PfDataSchema


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator in (0, None):
        return None
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None


def _growth(current: float, previous: float | None) -> float | None:
    if previous in (None, 0):
        return None
    try:
        return (current - previous) / previous
    except ZeroDivisionError:
        return None


def _direction_from_points(values: Sequence[float | None]) -> TrendDirection:
    clean = [value for value in values if value is not None]
    if len(clean) < 2:
        return TrendDirection.STABLE

    start, end = clean[0], clean[-1]
    if start is None or end is None:
        return TrendDirection.STABLE

    delta = end - start
    tolerance = abs(start) * 0.02 if start else 0.01
    if abs(delta) <= tolerance:
        return TrendDirection.STABLE

    if len(clean) > 2:
        swings = sum(
            1
            for idx in range(1, len(clean) - 1)
            if (clean[idx] - clean[idx - 1]) * (clean[idx + 1] - clean[idx]) < 0
        )
        if swings >= len(clean) // 2:
            return TrendDirection.VOLATILE

    return TrendDirection.IMPROVING if delta > 0 else TrendDirection.DECLINING


def _cagr(start: float | None, end: float | None, periods: int) -> float | None:
    if start is None or end is None or start <= 0 or end <= 0 or periods <= 0:
        return None
    return (end / start) ** (1 / periods) - 1


def build_snapshots(bundles: Sequence[SnapshotBundle]) -> List[YearlySnapshot]:
    snapshots: List[YearlySnapshot] = []
    previous_revenue = None
    previous_expenses = None

    for bundle in bundles:
        rev = bundle.extraction.revenue_breakdown.total_revenue
        exp = bundle.extraction.expenses_breakdown.total_expenses
        program = bundle.extraction.expenses_breakdown.program_services_expenses
        admin = bundle.extraction.expenses_breakdown.management_general_expenses
        fundraising = bundle.extraction.expenses_breakdown.fundraising_expenses

        snapshots.append(
            YearlySnapshot(
                year=bundle.year,
                total_revenue=rev,
                total_expenses=exp,
                revenue_growth=_growth(rev, previous_revenue),
                expense_growth=_growth(exp, previous_expenses),
                surplus=rev - exp,
                program_ratio=_safe_ratio(program, exp),
                admin_ratio=_safe_ratio(admin, exp),
                fundraising_ratio=_safe_ratio(fundraising, exp),
                net_margin=_safe_ratio(rev - exp, rev),
            )
        )
        previous_revenue = rev
        previous_expenses = exp

    return snapshots


def _metric_from_series(
    name: str,
    unit: str,
    description: str,
    values: Iterable[Tuple[int, float | None]],
) -> TrendMetric:
    points = [
        TrendMetricPoint(year=year, value=value or 0.0, growth=None)
        for year, value in values
    ]

    for idx in range(1, len(points)):
        prev = points[idx - 1].value
        curr = points[idx].value
        points[idx].growth = _growth(curr, prev)

    data_values = [point.value for point in points]
    direction = _direction_from_points(data_values)
    cagr = None
    if len(points) >= 2:
        cagr = _cagr(points[0].value, points[-1].value, len(points) - 1)

    return TrendMetric(
        name=name,
        unit=unit,
        description=description,
        points=points,
        cagr=cagr,
        direction=direction,
    )


def build_key_metrics(snapshots: Sequence[YearlySnapshot]) -> List[TrendMetric]:
    if not snapshots:
        return []

    metrics = [
        _metric_from_series(
            "Total Revenue",
            "USD",
            "Reported total revenue in Part I.",
            [(snap.year, snap.total_revenue) for snap in snapshots],
        ),
        _metric_from_series(
            "Total Expenses",
            "USD",
            "Reported total expenses in Part I.",
            [(snap.year, snap.total_expenses) for snap in snapshots],
        ),
        _metric_from_series(
            "Operating Surplus",
            "USD",
            "Difference between total revenue and total expenses.",
            [(snap.year, snap.surplus) for snap in snapshots],
        ),
        _metric_from_series(
            "Program Service Ratio",
            "Ratio",
            "Program service expenses divided by total expenses.",
            [
                (
                    snap.year,
                    snap.program_ratio if snap.program_ratio is not None else 0.0,
                )
                for snap in snapshots
            ],
        ),
        _metric_from_series(
            "Administrative Ratio",
            "Ratio",
            "Management & general expenses divided by total expenses.",
            [
                (snap.year, snap.admin_ratio if snap.admin_ratio is not None else 0.0)
                for snap in snapshots
            ],
        ),
        _metric_from_series(
            "Fundraising Ratio",
            "Ratio",
            "Fundraising expenses divided by total expenses.",
            [
                (
                    snap.year,
                    snap.fundraising_ratio
                    if snap.fundraising_ratio is not None
                    else 0.0,
                )
                for snap in snapshots
            ],
        ),
    ]

    for metric in metrics:
        if metric.name.endswith("Ratio"):
            metric.notes = "Higher values indicate greater spending share."
        elif metric.name == "Operating Surplus":
            metric.notes = "Positive surplus implies revenues exceeded expenses."

    return metrics
