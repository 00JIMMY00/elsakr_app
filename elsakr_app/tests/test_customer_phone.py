import unittest
from uuid import uuid4

import frappe

from elsakr_app.invoice_customer import customer_details, search_customers


class TestCustomerPhone(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("customer_phone_test")
		self.label = f"_Direct Phone Test {uuid4().hex[:10]}"

	def tearDown(self):
		frappe.db.rollback(save_point="customer_phone_test")

	def customer(self, phone=""):
		return frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": self.label,
				"customer_type": "Individual",
				"custom_phone": phone,
			}
		).insert()

	def test_name_and_optional_phone_create_native_contact(self):
		doc = self.customer("01000000881")
		doc.reload()
		self.assertEqual(doc.custom_phone, "01000000881")
		self.assertTrue(doc.customer_primary_contact)
		self.assertEqual(customer_details(doc.name)["phone"], "01000000881")
		self.assertIn(doc.name, [row.value for row in search_customers("000000881")])
		doc.save()
		self.assertEqual(len(self.contacts(doc)), 1)

	def test_name_only_then_add_phone(self):
		doc = self.customer()
		self.assertFalse(doc.customer_primary_contact)
		doc.custom_phone = "01000000882"
		doc.save()
		doc.reload()
		self.assertEqual(doc.mobile_no, "01000000882")
		self.assertTrue(doc.customer_primary_contact)

	def test_changed_phone_preserves_old_contact_and_reuses_matches(self):
		doc = self.customer("01000000883")
		doc.reload()
		original_contact = doc.customer_primary_contact
		doc.custom_phone = "01000000884"
		doc.save()
		doc.reload()
		self.assertNotEqual(doc.customer_primary_contact, original_contact)
		self.assertEqual(customer_details(doc.name)["phone"], "01000000884")
		self.assertEqual(frappe.db.get_value("Contact", original_contact, "mobile_no"), "01000000883")
		doc.custom_phone = "01000000883"
		doc.save()
		self.assertEqual(doc.customer_primary_contact, original_contact)
		self.assertEqual(len(self.contacts(doc)), 2)

	def test_native_contact_edit_refreshes_direct_phone(self):
		doc = self.customer("01000000885")
		doc.reload()
		contact = frappe.get_doc("Contact", doc.customer_primary_contact)
		contact.phone_nos[0].phone = "01000000886"
		contact.save()
		doc.save()
		self.assertEqual(doc.custom_phone, "01000000886")
		self.assertEqual(len(self.contacts(doc)), 1)

	def test_shared_contact_phone_is_not_rewritten(self):
		doc = self.customer("01000000887")
		doc.reload()
		other = frappe.get_doc(
			{"doctype": "Customer", "customer_name": self.label + " Other", "customer_type": "Individual"}
		).insert()
		contact = frappe.get_doc("Contact", doc.customer_primary_contact)
		contact.append("links", {"link_doctype": "Customer", "link_name": other.name})
		contact.append("phone_nos", {"phone": "01000000888"})
		contact.save()
		doc.custom_phone = "01000000888"
		doc.save()
		self.assertNotEqual(doc.customer_primary_contact, contact.name)
		self.assertEqual(frappe.db.get_value("Contact", contact.name, "mobile_no"), "01000000887")

	def contacts(self, doc):
		return frappe.get_all(
			"Dynamic Link",
			filters={"link_doctype": "Customer", "link_name": doc.name, "parenttype": "Contact"},
			pluck="parent",
		)
