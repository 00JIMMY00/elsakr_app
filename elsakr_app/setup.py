from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

TRANSACTION_DOCTYPES = {
	"Quotation": "Quotation Item",
	"Sales Order": "Sales Order Item",
	"Delivery Note": "Delivery Note Item",
	"Sales Invoice": "Sales Invoice Item",
	"Supplier Quotation": "Supplier Quotation Item",
	"Purchase Order": "Purchase Order Item",
	"Purchase Receipt": "Purchase Receipt Item",
	"Purchase Invoice": "Purchase Invoice Item",
	"Material Request": "Material Request Item",
	"Stock Entry": "Stock Entry Detail",
	"Stock Reconciliation": "Stock Reconciliation Item",
	"Pick List": "Pick List Item",
}


def setup_item_size():
	create_custom_fields(
		{
			"Item": [
				{
					"fieldname": "custom_size",
					"label": "المقاس",
					"fieldtype": "Link",
					"options": "Item Size",
					"insert_after": "item_group",
					"in_standard_filter": 1,
				}
			]
		}
	)
	create_custom_fields(
		{
			doctype: [
				{
					"fieldname": "custom_size",
					"label": "المقاس",
					"fieldtype": "Link",
					"options": "Item Size",
					"insert_after": "item_code",
					"fetch_from": "item_code.custom_size",
					"read_only": 1,
					"in_list_view": 1,
					"columns": 1,
				}
			]
			for doctype in [*TRANSACTION_DOCTYPES.values(), "Packed Item"]
		}
	)
