from __future__ import annotations

from collections import Counter, defaultdict

from .models import (
    AuditFinding,
    AuditSectionSummary,
    ExtractedIrsForm990PfDataSchema,
    Severity,
)


def aggregate_findings(findings: list[AuditFinding]) -> Severity:
    order = {Severity.ERROR: 3, Severity.WARNING: 2, Severity.PASS: 1}
    overall = Severity.PASS
    for finding in findings:
        if order[finding.severity] > order[overall]:
            overall = finding.severity
    return overall


def check_revenue_totals(data: ExtractedIrsForm990PfDataSchema) -> AuditFinding:
    subtotal = sum(
        value
        for key, value in data.revenue_breakdown.model_dump().items()
        if key != "total_revenue"
    )
    if abs(subtotal - data.revenue_breakdown.total_revenue) <= 1:
        return AuditFinding(
            check_id="revenue_totals",
            category="Revenue",
            severity=Severity.PASS,
            message=f"Revenue categories sum (${subtotal:,.2f}) matches total revenue.",
            mitigation="Maintain detailed support for each revenue source to preserve reconciliation trail.",
            confidence=0.95,
        )
    return AuditFinding(
        check_id="revenue_totals",
        category="Revenue",
        severity=Severity.ERROR,
        message=(
            f"Revenue categories sum (${subtotal:,.2f}) does not equal reported total "
            f"(${data.revenue_breakdown.total_revenue:,.2f})."
        ),
        mitigation="Recalculate revenue totals and correct line items or Schedule A before filing.",
        confidence=0.95,
    )


def check_expense_totals(data: ExtractedIrsForm990PfDataSchema) -> AuditFinding:
    subtotal = (
        data.expenses_breakdown.program_services_expenses
        + data.expenses_breakdown.management_general_expenses
        + data.expenses_breakdown.fundraising_expenses
    )
    if abs(subtotal - data.expenses_breakdown.total_expenses) <= 1:
        return AuditFinding(
            check_id="expense_totals",
            category="Expenses",
            severity=Severity.PASS,
            message="Functional expenses match total expenses.",
            mitigation="Keep functional allocation workpapers to support the reconciliation.",
            confidence=0.95,
        )
    return AuditFinding(
        check_id="expense_totals",
        category="Expenses",
        severity=Severity.ERROR,
        message=(
            f"Functional expenses (${subtotal:,.2f}) do not reconcile to total expenses "
            f"(${data.expenses_breakdown.total_expenses:,.2f})."
        ),
        mitigation="Review Part I, lines 23–27 and reclassify functional expenses to tie to Part II totals.",
        confidence=0.95,
    )


def check_fundraising_alignment(
    data: ExtractedIrsForm990PfDataSchema,
) -> AuditFinding:
    reported_fundraising = data.expenses_breakdown.fundraising_expenses
    event_expenses = data.fundraising_grantmaking.total_fundraising_event_expenses
    difference = abs(reported_fundraising - event_expenses)
    if difference <= 1:
        return AuditFinding(
            check_id="fundraising_alignment",
            category="Fundraising",
            severity=Severity.PASS,
            message="Fundraising functional expenses align with reported event expenses.",
            mitigation="Retain event ledgers and allocations to support matching totals.",
            confidence=0.9,
        )
    severity = (
        Severity.WARNING
        if reported_fundraising and difference <= reported_fundraising * 0.1
        else Severity.ERROR
    )
    return AuditFinding(
        check_id="fundraising_alignment",
        category="Fundraising",
        severity=severity,
        message=(
            f"Fundraising functional expenses (${reported_fundraising:,.2f}) differ from "
            f"reported event expenses (${event_expenses:,.2f}) by ${difference:,.2f}."
        ),
        mitigation="Reconcile Schedule G and Part I allocations to eliminate the variance.",
        confidence=0.85,
    )


def check_balance_sheet_presence(
    data: ExtractedIrsForm990PfDataSchema,
) -> AuditFinding:
    if data.balance_sheet:
        return AuditFinding(
            check_id="balance_sheet_present",
            category="Balance Sheet",
            severity=Severity.PASS,
            message="Balance sheet data is present.",
            mitigation="Ensure ending net assets tie to Part I, line 30.",
            confidence=0.7,
        )
    return AuditFinding(
        check_id="balance_sheet_absent",
        category="Balance Sheet",
        severity=Severity.WARNING,
        message="Balance sheet section is empty; confirm Part II filing requirements.",
        mitigation="Populate assets, liabilities, and net assets or attach supporting schedules.",
        confidence=0.6,
    )


