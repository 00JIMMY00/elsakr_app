import unittest

import frappe

from elsakr_app.currency_setup import setup_currency_display


class TestCurrencySetup(unittest.TestCase):
	def test_symbol_setup_is_repeatable_and_preserves_currency_codes(self):
		frappe.db.savepoint("currency_display")
		try:
			code = frappe.db.get_single_value("Global Defaults", "default_currency")
			companies = frappe.get_all("Company", fields=["name", "default_currency"])
			for _ in range(2):
				setup_currency_display()
				self.assertEqual(frappe.db.get_value("Currency", "EGP", "symbol"), "ج.م")
				self.assertEqual(frappe.defaults.get_global_default("hide_currency_symbol"), "No")
			self.assertEqual(frappe.db.get_single_value("Global Defaults", "default_currency"), code)
			self.assertEqual(frappe.get_all("Company", fields=["name", "default_currency"]), companies)
		finally:
			frappe.db.rollback(save_point="currency_display")
			frappe.clear_cache()
