frappe.ui.form.on("Customer", {
	refresh(frm) {
		const section = frm.fields_dict.primary_address_and_contact_detail;
		const details = frm.fields_dict.customer_name.tab;
		const header = frm.fields_dict.customer_name.section;
		section.wrapper.insertAfter(header.wrapper);
		section.parent = details.wrapper;
		section.tab = details;
		section.fields_list.forEach((field) => details.add_field(field));
		frm.toggle_display("contact_and_address_tab", false);
	},
});
