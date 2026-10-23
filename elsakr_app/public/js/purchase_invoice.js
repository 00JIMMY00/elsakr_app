frappe.ui.form.on("Purchase Invoice", {
	setup(frm) {
		// ERPNext's controller reveals the series after normal form handlers run.
		const native_refresh = frm.cscript.refresh;
		frm.cscript.refresh = async function (...args) {
			await native_refresh.apply(this, args);
			frm.toggle_display("naming_series", false);
		};
		frm.set_df_property("payments_section", "collapsible_depends_on", "eval:doc.is_paid");
		// Start each form with the requested layout, including users with older grid settings.
		// Keep this in memory: Configure Columns can still adjust the current session.
		const settings = frappe.model.user_settings[frm.doctype] || {};
		settings.GridView = {
			...settings.GridView,
			"Purchase Invoice Item": [
				{ fieldname: "item_code", columns: 2 },
				{ fieldname: "custom_size", columns: 1 },
				{ fieldname: "qty", columns: 1 },
				{ fieldname: "rate", columns: 2 },
				{ fieldname: "amount", columns: 2 },
			],
		};
		frappe.model.user_settings[frm.doctype] = settings;
	},
	refresh(frm) {
		position_purchase_payments(frm);
	},
	is_paid(frm) {
		position_purchase_payments(frm);
		if (frm.doc.is_paid && frm.doc.company && !frm.doc.docstatus) {
			frm.scroll_to_field("mode_of_payment", false);
		}
	},
});

function position_purchase_payments(frm) {
	const section = frm.fields_dict.mode_of_payment.section;
	const details = frm.fields_dict.is_paid.tab;
	section.wrapper.insertAfter(frm.fields_dict.is_paid.section.wrapper);
	section.parent = details.wrapper;
	section.tab = details;
	section.fields_list.forEach((field) => details.add_field(field));
	section.wrapper.css({ width: "100%", "max-width": "760px" });
}

frappe.ui.form.on("Purchase Invoice", {
	setup(frm) {
		const field = frm.fields_dict.custom_supplier_entry;
		field.df.formatter = (value) => {
			const label = value || frm.doc.supplier_name || frm.doc.supplier || "";
			if (!frm.doc.supplier) return frappe.utils.escape_html(label);
			return $("<a>")
				.attr("href", frappe.utils.get_form_link("Supplier", frm.doc.supplier))
				.text(label)[0].outerHTML;
		};
		// Retain text entry on drafts and provide the native-style open link beside it.
		field.$supplier_link = $('<a class="btn-open no-decoration">')
			.attr("title", __("Open Supplier"))
			.attr("aria-label", __("Open Supplier"))
			.html(frappe.utils.icon("external-link", "sm"));
		$("<span class='link-btn'>").append(field.$supplier_link).appendTo(field.input_area);
		field.df.ignore_validation = true;
		field.get_query = () => ({ query: "elsakr_app.invoice_supplier.search_suppliers" });
		const validate_party = frm.cscript.validate_company_and_party;
		frm.cscript.validate_company_and_party = function (...args) {
			if (frm.doc.company && !frm.doc.supplier && frm.doc.custom_supplier_entry?.trim()) {
				return true;
			}
			return validate_party.apply(this, args);
		};
	},
	onload(frm) {
		if (frm.doc.supplier && !frm.doc.custom_supplier_entry) {
			return load_invoice_supplier(frm);
		}
	},
	refresh(frm) {
		const field = frm.fields_dict.custom_supplier_entry;
		update_invoice_supplier_link(frm);
		if (field.awesomplete) {
			field.awesomplete.filter = () => true;
			// Supplier labels must be rendered as text.
			field.awesomplete.item = (item) => {
				const row = field.get_data().find((d) => d.value === item.value) || item;
				return $("<li>").append(
					$("<strong>").text(row.label),
					$("<div>").text(row.description || "")
				)[0];
			};
		}
		frm.toggle_display("supplier", false);
		frm.toggle_reqd("supplier", false);
		frm.toggle_reqd("custom_supplier_entry", true);
	},
	before_save(frm) {
		// ERPNext fills these from the new Supplier during server validation.
		if (!frm.doc.supplier && frm.doc.custom_supplier_entry?.trim()) {
			frm.toggle_reqd("credit_to", false);
			frm.toggle_reqd("due_date", false);
		}
	},
	async custom_supplier_entry(frm) {
		if (frm._setting_inline_supplier) return;
		const value = frm.doc.custom_supplier_entry;
		const selected = frm.fields_dict.custom_supplier_entry
			.get_data()
			.find((d) => d.value === value);
		if (selected) return select_invoice_supplier(frm, selected.value);
		if (frm.doc.supplier && value !== frm.doc.supplier_name) {
			await frm.set_value("supplier", "");
			update_invoice_supplier_link(frm);
			await frm.set_value({
				custom_supplier_phone: "",
				custom_supplier_address: "",
				contact_person: "",
				contact_mobile: "",
				supplier_address: "",
				address_display: "",
			});
		}
	},
	supplier(frm) {
		update_invoice_supplier_link(frm);
		if (frm.doc.supplier && !frm._setting_inline_supplier) return load_invoice_supplier(frm);
	},
});

