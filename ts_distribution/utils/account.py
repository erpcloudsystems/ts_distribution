from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.document import Document


@frappe.whitelist()
def getAccount(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select default_account from `tabMode of Payment Account` where 
		parent = '{0}' and company = '{1}' """.format(filters.get("name"),filters.get("company"))
	)

@frappe.whitelist(allow_guest=True)
def getDefaultAccount(method,company):
	account = frappe.db.sql(
		"""select default_account from `tabMode of Payment Account` where idx = 1 and parent = '{0}' and 
		company = '{1}';""".format(method,company))
	return account[0][0] if account else ""