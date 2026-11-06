"""Compact party balances from posted GL, in company currency as of a date."""

import frappe
from frappe.desk.reportview import get_match_cond
from frappe.utils import flt, getdate, nowdate

from elsakr_app.report_utils import column, report_company


def execute(filters=None, party_type="Customer"):
	filters = frappe._dict(filters or {})
	invoice_type = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
	account_type = "Receivable" if party_type == "Customer" else "Payable"
	for doctype in ("Company", "GL Entry", party_type, invoice_type):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	date = getdate(filters.report_date or nowdate())
	party_field = party_type.lower()
	party_filters = {"name": filters[party_field]} if filters.get(party_field) else {}
	parties = frappe.get_list(
		party_type,
		filters=party_filters,
		fields=["name", f"{party_field}_name as party_name"],
		limit_page_length=0,
	)
	columns = [
		column("party_name", f"{party_type} Name", width=300),
		column("outstanding", "Outstanding Amount", "Currency", "currency", 220),
	]
	if not parties:
		return columns, []
	amount = "debit - `tabGL Entry`.credit" if party_type == "Customer" else "credit - `tabGL Entry`.debit"
	balances = frappe.db.sql(
		f"""
		SELECT `tabGL Entry`.party, SUM(`tabGL Entry`.{amount}) AS outstanding
		FROM `tabGL Entry`
		JOIN `tabAccount` account ON account.name = `tabGL Entry`.account
		WHERE `tabGL Entry`.company = %(company)s
			AND `tabGL Entry`.posting_date <= %(report_date)s
			AND `tabGL Entry`.is_cancelled = 0
			AND `tabGL Entry`.party_type = %(party_type)s
			AND `tabGL Entry`.party IN %(parties)s
			AND account.account_type = %(account_type)s {get_match_cond("GL Entry")}
		GROUP BY `tabGL Entry`.party
		""",
		{
			"company": company.name,
			"report_date": date,
			"party_type": party_type,
			"account_type": account_type,
			"parties": tuple(row.name for row in parties),
		},
		as_dict=True,
	)
	precision = frappe.get_precision(invoice_type, "base_grand_total", currency=company.default_currency)
	names = {row.name: row.party_name or row.name for row in parties}
	data = [
		frappe._dict(
			party=row.party,
			party_name=names[row.party],
			outstanding=flt(row.outstanding, precision),
			currency=company.default_currency,
		)
		for row in balances
		if flt(row.outstanding, precision) > 0
	]
	data.sort(key=lambda row: (-row.outstanding, row.party_name))
	return columns, data
