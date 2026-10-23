"""Purchasing counterparts of the simplified Customer and Sales Invoice forms."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.naming import get_default_naming_series

SUPPLIER_HIDDEN = (
	"naming_series",
	"mobile_no",
	"image",
	"is_transporter",
	"defaults_section",
	"internal_supplier_section",
	"column_break2",
	"tax_tab",
	"portal_users_tab",
	"contact_and_address_tab",
)
PURCHASE_INVOICE_HIDDEN = (
	"naming_series",
	"accounting_dimensions_section",
	"more_info_tab",
	"payments_tab",
	"pricing_rule_details",
	"sec_tax_breakup",
	"taxes_section",
	"section_break_51",
)


def setup_supplier_flow():
	for doctype in ("Supplier", "Purchase Invoice"):
		if not frappe.get_meta(doctype).get_field("naming_series").default:
			make_property_setter(
				doctype, "naming_series", "default", get_default_naming_series(doctype), "Data"
			)
	for doctype, fieldnames in (("Supplier", SUPPLIER_HIDDEN), ("Purchase Invoice", PURCHASE_INVOICE_HIDDEN)):
		fields = {field.fieldname: field for field in frappe.get_doc("DocType", doctype).fields}
		for fieldname in fieldnames:
			frappe.db.set_value("DocField", fields[fieldname].name, "hidden", 1, update_modified=False)
			make_property_setter(doctype, fieldname, "hidden", 1, "Check")
	make_property_setter("Supplier", "supplier_type", "default", "Individual", "Data")
	create_custom_fields(
		{
			"Supplier": [
				{
					"fieldname": "custom_phone",
					"label": "Phone",
					"fieldtype": "Data",
					"insert_after": "supplier_name",
					"no_copy": 1,
				}
			],
			"Purchase Invoice": [
				{
					"fieldname": "custom_supplier_entry",
					"label": "Supplier Name",
					"fieldtype": "Autocomplete",
					"insert_after": "supplier",
					"description": "Search by name or phone, or type a new supplier name.",
				},
				{
					"fieldname": "custom_supplier_phone",
					"label": "Phone",
					"fieldtype": "Data",
					"insert_after": "custom_supplier_entry",
				},
				{
					"fieldname": "custom_supplier_address",
					"label": "Address",
					"fieldtype": "Small Text",
					"insert_after": "custom_supplier_phone",
				},
			],
		}
	)
	frappe.clear_cache()
