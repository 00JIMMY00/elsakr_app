frappe.query_reports["Stock Size Search"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{ fieldname: "search", label: __("Search item or size"), fieldtype: "Data" },
		{
			fieldname: "custom_size",
			label: __("Item Size"),
			fieldtype: "Link",
			options: "Item Size",
		},
		{ fieldname: "item_code", label: __("Item"), fieldtype: "Link", options: "Item" },
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
			get_query: () => ({
				filters: { company: frappe.query_report.get_filter_value("company"), is_group: 0 },
			}),
		},
	],
	formatter(value, row, column, data, default_formatter) {
		const formatted = default_formatter(value, row, column, data);
		if (column.fieldname === "actual_qty" && data) {
			return `<span class="text-${
				data.actual_qty < 0 ? "danger" : "success"
			}" style="font-weight:600">${formatted}</span>`;
		}
		return formatted;
	},
};
