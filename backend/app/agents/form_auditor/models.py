from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
        ...,
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


class ValidatorState(BaseModel):
    extraction: ExtractedIrsForm990PfDataSchema
    initial_findings: list[AuditFinding] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
