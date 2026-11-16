frappe.query_reports["Simple Payable Summary"] = {
	tree: true,
	initial_depth: 1,
	filters: [
		{
			fieldname: "company",
			label: __("الشركة"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "report_date",
			label: __("التاريخ"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{ fieldname: "supplier", label: __("المورد"), fieldtype: "Link", options: "Supplier" },
		{
			fieldname: "group_by",
			label: __("تجميع حسب"),
			fieldtype: "Select",
			options: [
				{ value: "Supplier", label: "المورد" },
				{ value: "Invoice", label: "الفاتورة" },
				{ value: "Supplier Group", label: "مجموعة الموردين" },
				{ value: "Country", label: "الدولة" },
			],
			default: "Supplier",
			reqd: 1,
		},
		{ fieldname: "overdue_only", label: __("المتأخر فقط"), fieldtype: "Check" },
	],
	onload(report) {
		report.page.set_title("ملخص استحقاقات الموردين");
		if (!document.getElementById("elsakr-payable-style")) {
			$(`<style id="elsakr-payable-style">
				body[data-route="query-report/Simple Payable Summary"] .report-summary {
					display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px;
				}
				body[data-route="query-report/Simple Payable Summary"] .summary-item {
					min-width: 0; max-width: none; margin: 0; height: 64px;
				}
				body[data-route="query-report/Simple Payable Summary"] .summary-value.orange {
					color: var(--orange-600, #d97706);
				}
				@media (max-width: 767px) {
					body[data-route="query-report/Simple Payable Summary"] .report-summary {
						grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 12px;
						padding: 12px; gap: 8px;
					}
					body[data-route="query-report/Simple Payable Summary"] .summary-item:last-child {
						grid-column: 1 / -1;
					}
					body[data-route="query-report/Simple Payable Summary"] .summary-value {
						font-size: 17px;
					}
					body[data-route="query-report/Simple Payable Summary"] .summary-label {
						font-size: 11px;
					}
				}
			</style>`).appendTo(document.head);
		}
		if (!frappe.model.can_create("Payment Entry")) return;
		report.page.add_inner_button(__("سداد الفواتير المحددة"), () => {
			const checked = report.datatable ? report.get_checked_items() : [];
			const names = [
				...new Set(
					checked.flatMap((row) => row.invoice_names || [row.invoice]).filter(Boolean)
				),
			];
			if (!names.length) {
				frappe.msgprint(__("حدد فاتورة أو أكثر للمورد نفسه."));
				return;
			}
			this.pay(report, names);
		});
		$(report.page.wrapper)
			.off("click.elsakr_payable", "[data-elsakr-supplier-pay]")
			.on("click.elsakr_payable", "[data-elsakr-supplier-pay]", (event) => {
				event.preventDefault();
				event.stopPropagation();
				this.pay(
					report,
					JSON.parse(decodeURIComponent(event.currentTarget.dataset.elsakrSupplierPay))
				);
			});
	},
	get_datatable_options(options) {
		return {
			...options,
			direction: "rtl",
			checkboxColumn: frappe.model.can_create("Payment Entry"),
		};
	},
	async pay(report, invoices) {
		if (report.elsakr_payment_pending) return;
		report.elsakr_payment_pending = true;
		try {
			// frappe.call displays server validation errors; keep rejected requests
			// from becoming unhandled promises in delegated button handlers.
			const response = await frappe
				.call({
					method: "elsakr_app.payable_payments.make_payment_entry",
					args: { invoices },
					freeze: true,
					freeze_message: __("جارٍ تجهيز قيد الدفع"),
				})
				.catch(() => null);
			const message = response?.message;
			if (message) {
				await frappe.model.with_doctype("Payment Entry");
				const doc = frappe.model.sync(message)[0];
				frappe.set_route("Form", "Payment Entry", doc.name);
			}
		} finally {
			report.elsakr_payment_pending = false;
		}
	},
	formatter(value, row, column, data, default_formatter) {
		if (!data) return default_formatter(value, row, column, data);
		if (column.fieldname === "payment") {
			if (!frappe.model.can_create("Payment Entry") || (data.is_group && !data.supplier))
				return "";
			const names = data.invoice_names || [data.invoice];
			const encoded = frappe.utils.escape_html(encodeURIComponent(JSON.stringify(names)));
			return `<button type="button" class="btn btn-xs btn-primary" data-elsakr-supplier-pay="${encoded}">${
				data.is_group ? __("سداد للمورد") : __("سداد")
			}</button>`;
		}
		value = default_formatter(value, row, column, data);
		if (data.is_group) return `<strong>${value || ""}</strong>`;
		if (["outstanding", "days_overdue", "status"].includes(column.fieldname)) {
			return `<span class="${
				data.days_overdue > 0 ? "text-danger" : "text-warning"
			}">${value}</span>`;
		}
		if (column.fieldname === "paid") return `<span class="text-success">${value}</span>`;
		return value;
	},
};
