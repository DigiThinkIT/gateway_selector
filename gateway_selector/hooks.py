# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "gateway_selector"
app_title = "Gateway Selector"
app_publisher = "DigiThinkIT, Inc."
app_description = "An integration broker payment gateway selector to present users with more than one way to fullfill payments."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "forellana@digithinkit.com"
app_license = "MIT"


integration_services = ["Gateway Selector"]
app_include_js = "/assets/js/gateway_selector_settings.js"

website_route_rules = [
	{ "from_route": "/integrations/gateway_selector/<name>", "to_route": "integrations/gateway_selector" }
]

awc_gateway_form_provider = "gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings.get_awc_gateway_form"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gateway_selector/css/gateway_selector.css"
# app_include_js = "/assets/gateway_selector/js/gateway_selector.js"

# include js, css files in header of web template
# web_include_css = "/assets/gateway_selector/css/gateway_selector.css"
# web_include_js = "/assets/gateway_selector/js/gateway_selector.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "gateway_selector.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "gateway_selector.install.before_install"
# after_install = "gateway_selector.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gateway_selector.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"gateway_selector.tasks.all"
# 	],
# 	"daily": [
# 		"gateway_selector.tasks.daily"
# 	],
# 	"hourly": [
# 		"gateway_selector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gateway_selector.tasks.weekly"
# 	]
# 	"monthly": [
# 		"gateway_selector.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "gateway_selector.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gateway_selector.event.get_events"
# }
