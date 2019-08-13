# -*- coding: utf-8 -*-
# Copyright (c) 2015, DigiThinkIT, Inc. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _dict
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method
from awesome_cart.compat.customer import get_current_customer
from frappe.integrations.utils import get_payment_gateway_controller
from frappe.integrations.utils import create_payment_gateway

class GatewaySelectorSettings(Document):
	service_name = "Gateway Selector"

	def validate(self):
		create_payment_gateway("Gateway Selector")
		call_hook_method("payment_gateway_enabled", gateway=self.service_name)


	def on_update(self):
		pass


	def validate_transaction_currency(self, currency):
		pass
		# for gateway in self.gateways:
			# controller = get_payment_gateway_controller(gateway.service)
			# controller.validate_transaction_currency(currency)

	def get_payment_url(self, **kwargs):
		proxy = self.build_proxy(**kwargs)
		#url = "./integrations/gateway_selector/{0}"
		url = "./payments/{0}"
		return get_url(url.format(proxy.get("name" )))

	def build_proxy(self, **kwargs):
		data = {
			"doctype": "Gateway Selector Proxy"
		}
		data.update(kwargs)

		# When a PR request is built system references order_id as the PR itself
		# here we are checking if we have a Payment Request to update the proxy's
		# order_id field to match the PR doctype's name
		if kwargs.get("reference_doctype") == 'Payment Request':
			pr = frappe.get_doc("Payment Request", kwargs.get("reference_docname"))
			data.update({ "order_id": pr.reference_name })

		proxy = frappe.get_doc(data)

		proxy.flags.ignore_permissions = 1
		proxy.insert()

		return proxy


@frappe.whitelist()
def get_service_details():
	return """
		<div>
			<p>    This service is a proxy gateway which allows your users
				to select their own payment gateway from a list of available
				preconfigured gateways.
			</p>
			<p> Click the settings button above to configure available gateways</p>
		</div>
	"""

def get_awc_gateway_form(context={}):
	"""This is the Gateway Selector embed form used by awc to embed itself on
	the cart's frontend"""

	context.update({
		"source": "templates/includes/integrations/gateway_selector/embed.html",
		"submit_source": "templates/includes/integrations/gateway_selector/submit.html"
	})

	context = _dict(context)
	build_embed_context(context)

	return {
		"form": frappe.render_template(context.source, context),
		"context": context,
		"submit": frappe.render_template(context.submit_source, context),
		"styles": context["gateway_styles"],
		"scripts": context["gateway_scripts"],
		"js_api_factory": "frappe.integration_service.gateway_selector_gateway"
	}

def is_gateway_embedable(name):
	"""Returns True if the the gateway supports get_embed_form api"""

	controller = get_payment_gateway_controller(name)
	return hasattr(controller, "is_embedable") and controller.is_embedable

def is_gateway_available(name, context, is_backend=0):
	controller = get_payment_gateway_controller(name)
	if hasattr(controller, "is_available"):
		return controller.is_available(context, is_backend=is_backend)

	return True

def get_gateway_embed_form(name, context={}):
	"""Gets the gateway's embedable form information"""

	controller = get_payment_gateway_controller(name)
	return controller.get_embed_form(context=context)

@frappe.whitelist(allow_guest=True)
def get_url_from_gateway(gateway, data):
	"""Gets the gateway url when deferring gateways that can not be embeded"""

	if isinstance(data, unicode) or isinstance(data, str):
		data = json.loads(data)

	gateway_selector = get_payment_gateway_controller("Gateway Selector")

	for g in gateway_selector.gateways:
		if g.service.replace(' ', '_').lower() == gateway:
			gateway_name = g.service
			break
	else:
		gateway_name = None

	controller = get_payment_gateway_controller(gateway_name)

	return controller.get_payment_url(**data)

@frappe.whitelist(allow_guest=True)
def get_gateways(context="{}", is_backend=0):
	"""Gets a list of gateways that can be selected and their embedding information"""

	context = json.loads(context)
	context['is_backend'] = is_backend
	gateway_selector = get_payment_gateway_controller("Gateway Selector")
	gateways = []
	for gateway in gateway_selector.gateways:
		if is_gateway_available(gateway.service, context, is_backend=is_backend):
			payload = {
				"name": gateway.service.replace(' ', '_').lower(),
				"data": { key: gateway.get(key) for key in ['label', 'icon', 'service', 'is_default'] },
				"is_embedable": is_gateway_embedable(gateway.service)
			}

			if payload["is_embedable"]:
				payload["embed_form"] = get_gateway_embed_form(gateway.service, context=context)

			gateways.append(payload)

	return gateways

def build_embed_context(context, is_backend=False):
	"""Convenience method that adds gateway information for a page's context"""

	context["data"] = {}
	gateways = get_gateways(is_backend=is_backend)


	# Build billing address context
	context["billing_countries"] = [ x for x in frappe.get_list("Country", fields=["country_name", "name"], ignore_permissions=1) ]
	context["is_backend"] = is_backend

	default_country = frappe.get_value("System Settings", "System Settings", "country")
	default_country_doc = next((x for x in context["billing_countries"] if x.name == default_country), None)
	customer = get_current_customer()
	if customer:
		context["addresses"] = frappe.get_all("Address", filters={"customer" : customer.name, "disabled" : 0}, fields="*")

	country_idx = context["billing_countries"].index(default_country_doc)
	context["billing_countries"].pop(country_idx)
	context["billing_countries"] = [default_country_doc] + context["billing_countries"]

	context["gateway_scripts"] = ['/assets/js/gateway_selector_embed.js']
	context["gateway_styles"] = ['/assets/css/gateway_selector_embed.css']
	context["gateways"] = gateways

	for gateway in gateways:
		if gateway.get('embed_form'):
			context["gateway_scripts"].append(gateway.get('embed_form').get("script_url"))
			context["gateway_styles"].append(gateway.get('embed_form').get("style_url"))

@frappe.whitelist(allow_guest=True)
def update_proxy_gateway(name, gateway_service):
	frappe.db.set_value('Gateway Selector Proxy', name, 'gateway_service', gateway_service)
	frappe.db.commit()
