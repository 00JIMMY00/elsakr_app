"""Apply the site-owned Elsakr identity through native Frappe settings."""

import frappe


def setup_branding():
	"""Reapply branding on installation/migration, after shared theme defaults."""
	assets = "/assets/elsakr_app/branding"
	for doctype, values in {
		"Navbar Settings": {"app_logo": f"{assets}/tire-logo.svg"},
		"Website Settings": {
			"app_logo": f"{assets}/tire-logo.svg",
			"app_name": "Elsakr | الصقر",
			"title_prefix": "Elsakr",
			"favicon": f"{assets}/tire-favicon.ico?v=20261025-2",
			"splash_image": f"{assets}/tire-loader.webp",
		},
	}.items():
		for fieldname, value in values.items():
			frappe.db.set_single_value(doctype, fieldname, value)
	frappe.clear_cache()
