import frappe


def set_item_sizes(doc, method=None):
	"""Keep transaction rows consistent with their selected Item, including API saves."""
	rows = [
		row
		for field in doc.meta.get_table_fields()
		for row in doc.get(field.fieldname) or []
		if row.meta.has_field("custom_size") and row.meta.has_field("item_code")
	]
	item_codes = {row.item_code for row in rows if row.item_code}
	sizes = (
		dict(
			frappe.get_all(
				"Item",
				filters={"name": ["in", list(item_codes)]},
				fields=["name", "custom_size"],
				as_list=True,
			)
		)
		if item_codes
		else {}
	)
	for row in rows:
		row.custom_size = sizes.get(row.item_code)
