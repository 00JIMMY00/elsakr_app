"""Open customer/supplier invoices using native as-of Payment Ledger balances."""

from collections import defaultdict

import frappe
from erpnext.accounts.report.accounts_payable.accounts_payable import execute as payables
from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as receivables
from frappe.utils import cint, date_diff, flt, getdate, nowdate

from elsakr_app.report_utils import column as make_column
from elsakr_app.report_utils import report_company

GROUP_FIELDS = {
	"Customer": {"Customer": "customer", "Customer Group": "customer_group", "Territory": "territory"},
	"Supplier": {"Supplier": "supplier", "Supplier Group": "supplier_group", "Country": "country"},
}


def report_text(message):
	return frappe._(message, lang="ar")


def column(fieldname, label, *args, **kwargs):
	result = make_column(fieldname, label, *args, **kwargs)
	result["label"] = report_text(label)
	return result


AMOUNTS = ("invoiced", "paid", "credit_note", "outstanding", "overdue")


def execute(filters=None, party_type="Customer"):
	is_supplier = party_type == "Supplier"
	invoice_type = "Purchase Invoice" if is_supplier else "Sales Invoice"
	party_field = party_type.lower()
	group_fields = GROUP_FIELDS[party_type]
	filters = frappe._dict(filters or {})
	for doctype in ("Company", party_type, invoice_type, "GL Entry"):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	report_date = getdate(filters.report_date or nowdate())
	group_by = filters.group_by or party_type
	if group_by not in (*group_fields, "Invoice"):
		frappe.throw(report_text("Invalid Group By option"))
	party_filters = {"name": filters.get(party_field)} if filters.get(party_field) else {}
	parties = {
		row.name: row
		for row in frappe.get_list(
			party_type,
			filters=party_filters,
			fields=["name", f"{party_field}_name", *list(group_fields.values())[1:]],
			limit_page_length=0,
		)
	}
	invoices = {}
	if parties:
		invoices = {
			row.name: row
			for row in frappe.get_list(
				invoice_type,
				filters={
					"company": company.name,
					"docstatus": 1,
					"is_return": 0,
					"posting_date": ["<=", report_date],
					party_field: ["in", list(parties)],
				},
				fields=["name", party_field, "posting_date", "due_date"]
				+ (["bill_no"] if is_supplier else []),
				limit_page_length=0,
			)
		}
	rows = []
	if invoices:
		# Delegate payments, POS receipts, returns, currency conversion and historical
		# cutoffs to ERPNext's Payment Ledger implementation (including its match conditions).
		native_rows = (payables if is_supplier else receivables)(
			{
				"company": company.name,
				"report_date": report_date,
				"party_type": party_type,
				"party": list(parties),
				"ageing_based_on": "Due Date",
				"age_as_on": "Report Date",
				"ignore_accounts": 1,
			}
		)[1]
		precision = frappe.get_precision(invoice_type, "base_grand_total", currency=company.default_currency)
		for native in native_rows:
			invoice = invoices.get(native.get("voucher_no"))
			if native.get("voucher_type") != invoice_type or not invoice:
				continue
			outstanding = flt(native.get("outstanding"), precision)
			if outstanding <= 0:
				continue
			party = parties[invoice[party_field]]
			days = max(0, date_diff(report_date, invoice.due_date or invoice.posting_date))
			if cint(filters.overdue_only) and not days:
				continue
			row = frappe._dict(
				invoice=invoice.name,
				posting_date=invoice.posting_date,
				due_date=invoice.due_date,
				days_overdue=days,
				status=report_text("Overdue") if days else report_text("Not Due"),
				currency=company.default_currency,
				company=company.name,
				indent=0,
			)
			row.update({key: flt(native.get(key), precision) for key in AMOUNTS[:-1]})
			row.overdue = outstanding if days else 0
			row[party_field] = invoice[party_field]
			row[f"{party_field}_name"] = party.get(f"{party_field}_name") or party.name
			row.update({field: party.get(field) for field in list(group_fields.values())[1:]})
			if is_supplier:
				row.bill_no = invoice.bill_no
			row.label = row[f"{party_field}_name"]
			rows.append(row)
	rows.sort(key=lambda row: (-row.days_overdue, row.due_date or row.posting_date, row.invoice))
	return (
		get_columns(party_type),
		group_rows(rows, group_by, party_type),
		report_text(
			"Open purchase invoices as of the selected date, in company currency. Paid amounts follow ERPNext allocations; debit notes are separate. Unallocated advances and journal balances are excluded. Pay uses today's remaining balance and opens an unsaved Pay Payment Entry."
		)
		if is_supplier
		else report_text(
			"Open sales invoices as of the selected date, in company currency. Paid amounts follow ERPNext allocations; credit notes are separate. Unallocated advances and journal balances are excluded. Pay uses today's remaining balance and opens an unsaved Payment Entry."
		),
		get_chart(rows, party_type),
		get_summary(rows, company.default_currency),
		1,
	)


