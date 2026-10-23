import unittest
from uuid import uuid4

import frappe

from elsakr_app.invoice_supplier import search_suppliers, supplier_details


class TestSupplierPhone(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("supplier_phone_test")
		self.label = f"_Direct Phone Test {uuid4().hex[:10]}"

	def tearDown(self):
		frappe.db.rollback(save_point="supplier_phone_test")

	def supplier(self, phone=""):
		return frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": self.label,
				"supplier_type": "Individual",
				"custom_phone": phone,
			}
		).insert()

	def test_name_and_optional_phone_create_native_contact(self):
		doc = self.supplier("01000000881")
		doc.reload()
		self.assertEqual(doc.custom_phone, "01000000881")
		self.assertTrue(doc.supplier_primary_contact)
		self.assertEqual(supplier_details(doc.name)["phone"], "01000000881")
		self.assertIn(doc.name, [row.value for row in search_suppliers("000000881")])
		doc.save()
		self.assertEqual(len(self.contacts(doc)), 1)

	def test_name_only_then_add_phone(self):
		doc = self.supplier()
		self.assertFalse(doc.supplier_primary_contact)
		doc.custom_phone = "01000000882"
		doc.save()
		doc.reload()
		self.assertEqual(doc.mobile_no, "01000000882")
		self.assertTrue(doc.supplier_primary_contact)

	def test_changed_phone_preserves_old_contact_and_reuses_matches(self):
		doc = self.supplier("01000000883")
		doc.reload()
		original_contact = doc.supplier_primary_contact
		doc.custom_phone = "01000000884"
		doc.save()
		doc.reload()
		self.assertNotEqual(doc.supplier_primary_contact, original_contact)
		self.assertEqual(supplier_details(doc.name)["phone"], "01000000884")
		self.assertEqual(frappe.db.get_value("Contact", original_contact, "mobile_no"), "01000000883")
		doc.custom_phone = "01000000883"
		doc.save()
		self.assertEqual(doc.supplier_primary_contact, original_contact)
		self.assertEqual(len(self.contacts(doc)), 2)

	def test_native_contact_edit_refreshes_direct_phone(self):
		doc = self.supplier("01000000885")
		doc.reload()
		contact = frappe.get_doc("Contact", doc.supplier_primary_contact)
		contact.phone_nos[0].phone = "01000000886"
		contact.save()
		doc.save()
		self.assertEqual(doc.custom_phone, "01000000886")
		self.assertEqual(len(self.contacts(doc)), 1)

	def test_shared_contact_phone_is_not_rewritten(self):
		doc = self.supplier("01000000887")
		doc.reload()
		other = frappe.get_doc(
			{"doctype": "Supplier", "supplier_name": self.label + " Other", "supplier_type": "Individual"}
		).insert()
		contact = frappe.get_doc("Contact", doc.supplier_primary_contact)
		contact.append("links", {"link_doctype": "Supplier", "link_name": other.name})
		contact.append("phone_nos", {"phone": "01000000888"})
		contact.save()
		doc.custom_phone = "01000000888"
		doc.save()
		self.assertNotEqual(doc.supplier_primary_contact, contact.name)
		self.assertEqual(frappe.db.get_value("Contact", contact.name, "mobile_no"), "01000000887")

	def contacts(self, doc):
		return frappe.get_all(
			"Dynamic Link",
			filters={"link_doctype": "Supplier", "link_name": doc.name, "parenttype": "Contact"},
			pluck="parent",
		)
