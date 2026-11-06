"""Outstanding supplier balances as of the selected date."""

from elsakr_app.party_balance_summary import execute as execute_summary


def execute(filters=None):
	return execute_summary(filters, party_type="Supplier")
