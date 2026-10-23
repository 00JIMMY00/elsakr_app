frappe.ui.form.on("Sales Invoice", {
	setup(frm) {
		// A true collapsible dependency expands the section in Frappe v15.
		frm.set_df_property("payments_section", "collapsible_depends_on", "eval:doc.is_pos");
	},
	refresh(frm) {
		position_pos_payments(frm);
	},
	is_pos(frm) {
		position_pos_payments(frm);
		if (frm.doc.is_pos && frm.doc.company && !frm.doc.docstatus) {
			frm.scroll_to_field("payments", false);
		}
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
