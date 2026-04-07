from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


def register_ltl_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(name="freight_audit_workflow")
    async def freight_audit_workflow(
        carrier: str,
        invoice_date: str,
        invoiced_fuel_surcharge_pct: str,
    ) -> list[dict]:
        text = (
            f"You are auditing an LTL freight invoice.\n\n"
            f"Invoice details:\n"
            f"- Carrier: {carrier}\n"
            f"- Invoice date: {invoice_date}\n"
            f"- Fuel surcharge applied: {invoiced_fuel_surcharge_pct}%\n\n"
            f"Step 1: Call ltl_get_fuel_surcharge with carriers=[\"{carrier}\"] and weeks=4 to "
            f"retrieve the published rates for the 4 weeks surrounding {invoice_date}.\n\n"
            f"Step 2: Identify the published rate for the week containing {invoice_date}. "
            f"Compare it against the invoiced rate ({invoiced_fuel_surcharge_pct}%). "
            f"A discrepancy greater than 0.5 percentage points indicates a potential overbilling.\n\n"
            f"Step 3: Check the _verifiability block: extraction_confidence must be >= 0.85 and "
            f"source_timestamp must be within data_freshness_ttl_seconds of now before using the "
            f"data in a dispute claim.\n\n"
            f"Step 4: Summarize your findings: (a) the published rate for the invoice week, "
            f"(b) the invoiced rate, (c) the variance in percentage points, and (d) whether the "
            f"_verifiability confidence meets the threshold for a formal dispute."
        )
        return [{"role": "user", "content": {"type": "text", "text": text}}]


def register_abc_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(name="license_compliance_check")
    async def license_compliance_check(
        state: str,
        business_name: str,
        transaction_type: str | None = None,
    ) -> list[dict]:
        transaction_line = f"- Transaction type: {transaction_type}\n" if transaction_type else ""
        text = (
            f"You are performing a liquor license compliance check.\n\n"
            f"Request details:\n"
            f"- State: {state}\n"
            f"- Business: {business_name}\n"
            f"{transaction_line}\n"
            f"Step 1: Call abc_search_licenses with state=\"{state}\" and "
            f"trade_name=\"{business_name}\". If no results are returned, retry with "
            f"owner_name=\"{business_name}\".\n\n"
            f"Step 2: For any matching record, call abc_lookup_license with the license_number "
            f"and state=\"{state}\" to retrieve the full current record including suspension history.\n\n"
            f"Step 3: Evaluate the result:\n"
            f"- PASS: status is ACTIVE or ACTIVE_RENEWAL_PENDING, expiration_date is in the future, "
            f"and suspensions list is empty or all historical (end_date in the past).\n"
            f"- CONDITIONAL: status is ACTIVE but suspensions contains an active record "
            f"(end_date is null or in the future).\n"
            f"- FAIL: status is SUSPENDED, REVOKED, EXPIRED, or CANCELLED; or no license found.\n\n"
            f"Step 4: Check _verifiability: extraction_confidence >= 0.90 is required for "
            f"compliance-critical decisions. If confidence is below threshold, report the result "
            f"as UNVERIFIED and recommend manual verification at the state ABC portal.\n\n"
            f"Step 5: Return a structured compliance summary with: verdict (PASS/CONDITIONAL/FAIL/"
            f"UNVERIFIED), license_number, expiration_date, active_conditions, and the evidence "
            f"URL from _verifiability."
        )
        return [{"role": "user", "content": {"type": "text", "text": text}}]
