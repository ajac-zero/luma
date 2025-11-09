from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Severity(str, Enum):
    PASS = "Pass"
    WARNING = "Warning"
    ERROR = "Error"


class AuditFinding(BaseModel):
    check_id: str
    category: str
    severity: Severity
    message: str
    mitigation: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class AuditSectionSummary(BaseModel):
    section: str
    severity: Severity
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class AuditReport(BaseModel):
    organisation_ein: str
    organisation_name: str
    year: int | None
    overall_severity: Severity
    findings: list[AuditFinding]
    sections: list[AuditSectionSummary] = Field(default_factory=list)
    overall_summary: str | None = None
    notes: str | None = None


class CoreOrgMetadata(BaseModel):
    ein: str
    legal_name: str
    return_type: str
    accounting_method: str
    incorporation_state: str | None = None


class CoreOrganizationMetadata(BaseModel):
    ein: str = Field(
        ...,
        description="Unique IRS identifier for the organization.",
        title="Employer Identification Number (EIN)",
    )
    legal_name: str = Field(
        ...,
        description="Official registered name of the organization.",
        title="Legal Name of Organization",
    )
    phone_number: str = Field(
        ..., description="Primary contact phone number.", title="Phone Number"
    )
    website_url: str = Field(
        ..., description="Organization's website address.", title="Website URL"
    )
    return_type: str = Field(
        ...,
        description="Type of IRS return filed (e.g., 990, 990-EZ, 990-PF).",
        title="Return Type",
    )
    amended_return: str = Field(
        ...,
        description="Indicates if the return is amended.",
        title="Amended Return Flag",
    )
    group_exemption_number: str = Field(
        ...,
        description="IRS group exemption number, if applicable.",
        title="Group Exemption Number",
    )
    subsection_code: str = Field(
        ...,
        description="IRS subsection code (e.g., 501(c)(3)).",
        title="Subsection Code",
    )
    ruling_date: str = Field(
        ...,
        description="Date of IRS ruling or determination letter.",
        title="Ruling/Determination Letter Date",
    )
    accounting_method: str = Field(
        ...,
        description="Accounting method used (cash, accrual, other).",
        title="Accounting Method",
    )
    organization_type: str = Field(
        ...,
        description="Legal structure (corporation, trust, association, etc.).",
        title="Organization Type",
    )
    year_of_formation: str = Field(
        ..., description="Year the organization was formed.", title="Year of Formation"
    )
    incorporation_state: str = Field(
        ..., description="State of incorporation.", title="Incorporation State"
    )


class RevenueBreakdown(BaseModel):
    total_revenue: float = Field(
        ..., description="Sum of all revenue sources.", title="Total Revenue"
    )
    contributions_gifts_grants: float = Field(
        ...,
        description="Revenue from donations and grants.",
        title="Contributions, Gifts, and Grants",
    )
    program_service_revenue: float = Field(
        ...,
        description="Revenue from program services.",
        title="Program Service Revenue",
    )
    membership_dues: float = Field(
        ..., description="Revenue from membership dues.", title="Membership Dues"
    )
    investment_income: float = Field(
        ...,
        description="Revenue from interest and dividends.",
        title="Investment Income",
    )
    gains_losses_sales_assets: float = Field(
        ...,
        description="Net gains or losses from asset sales.",
        title="Gains/Losses from Sales of Assets",
    )
    rental_income: float = Field(
        ...,
        description="Income from rental of real estate or equipment.",
        title="Rental Income",
    )
    related_organizations_revenue: float = Field(
        ...,
        description="Revenue from related organizations.",
        title="Related Organizations Revenue",
    )
    gaming_revenue: float = Field(
        ..., description="Revenue from gaming activities.", title="Gaming Revenue"
    )
    other_revenue: float = Field(
        ..., description="Miscellaneous revenue sources.", title="Other Revenue"
    )
    government_grants: float = Field(
        ...,
        description="Revenue from government grants.",
        title="Revenue from Government Grants",
    )
    foreign_contributions: float = Field(
        ..., description="Revenue from foreign sources.", title="Foreign Contributions"
    )


