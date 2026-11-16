// Keep the native invoice picker available directly in the form toolbar.
frappe.ui.form.on("Payment Entry", {
	refresh: setup_outstanding_button,
	payment_type: setup_outstanding_button,
});

function setup_outstanding_button(frm) {
	frm.remove_custom_button(__("Get Outstanding Invoices"));
	if (frm.doc.docstatus !== 0 || frm.doc.payment_type === "Internal Transfer") return;
	if (
		frm.is_new()
			? !frappe.model.can_create("Payment Entry")
			: !frm.perm.some((perm) => perm.write)
	)
		return;
	frm.add_custom_button(__("Get Outstanding Invoices"), () => {
		if (!frm.doc.company || !frm.doc.party_type || !frm.doc.party) {
			frappe.msgprint(__("Select Company, Party Type and Party first."));
			return;
		}
		frm.events.check_mandatory_to_fetch(frm);
		const open_picker = () => frm.trigger("get_outstanding_invoices");
		if (frm.doc.references?.length) {
			frappe.confirm(
				__("Replace the current reference rows with outstanding invoices?"),
				open_picker
			);
		} else {
			open_picker();
		}
	});
}
