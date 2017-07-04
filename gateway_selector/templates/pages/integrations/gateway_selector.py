from __future__ import unicode_literals, absolute_import

import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.utils.formatters import format_value
from awesome_cart.compat.customer import get_current_customer
from frappe.integration_broker.doctype.integration_service.integration_service import get_integration_controller
from gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings import is_gateway_embedable, build_embed_context

import json
from datetime import datetime

no_cache = 1
no_sitemap = 1
expected_keys = ('amount', 'title', 'description', 'reference_doctype', 'reference_docname',
    'payer_name', 'payer_email', 'order_id', 'currency')

def get_context(context):
    if frappe.session.user=='Guest':
		frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    context.no_cache = 1

    # get request name from query string
    proxy_name = frappe.form_dict.get("id")
    # or from pathname, this works better for redirection on auth errors
    if not proxy_name:
        path_parts = context.get("pathname", "").split('/')
        proxy_name = path_parts[-1]

    # attempt to fetch AuthorizeNet Request record
    try:
        proxy = frappe.get_doc("Gateway Selector Proxy", proxy_name)
    except Exception as ex:
        proxy = None

    # Captured/Authorized transaction redirected to home page
    # TODO: Should we redirec to a "Payment already received" Page?
    if not proxy:
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect

    build_embed_context(context)

    if proxy_name and proxy:
        context["data"] = { key: proxy.get(key) for key in expected_keys }

	context["billing_countries"] = [ x for x in frappe.get_list("Country", fields=["country_name", "name"], ignore_permissions=1) ]

	default_country = frappe.get_value("System Settings", "System Settings", "country")
	default_country_doc = next((x for x in context["billing_countries"] if x.name == default_country), None)

	context["addresses"] = frappe.get_all("Address", filters={"customer" : get_current_customer().name, "disabled" : 0}, fields="*")

	country_idx = context["billing_countries"].index(default_country_doc)
	context["billing_countries"].pop(country_idx)
	context["billing_countries"] = [default_country_doc] + context["billing_countries"]


    else:
        frappe.redirect_to_message(_('Some information is missing'), _(
            'Looks like someone sent you to an incomplete URL. Please ask them to look into it.'))
        frappe.local.flags.redirect_location = frappe.local.response.location
        raise frappe.Redirect

    return context
