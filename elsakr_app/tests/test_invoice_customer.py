import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe

from elsakr_app.customer_setup import validate_address_city
from elsakr_app.invoice_customer import customer_details, prepare_invoice_customer, search_customers
from elsakr_app.overrides.sales_invoice import ElsakrSalesInvoice


class TestInvoiceCustomer(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.company = frappe.db.get_value("Company", {}, "name")
		if not self.company:
			self.skipTest("Requires a configured company")
		frappe.db.savepoint("inline_customer_test")
		self.label = f"_Inline Customer Test {uuid4().hex[:10]}"

	def tearDown(self):
		frappe.db.rollback(save_point="inline_customer_test")

	def invoice(self, **kwargs):
		doc = frappe.new_doc("Sales Invoice")
		doc.update({"company": self.company, "custom_customer_entry": self.label, **kwargs})
		return doc

	def test_name_only_and_exact_name_reuse(self):
		doc = self.invoice()
		prepare_invoice_customer(doc)
		self.assertEqual(frappe.db.get_value("Customer", doc.customer, "customer_type"), "Individual")
		self.assertFalse(doc.contact_person)
		self.assertFalse(doc.customer_address)
		another = self.invoice()
		prepare_invoice_customer(another)
		self.assertEqual(another.customer, doc.customer)

	def test_linked_details_phone_search_and_repeated_save(self):
		doc = self.invoice(custom_customer_phone="01000000993", custom_customer_address="Test Road 10")
		prepare_invoice_customer(doc)
		links = (doc.customer, doc.contact_person, doc.customer_address)
		prepare_invoice_customer(doc)
		self.assertEqual(links, (doc.customer, doc.contact_person, doc.customer_address))
		self.assertEqual(customer_details(doc.customer)["phone"], "01000000993")
		self.assertEqual(customer_details(doc.customer)["address"], "Test Road 10")
		self.assertIn(doc.customer, [row.value for row in search_customers("000000993")])
		self.assertFalse(frappe.db.get_value("Address", doc.customer_address, "city"))

	def test_blank_name_and_ambiguous_name_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			prepare_invoice_customer(self.invoice(custom_customer_entry="   "))
		for _ in range(2):
			frappe.get_doc(
				{"doctype": "Customer", "customer_name": self.label, "customer_type": "Individual"}
			).insert()
		with self.assertRaises(frappe.ValidationError):
			prepare_invoice_customer(self.invoice())

	def test_creation_rolls_back_with_failed_invoice(self):
		doc = self.invoice(custom_customer_phone="01000000994", custom_customer_address="Rollback Road")
		frappe.db.savepoint("failed_inline_invoice")
		with patch.object(
			ElsakrSalesInvoice, "validate", side_effect=frappe.ValidationError("Invalid invoice")
		):
			with self.assertRaises(frappe.ValidationError):
				doc.insert()
		self.assertTrue(frappe.db.exists("Customer", {"customer_name": self.label}))
		frappe.db.rollback(save_point="failed_inline_invoice")
		self.assertFalse(frappe.db.exists("Customer", {"customer_name": self.label}))

	def test_address_city_stays_required_for_regular_addresses(self):
		with self.assertRaises(frappe.MandatoryError):
			validate_address_city(frappe.get_doc({"doctype": "Address"}))
		validate_address_city(frappe.get_doc({"doctype": "Address", "custom_freeform_address": 1}))

	def test_guest_cannot_search_or_create(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.PermissionError):
				search_customers(self.label)
			with self.assertRaises(frappe.PermissionError):
				prepare_invoice_customer(self.invoice())
		finally:
			frappe.set_user("Administrator")