class ExpensesBreakdown(BaseModel):
    total_expenses: float = Field(
        ..., description="Sum of all expenses.", title="Total Functional Expenses"
    )
    program_services_expenses: float = Field(
        ...,
        description="Expenses for program services.",
        title="Program Services Expenses",
    )
    management_general_expenses: float = Field(
        ...,
        description="Administrative and management expenses.",
        title="Management & General Expenses",
    )
    fundraising_expenses: float = Field(
        ...,
        description="Expenses for fundraising activities.",
        title="Fundraising Expenses",
    )
    grants_us_organizations: float = Field(
        ...,
        description="Grants and assistance to U.S. organizations.",
        title="Grants to U.S. Organizations",
    )
    grants_us_individuals: float = Field(
        ...,
        description="Grants and assistance to U.S. individuals.",
        title="Grants to U.S. Individuals",
    )
    grants_foreign_organizations: float = Field(
        ...,
        description="Grants and assistance to foreign organizations.",
        title="Grants to Foreign Organizations",
    )
    grants_foreign_individuals: float = Field(
        ...,
        description="Grants and assistance to foreign individuals.",
        title="Grants to Foreign Individuals",
    )
    compensation_officers: float = Field(
        ...,
        description="Compensation paid to officers and key employees.",
        title="Compensation of Officers/Key Employees",
    )
    compensation_other_staff: float = Field(
        ...,
        description="Compensation paid to other staff.",
        title="Compensation of Other Staff",
    )
    payroll_taxes_benefits: float = Field(
        ...,
        description="Payroll taxes and employee benefits.",
        title="Payroll Taxes and Benefits",
    )
    professional_fees: float = Field(
        ...,
        description="Legal, accounting, and lobbying fees.",
        title="Professional Fees",
    )
    office_occupancy_costs: float = Field(
        ...,
        description="Office and occupancy expenses.",
        title="Office and Occupancy Costs",
    )
    information_technology_costs: float = Field(
        ..., description="IT-related expenses.", title="Information Technology Costs"
    )
    travel_conference_expenses: float = Field(
        ...,
        description="Travel and conference costs.",
        title="Travel and Conference Expenses",
    )
    depreciation_amortization: float = Field(
        ...,
        description="Depreciation and amortization expenses.",
        title="Depreciation and Amortization",
    )
    insurance: float = Field(..., description="Insurance expenses.", title="Insurance")


class OfficersDirectorsTrusteesKeyEmployee(BaseModel):
    name: str = Field(..., description="Full name of the individual.", title="Name")
    title_position: str = Field(
        ..., description="Role or position held.", title="Title/Position"
    )
    average_hours_per_week: float = Field(
        ...,
        description="Average weekly hours devoted to position.",
        title="Average Hours Per Week",
    )
    related_party_transactions: str = Field(
        ...,
        description="Indicates if related-party transactions occurred.",
        title="Related-Party Transactions",
    )
    former_officer: str = Field(
        ...,
        description="Indicates if the individual is a former officer.",
        title="Former Officer Indicator",
    )
    governance_role: str = Field(
        ...,
        description="Role in governance (voting, independent, etc.).",
        title="Governance Role",
    )


class GovernanceManagementDisclosure(BaseModel):
    governing_body_size: float = Field(
        ...,
        description="Number of voting members on the governing body.",
        title="Governing Body Size",
    )
    independent_members: float = Field(
        ...,
        description="Number of independent voting members.",
        title="Number of Independent Members",
    )
    financial_statements_reviewed: str = Field(
        ...,
        description="Indicates if financial statements were reviewed or audited.",
        title="Financial Statements Reviewed/Audited",
    )
    form_990_provided_to_governing_body: str = Field(
        ...,
        description="Indicates if Form 990 was provided to governing body before filing.",
        title="Form 990 Provided to Governing Body",
    )
    conflict_of_interest_policy: str = Field(
        ...,
        description="Indicates if a conflict-of-interest policy is in place.",
        title="Conflict-of-Interest Policy",
    )
    whistleblower_policy: str = Field(
        ...,
        description="Indicates if a whistleblower policy is in place.",
        title="Whistleblower Policy",
    )
    document_retention_policy: str = Field(
        ...,
        description="Indicates if a document retention/destruction policy is in place.",
        title="Document Retention/Destruction Policy",
    )
    ceo_compensation_review_process: str = Field(
        ...,
        description="Description of CEO compensation review process.",
        title="CEO Compensation Review Process",
    )
    public_disclosure_practices: str = Field(
        ...,
        description="Description of public disclosure practices.",
        title="Public Disclosure Practices",
    )


