"""Use native inline editing for the Elsakr expense rows."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def setup_expense_entry_grid():
	if not frappe.db.exists("DocType", "Expense Entry Detail"):
		return
	make_property_setter("Expense Entry Detail", None, "editable_grid", 1, "Check", for_doctype=True)
	make_property_setter("Expense Entry", "expenses", "in_place_edit", 1, "Check")
	for doctype in ("Expense Entry Detail", "Expense Entry"):
		frappe.clear_cache(doctype=doctype)
