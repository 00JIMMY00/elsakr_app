frappe.ui.form.on("Customer", {
	onload(frm) {
		// Display existing phones without turning an opened Customer into an unsaved edit.
		if (!frm.doc.custom_phone && frm.doc.mobile_no) {
			frm.doc.custom_phone = frm.doc.mobile_no;
			frm.refresh_field("custom_phone");
		}
	},
	mobile_no(frm) {
		// Native contact selection still fetches mobile_no from the selected Contact.
		return frm.set_value("custom_phone", frm.doc.mobile_no || "");
	},
	refresh(frm) {
		const section = frm.fields_dict.primary_address_and_contact_detail;
		const details = frm.fields_dict.customer_name.tab;
		const header = frm.fields_dict.customer_name.section;
		section.wrapper.insertAfter(header.wrapper);
		section.parent = details.wrapper;
		section.tab = details;
		section.fields_list.forEach((field) => details.add_field(field));
		frm.toggle_display("contact_and_address_tab", false);
		frm.toggle_display("primary_address_and_contact_detail", !frm.is_new());
	},
});