class ProgramServiceAccomplishment(BaseModel):
    program_name: str = Field(
        ..., description="Name of the program.", title="Program Name"
    )
    program_description: str = Field(
        ..., description="Description of the program.", title="Program Description"
    )
    expenses: float = Field(
        ..., description="Expenses for the program.", title="Program Expenses"
    )
    grants: float = Field(
        ..., description="Grants made under the program.", title="Program Grants"
    )
    revenue_generated: float = Field(
        ..., description="Revenue generated by the program.", title="Revenue Generated"
    )
    quantitative_outputs: str = Field(
        ...,
        description="Quantitative outputs (e.g., number served, events held).",
        title="Quantitative Outputs",
    )


class FundraisingGrantmaking(BaseModel):
    total_fundraising_event_revenue: float = Field(
        ...,
        description="Total revenue from fundraising events.",
        title="Total Fundraising Event Revenue",
    )
    total_fundraising_event_expenses: float = Field(
        ...,
        description="Total direct expenses for fundraising events.",
        title="Total Fundraising Event Expenses",
    )
    professional_fundraiser_fees: float = Field(
        ...,
        description="Fees paid to professional fundraisers.",
        title="Professional Fundraiser Fees",
    )


class FunctionalOperationalData(BaseModel):
    number_of_employees: float = Field(
        ..., description="Total number of employees.", title="Number of Employees"
    )
    number_of_volunteers: float = Field(
        ..., description="Total number of volunteers.", title="Number of Volunteers"
    )
    occupancy_costs: float = Field(
        ..., description="Total occupancy costs.", title="Occupancy Costs"
    )
    fundraising_method_descriptions: str = Field(
        ...,
        description="Descriptions of fundraising methods used.",
        title="Fundraising Method Descriptions",
    )
    joint_ventures_disregarded_entities: str = Field(
        ...,
        description="Details of joint ventures and disregarded entities.",
        title="Joint Ventures and Disregarded Entities",
    )


class CompensationDetails(BaseModel):
    base_compensation: float = Field(
        ..., description="Base salary or wages.", title="Base Compensation"
    )
    bonus: float = Field(
        ..., description="Bonus or incentive compensation.", title="Bonus Compensation"
    )
    incentive: float = Field(
        ..., description="Incentive compensation.", title="Incentive Compensation"
    )
    other: float = Field(
        ..., description="Other forms of compensation.", title="Other Compensation"
    )
    non_fixed_compensation: str = Field(
        ...,
        description="Indicates if compensation is non-fixed.",
        title="Non-Fixed Compensation Flag",
    )
    first_class_travel: str = Field(
        ...,
        description="Indicates if first-class travel was provided.",
        title="First-Class Travel",
    )
    housing_allowance: str = Field(
        ...,
        description="Indicates if housing allowance was provided.",
        title="Housing Allowance",
    )
    expense_account_usage: str = Field(
        ...,
        description="Indicates if expense account was used.",
        title="Expense Account Usage",
    )
    supplemental_retirement: str = Field(
        ...,
        description="Indicates if supplemental retirement or deferred comp was provided.",
        title="Supplemental Retirement/Deferred Comp",
    )


class PoliticalLobbyingActivities(BaseModel):
    lobbying_expenditures_direct: float = Field(
        ...,
        description="Direct lobbying expenditures.",
        title="Direct Lobbying Expenditures",
    )
    lobbying_expenditures_grassroots: float = Field(
        ...,
        description="Grassroots lobbying expenditures.",
        title="Grassroots Lobbying Expenditures",
    )
    election_501h_status: str = Field(
        ...,
        description="Indicates if 501(h) election was made.",
        title="501(h) Election Status",
    )
    political_campaign_expenditures: float = Field(
        ...,
        description="Expenditures for political campaigns.",
        title="Political Campaign Expenditures",
    )
    related_organizations_affiliates: str = Field(
        ...,
        description="Details of related organizations or affiliates involved.",
        title="Related Organizations/Affiliates Involved",
    )


