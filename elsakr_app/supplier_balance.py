"""Read the supplier's current net payable balance for the invoice company."""

import frappe
from frappe.desk.reportview import get_match_cond
from frappe.utils import flt, nowdate


@frappe.whitelist()
@frappe.read_only()
def get_supplier_unpaid_balance(supplier, company):
	for doctype in ("Purchase Invoice", "GL Entry"):
		frappe.has_permission(doctype, "read", throw=True)
	supplier_doc = frappe.get_doc("Supplier", supplier)
	supplier_doc.check_permission("read")
	company_doc = frappe.get_doc("Company", company)
	company_doc.check_permission("read")
	balance = frappe.db.sql(
		f"""select coalesce(sum(`tabGL Entry`.credit - `tabGL Entry`.debit), 0)
		from `tabGL Entry`
		join `tabAccount` account on account.name = `tabGL Entry`.account
		where `tabGL Entry`.company = %(company)s
			and `tabGL Entry`.party_type = 'Supplier' and `tabGL Entry`.party = %(supplier)s
			and `tabGL Entry`.is_cancelled = 0 and `tabGL Entry`.posting_date <= %(today)s
			and account.account_type = 'Payable'
			{get_match_cond('GL Entry')}""",
		{"company": company, "supplier": supplier, "today": nowdate()},
	)[0][0]
	currency = company_doc.default_currency
	precision = frappe.get_precision("Purchase Invoice", "base_grand_total", currency=currency)
	return {
		"amount": max(flt(balance, precision), 0),
		"currency": currency,
		"precision": precision,
		"supplier_name": supplier_doc.supplier_name,
	}
