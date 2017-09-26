from __future__ import unicode_literals, absolute_import

import frappe

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
		except:
			proxy = None

	context["payment_request_name"] = form.get("payment_request_name", payment_request_name)
	context["payment_reference"] = form.get("payment_reference")

	return context