class InvestmentsEndowment(BaseModel):
    investment_types: str = Field(
        ...,
        description="Types of investments held (securities, partnerships, real estate).",
        title="Investment Types",
    )
    donor_restricted_endowment_values: float = Field(
        ...,
        description="Value of donor-restricted endowments.",
        title="Donor-Restricted Endowment Values",
    )
    net_appreciation_depreciation: float = Field(
        ...,
        description="Net appreciation or depreciation of investments.",
        title="Net Appreciation/Depreciation",
    )
    related_organization_transactions: str = Field(
        ...,
        description="Details of transactions with related organizations.",
        title="Related Organization Transactions",
    )
    loans_to_from_related_parties: str = Field(
        ...,
        description="Details of loans to or from related parties.",
        title="Loans to/from Related Parties",
    )


class TaxCompliancePenalties(BaseModel):
    penalties_excise_taxes_reported: str = Field(
        ...,
        description="Reported penalties or excise taxes.",
        title="Penalties or Excise Taxes Reported",
    )
    unrelated_business_income_disclosure: str = Field(
        ...,
        description="Disclosure of unrelated business income (UBI).",
        title="Unrelated Business Income Disclosure",
    )
    foreign_bank_account_reporting: str = Field(
        ...,
        description="Disclosure of foreign bank accounts (FBAR equivalent).",
        title="Foreign Bank Account Reporting",
    )
    schedule_o_narrative_explanations: str = Field(
        ...,
        description="Narrative explanations from Schedule O.",
        title="Schedule O Narrative Explanations",
    )


_OFFICER_HOURS_PATTERN = re.compile(r"([\d.]+)\s*hrs?/wk", re.IGNORECASE)


def _parse_officer_list(entries: list[str] | None) -> list[dict[str, Any]]:
    if not entries:
        return []
    parsed: list[dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, str):
            continue
        parts = [part.strip() for part in raw.split(",")]
        name = parts[0] if parts else ""
        title = parts[1] if len(parts) > 1 else ""
        role = parts[3] if len(parts) > 3 else ""
        hours = 0.0
        match = _OFFICER_HOURS_PATTERN.search(raw)
        if match:
            try:
                hours = float(match.group(1))
            except ValueError:
                hours = 0.0
        parsed.append(
            {
                "name": name,
                "title_position": title,
                "average_hours_per_week": hours,
                "related_party_transactions": "",
                "former_officer": "",
                "governance_role": role,
            }
        )
    return parsed


def _build_program_accomplishments(
    descriptions: list[str] | None,
) -> list[dict[str, Any]]:
    if not descriptions:
        return []
    programs: list[dict[str, Any]] = []
    for idx, description in enumerate(descriptions, start=1):
        if not isinstance(description, str):
            continue
        programs.append(
            {
                "program_name": f"Program {idx}",
                "program_description": description.strip(),
                "expenses": 0.0,
                "grants": 0.0,
                "revenue_generated": 0.0,
                "quantitative_outputs": "",
            }
        )
    return programs


