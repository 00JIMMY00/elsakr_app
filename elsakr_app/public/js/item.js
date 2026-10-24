frappe.ui.form.on("Item", {
	refresh(frm) {
		const price = frm.doc.__onload?.selling_price;
		if (!price || frm.is_new()) return;
		const escape = frappe.utils.escape_html;
		frm.set_df_property("standard_rate", "read_only", !!price.error);
		frm.set_df_property("standard_rate", "description",
			`${escape(price.price_list)} · ${escape(price.currency || "")} · ${escape(frm.doc.stock_uom)}` +
			(price.error ? `<br>${escape(price.error)}` : ""));
		frm.set_df_property("standard_rate", "options", price.currency || "");
	},
});
