"""Explicit, development-only tyre data; never called by install or migration."""

import frappe
from frappe.utils import flt

from elsakr_app.setup import TRANSACTION_DOCTYPES
from elsakr_app.transactions import set_item_sizes

DEMO_DATE = "2026-10-23"
SPECS = [
	("175-70-R13", "175/70 R13", 20, 3, 1000, 1300, 1),
	("185-65-R14", "185/65 R14", 24, 4, 1200, 1500, -1),
	("195-65-R15", "195/65 R15", 30, 5, 1500, 1900, 2),
	("205-55-R16", "205/55 R16", 16, 2, 1800, 2300, 0),
]


def create_tyre_demo():
	if frappe.local.site != "elsakr-dev2.arab-erp.com":
		frappe.throw("Tyre demo is restricted to elsakr-dev2.arab-erp.com")
	if frappe.db.exists("Item", "DEMO-TYRE-175-70-R13"):
		frappe.throw("Tyre demo already exists; existing data will not be duplicated or reset")

	company = frappe.get_doc("Company", frappe.get_all("Company", pluck="name")[0])
	root = frappe.get_all("Warehouse", filters={"company": company.name, "is_group": 1}, pluck="name")[0]
	warehouses = []
	for label in ["DEMO Tyres Main", "DEMO Tyres Branch"]:
		warehouses.append(
			frappe.get_doc(
				{
					"doctype": "Warehouse",
					"warehouse_name": label,
					"company": company.name,
					"parent_warehouse": root,
				}
			)
			.insert()
			.name
		)
	main, branch = warehouses
	group = (
		frappe.get_doc(
			{"doctype": "Item Group", "item_group_name": "DEMO Tyres", "parent_item_group": "All Item Groups"}
		)
		.insert()
		.name
	)
	customer = (
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "DEMO Tyres Customer",
				"customer_type": "Company",
				"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
				"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
			}
		)
		.insert()
		.name
	)
	supplier = (
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": "DEMO Tyres Supplier",
				"supplier_group": frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0],
				"supplier_type": "Company",
			}
		)
		.insert()
		.name
	)
	items = []
	for code, size, *_ in SPECS:
		if not frappe.db.exists("Item Size", size):
			frappe.get_doc({"doctype": "Item Size", "size": size}).insert()
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "DEMO-TYRE-" + code,
				"item_name": "كاوتش تجريبي " + size,
				"item_group": group,
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"custom_size": size,
				"valuation_method": "FIFO",
			}
		).insert()
		items.append(item.name)

	documents = []

	def submit(doctype, time, rows, **kwargs):
		doc = frappe.new_doc(doctype)
		doc.update(
			{
				"company": company.name,
				"posting_date": DEMO_DATE,
				"posting_time": time,
				"set_posting_time": 1,
				"remarks": "DEMO tyres: retained for manual size-filter testing",
				**kwargs,
			}
		)
		for row in rows:
			doc.append("items", row)
		doc.insert()
		doc.submit()
		assert all(
			row.custom_size == frappe.db.get_value("Item", row.item_code, "custom_size") for row in doc.items
		)
		documents.append({"doctype": doctype, "name": doc.name})
		return doc

	def rows(qty_index, rate_index):
		return [
			{
				"item_code": item,
				"qty": spec[qty_index],
				"rate": spec[rate_index],
				"warehouse": main,
				"uom": "Nos",
				"conversion_factor": 1,
				"cost_center": company.cost_center,
			}
			for item, spec in zip(items, SPECS, strict=True)
		]

	submit(
		"Purchase Invoice",
		"09:00:00",
		rows(2, 4),
		supplier=supplier,
		update_stock=1,
		bill_no="DEMO-TYRES-20261023",
		bill_date=DEMO_DATE,
	)
	submit("Sales Invoice", "10:00:00", rows(3, 5), customer=customer, update_stock=1)
	for purpose, time, source, target, qty in [
		("Material Receipt", "11:00:00", None, main, 3),
		("Material Transfer", "12:00:00", main, branch, 2),
		("Material Issue", "13:00:00", branch, None, 1),
	]:
		submit(
			"Stock Entry",
			time,
			[
				{
					"item_code": item,
					"qty": qty,
					"s_warehouse": source,
					"t_warehouse": target,
					"basic_rate": spec[4],
					"conversion_factor": 1,
					"cost_center": company.cost_center,
				}
				for item, spec in zip(items, SPECS, strict=True)
			],
			purpose=purpose,
			stock_entry_type=purpose,
		)

	submit(
		"Stock Reconciliation",
		"14:00:00",
		[
			{
				"item_code": item,
				"warehouse": main,
				"qty": spec[2] - spec[3] + 3 - 2 + spec[6],
				"valuation_rate": spec[4],
			}
			for item, spec in zip(items, SPECS, strict=True)
		],
		purpose="Stock Reconciliation",
		expense_account=company.stock_adjustment_account,
		cost_center=company.cost_center,
	)

	# Exercise the server synchronizer for every supported transaction table.
	for parent, child in TRANSACTION_DOCTYPES.items():
		doc = frappe.new_doc(parent)
		table = next(f.fieldname for f in doc.meta.get_table_fields() if f.options == child)
		row = doc.append(table, {"item_code": items[0], "custom_size": SPECS[1][1]})
		set_item_sizes(doc)
		assert row.custom_size == SPECS[0][1]
		row.item_code = items[1]
		set_item_sizes(doc)
		assert row.custom_size == SPECS[1][1]
		row.item_code = None
		set_item_sizes(doc)
		assert not row.custom_size

	from frappe.desk.query_report import run

	balances = []
	for item, spec in zip(items, SPECS, strict=True):
		expected = spec[2] - spec[3] + 3 - 1 + spec[6]
		for report_name in ["Stock Balance", "Stock Ledger"]:
			response = run(
				report_name,
				filters={
					"company": company.name,
					"from_date": DEMO_DATE,
					"to_date": DEMO_DATE,
					"custom_size": spec[1],
					"ignore_closing_balance": 1,
				},
				ignore_prepared_report=True,
			)
			data = [r for r in response["result"] if isinstance(r, dict) and r.get("item_code")]
			assert data and {r["item_code"] for r in data} == {item}, report_name
			if report_name == "Stock Balance":
				assert flt(sum(r["bal_qty"] for r in data)) == expected
		bin_qty = sum(frappe.get_all("Bin", filters={"item_code": item}, pluck="actual_qty"))
		assert flt(bin_qty) == expected
		balances.append({"item": item, "size": spec[1], "qty": expected})
	return {
		"date": DEMO_DATE,
		"warehouses": warehouses,
		"documents": documents,
		"items": balances,
		"checks": "12 transaction types; 8 report runs; Bin quantities; submitted-row sizes",
	}