def _transform_flat_payload(data: dict[str, Any]) -> dict[str, Any]:
    def get_str(key: str) -> str:
        value = data.get(key)
        if value is None:
            return ""
        return str(value)

    def get_value(key: str, default: Any = 0) -> Any:
        return data.get(key, default)

    transformed: dict[str, Any] = {
        "core_organization_metadata": {
            "ein": get_str("ein"),
            "legal_name": get_str("legal_name"),
            "phone_number": get_str("phone_number"),
            "website_url": get_str("website_url"),
            "return_type": get_str("return_type"),
            "amended_return": get_str("amended_return"),
            "group_exemption_number": get_str("group_exemption_number"),
            "subsection_code": get_str("subsection_code"),
            "ruling_date": get_str("ruling_date"),
            "accounting_method": get_str("accounting_method"),
            "organization_type": get_str("organization_type"),
            "year_of_formation": get_str("year_of_formation"),
            "incorporation_state": get_str("incorporation_state"),
        },
        "revenue_breakdown": {
            "total_revenue": get_value("total_revenue"),
            "contributions_gifts_grants": get_value("contributions_gifts_grants"),
            "program_service_revenue": get_value("program_service_revenue"),
            "membership_dues": get_value("membership_dues"),
            "investment_income": get_value("investment_income"),
            "gains_losses_sales_assets": get_value("gains_losses_sales_assets"),
            "rental_income": get_value("rental_income"),
            "related_organizations_revenue": get_value("related_organizations_revenue"),
            "gaming_revenue": get_value("gaming_revenue"),
            "other_revenue": get_value("other_revenue"),
            "government_grants": get_value("government_grants"),
            "foreign_contributions": get_value("foreign_contributions"),
        },
        "expenses_breakdown": {
            "total_expenses": get_value("total_expenses"),
            "program_services_expenses": get_value("program_services_expenses"),
            "management_general_expenses": get_value("management_general_expenses"),
            "fundraising_expenses": get_value("fundraising_expenses"),
            "grants_us_organizations": get_value("grants_us_organizations"),
            "grants_us_individuals": get_value("grants_us_individuals"),
            "grants_foreign_organizations": get_value("grants_foreign_organizations"),
            "grants_foreign_individuals": get_value("grants_foreign_individuals"),
            "compensation_officers": get_value("compensation_officers"),
            "compensation_other_staff": get_value("compensation_other_staff"),
            "payroll_taxes_benefits": get_value("payroll_taxes_benefits"),
            "professional_fees": get_value("professional_fees"),
            "office_occupancy_costs": get_value("office_occupancy_costs"),
            "information_technology_costs": get_value("information_technology_costs"),
            "travel_conference_expenses": get_value("travel_conference_expenses"),
            "depreciation_amortization": get_value("depreciation_amortization"),
            "insurance": get_value("insurance"),
        },
        "balance_sheet": data.get("balance_sheet") or {},
        "officers_directors_trustees_key_employees": _parse_officer_list(
            data.get("officers_list")
        ),
        "governance_management_disclosure": {
            "governing_body_size": get_value("governing_body_size"),
            "independent_members": get_value("independent_members"),
            "financial_statements_reviewed": get_str("financial_statements_reviewed"),
            "form_990_provided_to_governing_body": get_str(
                "form_990_provided_to_governing_body"
            ),
            "conflict_of_interest_policy": get_str("conflict_of_interest_policy"),
            "whistleblower_policy": get_str("whistleblower_policy"),
            "document_retention_policy": get_str("document_retention_policy"),
            "ceo_compensation_review_process": get_str(
                "ceo_compensation_review_process"
            ),
            "public_disclosure_practices": get_str("public_disclosure_practices"),
        },
        "program_service_accomplishments": _build_program_accomplishments(
            data.get("program_accomplishments_list")
        ),
        "fundraising_grantmaking": {
            "total_fundraising_event_revenue": get_value(
                "total_fundraising_event_revenue"
            ),
            "total_fundraising_event_expenses": get_value(
                "total_fundraising_event_expenses"
            ),
            "professional_fundraiser_fees": get_value("professional_fundraiser_fees"),
        },
        "functional_operational_data": {
            "number_of_employees": get_value("number_of_employees"),
            "number_of_volunteers": get_value("number_of_volunteers"),
            "occupancy_costs": get_value("occupancy_costs"),
            "fundraising_method_descriptions": get_str(
                "fundraising_method_descriptions"
            ),
            "joint_ventures_disregarded_entities": get_str(
                "joint_ventures_disregarded_entities"
            ),
        },
        "compensation_details": {
            "base_compensation": get_value("base_compensation"),
            "bonus": get_value("bonus"),
            "incentive": get_value("incentive"),
            "other": get_value("other_compensation", get_value("other", 0)),
            "non_fixed_compensation": get_str("non_fixed_compensation"),
            "first_class_travel": get_str("first_class_travel"),
            "housing_allowance": get_str("housing_allowance"),
            "expense_account_usage": get_str("expense_account_usage"),
            "supplemental_retirement": get_str("supplemental_retirement"),
        },
        "political_lobbying_activities": {
            "lobbying_expenditures_direct": get_value("lobbying_expenditures_direct"),
            "lobbying_expenditures_grassroots": get_value(
                "lobbying_expenditures_grassroots"
            ),
            "election_501h_status": get_str("election_501h_status"),
            "political_campaign_expenditures": get_value(
                "political_campaign_expenditures"
            ),
            "related_organizations_affiliates": get_str(
                "related_organizations_affiliates"
            ),
        },
        "investments_endowment": {
            "investment_types": get_str("investment_types"),
            "donor_restricted_endowment_values": get_value(
                "donor_restricted_endowment_values"
            ),
            "net_appreciation_depreciation": get_value("net_appreciation_depreciation"),
            "related_organization_transactions": get_str(
                "related_organization_transactions"
            ),
            "loans_to_from_related_parties": get_str("loans_to_from_related_parties"),
        },
        "tax_compliance_penalties": {
            "penalties_excise_taxes_reported": get_str(
                "penalties_excise_taxes_reported"
            ),
            "unrelated_business_income_disclosure": get_str(
                "unrelated_business_income_disclosure"
            ),
            "foreign_bank_account_reporting": get_str("foreign_bank_account_reporting"),
            "schedule_o_narrative_explanations": get_str(
                "schedule_o_narrative_explanations"
            ),
        },
    }
    return transformed


