frappe.provide("frappe.integration_service")
frappe.provide("frappe.gateway_selector")

frappe.gateway_selector.AddressFormProvider = Class.extend({
	init: function($form) {
		this.data = {};
		this.$form = $form;

		console.log("address form initialized")
	},

	form: function() {
		var $form = this.$form;

		var on_update = function() {
				var field = {
						name: $(this).attr('data-type'),
						value: $(this).val()
				};
				$form.trigger('field-change', field);
		}

		$form.find('input[name="phone"]').change(on_update);
		$form.find('input[name="title"]').change(on_update);
		$form.find('input[name="address_1"]').change(on_update);
		$form.find('input[name="address_2"]').change(on_update);
		$form.find('input[name="city"]').change(on_update);
		$form.find('input[name="state"]').change(on_update);
		$form.find('input[name="pincode"]').change(on_update);
		$form.find('select[name="country"]').change(on_update);

	},

	validate: function() {
		var $form = this.$form;

		if ($form.parent().attr('data-select') == 'true') {
				this.data.phone = $form.find('input[name="phone"]').val();
				this.data.title = $form.find('input[name="title"]').val();
				this.data.address_1 = $form.find('input[name="address_1"]').val();
				this.data.address_2 = $form.find('input[name="address_2"]').val();
				this.data.city = $form.find('input[name="city"]').val();
				this.data.state = $form.find('input[name="state"]').val();
				this.data.pincode = $form.find('input[name="pincode"]').val();
				this.data.country = $form.find('select[name="country"] option:checked').attr('value');
		} else {
				this.data.billing_address = $('#billing-addrs div.selected').attr('data-name');
				this.data.title = $('#billing-addrs .selected span#title strong').text();
        this.data.phone = $('#billing-addrs .selected span#phone').text();
				this.data.address_1 = $('#billing-addrs .selected span#line1').text();
				this.data.address_2 = $('#billing-addrs .selected span#line2').text();
				this.data.city = $('#billing-addrs .selected span#city').text();
				this.data.state = $('#billing-addrs .selected span#state').text();
				this.data.pincode = $('#billing-addrs .selected span#postal_code').text();
				this.data.country = $('#billing-addrs .selected span#country').text();
		}

		$form.trigger('address_change', this.data);

		var result = {
				valid: true,
				address: this.data
		}

		if (!this.data.title) {
				result.valid = false;
		}
		if (!this.data.address_1) {
				result.valid = false;
		}
		if (!this.data.city) {
				result.valid = false;
		}
		if (!this.data.pincode) {
				result.valid = false;
		}
		if (!this.data.country) {
				result.valid = false;
		}
		if (!this.data.phone) {
				result.valid = false;
		}

		return result;
	}
})

/* stub class for non embedable gateways, this functions as simple redirection
form implementation */
frappe.gateway_selector._generic_embed = Class.extend({

  init: function(gateway, addressForm, formData) {
    this.gateway = gateway;
		this.addressForm = addressForm;
		this.formData = formData;
  },

  /**
   * Called when the form is displayed
   */
  show: function() {
    $('#gateway-selector-continue').text("Continue with " + this.gateway.label);
    if ( this.gateway.name.toLowerCase() == "paypal" ) {
      $('#gateway-selector-continue').addClass('paypal');
    }
  },

  /**
   * Called when the form is hidden
   */
  hide: function() {
    if ( this.gateway.name.toLowerCase() == "paypal" ) {
      $('#gateway-selector-continue').removeClass('paypal');
    }

  },

  /**
   * Collects all authnet fields necessary to process payment
   */
  collect: function() {
  },

  getSummary: function() {
    return "You will be redirected to " + this.gateway.label + " to finalize payment.";
  },

  validate: function() {
    return { valid: true, address: this.addressForm.validate().address };
  },

  process: function(data, callback) {
    // trigger payment gateway to use
    frappe.call({
      method: "gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings.get_url_from_gateway",
      args: {
        data: data,
        gateway: this.gateway.name
      },
      callback: function(data) {
        // redirect to gateway page
        window.location.href = data.message
      }
    })
  }
})

