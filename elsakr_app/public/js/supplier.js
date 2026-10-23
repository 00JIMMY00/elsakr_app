frappe.ui.form.on("Supplier", {
	setup(frm) {
		const native_refresh = frm.cscript.refresh;
		frm.cscript.refresh = async function (...args) {
			if (native_refresh) await native_refresh.apply(this, args);
			frm.toggle_display("naming_series", false);
		};
	},
	onload(frm) {
		if (!frm.doc.custom_phone && frm.doc.mobile_no) {
			frm.doc.custom_phone = frm.doc.mobile_no;
			frm.refresh_field("custom_phone");
		}
	},
	mobile_no(frm) {
		return frm.set_value("custom_phone", frm.doc.mobile_no || "");
	},
	refresh(frm) {
		const details = frm.fields_dict.supplier_name.tab;
		let previous = frm.fields_dict.supplier_name.section;
		for (const fieldname of [
			"address_contacts",
			"primary_address_and_contact_detail_section",
		]) {
			const section = frm.fields_dict[fieldname];
			section.wrapper.insertAfter(previous.wrapper);
			section.parent = details.wrapper;
			section.tab = details;
			section.fields_list.forEach((field) => details.add_field(field));
			frm.toggle_display(fieldname, !frm.is_new());
			previous = section;
		}
		frm.toggle_display("naming_series", false);
		frm.toggle_display("contact_and_address_tab", false);
	},
});
