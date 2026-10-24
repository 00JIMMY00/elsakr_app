"""Keep the Elsakr landing route and release notification preferences."""

import frappe


def setup_site_preferences():
	settings = frappe.get_single("System Settings")
	settings.disable_system_update_notification = 1
	settings.disable_change_log_notification = 1
	settings.save(ignore_permissions=True)

	website = frappe.get_single("Website Settings")
	root_redirects = [row for row in website.route_redirects if row.source.strip("/ ") == ""]
	if root_redirects:
		redirect = root_redirects[0]
		for duplicate in root_redirects[1:]:
			website.remove(duplicate)
	else:
		redirect = website.append("route_redirects", {"source": "/"})
	redirect.target = "/app/operations-dashboard"
	redirect.redirect_http_status = "302"
	website.save(ignore_permissions=True)
	frappe.clear_cache()
