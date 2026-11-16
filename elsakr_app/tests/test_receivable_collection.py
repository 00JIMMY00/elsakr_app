"""Database checks for as-of invoice balances and unsaved native receipt mapping."""

import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe
from frappe.utils import add_days, nowdate

from elsakr_app.elsakr_app.report.simple_receivable_summary.simple_receivable_summary import execute
from elsakr_app.receivable_payments import make_payment_entry


class TestReceivableCollection(unittest.TestCase):
	def setUp(self):
		self.previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("receivable_collection")
		self.prefix = f"_Collect-{uuid4().hex[:8]}"
		self.company = frappe.db.get_value("Company", {}, "name")
		self.currency = frappe.db.get_value("Company", self.company, "default_currency")
		self.account = frappe.db.get_value(
			"Account", {"company": self.company, "account_type": "Receivable", "is_group": 0}, "name"
		)
		self.customer = self.party("customer")
		self.filters = {"company": self.company, "customer": self.customer, "group_by": "Invoice"}

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="receivable_collection")
		frappe.set_user(self.previous_user)

	def party(self, suffix):
		name = f"{self.prefix}-{suffix}"
		frappe.get_doc(
			{
				"doctype": "Customer",
				"name": name,
				"customer_name": "Collection Test",
				"customer_type": "Individual",
				"customer_group": frappe.db.get_value("Customer Group", {}, "name"),
				"territory": frappe.db.get_value("Territory", {}, "name"),
			}
		).db_insert()
		return name

	def invoice(self, suffix, amount=100, outstanding=None, **values):
		doc = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"name": f"{self.prefix}-{suffix}",
				"company": self.company,
				"customer": self.customer,
				"customer_name": "Collection Test",
				"posting_date": add_days(nowdate(), -10),
				"due_date": add_days(nowdate(), -5),
				"docstatus": 1,
				"is_pos": 0,
				"is_return": 0,
				"debit_to": self.account,
				"currency": self.currency,
				"party_account_currency": self.currency,
				"conversion_rate": 1,
				"base_grand_total": amount,
				"grand_total": amount,
				"outstanding_amount": amount if outstanding is None else outstanding,
				**values,
			}
		)
		doc.db_insert()
		self.ledger(doc, amount, date=doc.posting_date, delinked=int(doc.docstatus == 2))
		return doc

	def ledger(self, invoice, amount, date=None, voucher_type="Sales Invoice", delinked=0, **values):
		frappe.get_doc(
			{
				"doctype": "Payment Ledger Entry",
				"name": f"{self.prefix}-{uuid4().hex[:8]}",
				"company": self.company,
				"account": self.account,
				"account_type": "Receivable",
				"account_currency": self.currency,
				"party_type": "Customer",
				"party": invoice.customer,
				"posting_date": date or nowdate(),
				"due_date": invoice.due_date,
				"voucher_type": voucher_type,
				"voucher_no": invoice.name if voucher_type == "Sales Invoice" else f"{self.prefix}-payment",
				"against_voucher_type": "Sales Invoice",
				"against_voucher_no": invoice.name,
				"amount": amount,
				"amount_in_account_currency": amount,
				"delinked": delinked,
				**values,
			}
		).db_insert()

	def test_as_of_payments_credits_and_ageing(self):
		invoice = self.invoice("open", outstanding=50)
		self.ledger(invoice, -30, voucher_type="Payment Entry")
		self.ledger(invoice, -20, voucher_no=f"{self.prefix}-credit")
		self.ledger(invoice, -25, voucher_type="Payment Entry", date=add_days(nowdate(), 1))
		self.ledger(invoice, -999, voucher_type="Payment Entry", delinked=1)
		self.invoice("draft", docstatus=0)
		self.invoice("cancelled", docstatus=2)
		self.invoice("future", posting_date=add_days(nowdate(), 1))
		self.invoice("return", amount=-10, is_return=1)
		paid = self.invoice("settled", outstanding=0)
		self.ledger(paid, -100, voucher_type="Payment Entry")
		columns, rows, _, chart, cards, skip_total = execute(self.filters)
		self.assertIn("invoice", [col["fieldname"] for col in columns])
		self.assertEqual(len(rows), 1)
		row = rows[0]
		self.assertEqual(
			(row.invoice, row.invoiced, row.paid, row.credit_note, row.outstanding),
			(invoice.name, 100, 30, 20, 50),
		)
		self.assertEqual((row.days_overdue, row.overdue, row.currency), (5, 50, self.currency))
		self.assertEqual([card["value"] for card in cards], [100, 30, 50, 50, 1])
		self.assertEqual(sum(sum(ds["values"]) for ds in chart["data"]["datasets"]), 50)
		self.assertEqual(skip_total, 1)
		historical = execute({**self.filters, "report_date": add_days(nowdate(), -1)})[1][0]
		self.assertEqual((historical.paid, historical.credit_note, historical.outstanding), (0, 0, 100))

	def test_groups_no_double_count_and_overdue_filter(self):
		self.invoice("late", amount=80)
		self.invoice("not-due", amount=120, due_date=add_days(nowdate(), 3))
		for group in ("Customer", "Customer Group", "Territory"):
			result = execute({**self.filters, "group_by": group})
			parent, *children = result[1]
			self.assertEqual((parent.indent, parent.outstanding, len(parent.invoice_names)), (0, 200, 2))
			self.assertEqual([row.indent for row in children], [1, 1])
			self.assertEqual([card["value"] for card in result[4]], [200, 0, 200, 80, 2])
		self.assertEqual(len(execute({**self.filters, "overdue_only": 1})[1]), 1)
		with self.assertRaises(frappe.ValidationError):
			execute({**self.filters, "group_by": "unsupported"})

	def test_company_currency_uses_native_ledger_amounts(self):
		invoice = self.invoice("foreign", amount=200, currency="USD", conversion_rate=2)
		# Payment Ledger company amount already includes conversion; don't multiply again.
		self.ledger(invoice, -40, voucher_type="Payment Entry", amount_in_account_currency=-20)
		row = execute(self.filters)[1][0]
		self.assertEqual(
			(row.invoiced, row.paid, row.outstanding, row.currency), (200, 40, 160, self.currency)
		)

	def test_party_and_invoice_permissions_and_empty_results(self):
		self.invoice("hidden")
		original_get_list = frappe.get_list
		for hidden in ("Customer", "Sales Invoice"):
			with patch(
				"frappe.get_list",
				side_effect=lambda dt, **kw: [] if dt == hidden else original_get_list(dt, **kw),
			):
				result = execute(self.filters)
				self.assertEqual(result[1], [])
				self.assertIsNone(result[3])
				self.assertEqual([card["value"] for card in result[4]], [0, 0, 0, 0, 0])
		with self.assertRaises(frappe.PermissionError):
			execute({**self.filters, "company": "missing-company"})
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			execute(self.filters)
		with self.assertRaises(frappe.PermissionError):
			make_payment_entry(["missing-invoice"])

	def test_single_and_multiple_native_unsaved_payments(self):
		one = self.invoice("one", amount=100, outstanding=60)
		self.ledger(one, -40, voucher_type="Payment Entry")
		two = self.invoice("two", amount=200, outstanding=150)
		self.ledger(two, -50, voucher_type="Payment Entry")
		count = frappe.db.count("Payment Entry")
		payment = make_payment_entry([one.name])
		self.assertEqual(
			(payment.payment_type, payment.party, payment.paid_amount), ("Receive", self.customer, 60)
		)
		self.assertEqual(
			(payment.references[0].reference_name, payment.references[0].allocated_amount), (one.name, 60)
		)
		payment = make_payment_entry([one.name, two.name, one.name])
		self.assertEqual(payment.paid_amount, 210)
		self.assertEqual(payment.received_amount, 210)
		self.assertEqual(len(payment.references), 2)
		self.assertEqual(sum(ref.allocated_amount for ref in payment.references), 210)
		self.assertEqual(payment.unallocated_amount, 0)
		self.assertEqual(payment.difference_amount, 0)
		self.assertEqual(payment.docstatus, 0)
		self.assertTrue(payment.is_new())
		payment.reference_no = self.prefix
		payment.reference_date = nowdate()
		payment.validate()
		self.assertEqual(frappe.db.count("Payment Entry"), count)
		# A payment since the report loaded must replace the stale displayed amount.
		frappe.db.set_value("Sales Invoice", one.name, "outstanding_amount", 15)
		self.assertEqual(make_payment_entry([one.name]).paid_amount, 15)

	def test_native_payment_terms_and_pos_receipts(self):
		invoice = self.invoice("terms", outstanding=80)
		# A POS receipt is a negative entry under the invoice's own voucher number.
		self.ledger(invoice, -20)
		row = execute(self.filters)[1][0]
		self.assertEqual((row.paid, row.outstanding), (20, 80))
		template = f"{self.prefix}-terms"
		frappe.get_doc(
			{
				"doctype": "Payment Terms Template",
				"name": template,
				"allocate_payment_based_on_payment_terms": 1,
			}
		).db_insert()
		frappe.db.set_value("Sales Invoice", invoice.name, "payment_terms_template", template)
		for idx, (amount, paid) in enumerate(((40, 20), (60, 0))):
			term = invoice.append(
				"payment_schedule",
				{
					"payment_term": f"{self.prefix}-term-{idx}",
					"due_date": add_days(nowdate(), idx),
					"payment_amount": amount,
					"base_payment_amount": amount,
					"paid_amount": paid,
				},
			)
			term.db_insert()
		other = self.invoice("other-term-invoice", amount=50)
		payment = make_payment_entry([invoice.name, other.name])
		self.assertEqual(payment.paid_amount, 130)
		self.assertEqual(len(payment.references), 3)
		self.assertEqual([ref.allocated_amount for ref in payment.references], [20, 60, 50])
		self.assertTrue(all(ref.payment_term for ref in payment.references[:2]))
		self.assertEqual(payment.difference_amount, 0)

	def test_reject_mixed_customers_and_nonpayable_invoices(self):
		one = self.invoice("open")
		other = self.invoice("other", customer=self.party("other"))
		with self.assertRaises(frappe.ValidationError):
			make_payment_entry([one.name, other.name])
		for values in (
			{"docstatus": 0},
			{"docstatus": 2},
			{"is_return": 1},
			{"outstanding": 0},
			{"posting_date": add_days(nowdate(), 1)},
		):
			doc = self.invoice(uuid4().hex[:8], **values)
			with self.assertRaises(frappe.ValidationError):
				make_payment_entry([doc.name])
		for values in (
			{"party_account_currency": "USD" if self.currency != "USD" else "EUR"},
			{"debit_to": "different-account"},
			{"company": "different-company"},
		):
			doc = self.invoice(uuid4().hex[:8], **values)
			with self.assertRaises(frappe.ValidationError):
				make_payment_entry([one.name, doc.name])

		for selection in ([], {}, [None], [one.name] * 201):
			with self.assertRaises(frappe.ValidationError):
				make_payment_entry(selection)
