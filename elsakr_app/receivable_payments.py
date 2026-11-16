"""Prepare native, unsaved customer receipts from permitted invoices."""

import frappe

from elsakr_app.invoice_payments import make_payment_entry as prepare_payment_entry


@frappe.whitelist()
def make_payment_entry(invoices):
	return prepare_payment_entry(invoices, party_type="Customer")
