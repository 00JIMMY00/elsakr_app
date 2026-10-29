frappe.query_reports["Daily Sales Summary"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options:
				"\nPaid\nUnpaid\nPartly Paid\nOverdue\nReturn\nCredit Note Issued\nConsolidated",
		},
		{
			fieldname: "invoice_type",
			label: __("Invoice Type"),
			fieldtype: "Select",
			options: [
				"",
				{ label: __("Sales"), value: "Sales" },
				{ label: __("Returns"), value: "Returns" },
			],
		},
	],
	onload(report) {
		report.page.add_inner_button(__("Today"), () => {
			const today = frappe.datetime.get_today();
			report.set_filter_value({ from_date: today, to_date: today });
		});
	},
	formatter(value, row, column, data, default_formatter) {
		const formatted = default_formatter(value, row, column, data);
		if (!data) return formatted;
		if (column.fieldname === "status") {
			const color = data.is_return ? "blue" : data.outstanding > 0 ? "orange" : "green";
			return `<span class="indicator-pill ${color}">${frappe.utils.escape_html(
				__(value || "")
			)}</span>`;
		}
		if (column.fieldname === "base_grand_total" || column.fieldname === "outstanding") {
			const color =
				data[column.fieldname] < 0
					? "danger"
					: column.fieldname === "outstanding" && data.outstanding > 0
					? "warning"
					: "success";
			return `<span class="text-${color}" style="font-weight:600">${formatted}</span>`;
		}
		return formatted;
	},
};
