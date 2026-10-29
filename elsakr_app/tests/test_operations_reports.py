"""Database checks for compact report calculations, filters, and permissions."""

import unittest
from uuid import uuid4

import frappe
from frappe.utils import add_days, nowdate

from elsakr_app.elsakr_app.report.daily_purchase_summary.daily_purchase_summary import execute as purchases
from elsakr_app.elsakr_app.report.daily_sales_summary.daily_sales_summary import execute as sales
from elsakr_app.elsakr_app.report.stock_size_search.stock_size_search import execute as stock


class TestOperationsReports(unittest.TestCase):
	def setUp(self):
		self.previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("operations_reports")
		self.company = frappe.db.get_value("Company", {}, "name")
		self.prefix = f"_Report-{uuid4().hex[:8]}"
		self.currency = frappe.db.get_value("Company", self.company, "default_currency")
		self.foreign_currency = "USD" if self.currency != "USD" else "EUR"

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="operations_reports")
		frappe.set_user(self.previous_user)

	def invoice(self, suffix, doctype="Sales Invoice", **values):
		party = "supplier" if doctype == "Purchase Invoice" else "customer"
		# Query fixtures only: no accounting hooks or commits; all rows are rolled back.
		doc = frappe.get_doc(
			{
				"doctype": doctype,
				"name": f"{self.prefix}-{suffix}",
				"company": self.company,
				party: self.prefix,
				f"{party}_name": self.prefix,
				"posting_date": nowdate(),
				"posting_time": "12:00:00",
				"docstatus": 1,
				"base_net_total": 100,
				"base_grand_total": 110,
				"conversion_rate": 1,
				"currency": self.foreign_currency,
				"party_account_currency": self.foreign_currency,
				"outstanding_amount": 50,
				"status": "Partly Paid",
				"is_return": 0,
				**values,
			}
		)
		doc.db_insert()
		return doc

	def test_sales_dates_returns_currency_and_filters(self):
		self.invoice("sale", conversion_rate=2)
		self.invoice(
			"return",
			base_net_total=-20,
			base_grand_total=-22,
			outstanding_amount=0,
			is_return=1,
			status="Return",
		)
		self.invoice("draft", docstatus=0)
		self.invoice("cancelled", docstatus=2)
		self.invoice("yesterday", posting_date=add_days(nowdate(), -1))
		filters = {"company": self.company, "customer": self.prefix}
		_columns, rows, _, chart, summary = sales(filters)
		self.assertEqual(len(rows), 2)
		self.assertEqual([r["value"] for r in summary], [80, 88, 100, "1 / 1"])
		self.assertEqual(chart["data"]["datasets"][0]["values"], [88])
		self.assertEqual(next(r for r in rows if not r.is_return).outstanding, 100)
		self.assertEqual(len(sales({**filters, "invoice_type": "Returns"})[1]), 1)
		self.assertEqual(len(sales({**filters, "status": "Partly Paid"})[1]), 1)
		self.assertEqual(len(sales({**filters, "from_date": add_days(nowdate(), -1)})[1]), 3)
		self.assertEqual(sales({**filters, "customer": self.prefix + "missing"})[1], [])
		with self.assertRaises(frappe.ValidationError):
			sales({**filters, "from_date": add_days(nowdate(), 1)})

		company_account_invoice = self.invoice(
			"company-account", conversion_rate=2, party_account_currency=self.currency, outstanding_amount=15
		)
		company_row = next(row for row in sales(filters)[1] if row.invoice == company_account_invoice.name)
		self.assertEqual(company_row.outstanding, 15)

	def purchase_invoice(self, suffix, **values):
		return self.invoice(suffix, doctype="Purchase Invoice", **values)

	def test_purchases_dates_returns_currency_and_filters(self):
		self.purchase_invoice("purchase", conversion_rate=2)
		self.purchase_invoice(
			"return",
			base_net_total=-20,
			base_grand_total=-22,
			outstanding_amount=0,
			is_return=1,
			status="Return",
		)
		self.purchase_invoice("draft", docstatus=0)
		self.purchase_invoice("cancelled", docstatus=2)
		self.purchase_invoice("yesterday", posting_date=add_days(nowdate(), -1))
		filters = {"company": self.company, "supplier": self.prefix}
		_columns, rows, _, chart, summary = purchases(filters)
		self.assertEqual(len(rows), 2)
		self.assertEqual([r["value"] for r in summary], [80, 88, 100, "1 / 1"])
		self.assertEqual(chart["data"]["datasets"][0]["values"], [88])
		self.assertEqual(next(r for r in rows if not r.is_return).outstanding, 100)
		self.assertEqual(len(purchases({**filters, "invoice_type": "Returns"})[1]), 1)
		self.assertEqual(len(purchases({**filters, "invoice_type": "Purchases"})[1]), 1)
		self.assertEqual(len(purchases({**filters, "status": "Partly Paid"})[1]), 1)
		self.assertEqual(len(purchases({**filters, "from_date": add_days(nowdate(), -1)})[1]), 3)
		self.assertEqual(purchases({**filters, "supplier": self.prefix + "missing"})[1], [])
		with self.assertRaises(frappe.ValidationError):
			purchases({**filters, "from_date": add_days(nowdate(), 1)})

		company_account_invoice = self.purchase_invoice(
			"company-account", conversion_rate=2, party_account_currency=self.currency, outstanding_amount=15
		)
		company_row = next(
			row for row in purchases(filters)[1] if row.invoice == company_account_invoice.name
		)
		self.assertEqual(company_row.outstanding, 15)

	def test_stock_size_warehouse_search_and_negative_stock(self):
		size = frappe.get_doc({"doctype": "Item Size", "size": self.prefix}).insert()
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": self.prefix,
				"item_name": self.prefix,
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_sales_item": 0,
				"custom_size": size.name,
			}
		).insert()
		warehouses = []
		for index, qty in enumerate((7, -2, 0)):
			warehouse = frappe.get_doc(
				{"doctype": "Warehouse", "warehouse_name": f"{self.prefix}-{index}", "company": self.company}
			).insert()
			warehouses.append(warehouse.name)
			frappe.get_doc(
				{
					"doctype": "Bin",
					"item_code": item.name,
					"warehouse": warehouse.name,
					"actual_qty": qty,
					"stock_uom": "Nos",
				}
			).db_insert()
		filters = {"company": self.company, "custom_size": size.name}
		columns, rows = stock(filters)
		self.assertEqual(sorted(r.actual_qty for r in rows), [-2, 7])
		self.assertEqual(len(columns), 6)
		self.assertEqual(stock({**filters, "warehouse": warehouses[0]})[1][0].actual_qty, 7)
		self.assertEqual(len(stock({"company": self.company, "search": self.prefix})[1]), 2)
		self.assertEqual(stock({**filters, "item_code": "missing"})[1], [])
		self.assertEqual(stock({**filters, "warehouse": warehouses[2]})[1], [])

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": f"{self.prefix.lower()}@example.invalid",
				"first_name": "Report permission check",
				"send_welcome_email": 0,
				"roles": [{"role": "Stock User"}],
			}
		).insert()
		frappe.get_doc(
			{
				"doctype": "User Permission",
				"user": user.name,
				"allow": "Warehouse",
				"for_value": warehouses[0],
				"apply_to_all_doctypes": 1,
			}
		).insert()
		frappe.set_user(user.name)
		self.assertEqual([r.warehouse for r in stock(filters)[1]], [warehouses[0]])
		self.assertEqual(stock({**filters, "warehouse": warehouses[1]})[1], [])

	def test_guest_and_unpermitted_company_are_rejected(self):
		for execute in (stock, sales, purchases):
			with self.assertRaises(frappe.PermissionError):
				execute({"company": "missing"})
		frappe.set_user("Guest")
		for execute in (stock, sales, purchases):
			with self.assertRaises(frappe.PermissionError):
				execute({"company": self.company})
