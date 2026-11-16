"""Prepare native unsaved receipts/payments from permitted open invoices."""

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe import _
from frappe.utils import flt, getdate, nowdate

from elsakr_app.report_utils import report_company


def make_payment_entry(invoices, party_type="Customer"):
	is_supplier = party_type == "Supplier"
	invoice_type = "Purchase Invoice" if is_supplier else "Sales Invoice"
	party_field = party_type.lower()
	account_field = "credit_to" if is_supplier else "debit_to"
	frappe.has_permission("Payment Entry", "create", throw=True)
	if isinstance(invoices, str):
		invoices = frappe.parse_json(invoices)
	if not isinstance(invoices, list) or not invoices or len(invoices) > 200:
		frappe.throw(
			_("Select between 1 and 200 invoices for one supplier.")
			if is_supplier
			else _("Select between 1 and 200 invoices for one customer.")
		)
	if any(not isinstance(name, str) or not name for name in invoices):
		frappe.throw(_("Invalid invoice selection"))
	invoices = list(dict.fromkeys(invoices))
	documents = []
	for name in invoices:
		doc = frappe.get_doc(invoice_type, name)
		doc.check_permission("read")
		if doc.docstatus != 1 or doc.is_return or flt(doc.outstanding_amount) <= 0:
			frappe.throw(_("An invoice is no longer payable. Refresh the report and select open invoices."))
		if getdate(doc.posting_date) > getdate(nowdate()):
			frappe.throw(_("Future-dated invoices cannot be paid from this report."))
		if is_supplier and doc.invoice_is_blocked():
			frappe.throw(_("A selected purchase invoice is on hold. Release it before making a payment."))
		documents.append(doc)
	first = documents[0]
	report_company(first.company)
	frappe.get_doc(party_type, first.get(party_field)).check_permission("read")
	if any(
		(doc.get(party_field), doc.company, doc.get(account_field), doc.party_account_currency)
		!= (first.get(party_field), first.company, first.get(account_field), first.party_account_currency)
		for doc in documents
	):
		frappe.throw(
			_("Select invoices for the same supplier, company, payable account and currency.")
			if is_supplier
			else _("Select invoices for the same customer, company, receivable account and currency.")
		)
	payment = None
	for doc in documents:
		# Native mapping preserves payment terms, discounts, exchange rates,
		# reference details and payment-request allocations. Nothing is saved here.
		bank_account = payment.get("paid_from" if is_supplier else "paid_to") if payment else None
		mapped = get_payment_entry(invoice_type, doc.name, bank_account=bank_account)
		if not mapped.references:
			frappe.throw(_("An invoice is no longer payable. Refresh the report and select open invoices."))
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
