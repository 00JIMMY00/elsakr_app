"""App-owned snapshot of the simplified development Customer form."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

CUSTOMER_HIDDEN = (
	"salutation",
	"mobile_no",
	"naming_series",
	"territory",
	"gender",
	"lead_name",
	"opportunity_name",
	"prospect_name",
	"account_manager",
	"image",
	"defaults_tab",
	"internal_customer_section",
	"more_info",
	"first_name",
	"last_name",
	"tax_tab",
	"sales_team_tab",
	"portal_users_tab",
	"contact_and_address_tab",
)


def setup_customer_flow():
	for fieldname in CUSTOMER_HIDDEN:
		field = frappe.get_meta("Customer").get_field(fieldname)
		frappe.db.set_value("DocField", field.name, "hidden", 1, update_modified=False)
		make_property_setter("Customer", fieldname, "hidden", 1, "Check")
	make_property_setter("Customer", "customer_type", "default", "Individual", "Data")
	make_property_setter("Customer", "naming_series", "reqd", 0, "Check")
	create_custom_fields(
		{
			"Customer": [
				{
					"fieldname": "custom_phone",
					"label": "Phone",
					"fieldtype": "Data",
					"insert_after": "customer_name",
					"no_copy": 1,
				}
			],
			"Sales Invoice": [
				{
					"fieldname": "custom_customer_entry",
					"label": "Customer Name",
					"fieldtype": "Autocomplete",
					"insert_after": "customer",
					"ignore_validation": 1,
					"description": "Search by name or phone, or type a new customer name.",
				},
				{
					"fieldname": "custom_customer_phone",
					"label": "Phone",
					"fieldtype": "Data",
					"insert_after": "custom_customer_entry",
				},
				{
					"fieldname": "custom_customer_address",
					"label": "Address",
					"fieldtype": "Small Text",
					"insert_after": "custom_customer_phone",
				},
			],
			"Address": [
				{
					"fieldname": "custom_freeform_address",
					"label": "Freeform invoice address",
					"fieldtype": "Check",
					"hidden": 1,
					"insert_after": "city",
					"default": "0",
				}
			],
		}
	)
	# Only invoice-created freeform addresses may omit a separate city.
	make_property_setter("Address", "city", "reqd", 0, "Check")
	make_property_setter(
		"Address", "city", "mandatory_depends_on", "eval:!doc.custom_freeform_address", "Data"
	)
	frappe.clear_cache()


def validate_address_city(doc, method=None):
	if not doc.city and not doc.get("custom_freeform_address"):
		frappe.throw(frappe._("City/Town is required."), frappe.MandatoryError)
