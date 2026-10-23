"""Development-only Item Variants example retained for manual testing."""

import frappe
from erpnext.controllers.item_variant import create_variant
from frappe.desk.query_report import run

from elsakr_app.item_variants import SIZE_ATTRIBUTE

TEMPLATE = "DEMO-TYRE-MODEL-X"
SIZES = [
	("185/65 R14", "185-65-R14", 20, 2, 1200, 1500),
	("195/65 R15", "195-65-R15", 30, 3, 1500, 1900),
	("205/55 R16", "205-55-R16", 40, 4, 1800, 2300),
]


def create_variant_demo():
	if frappe.local.site != "elsakr-dev2.arab-erp.com":
		frappe.throw("Variant demo is restricted to elsakr-dev2.arab-erp.com")
	if frappe.db.exists("Item", TEMPLATE):
		frappe.throw("Variant demo already exists; records will not be reset")
	attribute = (
		frappe.get_doc("Item Attribute", SIZE_ATTRIBUTE)
		if frappe.db.exists("Item Attribute", SIZE_ATTRIBUTE)
		else frappe.new_doc("Item Attribute")
	)
	attribute.attribute_name = SIZE_ATTRIBUTE
	for size, abbr, *_ in SIZES:
		if not frappe.db.exists("Item Size", size):
			frappe.get_doc({"doctype": "Item Size", "size": size}).insert()
		if size not in [r.attribute_value for r in attribute.item_attribute_values]:
			attribute.append("item_attribute_values", {"attribute_value": size, "abbr": abbr})
	attribute.save()
	group = (
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": "DEMO Tyre Variants",
				"parent_item_group": "All Item Groups",
			}
		)
		.insert()
		.name
	)
	template = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": TEMPLATE,
			"item_name": "كاوتش تجريبي موديل X",
			"item_group": group,
			"stock_uom": "Nos",
			"is_stock_item": 1,
			"has_variants": 1,
			"variant_based_on": "Item Attribute",
			"attributes": [{"attribute": SIZE_ATTRIBUTE}],
		}
	).insert(set_name=TEMPLATE)
	variants = []
	for size, *_ in SIZES:
		variant = create_variant(template.name, {SIZE_ATTRIBUTE: size})
		variant.custom_size = "175/70 R13"
		variant.insert(set_name=variant.item_code)
		assert variant.custom_size == size and variant.variant_of == TEMPLATE, (
			variant.name,
			variant.custom_size,
			variant.variant_of,
			variant.has_variants,
			size,
			template.name,
		)
		variants.append(variant)
	company = frappe.get_doc("Company", frappe.get_all("Company", pluck="name")[0])
	warehouse = "DEMO Tyres Main - " + company.abbr
	documents = []
	for dt, time, party, qty_idx, rate_idx in [
		("Purchase Invoice", "15:00:00", {"supplier": "DEMO Tyres Supplier"}, 2, 4),
		("Sales Invoice", "16:00:00", {"customer": "DEMO Tyres Customer"}, 3, 5),
	]:
		doc = frappe.new_doc(dt)
		doc.update(
			{
				"company": company.name,
				"posting_date": "2026-10-23",
				"posting_time": time,
				"set_posting_time": 1,
				"update_stock": 1,
				"remarks": "DEMO Item Variants - retained for manual testing",
				**party,
			}
		)
		for variant, spec in zip(variants, SIZES, strict=True):
			doc.append(
				"items",
				{
					"item_code": variant.name,
					"qty": spec[qty_idx],
					"rate": spec[rate_idx],
					"warehouse": warehouse,
					"uom": "Nos",
					"conversion_factor": 1,
					"cost_center": company.cost_center,
				},
			)
		doc.insert()
		doc.submit()
		assert [r.custom_size for r in doc.items] == [s[0] for s in SIZES]
		documents.append({"doctype": dt, "name": doc.name})
	result = []
	for variant, spec in zip(variants, SIZES, strict=True):
		expected = spec[2] - spec[3]
		assert sum(frappe.get_all("Bin", filters={"item_code": variant.name}, pluck="actual_qty")) == expected
		for report in ["Stock Balance", "Stock Ledger"]:
			response = run(
				report,
				filters={
					"company": company.name,
					"from_date": "2026-10-23",
					"to_date": "2026-10-23",
					"item_group": group,
					"custom_size": spec[0],
					"ignore_closing_balance": 1,
				},
				ignore_prepared_report=True,
			)
			rows = [r for r in response["result"] if isinstance(r, dict) and r.get("item_code")]
			assert rows and {r["item_code"] for r in rows} == {variant.name}
			assert all(r["custom_size"] == spec[0] for r in rows)
			if report == "Stock Balance":
				assert sum(r["bal_qty"] for r in rows) == expected
		result.append({"item": variant.name, "size": spec[0], "qty": expected})
	assert not frappe.db.exists("Stock Ledger Entry", {"item_code": TEMPLATE})
	return {"template": TEMPLATE, "group": group, "items": result, "documents": documents}