class ExtractedIrsForm990PfDataSchema(BaseModel):
    core_organization_metadata: CoreOrganizationMetadata = Field(
        ...,
        description="Essential identifiers and attributes for normalizing entities across filings and years.",
        title="Core Organization Metadata",
    )
    revenue_breakdown: RevenueBreakdown = Field(
        ...,
        description="Detailed breakdown of revenue streams for the fiscal year.",
        title="Revenue Breakdown",
    )
    expenses_breakdown: ExpensesBreakdown = Field(
        ...,
        description="Detailed breakdown of expenses for the fiscal year.",
        title="Expenses Breakdown",
    )
    balance_sheet: dict[str, Any] = Field(
        default_factory=dict,
        description="Assets, liabilities, and net assets at year end.",
        title="Balance Sheet Data",
    )
    officers_directors_trustees_key_employees: list[
        OfficersDirectorsTrusteesKeyEmployee
    ] = Field(
        ...,
        description="List of key personnel and their compensation.",
        title="Officers, Directors, Trustees, Key Employees",
    )
    governance_management_disclosure: GovernanceManagementDisclosure = Field(
        ...,
        description="Governance and management practices, policies, and disclosures.",
        title="Governance, Management, and Disclosure",
    )
    program_service_accomplishments: list[ProgramServiceAccomplishment] = Field(
        ...,
        description="Major programs and their outputs for the fiscal year.",
        title="Program Service Accomplishments",
    )
    fundraising_grantmaking: FundraisingGrantmaking = Field(
        ...,
        description="Fundraising event details and grantmaking activities.",
        title="Fundraising & Grantmaking",
    )
    functional_operational_data: FunctionalOperationalData = Field(
        ...,
        description="Operational metrics and related-organization relationships.",
        title="Functional & Operational Data",
    )
    compensation_details: CompensationDetails = Field(
        ...,
        description="Detailed breakdown of officer compensation and benefits.",
        title="Compensation Details",
    )
    political_lobbying_activities: PoliticalLobbyingActivities = Field(
        ...,
        description="Details of political and lobbying expenditures and affiliations.",
        title="Political & Lobbying Activities",
    )
    investments_endowment: InvestmentsEndowment = Field(
        ...,
        description="Investment holdings, endowment values, and related transactions.",
        title="Investments & Endowment",
    )
    tax_compliance_penalties: TaxCompliancePenalties = Field(
        ...,
        description="Tax compliance indicators, penalties, and narrative explanations.",
        title="Tax Compliance / Penalties",
    )

    @model_validator(mode="before")
    @classmethod
    def _ensure_structure(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        if "core_organization_metadata" in value:
            return value
        return _transform_flat_payload(value)


class ValidatorState(BaseModel):
    extraction: ExtractedIrsForm990PfDataSchema
    initial_findings: list[AuditFinding] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
