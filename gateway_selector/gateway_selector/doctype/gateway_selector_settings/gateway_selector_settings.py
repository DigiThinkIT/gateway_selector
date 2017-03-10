# -*- coding: utf-8 -*-
# Copyright (c) 2015, DigiThinkIT, Inc. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_url, call_hook_method, cint, flt
from urllib import urlencode
from frappe.integration_broker.doctype.integration_service.integration_service import IntegrationService, get_integration_controller

class GatewaySelectorSettings(IntegrationService):
    service_name = "Gateway Selector"

    def validate(self):
        pass

    def on_update(self):
        pass

    def enable(self):
        call_hook_method("payment_gateway_enabled", gateway=self.service_name)

    def validate_transaction_currency(self, currency):
        for gateway in self.gateways:
            controller = get_integration_controller(gateway.service)
            controller.validate_transaction_currency(currency)

    def get_payment_url(self, **kwargs):
        proxy = self.build_proxy(**kwargs)
        url = "./integrations/gateway_selector/{0}"
        return get_url(url.format(proxy.get("name" )))

    def build_proxy(self, **kwargs):
        data = {
            "doctype": "Gateway Selector Proxy"
        }
        data.update(kwargs)
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

def is_gateway_embedable(name):
    controller = get_integration_controller(name)
    return hasattr(controller, "is_embedable") and controller.is_embedable

def get_gateway_embed_form(name):
    controller = get_integration_controller(name)
    return controller.get_embed_form()

@frappe.whitelist(allow_guest=True)
def get_gateways():
    gateway_selector = get_integration_controller("Gateway Selector")
    gateways = []
    for gateway in gateway_selector.gateways:
        gtwy = {
            "name": gateway.service.replace(' ', '_').lower(),
            "data": { key: gateway.get(key) for key in ['label', 'icon', 'service', 'is_default'] },
            "is_embedable": is_gateway_embedable(gateway.service)
        }

        if gtwy["is_embedable"]:
            gtwy["embed_form"] = get_gateway_embed_form(gateway.service)

        gateways.append(gtwy)

    return gateways
