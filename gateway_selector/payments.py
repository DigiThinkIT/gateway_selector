from __future__ import unicode_literals
import frappe
import hashlib
from frappe.sessions import get_csrf_token
from awesome_cart.session import get_awc_session, set_awc_session

ERROR_INVALID_KEY=101
ERROR_NOT_AVAILABLE=102

@frappe.whitelist(allow_guest=True)
def login(payment_request_name, payment_reference):

	pr = frappe.get_doc("Payment Request", payment_request_name.strip().upper())

	if pr.get("status") != "Initiated":
		return "This Payment Request was Already Fulfilled"

	if pr.reference_name.strip().upper() == payment_reference.strip().upper():

		awc_session = get_awc_session()
		awc_session["gateway_selector_pr_access"] = pr.name
		set_awc_session(awc_session)

		parts = pr.payment_url.split('/')

		frappe.response.redirec_url = "/integrations/gateway_selector/{0}".format(parts[-1])
		return

	return "Sorry, Payment Request and/or Reference Number not found!"
