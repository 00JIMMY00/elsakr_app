"""Current physical stock by item and warehouse, using current Item sizes."""

import frappe
from frappe.desk.reportview import get_match_cond

from elsakr_app.report_utils import column, report_company


def execute(filters=None):
	filters = frappe._dict(filters or {})
	for doctype in ("Stock Ledger Entry", "Item", "Warehouse", "Company"):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	columns = [
		column("item_code", "Item", "Link", "Item", 190),
		column("item_name", "Item Name", width=240),
		column("custom_size", "Item Size", "Link", "Item Size"),
		column("warehouse", "Warehouse", "Link", "Warehouse", 220),
		column("actual_qty", "Stock Quantity", "Float"),
		column("stock_uom", "Stock UOM", "Link", "UOM", 100),
	]
	conditions = ["`tabWarehouse`.company = %(company)s", "bin.actual_qty != 0"]
	params = {"company": company.name}
	for key, field in (
		("custom_size", "`tabItem`.custom_size"),
		("item_code", "`tabItem`.name"),
		("warehouse", "`tabWarehouse`.name"),
	):
		if filters.get(key):
			conditions.append(f"{field} = %({key})s")
			params[key] = filters[key]
	if filters.search:
		conditions.append(
			"(`tabItem`.name LIKE %(search)s OR `tabItem`.item_name LIKE %(search)s OR `tabItem`.custom_size LIKE %(search)s)"
		)
		params["search"] = f"%{filters.search}%"
	data = frappe.db.sql(
		f"""SELECT bin.item_code, `tabItem`.item_name, `tabItem`.custom_size,
			bin.warehouse, bin.actual_qty, `tabItem`.stock_uom
		FROM `tabBin` bin
		JOIN `tabItem` ON `tabItem`.name = bin.item_code
		JOIN `tabWarehouse` ON `tabWarehouse`.name = bin.warehouse
		WHERE {" AND ".join(conditions)}
			{get_match_cond("Item")} {get_match_cond("Warehouse")}
		ORDER BY `tabItem`.custom_size, `tabItem`.item_name, bin.item_code, bin.warehouse""",
		params,
		as_dict=True,
	)
	# Quantities in different stock units must not be added into a grand total.
	return columns, data