def check_governance_policies(
    data: ExtractedIrsForm990PfDataSchema,
) -> list[AuditFinding]:
    gm = data.governance_management_disclosure
    findings: list[AuditFinding] = []
    policy_fields = {
        "conflict_of_interest_policy": "Document the policy in Part VI or adopt one prior to filing.",
        "whistleblower_policy": "Document whistleblower protections for staff and volunteers.",
        "document_retention_policy": "Adopt and document a record retention policy.",
    }
    affirmative_fields = {
        "financial_statements_reviewed": "Capture whether the board reviewed or audited year-end financials.",
        "form_990_provided_to_governing_body": "Provide Form 990 to the board before submission and note the date of review.",
    }

    for field, mitigation in policy_fields.items():
        value = (getattr(gm, field) or "").strip()
        if not value or value.lower() in {"no", "n", "false"}:
            findings.append(
                AuditFinding(
                    check_id=f"{field}_missing",
                    category="Governance",
                    severity=Severity.WARNING,
                    message=f"{field.replace('_', ' ').title()} not reported or marked 'No'.",
                    mitigation=mitigation,
                    confidence=0.55,
                )
            )

    for field, mitigation in affirmative_fields.items():
        value = (getattr(gm, field) or "").strip()
        if not value:
            findings.append(
                AuditFinding(
                    check_id=f"{field}_blank",
                    category="Governance",
                    severity=Severity.WARNING,
                    message=f"{field.replace('_', ' ').title()} left blank.",
                    mitigation=mitigation,
                    confidence=0.5,
                )
            )
    return findings


def check_board_engagement(data: ExtractedIrsForm990PfDataSchema) -> AuditFinding:
    hours = [
        member.average_hours_per_week
        for member in data.officers_directors_trustees_key_employees
        if member.average_hours_per_week is not None
    ]
    total_hours = sum(hours)
    if total_hours >= 5:
        return AuditFinding(
            check_id="board_hours",
            category="Governance",
            severity=Severity.PASS,
            message="Officer and director time commitments appear reasonable.",
            mitigation="Continue documenting board attendance and oversight responsibilities.",
            confidence=0.7,
        )
    return AuditFinding(
        check_id="board_hours",
        category="Governance",
        severity=Severity.WARNING,
        message=(
            f"Aggregate reported board hours ({total_hours:.1f} per week) are low; "
            "confirm entries reflect actual governance involvement."
        ),
        mitigation="Verify hours in Part VII; update if officers volunteer significant time.",
        confidence=0.6,
    )


def check_missing_operational_details(
    data: ExtractedIrsForm990PfDataSchema,
) -> AuditFinding:
    descriptors = (
        data.functional_operational_data.fundraising_method_descriptions or ""
    ).strip()
    if descriptors:
        return AuditFinding(
            check_id="fundraising_methods_documented",
            category="Operations",
            severity=Severity.PASS,
            message="Fundraising method descriptions provided.",
            mitigation="Update narratives annually to reflect any new campaigns or joint ventures.",
            confidence=0.65,
        )
    return AuditFinding(
        check_id="fundraising_methods_missing",
        category="Operations",
        severity=Severity.WARNING,
        message="Fundraising method descriptions are blank.",
        mitigation="Add a brief Schedule G narrative describing major fundraising approaches.",
        confidence=0.55,
    )


def build_section_summaries(findings: list[AuditFinding]) -> list[AuditSectionSummary]:
    grouped: defaultdict[str, list[AuditFinding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.category].append(finding)

    summaries: list[AuditSectionSummary] = []
    severity_order = {Severity.ERROR: 3, Severity.WARNING: 2, Severity.PASS: 1}
    for category, category_findings in grouped.items():
        counter = Counter(f.severity for f in category_findings)
        severity = aggregate_findings(category_findings)
        summary = ", ".join(
            f"{count} {label}"
            for label, count in (
                ("passes", counter.get(Severity.PASS, 0)),
                ("warnings", counter.get(Severity.WARNING, 0)),
                ("errors", counter.get(Severity.ERROR, 0)),
            )
        )
        summary_text = f"{category} review: {summary}."
        confidence = sum(f.confidence for f in category_findings) / len(
            category_findings
        )
        summaries.append(
            AuditSectionSummary(
                section=category,
                severity=severity,
                summary=summary_text,
                confidence=confidence,
            )
        )
    summaries.sort(key=lambda s: (-severity_order[s.severity], s.section.lower()))
    return summaries


def compose_overall_summary(findings: list[AuditFinding]) -> str:
    if not findings:
        return "No automated findings generated."
    counter = Counter(f.severity for f in findings)
    parts = []
    if counter.get(Severity.ERROR):
        parts.append(f"{counter[Severity.ERROR]} error(s)")
    if counter.get(Severity.WARNING):
        parts.append(f"{counter[Severity.WARNING]} warning(s)")
    if counter.get(Severity.PASS):
        parts.append(f"{counter[Severity.PASS]} check(s) passed")
    summary = "Overall results: " + ", ".join(parts) + "."
    return summary


async def irs_ein_lookup(_ein: str) -> tuple[bool, float, str]:
    return False, 0.2, "IRS verification unavailable in current environment."
