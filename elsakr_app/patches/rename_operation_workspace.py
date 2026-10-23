"""Move the app Workspace away from ERPNext's Operation DocType route."""

import frappe
from frappe.desk.doctype.workspace.workspace import update_page


def execute():
	if not frappe.db.exists("Workspace", "Operation"):
		return

	doc = frappe.get_doc("Workspace", "Operation")
	if doc.module != "Elsakr App":
		return

	if frappe.db.exists("Workspace", "Operations"):
		frappe.throw("Cannot rename Operation: an Operations Workspace already exists.")

	update_page(
		name=doc.name,
		title="Operations",
		icon=doc.icon or "",
		indicator_color=doc.indicator_color or "",
		parent=doc.parent_page or "",
		public=doc.public,
	)
