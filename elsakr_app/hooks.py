app_name = "elsakr_app"
app_title = "Elsakr App"
app_publisher = "jimmy"
app_description = "app for client hassan"
app_email = "a@arab-erp.com"
app_license = "mit"

from elsakr_app.setup import TRANSACTION_DOCTYPES

required_apps = ["erpnext"]
after_install = [
	"elsakr_app.setup.setup_item_size",
	"elsakr_app.full_form.setup_full_form",
	"elsakr_app.customer_setup.setup_customer_flow",
	"elsakr_app.sales_invoice_setup.setup_sales_invoice_defaults",
	"elsakr_app.sales_invoice_visibility.setup_sales_invoice_visibility",
	"elsakr_app.dashboard_setup.setup_operations_dashboard",
]
after_migrate = after_install
doc_events = {
	doctype: {"validate": "elsakr_app.transactions.set_item_sizes"} for doctype in TRANSACTION_DOCTYPES
}
doc_events["Address"] = {"validate": "elsakr_app.customer_setup.validate_address_city"}
doc_events["Item"] = {"validate": "elsakr_app.item_variants.set_variant_size"}

doctype_js = {"Sales Invoice": "public/js/sales_invoice.js", "Customer": "public/js/customer.js"}
override_doctype_class = {
	"Report": "elsakr_app.overrides.report.ElsakrReport",
	"Sales Invoice": "elsakr_app.overrides.sales_invoice.ElsakrSalesInvoice",
}
override_whitelisted_methods = {
	"frappe.desk.query_report.get_script": "elsakr_app.report_filters.get_script",
}

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "elsakr_app",
# 		"logo": "/assets/elsakr_app/logo.png",
# 		"title": "Elsakr App",
# 		"route": "/elsakr_app",
# 		"has_permission": "elsakr_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/elsakr_app/css/elsakr_app.css"
# app_include_js = "/assets/elsakr_app/js/elsakr_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/elsakr_app/css/elsakr_app.css"
# web_include_js = "/assets/elsakr_app/js/elsakr_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "elsakr_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "elsakr_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "elsakr_app.utils.jinja_methods",
# 	"filters": "elsakr_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "elsakr_app.install.before_install"
# after_install = "elsakr_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "elsakr_app.uninstall.before_uninstall"
# after_uninstall = "elsakr_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "elsakr_app.utils.before_app_install"
# after_app_install = "elsakr_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "elsakr_app.utils.before_app_uninstall"
# after_app_uninstall = "elsakr_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "elsakr_app.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["elsakr_app.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"elsakr_app.tasks.all"
# 	],
# 	"daily": [
# 		"elsakr_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"elsakr_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"elsakr_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"elsakr_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "elsakr_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "elsakr_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "elsakr_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["elsakr_app.utils.before_request"]
# after_request = ["elsakr_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["elsakr_app.utils.before_job"]
# after_job = ["elsakr_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"elsakr_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
