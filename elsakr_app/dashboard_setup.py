"""Install the HTML blocks used by the standard Operations child Workspace."""

from pathlib import Path

import frappe


BLOCKS = {
	"Elsakr Operations Summary": ("operations_summary.html", "mountSummary"),
	"Elsakr Operations Charts": ("operations_charts.html", "mountCharts"),
}


def setup_operations_dashboard():
	folder = Path(__file__).parent / "public" / "html"
	style = (folder / "operations_dashboard.css").read_text()
	for name, (html_file, mount) in BLOCKS.items():
		values = {
			"html": (folder / html_file).read_text(),
			"style": style,
			"script": (
				"frappe.require('/assets/elsakr_app/js/operations_dashboard.js', "
				f"() => window.elsakrOperationsDashboard.{mount}(root_element));"
			),
			"private": 0,
		}
		if frappe.db.exists("Custom HTML Block", name):
			frappe.db.set_value("Custom HTML Block", name, values)
		else:
			frappe.get_doc({"doctype": "Custom HTML Block", "name": name, **values}).insert(
				ignore_permissions=True
			)
