"""Install the app-managed, self-contained customer print formats."""

from pathlib import Path

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

FORMATS = {"Quotation": "Elsakr Quotation", "Sales Invoice": "Elsakr Sales Invoice"}


def get_format_values(doctype):
	root = Path(__file__).parent / "templates" / "print_formats"
	return {
		"doc_type": doctype,
		"module": "Elsakr App",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "Jinja",
		"print_format_builder": 0,
		"disabled": 0,
		"default_print_language": "ar",
		"html": (root / "sales_document.html").read_text(),
		"css": (root / "sales_document.css").read_text(),
		"margin_top": 12,
		"margin_bottom": 12,
		"margin_left": 12,
		"margin_right": 12,
	}


def setup_print_formats():
	for doctype, name in FORMATS.items():
		values = get_format_values(doctype)
		if frappe.db.exists("Print Format", name):
			doc = frappe.get_doc("Print Format", name)
			doc.update(values)
			doc.save()
		else:
			frappe.get_doc({"doctype": "Print Format", "name": name, **values}).insert()
		make_property_setter(doctype, None, "default_print_format", name, "Data", for_doctype=True)
