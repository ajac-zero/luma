from __future__ import annotations

from collections.abc import Iterable

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from app.core.config import settings

from .checks import (
    aggregate_findings,
    build_section_summaries,
    check_balance_sheet_presence,
    check_board_engagement,
    check_expense_totals,
    check_fundraising_alignment,
    check_governance_policies,
    check_missing_operational_details,
    check_revenue_totals,
    compose_overall_summary,
    irs_ein_lookup,
)
from .models import (
    AuditFinding,
    AuditReport,
    ExtractedIrsForm990PfDataSchema,
    Severity,
    ValidatorState,
)

provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)
model = OpenAIChatModel(model_name="gpt-4o", provider=provider)
agent = Agent(model=model)


def prepare_initial_findings(
    extraction: ExtractedIrsForm990PfDataSchema,
) -> list[AuditFinding]:
    findings = [
        check_revenue_totals(extraction),
        check_expense_totals(extraction),
        check_fundraising_alignment(extraction),
        check_balance_sheet_presence(extraction),
        check_board_engagement(extraction),
        check_missing_operational_details(extraction),
    ]
    findings.extend(check_governance_policies(extraction))
    return findings


def _merge_findings(
    findings: Iterable[AuditFinding],
    added: Iterable[AuditFinding],
) -> list[AuditFinding]:
    existing = {finding.check_id: finding for finding in findings}
    for finding in added:
        existing[finding.check_id] = finding
    return list(existing.values())


agent = Agent(
    model=model,
    name="FormValidator",
    deps_type=ValidatorState,
    output_type=AuditReport,
    system_prompt=(
        "You are a Form 990 auditor. Review the extraction data and deterministic "
        "checks provided in deps. Use tools to confirm calculations, add or adjust "
        "findings, supply mitigation guidance, and craft concise section summaries. "
        "The AuditReport must include severity (`Pass`, `Warning`, `Error`), "
        "confidence scores, mitigation advice, section summaries, and an overall summary. "
        "Ground every statement in supplied data; do not invent financial figures."
    ),
)


@agent.tool
def revenue_check(ctx: RunContext[ValidatorState]) -> AuditFinding:
    return check_revenue_totals(ctx.deps.extraction)


@agent.tool
def expense_check(ctx: RunContext[ValidatorState]) -> AuditFinding:
    return check_expense_totals(ctx.deps.extraction)


@agent.tool
def fundraising_alignment_check(ctx: RunContext[ValidatorState]) -> AuditFinding:
    return check_fundraising_alignment(ctx.deps.extraction)


@agent.tool
async def verify_ein(ctx: RunContext[ValidatorState]) -> AuditFinding:
    ein = ctx.deps.extraction.core_organization_metadata.ein
    exists, confidence, note = await irs_ein_lookup(ein)
    if exists:
        return AuditFinding(
            check_id="irs_ein_match",
            category="Compliance",
            severity=Severity.PASS,
            message="EIN confirmed against IRS index.",
            mitigation="Document verification in the filing workpapers.",
            confidence=confidence,
        )
    return AuditFinding(
        check_id="irs_ein_match",
        category="Compliance",
        severity=Severity.WARNING,
        message=f"EIN {ein} could not be confirmed. {note}",
        mitigation="Verify the EIN against the IRS EO BMF or IRS determination letter.",
        confidence=confidence,
    )


@agent.output_validator
def finalize_report(
    ctx: RunContext[ValidatorState],
    report: AuditReport,
) -> AuditReport:
    merged_findings = _merge_findings(ctx.deps.initial_findings, report.findings)
    overall = aggregate_findings(merged_findings)
    sections = build_section_summaries(merged_findings)
    overall_summary = compose_overall_summary(merged_findings)
    metadata = ctx.deps.metadata
    notes = report.notes
    if notes is None and isinstance(metadata, dict) and metadata.get("source"):
        notes = f"Reviewed data source: {metadata['source']}."
    year: int | None = None
    if isinstance(metadata, dict):
        metadata_year = metadata.get("return_year")
        if metadata_year is not None:
            try:
                year = int(metadata_year)
            except (TypeError, ValueError):
                pass
    core = ctx.deps.extraction.core_organization_metadata
    organisation_name = core.legal_name or report.organisation_name
    organisation_ein = core.ein or report.organisation_ein
    return report.model_copy(
        update={
            "organisation_ein": organisation_ein,
            "organisation_name": organisation_name,
            "year": year,
            "findings": merged_findings,
            "overall_severity": overall,
            "sections": sections,
            "overall_summary": overall_summary,
            "notes": notes,
        }
    )
