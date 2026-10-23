"""Explicit development-only POS payment example and accounting verification."""

import frappe
from frappe.utils import flt


def create_payment_demo():
	if frappe.local.site != "elsakr-dev2.arab-erp.com":
		frappe.throw("Payment demo is restricted to elsakr-dev2.arab-erp.com")
	marker = "DEMO POS payment split - retained for manual testing"
	if frappe.db.exists("Sales Invoice", {"remarks": marker}):
		frappe.throw("Payment demo already exists; records will not be reset")
	company = frappe.get_doc("Company", "test")
	bank_name = "DEMO POS Bank - " + company.abbr
	if not frappe.db.exists("Account", bank_name):
		frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": "DEMO POS Bank",
				"parent_account": frappe.db.get_value(
					"Account", {"company": company.name, "account_type": "Bank", "is_group": 1}, "name"
				),
				"company": company.name,
				"account_type": "Bank",
				"is_group": 0,
			}
		).insert()
	# Correct the development profile's card mapping before testing its postings.
	card = frappe.get_doc("Mode of Payment", "Credit Card")
	for row in card.accounts:
		if row.company == company.name:
			row.default_account = bank_name
	card.save()

	probe = frappe.new_doc("Sales Invoice")
	probe.company = company.name
	probe.is_pos = 1
	probe.flags.ignore_pos_profile = True
	probe.set_pos_fields()
	assert {r.mode_of_payment for r in probe.payments} == {"Cash", "Credit Card"}
	probe.payments[0].amount = 123
	probe.set_pos_fields()
	assert len(probe.payments) == 2 and probe.payments[0].amount == 123
	probe.is_pos = 0
	assert probe.set_pos_fields() is None

	result = []
	for cash, card_amount in [(1000, 0), (400, 600)]:
		doc = frappe.new_doc("Sales Invoice")
		doc.update(
			{
				"company": company.name,
				"customer": "DEMO Tyres Customer",
				"posting_date": "2026-10-23",
				"is_pos": 1,
				"update_stock": 0,
				"remarks": marker,
			}
		)
		doc.set_pos_fields()
		assert {r.mode_of_payment for r in doc.payments} == {"Cash", "Credit Card"}
		for row in doc.payments:
			row.amount = cash if row.mode_of_payment == "Cash" else card_amount
		doc.append(
			"items",
			{
				"item_code": "DEMO-TYRE-175-70-R13",
				"qty": 1,
				"rate": 1000,
				"cost_center": company.cost_center,
			},
		)
		doc.insert()
		doc.submit()
		doc.reload()
		assert doc.docstatus == 1 and doc.grand_total == 1000
		assert doc.paid_amount == 1000 and doc.outstanding_amount == 0
		assert len(doc.payments) == (2 if card_amount else 1)
		entries = frappe.get_all(
			"GL Entry",
			filters={"voucher_type": "Sales Invoice", "voucher_no": doc.name, "is_cancelled": 0},
			fields=["account", "party_type", "debit", "credit"],
			order_by="creation, name",
		)
		assert entries and flt(sum(r.debit - r.credit for r in entries), 2) == 0
		for account, amount in [(company.default_cash_account, cash), (bank_name, card_amount)]:
			assert flt(sum(r.debit - r.credit for r in entries if r.account == account), 2) == amount
		assert sum(r.debit - r.credit for r in entries if r.party_type == "Customer") == 0
		assert sum(r.credit - r.debit for r in entries if r.account == doc.items[0].income_account) == 1000
		assert not frappe.db.exists("Stock Ledger Entry", {"voucher_no": doc.name})
		result.append(
			{
				"invoice": doc.name,
				"paid": doc.paid_amount,
				"outstanding": doc.outstanding_amount,
				"gl": entries,
			}
		)
	return result
