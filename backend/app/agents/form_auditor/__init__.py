from __future__ import annotations

from typing import Any

from .agent import agent, prepare_initial_findings
from .models import (
    AuditReport,
    ExtractedIrsForm990PfDataSchema,
    ValidatorState,
)


async def build_audit_report(payload: dict[str, Any]) -> AuditReport:
    extraction_payload = payload.get("extraction")
    if extraction_payload is None:
        raise ValueError("Payload missing 'extraction' key.")
    extraction = ExtractedIrsForm990PfDataSchema.model_validate(extraction_payload)

    initial_findings = prepare_initial_findings(extraction)

    metadata: dict[str, Any] = {}
    metadata_raw = payload.get("metadata")
    if isinstance(metadata_raw, dict):
        metadata = {str(k): v for k, v in metadata_raw.items()}

    state = ValidatorState(
        extraction=extraction,
        initial_findings=initial_findings,
        metadata=metadata,
    )

    prompt = (
        "Review the Form 990 extraction and deterministic checks. Validate or adjust "
        "the findings, add any additional issues or mitigations, and craft narrative "
        "section summaries that highlight the most material points. Focus on concrete "
        "evidence; do not fabricate figures."
    )
    result = await agent.run(prompt, deps=state)
    return result.output
