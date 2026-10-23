import frappe

SIZE_ATTRIBUTE = "Item Size"
SIZE_ATTRIBUTES = {SIZE_ATTRIBUTE, "Size", "المقاس"}


def set_variant_size(doc, method=None):
	"""Derive variant names and sizes from full attribute values."""
	attributes = list(doc.attributes or [])
	size_attributes = [row for row in attributes if row.attribute in SIZE_ATTRIBUTES]
	if doc.has_variants:
		if size_attributes:
			doc.custom_size = None
		return
	if not doc.variant_of or not attributes:
		return

	values = [row.attribute_value for row in attributes if row.attribute_value]
	template_name = frappe.get_cached_value("Item", doc.variant_of, "item_name")
	if values:
		doc.item_name = "-".join([template_name or doc.variant_of, *values])

	# A single attribute is unambiguous even when named Colour or another label.
	# For multiple attributes only a recognized size attribute defines size.
	if not size_attributes and len(attributes) == 1:
		size_attributes = attributes
	if not size_attributes:
		return
	if len(size_attributes) > 1:
		frappe.throw(frappe._("Use only one size attribute on an Item variant."))
	size = size_attributes[0].attribute_value
	if not size:
		frappe.throw(frappe._("Please select a value for the size attribute."))
	if not frappe.db.exists("Item Size", size):
		frappe.get_doc({"doctype": "Item Size", "size": size}).insert(ignore_if_duplicate=True)
	doc.custom_size = size
