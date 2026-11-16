"""Prepare native, unsaved customer receipts from permitted open invoices."""

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe import _
from frappe.utils import flt, getdate, nowdate

from elsakr_app.report_utils import report_company


@frappe.whitelist()
def make_payment_entry(invoices):
	frappe.has_permission("Payment Entry", "create", throw=True)
	if isinstance(invoices, str):
		invoices = frappe.parse_json(invoices)
	if not isinstance(invoices, list) or not invoices or len(invoices) > 200:
		frappe.throw(_("Select between 1 and 200 invoices for one customer."))
	if any(not isinstance(name, str) or not name for name in invoices):
		frappe.throw(_("Invalid invoice selection"))
	invoices = list(dict.fromkeys(invoices))
	documents = []
	for name in invoices:
		doc = frappe.get_doc("Sales Invoice", name)
		doc.check_permission("read")
		if doc.docstatus != 1 or doc.is_return or flt(doc.outstanding_amount) <= 0:
			frappe.throw(_("An invoice is no longer payable. Refresh the report and select open invoices."))
		if getdate(doc.posting_date) > getdate(nowdate()):
			frappe.throw(_("Future-dated invoices cannot be paid from this report."))
		documents.append(doc)
	first = documents[0]
	report_company(first.company)
	frappe.get_doc("Customer", first.customer).check_permission("read")
	if any(
		(doc.customer, doc.company, doc.debit_to, doc.party_account_currency)
		!= (first.customer, first.company, first.debit_to, first.party_account_currency)
		for doc in documents
	):
		frappe.throw(_("Select invoices for the same customer, company, receivable account and currency."))
	payment = None
	for doc in documents:
		# Native mapping preserves payment terms, discounts, exchange rates,
		# reference details and payment-request allocations. Nothing is saved here.
		mapped = get_payment_entry(
			"Sales Invoice", doc.name, bank_account=payment.paid_to if payment else None
		)
		if payment is None:
			payment = mapped
			continue
		if (mapped.paid_from, mapped.paid_to) != (payment.paid_from, payment.paid_to):
			frappe.throw(_("These invoices require separate payments because their payment accounts differ."))
		for table in ("references", "deductions"):
			for row in mapped.get(table):
				values = row.as_dict()
				for key in ("name", "parent", "parenttype", "parentfield", "idx"):
					values.pop(key, None)
				payment.append(table, values)
		payment.paid_amount += mapped.paid_amount
		payment.received_amount += mapped.received_amount
	if payment.paid_from and payment.paid_to:
		payment.set_amounts()
	return payment
