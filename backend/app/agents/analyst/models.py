from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    IMPROVING = "Improving"
    DECLINING = "Declining"
    STABLE = "Stable"
    VOLATILE = "Volatile"


class TrendMetricPoint(BaseModel):
    year: int
    value: float
    growth: float | None = Field(
        default=None, description="Year-over-year growth expressed as a decimal."
    )


class TrendMetric(BaseModel):
    name: str
    unit: str
    description: str
    points: List[TrendMetricPoint]
    cagr: float | None = Field(
        default=None,
        description="Compound annual growth rate across the analyzed period.",
    )
    direction: TrendDirection = Field(
        default=TrendDirection.STABLE, description="Overall direction of the metric."
    )
    notes: str | None = None


class TrendInsight(BaseModel):
    category: str
    direction: TrendDirection
    summary: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class AnalystReport(BaseModel):
    organisation_name: str
    organisation_ein: str
    years_analyzed: List[int] = Field(default_factory=list)
    key_metrics: List[TrendMetric] = Field(default_factory=list)
    insights: List[TrendInsight] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    outlook: str = "Pending analysis"


class YearlySnapshot(BaseModel):
    year: int
    total_revenue: float
    total_expenses: float
    revenue_growth: float | None = None
    expense_growth: float | None = None
    surplus: float | None = None
    program_ratio: float | None = None
    admin_ratio: float | None = None
    fundraising_ratio: float | None = None
    net_margin: float | None = None


class AnalystState(BaseModel):
    organisation_name: str
    organisation_ein: str
    series: List[YearlySnapshot]
    key_metrics: List[TrendMetric]
    notes: List[str] = Field(default_factory=list)