frappe.integration_service.gateway_selector_gateway = Class.extend({

  services: {},
  current_gateway: null,
  current_gateway_name: null,
  on_process: null,

  init: function(context) {
    this._is_enabled = true;
		this._context = context;
  },

  process: function(overrides, callback) {
    if ( this.current_gateway ) {
      this.current_gateway.collect();
      this.current_gateway.process(overrides, callback);
    }
  },

  form: function(request_data) {
    var base = this;
    this.request_data = request_data;
    if ( !this.request_data ) {
      this.request_data = {};
    }

		this.addressForm = new frappe.gateway_selector.AddressFormProvider($('#gateway-selector-billing-form'));

    $(function() {
      frappe.call({
        method: "gateway_selector.gateway_selector.doctype.gateway_selector_settings.gateway_selector_settings.get_gateways",
        freeze: 1,
        args: {
					context: base._context
				},
        callback: function(data) {

          for(var i=0; i < data.message.length; i++) {
            var gateway = data.message[i];
            if ( gateway.is_embedable ) {
              $('#gateway-selector-forms').append('<div id="gateway_option_'+gateway.name+'">'+gateway.embed_form.form+'</div>');
              if ( frappe.gateway_selector[gateway.name + "_embed"] !== undefined ) {
                base.services[gateway.name] = new frappe.gateway_selector[gateway.name + "_embed"](base.addressForm, gateway.embed_form)
              } else {
                base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway, base.addressForm, gateway.embed_form);
              }

              $('#gateway_option_'+gateway.name).hide();
            } else {
              base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway, base.addressForm, gateway.embed_form);
            }
          }

          var $active_gateway = $('input:radio[name="gateway_selector_option"]:checked');
          if ( $active_gateway.length > 0 ) {
            base.activate_gateway($active_gateway.val());
          }

          $('#gateway-selector-options').fadeIn('fast');
        }
      })
    });

    $('input:radio[name="gateway_selector_option"]').change(function() {
      if ( $(this).is(':checked') ) {
        base.activate_gateway($(this).val());
      }
    })

    $('#gateway-selector-continue').click(function() {

      if ( !base._is_enabled ) {
        return;
      }

      if ( base.on_process ) {
        var err = base.on_process(base.request_data, base.current_gateway_name);
        if ( err ) {
          console.error(err);
        }
      } else {
        base.process(base.request_data, function(err, data) {
          if ( err ) {
            $('#gateway-selector-error').text(err);
          } else {
            window.location.href = data.redirect_to;
          }
        })
      }
    })

  },

  enable: function(enabled) {
    this._is_enabled = enabled;
    if ( enabled ) {
      $('#gateway-selector-continue').removeClass('disabled');
    } else {
      $('#gateway-selector-continue').addClass('disabled');
    }
  },

  validate: function() {
    if ( this.current_gateway ) {
      return this.current_gateway.validate();
    }
  },

  getSummary: function() {
    if ( this.current_gateway ) {
      return this.current_gateway.getSummary();
    }

    return "- no payment information found -";
  },

  activate_gateway: function(name) {
    var gateway = this.services[name];

    // hide previous form
    if ( this.current_gateway ) {
      this.current_gateway.hide();
    }

    // display gateway form
    if ( gateway ) {
      gateway.show();
      this.current_gateway = gateway;
      this.current_gateway_name = name;
    } else {
      this.current_gateway = null;
      this.current_gateway_name = null;
    }

    var $gateway_form = $('#gateway_option_' + name);
    // hide all other gateway forms
    $('div[id^=gateway_option_]').not($gateway_form).slideUp('fast');
    // display this gateway form
    $gateway_form.slideDown('fast');
  }

});
