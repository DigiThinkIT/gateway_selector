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
				this.data.pincode = $form.find('input[name="pincode"]').val() || "00000";
				this.data.country = $form.find('select[name="country"] option:checked').attr('value');
		} else {
				this.data.billing_address = $('#awc-billing-addrs div.awc-selected').attr('data-name');
				this.data.title = $('#awc-billing-addrs .awc-selected span#title strong').text();
				this.data.phone = $('#awc-billing-addrs .awc-selected span#phone').text();
				this.data.address_1 = $('#awc-billing-addrs .awc-selected span#line1').text();
				this.data.address_2 = $('#awc-billing-addrs .awc-selected span#line2').text();
				this.data.city = $('#awc-billing-addrs .awc-selected span#city').text();
				this.data.state = $('#awc-billing-addrs .awc-selected span#state').text();
				this.data.pincode = $('#awc-billing-addrs .awc-selected span#postal_code').text() || "00000";
				this.data.country = $('#awc-billing-addrs .awc-selected span#country').text();
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

  init: function(gateway, addressForm, formData, selector) {
    this.gateway = gateway;
		this.addressForm = addressForm;
		this.formData = formData;
		this.selector = selector;
  },

  /**
   * Called when the form is displayed
   */
  show: function() {
    $('#gateway-selector-continue').text("Continue with " + this.gateway.label);
    $('#gateway-selector-continue').addClass(this.gateway.name);
  },

  /**
   * Called when the form is hidden
   */
  hide: function() {
    $('#gateway-selector-continue').removeClass(this.gateway.name);
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
      }
		})
		.done(function(data, textStatus, xhr) {
      if(typeof data === "string") data = JSON.parse(data);
      var status = xhr.statusCode().status;

			var result = data;
			window.location.href = data.message

			if ( base.gateway.name.toLowerCase() != "paypal" ) {
				callback(null, result.message);
			}
		})
		.fail(function(xhr, textStatus) {
      if(typeof data === "string") data = JSON.parse(data);
      var status = xhr.statusCode().status;
			var errors = [];
			if (xhr.responseJSON && xhr.responseJSON._server_messages) {
        var _server_messages = JSON.parse(xhr.responseJSON._server_messages);
      }

      var errors = [];
      if ( _server_messages ) {
        try {
          for(var i = 0; i < _server_messages.length; i++) {
            errors.push("Server Error: " + JSON.parse(_server_messages[i]).message);
          }
        } catch(ex) {
          errors.push(_server_messages);
          errors.push(ex);
        }
      }

      callback({
        errors: errors,
        status: status,
        recoverable: 0,
        xhr: xhr,
        textStatus: textStatus
      }, null);
		});

  }
})

frappe.integration_service.gateway_selector_gateway = Class.extend({

  services: {},
  current_gateway: null,
  current_gateway_name: null,
  on_process: null,

  init: function(context, is_backend) {
    this._is_enabled = true;
		this._context = context;
		this.is_backend = is_backend;
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
					context: base._context,
					is_backend: base.is_backend
				},
        callback: function(data) {

          for(var i=0; i < data.message.length; i++) {
            var gateway = data.message[i];
            if ( gateway.is_embedable ) {
              $('#gateway-selector-forms').append('<div id="gateway_option_'+gateway.name+'">'+gateway.embed_form.form+'</div>');
              if ( frappe.gateway_selector[gateway.name + "_embed"] !== undefined ) {
                base.services[gateway.name] = new frappe.gateway_selector[gateway.name + "_embed"](base.addressForm, gateway.embed_form, base)
              } else {
                base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway, base.addressForm, gateway.embed_form, base);
              }

              $('#gateway_option_'+gateway.name).hide();
            } else {
              base.services[gateway.name] = new frappe.gateway_selector._generic_embed(gateway, base.addressForm, gateway.embed_form, base);
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

	  $('html, body').animate({ scrollTop: $('#awc-forms, #gateway-selector-forms').first().offset().top - 60 }, 'slow');
      if ( !base._is_enabled ) {
        return;
      }

      if ( base.on_process ) {
        var err = base.on_process(base.request_data, base.current_gateway_name);
        if ( err ) {
          console.error(err);
        }
      } else {
				$('#gateway-selector-error').removeClass('gateway-error').empty();
        base.process(base.request_data, function(err, data) {
          if ( err ) {
						if ( (!err.errors || err.errors.length == 0) || err.status == 500 ) {
							$('#gateway-selector-error').text("There was an internal server error while processing your order. Please contact us or try again later");
						} else {
							$('#gateway-selector-error').text(err.errors.join(', '));
						}
						$('#gateway-selector-error').addClass('gateway-error');

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
      var result = this.current_gateway.validate();
			if ( this.is_backend ) {
				if ( result.valid ) {
					$('#gateway-selector-continue').removeClass('disabled');
				} else {
					$('#gateway-selector-continue').addClass('disabled');
				}
			}

			return result;
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

		this.validate();

    var $gateway_form = $('#gateway_option_' + name);
    // hide all other gateway forms
    $('div[id^=gateway_option_]').not($gateway_form).slideUp('fast');
    // display this gateway form
    $gateway_form.slideDown('fast');
  }

});
