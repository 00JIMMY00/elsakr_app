"""Figures for the Operations dashboard, in the selected company's currency."""

import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond
from frappe.utils import getdate, nowdate


@frappe.whitelist()
@frappe.read_only()
def get_dashboard(from_date=None, to_date=None, company=None):
	for doctype in ("GL Entry", "Sales Invoice", "Company"):
		frappe.has_permission(doctype, "read", throw=True)

	today = getdate(nowdate())
	start = getdate(from_date) if from_date else today
	end = getdate(to_date) if to_date else today
	if start > end:
		frappe.throw(_("From Date cannot be after To Date"))

	companies = frappe.get_list("Company", fields=["name", "default_currency"], order_by="name")
	if not companies:
		frappe.throw(_("No permitted company was found"), frappe.PermissionError)
	allowed = {row.name: row.default_currency for row in companies}
	if not company:
		user_default = frappe.defaults.get_user_default("Company")
		company = user_default if user_default in allowed else companies[0].name
	if company not in allowed:
		frappe.throw(_("Not permitted for this company"), frappe.PermissionError)

	gl_match = get_match_cond("GL Entry")
	invoice_match = get_match_cond("Sales Invoice")
	params = {"company": company, "from_date": start, "to_date": end}

	activity = frappe.db.sql(
		f"""
		SELECT `tabGL Entry`.posting_date AS day,
			SUM(CASE WHEN account.root_type = 'Income' THEN `tabGL Entry`.credit - `tabGL Entry`.debit ELSE 0 END) AS revenue,
			SUM(CASE WHEN account.root_type = 'Expense' THEN `tabGL Entry`.debit - `tabGL Entry`.credit ELSE 0 END) AS expenses
		FROM `tabGL Entry`
		JOIN `tabAccount` account ON account.name = `tabGL Entry`.account
		WHERE `tabGL Entry`.company = %(company)s AND `tabGL Entry`.is_cancelled = 0
			AND `tabGL Entry`.posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND account.root_type IN ('Income', 'Expense') {gl_match}
		GROUP BY `tabGL Entry`.posting_date ORDER BY `tabGL Entry`.posting_date
		""",
		params,
		as_dict=True,
	)

	balances = frappe.db.sql(
		f"""
		SELECT `tabGL Entry`.party_type, `tabGL Entry`.party,
			SUM(CASE WHEN account.account_type = 'Receivable' THEN `tabGL Entry`.debit - `tabGL Entry`.credit
				ELSE `tabGL Entry`.credit - `tabGL Entry`.debit END) AS balance
		FROM `tabGL Entry`
		JOIN `tabAccount` account ON account.name = `tabGL Entry`.account
		WHERE `tabGL Entry`.company = %(company)s AND `tabGL Entry`.is_cancelled = 0
			AND `tabGL Entry`.posting_date <= %(to_date)s
			AND ((account.account_type = 'Receivable' AND `tabGL Entry`.party_type = 'Customer')
				OR (account.account_type = 'Payable' AND `tabGL Entry`.party_type = 'Supplier'))
			AND `tabGL Entry`.party IS NOT NULL AND `tabGL Entry`.party != '' {gl_match}
		GROUP BY `tabGL Entry`.party_type, `tabGL Entry`.party
		""",
		params,
		as_dict=True,
	)

	best_sellers = frappe.db.sql(
		f"""
		SELECT item.item_code, MAX(item.item_name) AS item_name,
			SUM(item.stock_qty) AS qty, SUM(item.base_net_amount) AS amount
		FROM `tabSales Invoice Item` item
		JOIN `tabSales Invoice` ON `tabSales Invoice`.name = item.parent
		WHERE `tabSales Invoice`.docstatus = 1 AND `tabSales Invoice`.company = %(company)s
			AND `tabSales Invoice`.posting_date BETWEEN %(from_date)s AND %(to_date)s
			{invoice_match}
		GROUP BY item.item_code
		HAVING SUM(item.stock_qty) > 0
		ORDER BY qty DESC, amount DESC LIMIT 10
		""",
		params,
		as_dict=True,
	)

	return {
		"company": company,
		"companies": companies,
		"currency": allowed[company],
		"from_date": str(start),
		"to_date": str(end),
		"revenue": sum(row.revenue or 0 for row in activity),
		"expenses": sum(row.expenses or 0 for row in activity),
		"receivables": sum(max(row.balance or 0, 0) for row in balances if row.party_type == "Customer"),
		"payables": sum(max(row.balance or 0, 0) for row in balances if row.party_type == "Supplier"),
		"activity": activity,
		"best_sellers": best_sellers,
	}
