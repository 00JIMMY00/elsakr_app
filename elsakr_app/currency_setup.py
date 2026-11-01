"""Maintain the site's Egyptian pound display symbol through migrations."""

import frappe


def setup_currency_display():
	currency = frappe.get_doc("Currency", "EGP")
	currency.symbol = "ج.م"
	currency.save(ignore_permissions=True)
	defaults = frappe.get_single("Global Defaults")
	defaults.hide_currency_symbol = "No"
	defaults.save(ignore_permissions=True)
	frappe.clear_cache()
