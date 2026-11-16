"""Open purchase invoices, as-of balances and native payment actions."""

from elsakr_app.invoice_balance_summary import execute as execute_summary


def execute(filters=None):
	return execute_summary(filters, party_type="Supplier")
