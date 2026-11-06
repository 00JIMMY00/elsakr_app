"""Database regression checks for the two compact party balance reports."""

import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe
from frappe.utils import add_days, nowdate

from elsakr_app.party_balance_summary import execute


class TestPartyBalanceSummary(unittest.TestCase):
	def setUp(self):
		self.previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("party_summary")
		self.prefix = f"_Balance-{uuid4().hex[:8]}"
		self.company = frappe.db.get_value("Company", {}, "name")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="party_summary")
		frappe.set_user(self.previous_user)

	def check_balances(self, party_type, account_type):
		party_field = party_type.lower()
		party = f"{self.prefix}-{party_type}"
		frappe.get_doc(
			{"doctype": party_type, "name": party, f"{party_field}_name": "Display Name"}
		).db_insert()
		account = f"{self.prefix}-{account_type}"
		frappe.get_doc(
			{
				"doctype": "Account",
				"name": account,
				"account_name": account,
				"company": self.company,
				"account_type": account_type,
				"root_type": "Asset" if party_type == "Customer" else "Liability",
			}
		).db_insert()

		def entry(amount, **values):
			debit, credit = (amount, 0) if party_type == "Customer" else (0, amount)
			frappe.get_doc(
				{
					"doctype": "GL Entry",
					"name": f"{self.prefix}-{uuid4().hex[:8]}",
					"company": self.company,
					"account": account,
					"party_type": party_type,
					"party": party,
					"posting_date": nowdate(),
					"debit": debit,
					"credit": credit,
					"is_cancelled": 0,
					**values,
				}
			).db_insert()

		entry(100)
		entry(-30)
		entry(500, is_cancelled=1)
		entry(600, posting_date=add_days(nowdate(), 1))
		entry(700, company=f"{self.prefix}-other-company")
		entry(800, account=frappe.db.get_value("Account", {"company": self.company, "account_type": "Cash"}))
		filters = {"company": self.company, party_field: party}
		columns, rows = execute(filters, party_type)
		self.assertEqual([col["fieldname"] for col in columns], ["party_name", "outstanding"])
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0].party_name, "Display Name")
		self.assertEqual(rows[0].outstanding, 70)
		self.assertEqual(rows[0].currency, frappe.db.get_value("Company", self.company, "default_currency"))
		self.assertEqual(execute({**filters, "report_date": add_days(nowdate(), -1)}, party_type)[1], [])
		self.assertEqual(execute({**filters, party_field: "missing-party"}, party_type)[1], [])
		original_get_list = frappe.get_list
		with patch(
			"frappe.get_list",
			side_effect=lambda dt, **kw: [] if dt == party_type else original_get_list(dt, **kw),
		):
			self.assertEqual(execute(filters, party_type)[1], [])
		entry(-70)
		self.assertEqual(execute(filters, party_type)[1], [])
		entry(-20)
		self.assertEqual(execute(filters, party_type)[1], [])

	def test_customer_balances(self):
		self.check_balances("Customer", "Receivable")

	def test_supplier_balances(self):
		self.check_balances("Supplier", "Payable")

	def test_permissions(self):
		for party_type in ("Customer", "Supplier"):
			with self.assertRaises(frappe.PermissionError):
				execute({"company": "missing-company"}, party_type)
		frappe.set_user("Guest")
		for party_type in ("Customer", "Supplier"):
			with self.assertRaises(frappe.PermissionError):
				execute({"company": self.company}, party_type)
