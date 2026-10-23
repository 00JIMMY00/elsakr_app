"""Keep the requested Sales Invoice Hidden flags consistent in both editors."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.naming import get_default_naming_series
from frappe.utils import cint

# Explicit snapshot of the development site's Customize Form Hidden settings.
# Other properties, including mandatory and print settings, are left intact.
HIDDEN_FIELDS = {
	"accounting_dimensions_section": 1,
	"additional_discount_account": 1,
	"company_tax_id": 1,
	"is_debit_note": 1,
	"more_info_tab": 1,
	"naming_series": 1,
	"payments_tab": 1,
	"pricing_rule_details": 1,
	"sec_tax_breakup": 1,
	"taxes_section": 1,
	"time_sheet_list": 1,
	"base_rounded_total": 0,
	"in_words": 0,
	"rounded_total": 0,
	"scan_barcode": 0,
	"tax_id": 0,
}


def setup_sales_invoice_visibility():
	doctype = "Sales Invoice"
	# A mandatory hidden series needs a default; retain the site's current choice.
	if not frappe.get_meta(doctype).get_field("naming_series").default:
		make_property_setter(doctype, "naming_series", "default", get_default_naming_series(doctype), "Data")
	fields = {field.fieldname: field for field in frappe.get_doc("DocType", doctype).fields}
	for fieldname, hidden in HIDDEN_FIELDS.items():
		field = fields[fieldname]
		# Update the database DocField without saving/exporting ERPNext's DocType.
		if cint(field.hidden) != hidden:
			frappe.db.set_value("DocField", field.name, "hidden", hidden, update_modified=False)
		current = frappe.db.get_value(
			"Property Setter",
			{"doc_type": doctype, "field_name": fieldname, "property": "hidden"},
			"value",
		)
		if current is None or cint(current) != hidden:
			make_property_setter(doctype, fieldname, "hidden", hidden, "Check")
	frappe.clear_cache(doctype=doctype)
