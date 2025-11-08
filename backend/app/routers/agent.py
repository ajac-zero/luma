from fastapi import APIRouter
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from starlette.requests import Request
from starlette.responses import Response

from app.agents import form_auditor, web_search
from app.core.config import settings

provider = AzureProvider(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    api_key=settings.AZURE_OPENAI_API_KEY,
)
model = OpenAIChatModel(model_name="gpt-4o", provider=provider)
agent = Agent(model=model)

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])

data = {
    "extraction": {
        "core_organization_metadata": {
            "ein": "84-2674654",
            "legal_name": "07 IN HEAVEN MEMORIAL SCHOLARSHIP",
            "phone_number": "(262) 215-0300",
            "website_url": "",
            "return_type": "990-PF",
            "amended_return": "No",
            "group_exemption_number": "",
            "subsection_code": "501(c)(3)",
            "ruling_date": "",
            "accounting_method": "Cash",
            "organization_type": "corporation",
            "year_of_formation": "",
            "incorporation_state": "WI",
        },
        "revenue_breakdown": {
            "total_revenue": 5227,
            "contributions_gifts_grants": 5227,
            "program_service_revenue": 0,
            "membership_dues": 0,
            "investment_income": 0,
            "gains_losses_sales_assets": 0,
            "rental_income": 0,
            "related_organizations_revenue": 0,
            "gaming_revenue": 0,
            "other_revenue": 0,
            "government_grants": 0,
            "foreign_contributions": 0,
        },
        "expenses_breakdown": {
            "total_expenses": 2104,
            "program_services_expenses": 0,
            "management_general_expenses": 0,
            "fundraising_expenses": 2104,
            "grants_us_organizations": 0,
            "grants_us_individuals": 0,
            "grants_foreign_organizations": 0,
            "grants_foreign_individuals": 0,
            "compensation_officers": 0,
            "compensation_other_staff": 0,
            "payroll_taxes_benefits": 0,
            "professional_fees": 0,
            "office_occupancy_costs": 0,
            "information_technology_costs": 0,
            "travel_conference_expenses": 0,
            "depreciation_amortization": 0,
            "insurance": 0,
        },
        "balance_sheet": {},
        "officers_directors_trustees_key_employees": [
            {
                "name": "REBECCA TERPSTRA",
                "title_position": "PRESIDENT",
                "average_hours_per_week": 0.1,
                "related_party_transactions": "",
                "former_officer": "",
                "governance_role": "",
            },
            {
                "name": "ROBERT GUZMAN",
                "title_position": "VICE PRESDEINT",
                "average_hours_per_week": 0.1,
                "related_party_transactions": "",
                "former_officer": "",
                "governance_role": "",
            },
            {
                "name": "ANDREA VALENTI",
                "title_position": "TREASURER",
                "average_hours_per_week": 0.1,
                "related_party_transactions": "",
                "former_officer": "",
                "governance_role": "",
            },
            {
                "name": "BETHANY WALSH",
                "title_position": "SECRETARY",
                "average_hours_per_week": 0.1,
                "related_party_transactions": "",
                "former_officer": "",
                "governance_role": "",
            },
        ],
        "governance_management_disclosure": {
            "governing_body_size": 4,
            "independent_members": 4,
            "financial_statements_reviewed": "",
            "form_990_provided_to_governing_body": "",
            "conflict_of_interest_policy": "",
            "whistleblower_policy": "",
            "document_retention_policy": "",
            "ceo_compensation_review_process": "",
            "public_disclosure_practices": "Yes",
        },
        "program_service_accomplishments": [],
        "fundraising_grantmaking": {
            "total_fundraising_event_revenue": 0,
            "total_fundraising_event_expenses": 2104,
            "professional_fundraiser_fees": 0,
        },
        "functional_operational_data": {
            "number_of_employees": 0,
            "number_of_volunteers": 0,
            "occupancy_costs": 0,
            "fundraising_method_descriptions": "",
            "joint_ventures_disregarded_entities": "",
        },
        "compensation_details": {
            "base_compensation": 0,
            "bonus": 0,
            "incentive": 0,
            "other": 0,
            "non_fixed_compensation": "",
            "first_class_travel": "",
            "housing_allowance": "",
            "expense_account_usage": "",
            "supplemental_retirement": "",
        },
        "political_lobbying_activities": {
            "lobbying_expenditures_direct": 0,
            "lobbying_expenditures_grassroots": 0,
            "election_501h_status": "",
            "political_campaign_expenditures": 0,
            "related_organizations_affiliates": "",
        },
        "investments_endowment": {
            "investment_types": "",
            "donor_restricted_endowment_values": 0,
            "net_appreciation_depreciation": 0,
            "related_organization_transactions": "",
            "loans_to_from_related_parties": "",
        },
        "tax_compliance_penalties": {
            "penalties_excise_taxes_reported": "No",
            "unrelated_business_income_disclosure": "No",
            "foreign_bank_account_reporting": "No",
            "schedule_o_narrative_explanations": "",
        },
    },
    "extraction_metadata": {
        "core_organization_metadata": {
            "ein": {"value": "84-2674654", "references": ["0-7"]},
            "legal_name": {
                "value": "07 IN HEAVEN MEMORIAL SCHOLARSHIP",
                "references": ["0-6"],
            },
            "phone_number": {"value": "(262) 215-0300", "references": ["0-a"]},
            "website_url": {"value": "", "references": []},
            "return_type": {
                "value": "990-PF",
                "references": ["4ade8ed0-bce7-4bd5-bd8d-190e3e4be95b"],
            },
            "amended_return": {
                "value": "No",
                "references": ["4ac9edc4-e9bb-430f-b4c4-a42bf4c04b28"],
            },
            "group_exemption_number": {"value": "", "references": []},
            "subsection_code": {
                "value": "501(c)(3)",
                "references": ["4ac9edc4-e9bb-430f-b4c4-a42bf4c04b28"],
            },
            "ruling_date": {"value": "", "references": []},
            "accounting_method": {"value": "Cash", "references": ["0-d"]},
            "organization_type": {
                "value": "corporation",
                "references": ["4ac9edc4-e9bb-430f-b4c4-a42bf4c04b28"],
            },
            "year_of_formation": {"value": "", "references": []},
            "incorporation_state": {
                "value": "WI",
                "references": ["4ac9edc4-e9bb-430f-b4c4-a42bf4c04b28"],
            },
        },
        "revenue_breakdown": {
            "total_revenue": {"value": 5227, "references": ["0-1z"]},
            "contributions_gifts_grants": {"value": 5227, "references": ["0-m"]},
            "program_service_revenue": {"value": 0, "references": []},
            "membership_dues": {"value": 0, "references": []},
            "investment_income": {"value": 0, "references": []},
            "gains_losses_sales_assets": {"value": 0, "references": []},
            "rental_income": {"value": 0, "references": []},
            "related_organizations_revenue": {"value": 0, "references": []},
            "gaming_revenue": {"value": 0, "references": []},
            "other_revenue": {"value": 0, "references": []},
            "government_grants": {"value": 0, "references": []},
            "foreign_contributions": {"value": 0, "references": []},
        },
        "expenses_breakdown": {
            "total_expenses": {"value": 2104, "references": ["0-2S"]},
            "program_services_expenses": {"value": 0, "references": []},
            "management_general_expenses": {"value": 0, "references": []},
            "fundraising_expenses": {"value": 2104, "references": ["13-d"]},
            "grants_us_organizations": {"value": 0, "references": []},
            "grants_us_individuals": {"value": 0, "references": []},
            "grants_foreign_organizations": {"value": 0, "references": []},
            "grants_foreign_individuals": {"value": 0, "references": []},
            "compensation_officers": {
                "value": 0,
                "references": ["5-1q", "5-1w", "5-1C", "5-1I"],
            },
            "compensation_other_staff": {"value": 0, "references": []},
            "payroll_taxes_benefits": {"value": 0, "references": []},
            "professional_fees": {"value": 0, "references": []},
            "office_occupancy_costs": {"value": 0, "references": []},
            "information_technology_costs": {"value": 0, "references": []},
            "travel_conference_expenses": {"value": 0, "references": []},
            "depreciation_amortization": {"value": 0, "references": []},
            "insurance": {"value": 0, "references": []},
        },
        "balance_sheet": {},
        "officers_directors_trustees_key_employees": [
            {
                "name": {"value": "REBECCA TERPSTRA", "references": ["5-1o"]},
                "title_position": {"value": "PRESIDENT", "references": ["5-1p"]},
                "average_hours_per_week": {"value": 0.1, "references": ["5-1p"]},
                "related_party_transactions": {"value": "", "references": []},
                "former_officer": {"value": "", "references": []},
                "governance_role": {"value": "", "references": []},
            },
            {
                "name": {"value": "ROBERT GUZMAN", "references": ["5-1u"]},
                "title_position": {
                    "value": "VICE PRESDEINT",
                    "references": ["5-1v"],
                },
                "average_hours_per_week": {"value": 0.1, "references": ["5-1v"]},
                "related_party_transactions": {"value": "", "references": []},
                "former_officer": {"value": "", "references": []},
                "governance_role": {"value": "", "references": []},
            },
            {
                "name": {"value": "ANDREA VALENTI", "references": ["5-1A"]},
                "title_position": {"value": "TREASURER", "references": ["5-1B"]},
                "average_hours_per_week": {"value": 0.1, "references": ["5-1B"]},
                "related_party_transactions": {"value": "", "references": []},
                "former_officer": {"value": "", "references": []},
                "governance_role": {"value": "", "references": []},
            },
            {
                "name": {"value": "BETHANY WALSH", "references": ["5-1G"]},
                "title_position": {"value": "SECRETARY", "references": ["5-1H"]},
                "average_hours_per_week": {"value": 0.1, "references": ["5-1H"]},
                "related_party_transactions": {"value": "", "references": []},
                "former_officer": {"value": "", "references": []},
                "governance_role": {"value": "", "references": []},
            },
        ],
        "governance_management_disclosure": {
            "governing_body_size": {
                "value": 4,
                "references": ["5-1o", "5-1u", "5-1A", "5-1G"],
            },
            "independent_members": {
                "value": 4,
                "references": ["5-1o", "5-1u", "5-1A", "5-1G"],
            },
            "financial_statements_reviewed": {"value": "", "references": []},
            "form_990_provided_to_governing_body": {"value": "", "references": []},
            "conflict_of_interest_policy": {"value": "", "references": []},
            "whistleblower_policy": {"value": "", "references": []},
            "document_retention_policy": {"value": "", "references": []},
            "ceo_compensation_review_process": {"value": "", "references": []},
            "public_disclosure_practices": {"value": "Yes", "references": ["4-g"]},
        },
        "program_service_accomplishments": [],
        "fundraising_grantmaking": {
            "total_fundraising_event_revenue": {"value": 0, "references": []},
            "total_fundraising_event_expenses": {
                "value": 2104,
                "references": ["13-d"],
            },
            "professional_fundraiser_fees": {"value": 0, "references": []},
        },
        "functional_operational_data": {
            "number_of_employees": {"value": 0, "references": []},
            "number_of_volunteers": {"value": 0, "references": []},
            "occupancy_costs": {"value": 0, "references": []},
            "fundraising_method_descriptions": {"value": "", "references": []},
            "joint_ventures_disregarded_entities": {"value": "", "references": []},
        },
        "compensation_details": {
            "base_compensation": {"value": 0, "references": ["5-1q", "5-1w"]},
            "bonus": {"value": 0, "references": []},
            "incentive": {"value": 0, "references": []},
            "other": {"value": 0, "references": []},
            "non_fixed_compensation": {"value": "", "references": []},
            "first_class_travel": {"value": "", "references": []},
            "housing_allowance": {"value": "", "references": []},
            "expense_account_usage": {"value": "", "references": []},
            "supplemental_retirement": {"value": "", "references": []},
        },
        "political_lobbying_activities": {
            "lobbying_expenditures_direct": {"value": 0, "references": []},
            "lobbying_expenditures_grassroots": {"value": 0, "references": []},
            "election_501h_status": {"value": "", "references": []},
            "political_campaign_expenditures": {"value": 0, "references": []},
            "related_organizations_affiliates": {"value": "", "references": []},
        },
        "investments_endowment": {
            "investment_types": {"value": "", "references": []},
            "donor_restricted_endowment_values": {"value": 0, "references": []},
            "net_appreciation_depreciation": {"value": 0, "references": []},
            "related_organization_transactions": {"value": "", "references": []},
            "loans_to_from_related_parties": {"value": "", "references": []},
        },
        "tax_compliance_penalties": {
            "penalties_excise_taxes_reported": {
                "value": "No",
                "references": ["3-I"],
            },
            "unrelated_business_income_disclosure": {
                "value": "No",
                "references": ["3-Y"],
            },
            "foreign_bank_account_reporting": {
                "value": "No",
                "references": ["4-H"],
            },
            "schedule_o_narrative_explanations": {"value": "", "references": []},
        },
    },
    "metadata": {
        "filename": "markdown.md",
        "org_id": None,
        "duration_ms": 16656,
        "credit_usage": 27.2,
        "job_id": "nnmr8lcxtykk5ll5wodjtrnn6",
        "version": "extract-20250930",
    },
}


@agent.tool_plain
async def build_audit_report():
    """Calls the audit subagent to get a full audit report of the organization"""
    result = await form_auditor.build_audit_report(data)

    return result.model_dump()


@agent.tool_plain
async def search_web_information(query: str, max_results: int = 5):
    """Search the web for up-to-date information using Tavily. Use this when you need current information, news, research, or facts not in your knowledge base."""
    result = await web_search.search_web(query=query, max_results=max_results)

    return result.model_dump()


@router.post("/chat")
async def chat(request: Request) -> Response:
    return await VercelAIAdapter.dispatch_request(request, agent=agent)
