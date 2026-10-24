"""Install the app-owned navigation block for the Operations Workspace."""

from pathlib import Path

import frappe


def setup_operations_workspace():
	folder = Path(__file__).parent / "public" / "html"
	values = {
		"html": (folder / "operations_workspace.html").read_text(),
		"style": (folder / "operations_workspace.css").read_text(),
		"script": (
			"frappe.require('/assets/elsakr_app/js/operations_workspace.js', "
			"() => window.elsakrOperationsWorkspace.mount(root_element));"
		),
		"private": 0,
	}
	name = "Elsakr Operations Hub"
	if frappe.db.exists("Custom HTML Block", name):
		frappe.db.set_value("Custom HTML Block", name, values)
	else:
		frappe.get_doc({"doctype": "Custom HTML Block", "name": name, **values}).insert(
			ignore_permissions=True
		)
