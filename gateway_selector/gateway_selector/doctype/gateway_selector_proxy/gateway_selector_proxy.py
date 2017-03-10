# -*- coding: utf-8 -*-
# Copyright (c) 2015, DigiThinkIT, Inc. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GatewaySelectorProxy(Document):

	def on_payment_authorized(payment_status):
		return frappe.get_doc(
			self.reference_doctype,
			self.reference_docname).run_method("on_payment_authorized",
			payment_status)
