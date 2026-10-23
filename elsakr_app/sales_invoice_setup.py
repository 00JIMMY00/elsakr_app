"""App defaults for new Sales Invoices."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def setup_sales_invoice_defaults():
	make_property_setter("Sales Invoice", "is_pos", "default", "1", "Data")
	frappe.clear_cache(doctype="Sales Invoice")
