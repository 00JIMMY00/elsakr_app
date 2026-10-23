import frappe
from frappe.core.doctype.report.report import Report
from frappe.utils.nestedset import get_descendants_of

STOCK_REPORTS = {"Stock Balance", "Stock Ledger"}


class ElsakrReport(Report):
	def execute_module(self, filters):
		if self.name not in STOCK_REPORTS:
			return super().execute_module(filters)

		result = self._execute_stock_report(filters)
		columns, data = result[:2]
		position = next(
			(index + 1 for index, column in enumerate(columns) if column.get("fieldname") == "item_name"),
			1,
		)
		columns.insert(
			position,
			{
				"label": "المقاس",
				"fieldname": "custom_size",
				"fieldtype": "Link",
				"options": "Item Size",
				"width": 130,
			},
		)
		item_codes = list({row.get("item_code") for row in data if row.get("item_code")})
		sizes = (
			dict(
				frappe.get_all(
					"Item", filters={"name": ["in", item_codes]}, fields=["name", "custom_size"], as_list=True
				)
			)
			if item_codes
			else {}
		)
		for row in data:
			row["custom_size"] = sizes.get(row.get("item_code"))
		return columns, data, *result[2:]

	def _execute_stock_report(self, filters):
		if not (filters or {}).get("custom_size"):
			return super().execute_module(filters)

		# Restrict items before ERPNext computes openings, balances and totals.
		# Copy filters so exports and prepared-report metadata retain the user's choices.
		filters = frappe._dict(filters.copy())
		item_filters = {"custom_size": filters.custom_size}
		if filters.item_code:
			item_codes = filters.item_code
			if isinstance(item_codes, str):
				item_codes = [item_codes]
			item_filters["name"] = ["in", item_codes]
		if filters.brand:
			item_filters["brand"] = filters.brand
		if filters.item_group:
			groups = get_descendants_of("Item Group", filters.item_group, ignore_permissions=True)
			item_filters["item_group"] = ["in", [filters.item_group, *groups]]

		items = frappe.get_all("Item", filters=item_filters, pluck="name")
		if not items:
			# An empty item list means "all items" in ERPNext, so return an empty report.
			if self.name == "Stock Balance":
				from erpnext.stock.report.stock_balance.stock_balance import StockBalanceReport

				return StockBalanceReport(filters).get_columns(), []
			from erpnext.stock.report.stock_ledger.stock_ledger import get_columns

			return get_columns(filters), []

		filters.item_code = items
		return super().execute_module(filters)
