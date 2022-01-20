from . import __version__ as app_version

app_name = "ts_distribution"
app_title = "Distribution"
app_publisher = "Tech Station"
app_description = "Distribution"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@techstation.com.eg"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ts_distribution/css/ts_distribution.css"
# app_include_js = "/assets/ts_distribution/js/ts_distribution.js"

# include js, css files in header of web template
# web_include_css = "/assets/ts_distribution/css/ts_distribution.css"
# web_include_js = "/assets/ts_distribution/js/ts_distribution.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ts_distribution/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {
	"Sales Order": "public/js/sales_order.js",
	"Customer": "public/js/customer.js",
}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ts_distribution.install.before_install"
# after_install = "ts_distribution.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ts_distribution.notifications.get_notification_config"

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

doc_events = {
	"Sales Order": {
		"validate": "ts_distribution.hook.sales_order.validate",
		"on_submit": "ts_distribution.hook.sales_order.on_submit",
	},
	"Sales Invoice": {
		"validate": "ts_distribution.hook.sales_invoice.validate",
		"on_submit": "ts_distribution.hook.sales_invoice.on_submit",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ts_distribution.tasks.all"
# 	],
# 	"daily": [
# 		"ts_distribution.tasks.daily"
# 	],
# 	"hourly": [
# 		"ts_distribution.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ts_distribution.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ts_distribution.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "ts_distribution.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ts_distribution.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ts_distribution.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ts_distribution.auth.validate"
# ]

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
		"name",
		"in",
			[
				# Customer Custom Field
				"Customer-distribution_type",
				"Customer-sales_officials",
				"Customer-sales_type",

				# Item Custom Field
				"Item-empty_consignment",
				"Item-shipping_discount",

				# Sales Order Custom Field
				"Sales Order-distribution_type",
				"Sales Order-customer_rating",
				"Sales Order-customer_credit_limit",
				"Sales Order-sales_type",
				"Sales Order-transportation_vehicle",
				"Sales Order-vehicle_type",
				"Sales Order-sales_type_credit_limit",
				"Sales Order-advance_payment_details",
				"Sales Order-advance_customer_payment",
				"Sales Order-multiple_payment_details",
				"Sales Order-multiple_payment",
				"Sales Order-fetch_advance_payment",
				"Sales Order-section_break_110",
				"Sales Order-advance_amount_adjusted",
				"Sales Order-paid_amount",
				"Sales Order-unpaid_amount",
				"Sales Order-outstanding_amount",
				"Sales Order-customer_driver",
				"Sales Order-company_drivers",
				"Sales Order-sales_officials",

				# Sales Order Item
				"Sales Order Item-shipping_discount_details",
				"Sales Order Item-column_break_36",
				"Sales Order Item-total_shipping_discount",
				"Sales Order Item-shipping_discount",

				# Sales Invoice Custom Field
				"Sales Invoice-distribution_type",
				"Sales Invoice-sales_type",
				"Sales Invoice-sales_officials",
				"Sales Invoice-transportation_vehicle",
				"Sales Invoice-vehicle_type",
				"Sales Invoice-customer_driver",
				"Sales Invoice-company_drivers",
				"Sales Invoice-multiple_payment_details",
				"Sales Invoice-multiple_payment",
				"Sales Invoice-advance_adjustment_details",
				"Sales Invoice-advance_amount_adjusted",
				"Sales Invoice-column_break_142",
				"Sales Invoice-unpaid_amount"

			]
		]
	]
	},
	{
		"doctype": "Property Setter",
		"filters": [
			[
		"name",
		"in",
			[
				# Sales Order Property
				"Sales Order-set_warehouse-read_only",
				"Sales Order-apply_discount_on-read_only",
				"Sales Order-apply_discount_on-default",
			]
		]
	]
	}
]