def get_columns(party_type):
	is_supplier = party_type == "Supplier"
	invoice_type = "Purchase Invoice" if is_supplier else "Sales Invoice"
	columns = [
		column("label", "Supplier / Group" if is_supplier else "Customer / Group", width=210),
		column("invoice", invoice_type, "Link", invoice_type, 190),
		column("payment", "Payment", width=125),
		column("invoiced", "Invoice Total", "Currency", "currency", 150),
		column("paid", "Total Paid", "Currency", "currency", 150),
		column("outstanding", "Outstanding Amount", "Currency", "currency", 170),
		column("credit_note", "Debit Note" if is_supplier else "Credit Note", "Currency", "currency", 140),
		column("due_date", "Due Date", "Date", width=110),
		column("days_overdue", "Days Overdue", "Int", width=105),
		column("status", "Status", width=110),
		column("posting_date", "Posting Date", "Date", width=110),
		column(party_type.lower(), party_type, "Link", party_type, 170),
	]
	if is_supplier:
		columns.append(column("bill_no", "Supplier Invoice No", width=170))
	return columns


def group_rows(rows, group_by, party_type):
	party_field = party_type.lower()
	if group_by == "Invoice":
		return rows
	groups = defaultdict(list)
	for row in rows:
		groups[row[GROUP_FIELDS[party_type][group_by]] or report_text("Not Set")].append(row)
	data = []
	for key, children in sorted(groups.items(), key=lambda item: -sum(r.outstanding for r in item[1])):
		first = children[0]
		parent = frappe._dict(
			label=first[f"{party_field}_name"] if group_by == party_type else key,
			currency=first.currency,
			company=first.company,
			indent=0,
			is_group=1,
			invoice_names=[row.invoice for row in children],
		)
		parent[party_field] = first[party_field] if group_by == party_type else None
		parent.update({amount: sum(row[amount] for row in children) for amount in AMOUNTS})
		data.append(parent)
		for row in children:
			data.append(frappe._dict(row, indent=1))
	return data


def get_chart(rows, party_type):
	if not rows:
		return None
	party_field = party_type.lower()
	totals = defaultdict(float)
	names = {}
	for row in rows:
		party = row[party_field]
		totals[party] += row.outstanding
		names[party] = row.get(f"{party_field}_name") or party
	# Keep distinct parties separate even when their display names match.
	name_counts = defaultdict(int)
	for name in names.values():
		name_counts[name] += 1
	parties = sorted(totals, key=lambda party: (-totals[party], names[party], party))
	return {
		"type": "bar",
		"title": report_text("Outstanding by Supplier")
		if party_type == "Supplier"
		else report_text("Outstanding by Customer"),
		"fieldtype": "Currency",
		"options": rows[0].currency,
		"animate": 0,
		"disableEntryAnimation": 1,
		"showLegend": 0,
		"colors": ["#3b82f6" if party_type == "Supplier" else "#14b8a6"],
		"data": {
			"labels": [
				f"{names[party]} ({party})" if name_counts[names[party]] > 1 else names[party]
				for party in parties
			],
			"datasets": [
				{"name": report_text("Outstanding Amount"), "values": [totals[party] for party in parties]}
			],
		},
	}


def get_summary(rows, currency):
	return [
		{
			"label": report_text(label),
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
		{"label": report_text("Open Invoices"), "value": len(rows), "datatype": "Int", "indicator": "Blue"},
	]
