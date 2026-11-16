"""Open sales invoices with native as-of receivables and collection actions."""

from collections import defaultdict

import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as receivables
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate, nowdate

from elsakr_app.report_utils import column, report_company

GROUP_FIELDS = {"Customer": "customer", "Customer Group": "customer_group", "Territory": "territory"}
AMOUNTS = ("invoiced", "paid", "credit_note", "outstanding", "overdue")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	for doctype in ("Company", "Customer", "Sales Invoice", "GL Entry"):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	report_date = getdate(filters.report_date or nowdate())
	group_by = filters.group_by or "Customer"
	if group_by not in (*GROUP_FIELDS, "Invoice"):
		frappe.throw(_("Invalid Group By option"))
	party_filters = {"name": filters.customer} if filters.customer else {}
	parties = {
		row.name: row
		for row in frappe.get_list(
			"Customer",
			filters=party_filters,
			fields=["name", "customer_name", "customer_group", "territory"],
			limit_page_length=0,
		)
	}
	invoices = {}
	if parties:
		invoices = {
			row.name: row
			for row in frappe.get_list(
				"Sales Invoice",
				filters={
					"company": company.name,
					"docstatus": 1,
					"is_return": 0,
					"posting_date": ["<=", report_date],
					"customer": ["in", list(parties)],
				},
				fields=["name", "customer", "posting_date", "due_date"],
				limit_page_length=0,
			)
		}
	rows = []
	if invoices:
		# Delegate payments, POS receipts, returns, currency conversion and historical
		# cutoffs to ERPNext's Payment Ledger implementation (including its match conditions).
		native_rows = receivables(
			{
				"company": company.name,
				"report_date": report_date,
				"party_type": "Customer",
				"party": list(parties),
				"ageing_based_on": "Due Date",
				"age_as_on": "Report Date",
				"ignore_accounts": 1,
			}
		)[1]
		precision = frappe.get_precision(
			"Sales Invoice", "base_grand_total", currency=company.default_currency
		)
		for native in native_rows:
			invoice = invoices.get(native.get("voucher_no"))
			if native.get("voucher_type") != "Sales Invoice" or not invoice:
				continue
			outstanding = flt(native.get("outstanding"), precision)
			if outstanding <= 0:
				continue
			party = parties[invoice.customer]
			days = max(0, date_diff(report_date, invoice.due_date or invoice.posting_date))
			if cint(filters.overdue_only) and not days:
				continue
			row = frappe._dict(
				invoice=invoice.name,
				customer=invoice.customer,
				customer_name=party.customer_name or party.name,
				customer_group=party.customer_group,
				territory=party.territory,
				posting_date=invoice.posting_date,
				due_date=invoice.due_date,
				days_overdue=days,
				status=_("Overdue") if days else _("Not Due"),
				currency=company.default_currency,
				company=company.name,
				indent=0,
			)
			row.update({key: flt(native.get(key), precision) for key in AMOUNTS[:-1]})
			row.overdue = outstanding if days else 0
			row.label = row.customer_name
			rows.append(row)
	rows.sort(key=lambda row: (-row.days_overdue, row.due_date or row.posting_date, row.invoice))
	return (
		get_columns(),
		group_rows(rows, group_by),
		_(
			"Open sales invoices as of the selected date, in company currency. Paid amounts follow ERPNext allocations; credit notes are separate. Unallocated advances and journal balances are excluded. Pay uses today's remaining balance and opens an unsaved Payment Entry."
		),
		get_chart(rows),
		get_summary(rows, company.default_currency),
		1,
	)


def get_columns():
	return [
		column("label", "Customer / Group", width=210),
		column("invoice", "Sales Invoice", "Link", "Sales Invoice", 190),
		column("payment", "Payment", width=125),
		column("invoiced", "Invoice Total", "Currency", "currency", 150),
		column("paid", "Total Paid", "Currency", "currency", 150),
		column("outstanding", "Outstanding Amount", "Currency", "currency", 170),
		column("credit_note", "Credit Note", "Currency", "currency", 140),
		column("due_date", "Due Date", "Date", width=110),
		column("days_overdue", "Days Overdue", "Int", width=105),
		column("status", "Status", width=110),
		column("posting_date", "Posting Date", "Date", width=110),
		column("customer", "Customer", "Link", "Customer", 170),
	]


def group_rows(rows, group_by):
	if group_by == "Invoice":
		return rows
	groups = defaultdict(list)
	for row in rows:
		groups[row[GROUP_FIELDS[group_by]] or _("Not Set")].append(row)
	data = []
	for key, children in sorted(groups.items(), key=lambda item: -sum(r.outstanding for r in item[1])):
		first = children[0]
		parent = frappe._dict(
			label=first.customer_name if group_by == "Customer" else key,
			customer=first.customer if group_by == "Customer" else None,
			currency=first.currency,
			company=first.company,
			indent=0,
			is_group=1,
			invoice_names=[row.invoice for row in children],
		)
		parent.update({amount: sum(row[amount] for row in children) for amount in AMOUNTS})
		data.append(parent)
		for row in children:
			data.append(frappe._dict(row, indent=1))
	return data


def get_chart(rows):
	if not rows:
		return None
	labels = [_("Not Due"), _("1-30 Days"), _("31-60 Days"), _("61-90 Days"), _("Over 90 Days")]
	buckets = [0.0] * 5
	for row in rows:
		days = row.days_overdue
		bucket = 0 if days == 0 else 1 if days <= 30 else 2 if days <= 60 else 3 if days <= 90 else 4
		buckets[bucket] += row.outstanding
	return {
		"type": "bar",
		"title": _("Outstanding by Days Overdue"),
		"fieldtype": "Currency",
		"options": rows[0].currency,
		"animate": 0,
		"disableEntryAnimation": 1,
		"showLegend": 0,
		"colors": ["#14b8a6", "#f59e0b", "#f97316", "#ef4444", "#b91c1c"],
		"data": {
			"labels": [_("Not Due"), "1-30", "31-60", "61-90", "90+"],
			"datasets": [
				{"name": label, "values": [amount if idx == pos else 0 for idx in range(5)]}
				for pos, (label, amount) in enumerate(zip(labels, buckets, strict=True))
			],
		},
		"barOptions": {"stacked": 1},
	}


def get_summary(rows, currency):
	return [
		{
			"label": _(label),
			"value": sum(row[field] for row in rows),
			"datatype": "Currency",
			"currency": currency,
			"indicator": indicator,
		}
		for label, field, indicator in (
			("Invoice Total", "invoiced", "Blue"),
			("Total Paid", "paid", "Green"),
			("Outstanding Amount", "outstanding", "Orange"),
			("Overdue Amount", "overdue", "Red"),
		)
	] + [
		{"label": _("Open Invoices"), "value": len(rows), "datatype": "Int", "indicator": "Blue"},
	]
