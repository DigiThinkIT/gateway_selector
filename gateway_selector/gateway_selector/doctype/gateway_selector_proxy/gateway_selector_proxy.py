# -*- coding: utf-8 -*-
# Copyright (c) 2015, DigiThinkIT, Inc. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


def call_hook(hook_name, **kwargs):
	hooks = frappe.get_hooks(hook_name) or []
	for hook in hooks:
		# don't allow hooks to break processing
		try:
			frappe.call(hook, **kwargs)
		except Exception:
			# Hook inception, pass exception to hook listening for exception reporting(sentry)
			error_hooks = frappe.get_hooks("error_capture_log") or []
			if len(error_hooks) > 0:
				for error_hook in error_hooks:
					frappe.call(error_hook, async=True)
			else:
				log("Error calling hook method: {}->{}".format(hook_name, hook))
				log(frappe.get_traceback())

class GatewaySelectorProxy(Document):

	def on_payment_authorized(self, payment_status):

		reference_doc = frappe.get_doc(
			self.reference_doctype,
			self.reference_docname)

		# This may be a quotation, sales order or sales invoice
		order_doc = frappe.get_doc(
			reference_doc.reference_doctype,
			reference_doc.get("reference_docname", reference_doc.get("reference_name"))
		)

		call_hook("gateway_selector_on_payment_authorized", transaction=self, order=order_doc, pr_result=None)

		result = reference_doc.run_method(
				"on_payment_authorized",
				payment_status)

		frappe.db.commit()

		return result