function update_invoice_supplier_link(frm) {
	const field = frm.fields_dict.custom_supplier_entry;
	field.$supplier_link
		.attr(
			"href",
			frm.doc.supplier ? frappe.utils.get_form_link("Supplier", frm.doc.supplier) : null
		)
		.toggle(!!frm.doc.supplier);
	if (field.disp_area) field.set_disp_area(frm.doc.custom_supplier_entry);
}

async function select_invoice_supplier(frm, supplier) {
	if (frm._setting_inline_supplier) return;
	frm._setting_inline_supplier = true;
	try {
		await frm.set_value("supplier", supplier);
		await load_invoice_supplier(frm);
	} finally {
		frm._setting_inline_supplier = false;
	}
}

async function load_invoice_supplier(frm) {
	const supplier = frm.doc.supplier;
	if (!supplier) return;
	const { message } = await frappe.call({
		method: "elsakr_app.invoice_supplier.supplier_details",
		args: { supplier },
	});
	if (frm.doc.supplier !== supplier) return;
	if (frm.doc.docstatus) {
		// Show details on older submitted invoices without marking them as modified.
		Object.assign(frm.doc, {
			custom_supplier_entry: message.supplier_name,
			custom_supplier_phone: frm.doc.contact_mobile || message.phone,
			custom_supplier_address: message.address,
		});
		frm.refresh_fields([
			"custom_supplier_entry",
			"custom_supplier_phone",
			"custom_supplier_address",
		]);
		return;
	}
	const previous = frm._setting_inline_supplier;
	frm._setting_inline_supplier = true;
	try {
		frm.fields_dict.custom_supplier_entry.set_data([]);
		await frm.set_value({
			custom_supplier_entry: message.supplier_name,
			custom_supplier_phone: message.phone,
			custom_supplier_address: message.address,
		});
	} finally {
		frm._setting_inline_supplier = previous;
	}
}

frappe.ui.form.on("Purchase Invoice", {
	refresh: update_supplier_unpaid_card,
	supplier: update_supplier_unpaid_card,
	company: update_supplier_unpaid_card,
});

async function update_supplier_unpaid_card(frm) {
	if (!frm.$supplier_unpaid_card) {
		frm.$supplier_unpaid_card = $(
			'<div class="elsakr-supplier-unpaid-card" role="status" aria-live="polite">'
		)
			.css({
				display: "none",
				padding: "16px 20px",
				margin: "0 0 16px",
				background: "var(--orange-50, #fff9f5)",
				color: "var(--orange-700, #9a3412)",
				border: "1px solid var(--orange-200, #fce6d5)",
				"border-inline-start": "4px solid var(--orange-500, #e86c13)",
				"border-radius": "12px",
			})
			.append(
				$('<div class="unpaid-title">')
					.css({ "font-weight": 600 })
					.text(__("Unpaid balance owed to supplier")),
				$('<div class="unpaid-amount">').css({
					"font-size": "24px",
					"font-weight": 700,
					"margin-top": "4px",
				}),
				$('<div class="unpaid-supplier">').css({
					"font-size": "12px",
					"margin-top": "4px",
				})
			);
	}
	// Reuse one card and immediately clear stale figures on supplier/company changes.
	frm.$supplier_unpaid_card
		.hide()
		.insertBefore(frm.fields_dict.custom_supplier_entry.section.wrapper);
	const request = (frm._unpaid_request || 0) + 1;
	frm._unpaid_request = request;
	const { supplier, company } = frm.doc;
	if (!supplier || !company || !frappe.model.can_read("GL Entry")) return;
	try {
		const { message } = await frappe.call({
			method: "elsakr_app.supplier_balance.get_supplier_unpaid_balance",
			args: { supplier, company },
		});
		if (
			request !== frm._unpaid_request ||
			supplier !== frm.doc.supplier ||
			company !== frm.doc.company
		)
			return;
		if (!message || message.amount <= 0) return;
		frm.$supplier_unpaid_card
			.find(".unpaid-amount")
			.text(format_currency(message.amount, message.currency, message.precision));
		frm.$supplier_unpaid_card
			.find(".unpaid-supplier")
			.text(`${message.supplier_name || supplier} · ${company}`);
		frm.$supplier_unpaid_card.show();
	} catch {
		// An unavailable balance must never leave a previous supplier's figure visible.
		if (request === frm._unpaid_request) frm.$supplier_unpaid_card.hide();
	}
}
