import unittest
from uuid import uuid4

import frappe
from erpnext.stock.get_item_details import get_price_list_rate_for

from elsakr_app.item_pricing import load_selling_price, price_context


class TestItemPricing(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("item_pricing_test")
		self.item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": f"_Selling Price {uuid4().hex[:10]}",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 0,
				"standard_rate": 125,
			}
		).insert()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="item_pricing_test")

	def load(self):
		doc = frappe.get_doc("Item", self.item.name)
		load_selling_price(doc)
		return doc

	def test_saved_price_edit_drives_native_invoice_lookup(self):
		doc = self.load()
		self.assertEqual(doc.standard_rate, 125)
		doc.standard_rate = 175
		doc.save()
		doc = self.load()
		self.assertEqual(doc.standard_rate, 175)
		context = price_context(doc)
		rate = get_price_list_rate_for(
			frappe._dict(
				price_list=context.price_list,
				uom="Nos",
				stock_uom="Nos",
				qty=1,
				transaction_date=frappe.utils.nowdate(),
				conversion_factor=1,
			),
			doc.name,
		)
		self.assertEqual(rate, 175)
		self.assertEqual(frappe.db.count("Item Price", {"item_code": doc.name}), 1)

	def test_external_price_is_authoritative_and_unrelated_save_preserves_it(self):
		context = price_context(self.item)
		price = frappe.get_doc("Item Price", context.name)
		price.price_list_rate = 240
		price.save()
		doc = self.load()
		self.assertEqual(doc.standard_rate, 240)
		doc.description = "Unrelated edit"
		doc.save()
		self.assertEqual(price_context(doc).rate, 240)

	def test_stale_price_edit_is_rejected(self):
		doc = self.load()
		price = frappe.get_doc("Item Price", price_context(doc).name)
		price.price_list_rate = 250
		price.save()
		doc.standard_rate = 180
		with self.assertRaises(frappe.ValidationError):
			doc.save()
		self.assertEqual(price_context(doc).rate, 250)

	def test_zero_and_negative_price(self):
		doc = self.load()
		doc.standard_rate = 0
		doc.save()
		self.assertEqual(price_context(doc).rate, 0)
		doc = self.load()
		doc.standard_rate = -1
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_missing_price_is_created_on_edit(self):
		frappe.delete_doc("Item Price", price_context(self.item).name)
		doc = self.load()
		self.assertEqual(doc.standard_rate, 0)
		doc.standard_rate = 200
		doc.save()
		self.assertEqual(price_context(doc).rate, 200)

	def test_multiple_active_prices_require_item_price_editor(self):
		context = price_context(self.item)
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": self.item.name,
				"price_list": context.price_list,
				"uom": "Nos",
				"price_list_rate": 300,
				"valid_from": "2020-01-01",
			}
		).insert()
		doc = self.load()
		self.assertTrue(doc.get_onload("selling_price").error)
		doc.standard_rate = 999
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_variant_price_remains_editable_after_creation(self):
		from erpnext.controllers.item_variant import create_variant

		attribute = frappe.get_doc(
			{
				"doctype": "Item Attribute",
				"attribute_name": f"_Price Attribute {uuid4().hex[:8]}",
				"item_attribute_values": [{"attribute_value": "Large", "abbr": "L"}],
			}
		).insert()
		template = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": f"_Price Template {uuid4().hex[:8]}",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"has_variants": 1,
				"attributes": [{"attribute": attribute.name}],
			}
		).insert()
		variant = create_variant(template.name, {attribute.name: "Large"})
		variant.standard_rate = 310
		variant.insert()
		variant = frappe.get_doc("Item", variant.name)
		load_selling_price(variant)
		self.assertEqual(variant.standard_rate, 310)
		variant.standard_rate = 350
		variant.save()
		self.assertEqual(price_context(variant).rate, 350)

	def test_item_price_write_permission_is_required(self):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": f"price-test-{uuid4().hex[:8]}@example.invalid",
				"first_name": "Price Permission Test",
				"send_welcome_email": 0,
				"roles": [{"role": "Stock Manager"}],
			}
		).insert()
		doc = self.load()
		doc.standard_rate = 900
		frappe.set_user(user.name)
		with self.assertRaises(frappe.PermissionError):
			doc.save()
