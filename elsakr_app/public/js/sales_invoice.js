frappe.ui.form.on("Sales Invoice", {
	setup(frm) {
		// ERPNext's controller reveals the series after normal form handlers run.
		const native_refresh = frm.cscript.refresh;
		frm.cscript.refresh = async function (...args) {
			await native_refresh.apply(this, args);
			frm.toggle_display("naming_series", false);
		};
		// A true collapsible dependency expands the section in Frappe v15.
		frm.set_df_property("payments_section", "collapsible_depends_on", "eval:doc.is_pos");
		// Start each form with the requested layout, including users with older grid settings.
		// Keep this in memory: Configure Columns can still adjust the current session.
		const settings = frappe.model.user_settings[frm.doctype] || {};
		settings.GridView = {
			...settings.GridView,
			"Sales Invoice Item": [
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
		position_pos_payments(frm);
	},
	is_pos(frm) {
		position_pos_payments(frm);
	},
});

function position_pos_payments(frm) {
	const payment_field = frm.fields_dict.payments;
	const section = payment_field.section;
	const details = frm.fields_dict.is_pos.tab;
	const customer_section = frm.fields_dict.is_pos.section;

	// Move the existing section, retaining the native editable grid and handlers.
	section.wrapper.insertAfter(customer_section.wrapper);
	section.parent = details.wrapper;
	section.tab = details;
	section.fields_list.forEach((field) => details.add_field(field));
	payment_field.$wrapper.css({ width: "100%", "max-width": "760px" });
}

frappe.ui.form.on("Sales Invoice", {
	setup(frm) {
		const field = frm.fields_dict.custom_customer_entry;
		field.df.formatter = (value) => {
			const label = value || frm.doc.customer_name || frm.doc.customer || "";
			if (!frm.doc.customer) return frappe.utils.escape_html(label);
			return $("<a>")
				.attr("href", frappe.utils.get_form_link("Customer", frm.doc.customer))
				.text(label)[0].outerHTML;
		};
		// Retain text entry on drafts and provide the native-style open link beside it.
		field.$customer_link = $('<a class="btn-open no-decoration">')
			.attr("title", __("Open Customer"))
			.attr("aria-label", __("Open Customer"))
			.html(frappe.utils.icon("external-link", "sm"));
		$("<span class='link-btn'>").append(field.$customer_link).appendTo(field.input_area);
		field.df.ignore_validation = true;
		field.get_query = () => ({ query: "elsakr_app.invoice_customer.search_customers" });
		const customer_address = frm.cscript.customer_address;
		frm.cscript.customer_address = function (...args) {
			// Empty Link validation also fires on a new name, before a Customer exists.
			// Clear the display without asking the native tax lookup for a missing party.
			if (!frm.doc.customer && !frm.doc.customer_address) {
				return frm.set_value("address_display", "");
			}
			return customer_address.apply(this, args);
		};
		const validate_party = frm.cscript.validate_company_and_party;
		frm.cscript.validate_company_and_party = function (...args) {
			if (frm.doc.company && !frm.doc.customer && frm.doc.custom_customer_entry?.trim()) {
				return true;
			}
			return validate_party.apply(this, args);
		};
	},
	onload(frm) {
		if (frm.doc.customer && !frm.doc.custom_customer_entry) {
			return load_invoice_customer(frm);
		}
	},
	refresh(frm) {
		const field = frm.fields_dict.custom_customer_entry;
		update_invoice_customer_link(frm);
		if (field.awesomplete) {
			field.awesomplete.filter = () => true;
			// Customer labels must be rendered as text.
			field.awesomplete.item = (item) => {
				const row = field.get_data().find((d) => d.value === item.value) || item;
				return $("<li>").append(
					$("<strong>").text(row.label),
					$("<div>").text(row.description || "")
				)[0];
			};
		}
		frm.toggle_display("customer", false);
		frm.toggle_reqd("customer", false);
		frm.toggle_reqd("custom_customer_entry", true);
	},
	before_save(frm) {
		// ERPNext fills these from the new Customer during server validation.
		if (!frm.doc.customer && frm.doc.custom_customer_entry?.trim()) {
			frm.toggle_reqd("debit_to", false);
			frm.toggle_reqd("due_date", false);
		}
	},
	async custom_customer_entry(frm) {
		if (frm._setting_inline_customer) return;
		const value = frm.doc.custom_customer_entry;
		const selected = frm.fields_dict.custom_customer_entry
			.get_data()
			.find((d) => d.value === value);
		if (selected) return select_invoice_customer(frm, selected.value);
		if (frm.doc.customer && value !== frm.doc.customer_name) {
			await frm.set_value("customer", "");
			update_invoice_customer_link(frm);
			await frm.set_value({
				custom_customer_phone: "",
				custom_customer_address: "",
				contact_person: "",
				contact_mobile: "",
				customer_address: "",
				address_display: "",
			});
		}
	},
	customer(frm) {
		update_invoice_customer_link(frm);
		if (frm.doc.customer && !frm._setting_inline_customer) return load_invoice_customer(frm);
	},
});

function update_invoice_customer_link(frm) {
	const field = frm.fields_dict.custom_customer_entry;
	field.$customer_link
		.attr(
			"href",
			frm.doc.customer ? frappe.utils.get_form_link("Customer", frm.doc.customer) : null
		)
		.toggle(!!frm.doc.customer);
	if (field.disp_area) field.set_disp_area(frm.doc.custom_customer_entry);
}

async function select_invoice_customer(frm, customer) {
	if (frm._setting_inline_customer) return;
	frm._setting_inline_customer = true;
	try {
		await frm.set_value("customer", customer);
		await load_invoice_customer(frm);
	} finally {
		frm._setting_inline_customer = false;
	}
}

async function load_invoice_customer(frm) {
	const customer = frm.doc.customer;
	if (!customer) return;
	const { message } = await frappe.call({
		method: "elsakr_app.invoice_customer.customer_details",
		args: { customer },
	});
	if (frm.doc.customer !== customer) return;
	if (frm.doc.docstatus) {
		// Show details on older submitted invoices without marking them as modified.
		Object.assign(frm.doc, {
			custom_customer_entry: message.customer_name,
			custom_customer_phone: frm.doc.contact_mobile || message.phone,
			custom_customer_address: message.address,
		});
		frm.refresh_fields([
			"custom_customer_entry",
			"custom_customer_phone",
			"custom_customer_address",
		]);
		return;
	}
	const previous = frm._setting_inline_customer;
	frm._setting_inline_customer = true;
	try {
		frm.fields_dict.custom_customer_entry.set_data([]);
		await frm.set_value({
			custom_customer_entry: message.customer_name,
			custom_customer_phone: message.phone,
			custom_customer_address: message.address,
		});
	} finally {
		frm._setting_inline_customer = previous;
	}
}

frappe.ui.form.on("Sales Invoice", {
	refresh: update_customer_unpaid_card,
	customer: update_customer_unpaid_card,
	company: update_customer_unpaid_card,
});

async function update_customer_unpaid_card(frm) {
	if (!frm.$customer_unpaid_card) {
		frm.$customer_unpaid_card = $(
			'<div class="elsakr-customer-unpaid-card" role="status" aria-live="polite">'
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
					.text(__("Customer has an unpaid balance")),
				$('<div class="unpaid-amount">').css({
					"font-size": "24px",
					"font-weight": 700,
					"margin-top": "4px",
				}),
				$('<div class="unpaid-customer">').css({
					"font-size": "12px",
					"margin-top": "4px",
				})
			);
	}
	// Reuse one card and immediately clear stale figures on customer/company changes.
	frm.$customer_unpaid_card
		.hide()
		.insertBefore(frm.fields_dict.custom_customer_entry.section.wrapper);
	const request = (frm._unpaid_request || 0) + 1;
	frm._unpaid_request = request;
	const { customer, company } = frm.doc;
	if (!customer || !company || !frappe.model.can_read("GL Entry")) return;
	try {
		const { message } = await frappe.call({
			method: "elsakr_app.customer_balance.get_customer_unpaid_balance",
			args: { customer, company },
		});
		if (
			request !== frm._unpaid_request ||
			customer !== frm.doc.customer ||
			company !== frm.doc.company
		)
			return;
		if (!message || message.amount <= 0) return;
		frm.$customer_unpaid_card
			.find(".unpaid-amount")
			.text(format_currency(message.amount, message.currency, message.precision));
		frm.$customer_unpaid_card
			.find(".unpaid-customer")
			.text(`${frm.doc.customer_name || customer} · ${company}`);
		frm.$customer_unpaid_card.show();
	} catch {
		// An unavailable balance must never leave a previous customer's figure visible.
		if (request === frm._unpaid_request) frm.$customer_unpaid_card.hide();
	}
}
