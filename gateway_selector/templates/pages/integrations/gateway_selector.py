from __future__ import unicode_literals, absolute_import

import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.utils.formatters import format_value
from awesome_cart.compat.customer import get_current_customer
from awesome_cart.session import get_awc_session, set_awc_session
from frappe.integration_broker.doctype.integration_service.integration_service import get_integration_controller
from gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings import is_gateway_embedable, build_embed_context
from gateway_selector import payments
import json
from datetime import datetime
from dti_devtools.debug import log, pretty_json

no_cache = 1
no_sitemap = 1
expected_keys = ('amount', 'title', 'description', 'reference_doctype', 'reference_docname',
	'payer_name', 'payer_email', 'order_id', 'currency')

def get_context(context):
	context.no_cache = 1

	# get request name from query string
	proxy_name = frappe.local.form_dict.get("name")

	awc_session = get_awc_session()
	pr_access = awc_session.get("gateway_selector_pr_access")

	print(pretty_json(awc_session))

	# or from pathname, this works better for redirection on auth errors
	if not proxy_name:
		path_parts = context.get("pathname", "").split('/')
		proxy_name = path_parts[-1]

	doc = None
	# attempt to fetch AuthorizeNet Request record
	try:
		proxy = frappe.get_doc("Gateway Selector Proxy", proxy_name)
		doc = frappe.get_doc(proxy.reference_doctype, proxy.reference_docname)

		if doc.get("status") != "Initiated":
			frappe.redirect_to_message(_("Payment Request Not Available"), _("This Payment Request is not available any longer"))
			frappe.local.flags.redirect_location = "/payments?e={0}".format(payments.ERROR_NOT_AVAILABLE)
			raise frappe.Redirect

	except Exception as ex:
		print(ex)
		proxy = None

	# Captured/Authorized transaction redirected to home page
	# TODO: Should we redirec to a "Payment already received" Page?
	if not proxy:
		frappe.redirect_to_message(_("Payment Request Not Available"), _("Invalid Payment Request"))
		frappe.local.flags.redirect_location = '/payments?e={0}'.format(payments.ERROR_NOT_AVAILABLE)
		raise frappe.Redirect

	if pr_access and doc.name != pr_access:
		frappe.redirect_to_message(_("Payment Request Not Available"), _("Invalid Request"))
		frappe.local.flags.redirect_location = "/payments/{0}?e={1}".format(proxy_name, payments.ERROR_INVALID_KEY)
		raise frappe.Redirect

	if not pr_access and frappe.session.user == 'Guest':
		print("Guest user")
		frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

	context["is_backend"]=1
	build_embed_context(context, is_backend=1)

	if proxy_name and proxy:
		context["data"] = { key: proxy.get(key) for key in expected_keys }

		context["billing_countries"] = [ x for x in frappe.get_list("Country", fields=["country_name", "name"], ignore_permissions=1) ]

		default_country = frappe.get_value("System Settings", "System Settings", "country")
		default_country_doc = next((x for x in context["billing_countries"] if x.name == default_country), None)

		customer = get_current_customer()

		if customer:
			context["addresses"] = frappe.get_all("Address", filters={"customer" : customer.name, "disabled" : 0, "address_type" : "Billing"}, fields="*")

		country_idx = context["billing_countries"].index(default_country_doc)
		context["billing_countries"].pop(country_idx)
		context["billing_countries"] = [default_country_doc] + context["billing_countries"]


	else:
		frappe.redirect_to_message(_('Some information is missing'), _(
			'Looks like someone sent you to an incomplete URL. Please ask them to look into it.'))
		frappe.local.flags.redirect_location = frappe.local.response.location
		raise frappe.Redirect

	return context
