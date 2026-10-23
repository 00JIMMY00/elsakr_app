import unittest
from uuid import uuid4

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import add_days, nowdate

from elsakr_app.supplier_balance import get_supplier_unpaid_balance


class TestSupplierBalance(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("Requires a configured company")
		frappe.db.savepoint("supplier_balance_test")
		self.company = frappe.get_doc("Company", company)
		self.supplier = frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": f"_Unpaid Test {uuid4().hex[:10]}",
				"supplier_type": "Individual",
			}
		).insert()
		self.item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": f"_Unpaid Item {uuid4().hex[:10]}",
				"item_group": "All Item Groups",
				"stock_uom": frappe.db.get_value("UOM", {}, "name"),
				"is_stock_item": 0,
			}
		).insert()

	def tearDown(self):
		frappe.db.rollback(save_point="supplier_balance_test")
		frappe.clear_cache()

	def invoice(self, submit=True, **kwargs):
		doc = frappe.new_doc("Purchase Invoice")
		doc.update(
			{
				"company": self.company.name,
				"supplier": self.supplier.name,
				"is_paid": 0,
				"set_posting_time": 1,
				"update_stock": 0,
				**kwargs,
			}
		)
		doc.append(
			"items",
			{
				"item_code": self.item.name,
				"qty": 1,
				"rate": 100,
				"expense_account": self.company.default_expense_account,
				"cost_center": self.company.cost_center,
			},
		)
		doc.insert()
		if submit:
			doc.submit()
		return doc

	def balance(self):
		return get_supplier_unpaid_balance(self.supplier.name, self.company.name)["amount"]

	def test_draft_and_cancelled_invoices_do_not_count(self):
		doc = self.invoice(submit=False)
		self.assertEqual(self.balance(), 0)
		doc.submit()
		self.assertEqual(self.balance(), 100)
		doc.cancel()
		self.assertEqual(self.balance(), 0)

	def test_partial_payment_and_full_settlement(self):
		doc = self.invoice()
		self.assertEqual(self.balance(), 100)
		payment = get_payment_entry(
			"Purchase Invoice", doc.name, bank_account=self.company.default_cash_account
		)
		payment.paid_amount = payment.received_amount = 25
		payment.references[0].allocated_amount = 25
		payment.insert().submit()
		self.assertEqual(self.balance(), 75)
		payment2 = get_payment_entry(
			"Purchase Invoice", doc.name, bank_account=self.company.default_cash_account
		)
		payment2.insert().submit()
		self.assertEqual(self.balance(), 0)

	def test_supplier_scope_currency_and_future_posting(self):
		self.invoice()
		result = get_supplier_unpaid_balance(self.supplier.name, self.company.name)
		self.assertEqual(result["currency"], self.company.default_currency)
		other = frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": self.supplier.name + " Other",
				"supplier_type": "Individual",
			}
		).insert()
		self.assertEqual(get_supplier_unpaid_balance(other.name, self.company.name)["amount"], 0)
		self.invoice(posting_date=add_days(nowdate(), 1))
		self.assertEqual(self.balance(), 100)

	def test_company_scope(self):
		self.invoice()
		other_company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": f"_Balance Company {uuid4().hex[:8]}",
				"abbr": uuid4().hex[:5].upper(),
				"country": self.company.country,
				"default_currency": self.company.default_currency,
				"create_chart_of_accounts_based_on": "Existing Company",
				"existing_company": self.company.name,
			}
		).insert()
		self.assertEqual(get_supplier_unpaid_balance(self.supplier.name, other_company.name)["amount"], 0)
		self.assertEqual(self.balance(), 100)

	def test_foreign_invoice_uses_company_currency(self):
		parent = frappe.db.get_value("Account", self.company.default_payable_account, "parent_account")
		account = frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": f"_Balance USD {uuid4().hex[:8]}",
				"company": self.company.name,
				"parent_account": parent,
				"account_type": "Payable",
				"account_currency": "USD",
				"is_group": 0,
			}
		).insert()
		self.supplier.default_currency = "USD"
		self.supplier.append("accounts", {"company": self.company.name, "account": account.name})
		self.supplier.save()
		doc = self.invoice(currency="USD", conversion_rate=50)
		self.assertEqual(doc.base_grand_total, 5000)
		self.assertEqual(self.balance(), 5000)

	def test_credit_balance_does_not_show_as_debt(self):
		doc = self.invoice()
		payment = get_payment_entry(
			"Purchase Invoice", doc.name, bank_account=self.company.default_cash_account
		)
		payment.paid_amount = payment.received_amount = 150
		payment.references[0].allocated_amount = 100
		payment.insert().submit()
		self.assertEqual(self.balance(), 0)

	def test_inline_name_only_invoice_posts_native_payable(self):
		doc = self.invoice(supplier=None, custom_supplier_entry=self.supplier.supplier_name + " Inline")
		self.assertTrue(doc.credit_to)
		self.assertTrue(doc.due_date)
		self.assertFalse(doc.contact_person)
		self.assertFalse(doc.supplier_address)
		self.assertEqual(get_supplier_unpaid_balance(doc.supplier, self.company.name)["amount"], 100)

	def test_paid_inline_invoice_posts_native_cash_and_clears_payable(self):
		doc = self.invoice(
			supplier=None,
			custom_supplier_entry=self.supplier.supplier_name + " Paid",
			custom_supplier_phone="01000000783",
			custom_supplier_address="Payment Test Road",
			is_paid=1,
			mode_of_payment="Cash",
			cash_bank_account=self.company.default_cash_account,
			paid_amount=100,
		)
		self.assertTrue(doc.contact_person)
		self.assertTrue(doc.supplier_address)
		self.assertEqual(doc.outstanding_amount, 0)
		self.assertEqual(get_supplier_unpaid_balance(doc.supplier, self.company.name)["amount"], 0)
		entries = frappe.get_all(
			"GL Entry",
			filters={"voucher_type": "Purchase Invoice", "voucher_no": doc.name, "is_cancelled": 0},
			fields=["account", "debit", "credit"],
		)
		self.assertEqual(sum(row.debit - row.credit for row in entries), 0)
		self.assertEqual(
			sum(
				row.credit - row.debit for row in entries if row.account == self.company.default_cash_account
			),
			100,
		)

	def test_guest_cannot_read_balance(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.PermissionError):
				self.balance()
		finally:
			frappe.set_user("Administrator")
