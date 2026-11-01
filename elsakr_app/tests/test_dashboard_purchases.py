"""Purchasing totals use submitted company-currency invoices in the selected range."""

import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe

from elsakr_app.operations_dashboard import get_dashboard


class TestDashboardPurchases(unittest.TestCase):
	def setUp(self):
		self.previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("dashboard_purchases")
		self.company = frappe.db.get_value("Company", {}, "name")
		self.prefix = f"_Dashboard-{uuid4().hex[:8]}"
		self.currency = frappe.db.get_value("Company", self.company, "default_currency")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dashboard_purchases")
		frappe.set_user(self.previous_user)

	def invoice(self, suffix, **values):
		# Read-query fixtures only; no accounting hooks or commits.
		frappe.get_doc(
			{
				"doctype": "Purchase Invoice",
				"name": f"{self.prefix}-{suffix}",
				"supplier": self.prefix,
				"company": self.company,
				"docstatus": 1,
				"posting_date": "2098-06-10",
				"currency": "USD",
				"conversion_rate": 50,
				"grand_total": 20,
				"base_grand_total": 1000,
				"base_net_total": 900,
				**values,
			}
		).db_insert()

	def test_dates_returns_status_company_currency_and_empty_period(self):
		self.invoice("first", posting_date="2098-06-01")
		self.invoice("last", posting_date="2098-06-30", base_grand_total=2000)
		self.invoice("return", base_grand_total=-250, is_return=1)
		self.invoice("draft", docstatus=0)
		self.invoice("cancelled", docstatus=2)
		self.invoice("before", posting_date="2098-05-31")
		self.invoice("after", posting_date="2098-07-01")
		self.invoice("other-company", company=f"{self.prefix}-other")
		result = get_dashboard("2098-06-01", "2098-06-30", self.company)
		self.assertEqual(result["purchases"], 2750)
		self.assertEqual(result["currency"], self.currency)
		self.assertEqual(get_dashboard("2098-06-02", "2098-06-29", self.company)["purchases"], -250)
		self.assertEqual(get_dashboard("2098-08-01", "2098-08-31", self.company)["purchases"], 0)

	def test_missing_purchase_read_access_is_unavailable_instead_of_zero(self):
		self.invoice("private")
		original = frappe.has_permission
		with patch(
			"frappe.has_permission",
			side_effect=lambda dt, *a, **kw: False if dt == "Purchase Invoice" else original(dt, *a, **kw),
		):
			result = get_dashboard("2098-06-01", "2098-06-30", self.company)
		self.assertIsNone(result["purchases"])
		self.assertIn("revenue", result)

	def test_invalid_dates_company_and_guest_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_dashboard("2098-06-30", "2098-06-01", self.company)
		with self.assertRaises(frappe.PermissionError):
			get_dashboard(company=f"{self.prefix}-missing")
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			get_dashboard(company=self.company)
