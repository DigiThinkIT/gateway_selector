frappe.provide("frappe.integration_service")

{% include "templates/includes/integrations/gateway_selector/base.js" with context %}

frappe.integration_service.gateway_selector_gateway =  frappe.integration_service.gateway_selector_gateway.extend({
  form: function(id) {
    this._super(id);
  }
});
