"""Submitted invoice purchases, including signed returns, in company currency."""

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

from elsakr_app.report_utils import column, report_company


def execute(filters=None):
	filters = frappe._dict(filters or {})
	for doctype in ("Purchase Invoice", "Company"):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	start, end = getdate(filters.from_date or nowdate()), getdate(filters.to_date or nowdate())
	if start > end:
		frappe.throw(_("From Date cannot be after To Date"))
	query = {"company": company.name, "docstatus": 1, "posting_date": ["between", [start, end]]}
	for key in ("supplier", "status"):
		if filters.get(key):
			query[key] = filters[key]
	if filters.invoice_type == "Purchases":
		query["is_return"] = 0
	elif filters.invoice_type == "Returns":
		query["is_return"] = 1
	data = frappe.get_list(
		"Purchase Invoice",
		filters=query,
		fields=[
			"name as invoice",
			"posting_date",
			"supplier",
			"supplier_name",
			"base_net_total",
			"base_grand_total",
			"outstanding_amount",
			"conversion_rate",
			"currency as invoice_currency",
			"party_account_currency",
			"status",
			"is_return",
		],
		order_by="posting_date desc, posting_time desc, name desc",
		limit_page_length=0,
	)
	activity = defaultdict(float)
	for row in data:
		row.currency = company.default_currency
		# ERPNext stores outstanding in party-account currency: either invoice
		# currency (convert once) or company currency (already converted).
		rate = flt(row.conversion_rate) if row.party_account_currency == row.invoice_currency else 1
		row.outstanding = flt(row.outstanding_amount) * rate
		activity[str(row.posting_date)] += flt(row.base_grand_total)
	columns = [
		column("posting_date", "Date", "Date", width=110),
		column("invoice", "Purchase Invoice", "Link", "Purchase Invoice", 200),
		column("supplier", "Supplier", "Link", "Supplier", 160),
		column("supplier_name", "Supplier Name", width=200),
		column("base_grand_total", "Invoice Total", "Currency", "currency", 150),
		column("outstanding", "Outstanding Amount", "Currency", "currency", 160),
		column("status", "Status", width=130),
	]
	days = sorted(activity)
	chart = (
		{
			"data": {
				"labels": days,
				"datasets": [{"name": _("Invoice Total"), "values": [activity[day] for day in days]}],
			},
			"type": "bar",
			"colors": ["#3b82f6"],
		}
		if days
		else None
	)
	summary = [
		{
			"label": _("Net Purchases"),
			"value": sum(flt(row.base_net_total) for row in data),
			"datatype": "Currency",
			"currency": company.default_currency,
			"indicator": "Blue",
		},
		{
			"label": _("Invoice Total"),
			"value": sum(flt(row.base_grand_total) for row in data),
			"datatype": "Currency",
			"currency": company.default_currency,
			"indicator": "Green",
		},
		{
			"label": _("Outstanding Amount"),
			"value": sum(row.outstanding for row in data),
			"datatype": "Currency",
			"currency": company.default_currency,
			"indicator": "Orange",
		},
		{
			"label": _("Purchase Invoices / Returns"),
			"value": f"{sum(not row.is_return for row in data)} / {sum(bool(row.is_return) for row in data)}",
			"datatype": "Data",
			"indicator": "Blue",
		},
	]
	return (
		columns,
		data,
		_(
			"Submitted invoices only. Returns reduce purchases. Amounts use company currency; outstanding balances are current."
		),
		chart,
		summary,
	)
