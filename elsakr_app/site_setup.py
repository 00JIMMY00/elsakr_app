"""Keep the Elsakr landing route and release notification preferences."""

import frappe

OPERATIONS_WORKSPACE = "Operations"
OPERATIONS_ROUTE = "/app/operations"


def set_user_home_workspace(doc, method=None):
	"""Keep current and future Desk users on the site's main workspace."""
	if doc.user_type == "System User":
		doc.default_workspace = OPERATIONS_WORKSPACE


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
	redirect.target = OPERATIONS_ROUTE
	redirect.redirect_http_status = "302"
	website.save(ignore_permissions=True)
	for user in frappe.get_all("User", filters={"user_type": "System User"}, pluck="name"):
		frappe.db.set_value("User", user, "default_workspace", OPERATIONS_WORKSPACE)
		frappe.clear_document_cache("User", user)
	frappe.clear_cache()
