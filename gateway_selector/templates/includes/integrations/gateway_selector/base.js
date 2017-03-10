frappe.provide("frappe.integration_service")
frappe.provide("frappe.gateway_selector")

/* stub class for non embedable gateways, this functions as simple redirection
form implementation */
frappe.gateway_selector._generic_embed = Class.extend({
  init: function(gateway) {
    this.gateway = gateway;
  },

  show: function() {
    console.log("Show", this.gateway.name);
  },

  hide: function() {
    console.log("Hide", this.gateway.name);
  }
})

frappe.integration_service.gateway_selector_gateway = Class.extend({

  services: {},
  current_gateway: null,

  init: function() {
  },

  form: function(id) {
    var base = this;
    $(function() {
      frappe.call({
        method: "gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings.get_gateways",
        args: {},
        callback: function(data) {

          for(var i=0; i < data.message.length; i++) {
            var gateway = data.message[i];
            if ( gateway.is_embedable ) {
              $('#gateway-selector-forms').append('<div id="gateway_option_'+gateway.name+'">'+gateway.embed_form.form+'</div>');
              if ( frappe.gateway_selector[gateway.name + "_embed"] !== undefined ) {
                base.services[gateway.name] = new frappe.gateway_selector[gateway.name + "_embed"]()
              } else {
                base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway);
              }

              $('#gateway_option_'+gateway.name).hide();
            } else {
              base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway);
            }
          }

        }
      })
    });

    $('input:radio[name="gateway_selector_option"]').change(function() {
      if ( $(this).is(':checked') ) {
        var gateway = base.services[$(this).val()];

        // hide previous form
        if ( base.current_gateway ) {
          base.current_gateway.hide();
        }

        // display gateway form
        if ( gateway ) {
          gateway.show();
          base.current_gateway = gateway;
        } else {
          base.current_gateway = null;
        }

        var $gateway_form = $('#gateway_option_' + $(this).val());
        // hide all other gateway forms
        $('div[id^=gateway_option_]').not($gateway_form).slideUp('fast');
        // display this gateway form
        $gateway_form.slideDown('fast');

      }
    })

  }
});
