"""Read the customer's current net receivable balance for the invoice company."""

import frappe
from frappe.desk.reportview import get_match_cond
from frappe.utils import flt, nowdate


@frappe.whitelist()
@frappe.read_only()
def get_customer_unpaid_balance(customer, company):
	for doctype in ("Sales Invoice", "GL Entry"):
		frappe.has_permission(doctype, "read", throw=True)
	frappe.get_doc("Customer", customer).check_permission("read")
	company_doc = frappe.get_doc("Company", company)
	company_doc.check_permission("read")
	balance = frappe.db.sql(
		f"""select coalesce(sum(`tabGL Entry`.debit - `tabGL Entry`.credit), 0)
		from `tabGL Entry`
		join `tabAccount` account on account.name = `tabGL Entry`.account
		where `tabGL Entry`.company = %(company)s
			and `tabGL Entry`.party_type = 'Customer' and `tabGL Entry`.party = %(customer)s
			and `tabGL Entry`.is_cancelled = 0 and `tabGL Entry`.posting_date <= %(today)s
			and account.account_type = 'Receivable'
			{get_match_cond('GL Entry')}""",
		{"company": company, "customer": customer, "today": nowdate()},
	)[0][0]
	currency = company_doc.default_currency
	precision = frappe.get_precision("Sales Invoice", "base_grand_total", currency=currency)
	return {"amount": max(flt(balance, precision), 0), "currency": currency, "precision": precision}
