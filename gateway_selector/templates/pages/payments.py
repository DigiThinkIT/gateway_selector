from __future__ import unicode_literals, absolute_import

import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.utils.formatters import format_value
from awesome_cart.compat.customer import get_current_customer
from frappe.integration_broker.doctype.integration_service.integration_service import get_integration_controller
from gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings import is_gateway_embedable, build_embed_context

from dti_devtools.debug import log, pretty_json

import json

no_cache = 1
no_sitemap = 1

def get_context(context):
	context["no_cache"] = 1
	context["no_sitemap"] = 1

	form = frappe.local.form_dict
	payment_request_name = None

	path_parts = context.get("pathname", "").split('/')

	if path_parts[-1] != "payments":
		proxy_name = path_parts[-1]

		try:
			proxy = frappe.get_doc("Gateway Selector Proxy", proxy_name)
			payment_request_name = proxy.get("reference_docname")
		except Exception as ex:
			proxy = None

	context["payment_request_name"] = form.get("payment_request_name", payment_request_name)
	context["payment_reference"] = form.get("payment_reference")

	return context
