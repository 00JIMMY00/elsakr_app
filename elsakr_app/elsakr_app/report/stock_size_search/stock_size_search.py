"""Current physical stock by item and warehouse, using current Item sizes."""

import frappe
from frappe.desk.reportview import get_match_cond
from frappe.utils import getdate, nowdate

from elsakr_app.report_utils import column, report_company


def execute(filters=None):
	filters = frappe._dict(filters or {})
	for doctype in ("Stock Ledger Entry", "Item", "Warehouse", "Company"):
		frappe.has_permission(doctype, "read", throw=True)
	company = report_company(filters.company)
	columns = [
		column("item_name", "Item Name", width=240),
		column("custom_size", "Item Size", "Link", "Item Size"),
		column("warehouse", "Warehouse", "Link", "Warehouse", 220),
		column("actual_qty", "Stock Quantity", "Float"),
		column("stock_uom", "Stock UOM", "Link", "UOM", 100),
		column("buying_price", "Purchasing Price (MA)", "Currency", "buying_currency", 240),
		column("selling_price", "Selling Price", "Currency", "selling_currency", 220),
	]
	conditions = ["`tabWarehouse`.company = %(company)s", "bin.actual_qty != 0"]
	params = {"company": company.name, "currency": company.default_currency}
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
			bin.warehouse, bin.actual_qty, `tabItem`.stock_uom,
			bin.valuation_rate AS buying_price, %(currency)s AS buying_currency
		FROM `tabBin` bin
		JOIN `tabItem` ON `tabItem`.name = bin.item_code
		JOIN `tabWarehouse` ON `tabWarehouse`.name = bin.warehouse
		WHERE {" AND ".join(conditions)}
			{get_match_cond("Item")} {get_match_cond("Warehouse")}
		ORDER BY `tabItem`.custom_size, `tabItem`.item_name, bin.item_code, bin.warehouse""",
		params,
		as_dict=True,
	)
	add_prices(data, filters)
	# Quantities in different stock units must not be added into a grand total.
	return columns, data


def add_prices(data, filters):
	"""Read permitted general selling prices once, rather than once per Bin."""
	if (
		not data
		or not frappe.has_permission("Item Price", "read")
		or not frappe.has_permission("Price List", "read")
	):
		return
	items = {row.item_code: row.stock_uom for row in data}
	today = getdate(nowdate())
	price_list = (
		filters.selling_price_list
		or frappe.db.get_single_value("Selling Settings", "selling_price_list")
		or "Standard Selling"
	)
	lists = frappe.get_list(
		"Price List",
		filters={"name": price_list, "enabled": 1, "selling": 1},
		fields=["name", "currency"],
	)
	if not lists:
		return
	prices = frappe.get_list(
		"Item Price",
		filters={"item_code": ["in", list(items)], "price_list": price_list},
		fields=[
			"item_code",
			"price_list_rate",
			"currency",
			"uom",
			"customer",
			"supplier",
			"batch_no",
			"packing_unit",
			"valid_from",
			"valid_upto",
		],
		limit_page_length=0,
	)
	applicable = {}
	for price in prices:
		if (
			price.customer
			or price.supplier
			or price.batch_no
			or (price.packing_unit or 0) > 1
			or price.uom not in (None, "", items[price.item_code])
			or (price.valid_from and getdate(price.valid_from) > today)
			or (price.valid_upto and getdate(price.valid_upto) < today)
			or price.currency != lists[0].currency
		):
			continue
		applicable.setdefault(price.item_code, []).append(price)
	for row in data:
		matches = applicable.get(row.item_code, [])
		if len(matches) == 1:
			row.selling_price = matches[0].price_list_rate
			row.selling_currency = matches[0].currency
