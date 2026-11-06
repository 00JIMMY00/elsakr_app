"""Native rendering checks without saving customer or accounting documents."""

import unittest

import frappe
from bs4 import BeautifulSoup
from frappe.www.printview import get_html_and_style

from elsakr_app.print_formats import FORMATS, setup_print_formats


class TestPrintFormats(unittest.TestCase):
	def setUp(self):
		self.previous_user = frappe.session.user
		frappe.set_user("Administrator")
		frappe.db.savepoint("elsakr_print_formats")
		setup_print_formats()
		self.company = frappe.db.get_value("Company", {}, "name")
		if not frappe.db.exists("Letter Head", "elsakr logo"):
			frappe.get_doc(
				{
					"doctype": "Letter Head",
					"letter_head_name": "elsakr logo",
					"source": "HTML",
					"content": '<img src="/files/elsakr_logo.jpeg">',
					"image": "/files/elsakr_logo.jpeg",
				}
			).insert()

	def tearDown(self):
		frappe.db.rollback(save_point="elsakr_print_formats")
		for doctype in FORMATS:
			frappe.clear_cache(doctype=doctype)
		frappe.set_user(self.previous_user)

	def document(self, doctype="Quotation", **values):
		return frappe.get_doc(
			{
				"doctype": doctype,
				"name": "PRINT-PREVIEW-001",
				"company": self.company,
				"customer_name": "عميل تجريبي <script>alert(1)</script>",
				"transaction_date": "2026-11-03",
				"posting_date": "2026-11-03",
				"valid_till": "2026-11-10",
				"currency": "EGP",
				"net_total": 8000,
				"grand_total": 9120,
				"total_taxes_and_charges": 1120,
				"items": [
					{
						"item_name": "إطار تجريبي <b>205</b>",
						"custom_size": "205/55 R16",
						"qty": 4,
						"uom": "Nos",
						"rate": 2000,
						"amount": 8000,
					}
				],
				**values,
			}
		)

	def render(self, doc, **kwargs):
		result = get_html_and_style(frappe.as_json(doc), print_format=FORMATS[doc.doctype], **kwargs)
		self.assertNotIn("{{", result["html"])
		return BeautifulSoup(result["html"], "html.parser")

	def test_setup_is_repeatable_and_sets_native_defaults(self):
		setup_print_formats()
		for doctype, name in FORMATS.items():
			self.assertEqual(frappe.db.count("Print Format", {"name": name}), 1)
			self.assertEqual(frappe.get_meta(doctype).default_print_format, name)
			self.assertEqual(frappe.db.get_value("Print Format", name, "standard"), "No")

	def test_quotation_logo_optional_size_escaping_and_validity(self):
		doc = self.document(custom_customer_address="شارع تجريبي\n<script>bad()</script>")
		soup = self.render(doc)
		self.assertTrue(soup.select_one('.brand-image img[src="/files/elsakr_logo.jpeg"]'))
		self.assertEqual(soup.h1.text, "عرض سعر")
		self.assertIn("ساري حتى", soup.text)
		self.assertIn("DRAFT", soup.text)
		self.assertIn("205/55 R16", soup.text)
		self.assertIn("9,120", soup.select_one(".grand-total").text)
		self.assertIsNone(soup.select_one(".customer-details script"))
		self.assertIsNone(soup.select_one(".item-name b"))
		self.assertNotIn("المتبقي", soup.text)
		doc.items[0].custom_size = ""
		soup = self.render(doc, no_letterhead=1)
		self.assertIsNone(soup.select_one(".brand-image img"))
		self.assertIsNone(soup.select_one(".item-size"))

	def test_invoice_rounding_payments_and_account_currency(self):
		doc = self.document(
			"Sales Invoice",
			docstatus=1,
			currency="USD",
			party_account_currency="EGP",
			conversion_rate=50,
			grand_total=9120.4,
			rounded_total=9120,
			rounding_adjustment=-0.4,
			discount_amount=200,
			paid_amount=10000,
			change_amount=880,
			total_advance=20,
			write_off_amount=10,
			outstanding_amount=500,
		)
		soup = self.render(doc)
		self.assertEqual(soup.h1.text, "فاتورة مبيعات")
		self.assertIn("فرق التقريب", soup.text)
		self.assertIn("9,120", soup.select_one(".grand-total").text)
		self.assertNotIn("9,120.40", soup.select_one(".grand-total").text)
		self.assertIn("500", soup.select_one(".outstanding").text)
		self.assertNotIn("$", soup.select_one(".outstanding").text)
		self.assertIn("$", soup.select_one(".grand-total").text)
		for label in ("المدفوع", "الباقي النقدي", "دفعات مقدمة", "تسوية", "الخصم المطبق"):
			self.assertIn(label, soup.text)
		doc.disable_rounded_total = 1
		doc.docstatus = 0
		soup = self.render(doc)
		self.assertIn("9,120.40", soup.select_one(".grand-total").text)
		self.assertIsNone(soup.select_one(".outstanding"))

	def test_credit_cancelled_zero_and_long_documents(self):
		doc = self.document("Sales Invoice", docstatus=2, is_return=1, grand_total=-9120)
		soup = self.render(doc, settings=frappe.as_json({"allow_print_for_cancelled": 1}))
		self.assertEqual(soup.h1.text, "إشعار دائن")
		self.assertIn("CANCELLED", soup.select_one(".state").text)
		self.assertIn("-9,120", soup.select_one(".grand-total").text)
		doc = self.document(net_total=0, grand_total=0, total_taxes_and_charges=0)
		doc.items = []
		for idx in range(70):
			doc.append("items", {"item_name": f"صنف تجريبي {idx}", "qty": 1, "rate": 0, "amount": 0})
		soup = self.render(doc)
		self.assertEqual(len(soup.select(".items-table tbody tr")), 70)
		self.assertIsNotNone(soup.select_one(".items-table thead"))
		self.assertIn("0.00", soup.select_one(".grand-total").text)
