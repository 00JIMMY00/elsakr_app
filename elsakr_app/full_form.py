"""Open commonly used DocTypes in the full form when creating a record."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import cint

FULL_FORM_DOCTYPES = (
	"Item",
	"Customer",
	"Supplier",
	"Sales Invoice",
	"Material Request",
	"Mode of Payment",
)


def setup_full_form():
	for doctype in FULL_FORM_DOCTYPES:
		current = frappe.db.get_value(
			"Property Setter",
			{"doc_type": doctype, "doctype_or_field": "DocType", "property": "quick_entry"},
			"value",
		)
		if current is None or cint(current) != 0:
			make_property_setter(doctype, None, "quick_entry", 0, "Check", for_doctype=True)
		frappe.clear_cache(doctype=doctype)
