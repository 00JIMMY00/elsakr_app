from pathlib import Path

import frappe
from frappe.desk.query_report import get_script as get_standard_script

from elsakr_app.overrides.report import STOCK_REPORTS


@frappe.whitelist()
def get_script(report_name: str):
	result = get_standard_script(report_name)
	if report_name in STOCK_REPORTS:
		# Append to the standard script to retain ERPNext filters, formatters and actions.
		script = Path(frappe.get_app_path("elsakr_app", "public", "js", "stock_size_filter.js"))
		result["script"] += "\n" + script.read_text(encoding="utf-8")
	return result
