for (const report_name of ["Stock Balance", "Stock Ledger"]) {
	const settings = frappe.query_reports[report_name];
	if (settings && !settings.filters.some((filter) => filter.fieldname === "custom_size")) {
		const item_index = settings.filters.findIndex((filter) => filter.fieldname === "item_code");
		settings.filters.splice(item_index + 1, 0, {
			fieldname: "custom_size",
			label: __("المقاس"),
			fieldtype: "Link",
			options: "Item Size",
		});
	}
}
