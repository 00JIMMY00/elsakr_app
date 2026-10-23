import unittest
from unittest.mock import patch
from uuid import uuid4

import frappe

from elsakr_app.customer_setup import validate_address_city
from elsakr_app.invoice_supplier import prepare_invoice_supplier, search_suppliers, supplier_details
from elsakr_app.overrides.purchase_invoice import ElsakrPurchaseInvoice


class TestInvoiceSupplier(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.company = frappe.db.get_value("Company", {}, "name")
		if not self.company:
			self.skipTest("Requires a configured company")
		frappe.db.savepoint("inline_supplier_test")
		self.label = f"_Inline Supplier Test {uuid4().hex[:10]}"

	def tearDown(self):
		frappe.db.rollback(save_point="inline_supplier_test")

	def invoice(self, **kwargs):
		doc = frappe.new_doc("Purchase Invoice")
		doc.update({"company": self.company, "custom_supplier_entry": self.label, **kwargs})
		return doc

	def test_name_only_and_exact_name_reuse(self):
		doc = self.invoice()
		prepare_invoice_supplier(doc)
		self.assertEqual(frappe.db.get_value("Supplier", doc.supplier, "supplier_type"), "Individual")
		self.assertFalse(doc.contact_person)
		self.assertFalse(doc.supplier_address)
		another = self.invoice()
		prepare_invoice_supplier(another)
		self.assertEqual(another.supplier, doc.supplier)

	def test_linked_details_phone_search_and_repeated_save(self):
		doc = self.invoice(custom_supplier_phone="01000000993", custom_supplier_address="Test Road 10")
		prepare_invoice_supplier(doc)
		links = (doc.supplier, doc.contact_person, doc.supplier_address)
		prepare_invoice_supplier(doc)
		self.assertEqual(links, (doc.supplier, doc.contact_person, doc.supplier_address))
		self.assertEqual(supplier_details(doc.supplier)["phone"], "01000000993")
		self.assertEqual(supplier_details(doc.supplier)["address"], "Test Road 10")
		self.assertIn(doc.supplier, [row.value for row in search_suppliers("000000993")])
		self.assertFalse(frappe.db.get_value("Address", doc.supplier_address, "city"))

	def test_blank_name_and_ambiguous_name_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			prepare_invoice_supplier(self.invoice(custom_supplier_entry="   "))
		for index in range(2):
			frappe.get_doc(
				{"doctype": "Supplier", "supplier_name": self.label, "supplier_type": "Individual"}
			).insert(set_name=f"{self.label}-{index}")
		with self.assertRaises(frappe.ValidationError):
			prepare_invoice_supplier(self.invoice())

	def test_creation_rolls_back_with_failed_invoice(self):
		doc = self.invoice(custom_supplier_phone="01000000994", custom_supplier_address="Rollback Road")
		frappe.db.savepoint("failed_inline_invoice")
		with patch.object(
			ElsakrPurchaseInvoice, "validate", side_effect=frappe.ValidationError("Invalid invoice")
		):
			with self.assertRaises(frappe.ValidationError):
				doc.insert()
		self.assertTrue(frappe.db.exists("Supplier", {"supplier_name": self.label}))
		frappe.db.rollback(save_point="failed_inline_invoice")
		self.assertFalse(frappe.db.exists("Supplier", {"supplier_name": self.label}))

	def test_address_city_stays_required_for_regular_addresses(self):
		with self.assertRaises(frappe.MandatoryError):
			validate_address_city(frappe.get_doc({"doctype": "Address"}))
		validate_address_city(frappe.get_doc({"doctype": "Address", "custom_freeform_address": 1}))

	def test_guest_cannot_search_or_create(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.PermissionError):
				search_suppliers(self.label)
			with self.assertRaises(frappe.PermissionError):
				prepare_invoice_supplier(self.invoice())
		finally:
			frappe.set_user("Administrator")
