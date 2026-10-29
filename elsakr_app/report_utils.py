"""Shared permission and column helpers for the compact Operations reports."""

import frappe
from frappe import _


def report_company(company=None):
	companies = frappe.get_list("Company", fields=["name", "default_currency"], limit_page_length=0)
	allowed = {row.name: row for row in companies}
	if not company:
		default = frappe.defaults.get_user_default("Company")
		company = default if default in allowed else next(iter(allowed), None)
	if company not in allowed:
		frappe.throw(_("Not permitted for this company"), frappe.PermissionError)
	return allowed[company]


def column(fieldname, label, fieldtype="Data", options=None, width=140):
	return dict(fieldname=fieldname, label=_(label), fieldtype=fieldtype, options=options, width=width)
