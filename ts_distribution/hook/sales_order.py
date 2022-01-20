from __future__ import unicode_literals
import frappe
from frappe import msgprint, throw, _
from frappe.utils import flt, get_url, money_in_words
from frappe.model.document import Document
from erpnext.accounts.utils import reconcile_against_document
from erpnext.accounts.party import get_party_account

def validate(doc,method):
	validate_discount(doc)
	if doc.outstanding_amount > 0:
		if len(doc.multiple_payment) == 0:
			frappe.throw("Please add payment method and account in <b>Multiple Payment</b> table")

def on_submit(doc, method):
	publish_message(doc)
	validate_discount(doc)
	if len(doc.multiple_payment) > 0:
		create_multi_payment_entry(doc)

	if len(doc.advance_customer_payment) > 0:
		updatePaymentEntry(doc)

def validate_discount(doc):
	if doc.distribution_type == "Indirect Sales" and doc.transportation_vehicle == "Customer Vehicles":
		for d in doc.items:
			if d.rate < d.shipping_discount:
				frappe.throw(_("Row <b>{0}</b>, Item Code <b>{1}</b><br><br>Rate Can Not Be Lesser Then \
				Shipping Discount <b>{2}</b>").format(d.idx,d.item_code,d.shipping_discount))

@frappe.whitelist()
def getCredit_Limit(customer,company):
	credit_limit = frappe.db.sql("""select sum(credit_limit) from `tabCustomer Credit Limit` 
    where parent = %s and company = %s;""",(customer,company)) or 0.0
	return credit_limit[0][0] if credit_limit else 0.0

@frappe.whitelist()
def return_unallocated_amount(customer):
	data = []
	payment_entry_list = frappe.db.sql("""select name,posting_date,mode_of_payment,unallocated_amount,paid_to
	from `tabPayment Entry` where unallocated_amount > 0 and docstatus = 1 and 
	party = %s order by posting_date desc;""",(customer),as_dict = True)

	for payment_entry in payment_entry_list:
		return_data = {}
		return_data["name"] = payment_entry.name
		return_data["posting_date"] = payment_entry.posting_date
		return_data["mode_of_payment"] = payment_entry.mode_of_payment
		return_data["unallocated_amount"] = payment_entry.unallocated_amount
		return_data["paid_to"] = payment_entry.paid_to
		data.append(return_data)
	return data

@frappe.whitelist()
def get_PaymentEntry_data(order_no,mode_of_payment,paid_amount):
	return frappe.db.get_value('Payment Entry', {'reference_no': order_no,'mode_of_payment': mode_of_payment,'paid_amount': paid_amount}, ['docstatus'])

def updatePaymentEntry(self):
	lst = []
	for d in self.get('advance_customer_payment'):
		if flt(d.adjust_amount) > 0:
			args = frappe._dict({
				'voucher_type': "Payment Entry",
				'voucher_no': d.payment_entry,
				'voucher_detail_no': d.reference_row,
				'against_voucher_type': self.doctype,
				'against_voucher': self.name,
				'account': get_party_account("Customer",self.customer,self.company),
				'party_type': "Customer",
				'party': self.customer,
				'is_advance': 'Yes',
				'dr_or_cr': "credit_in_account_currency",
				'unadjusted_amount': flt(d.unallocated_amount),
				'allocated_amount': flt(d.adjust_amount),
				'precision': d.precision('adjust_amount'),
				'grand_total': self.rounded_total,
				'outstanding_amount': flt(self.rounded_total - self.advance_paid),
				'difference_account': frappe.db.get_value('Company', self.company, 'exchange_gain_loss_account')
			})
			lst.append(args)

	if lst:
		from erpnext.accounts.utils import reconcile_against_document
		reconcile_against_document(lst)

def create_multi_payment_entry(doc):
	payment_entry_count =  0
	for mpe in doc.multiple_payment:
		if (mpe.amount > 0 and 
			mpe.payment_method and 
			mpe.create_payment_entry_on_so == 1):
			pe = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": "Receive",
			"company": doc.company,
			"cost_center": frappe.db.get_value("Company", doc.company, ["cost_center"]),
			"posting_date": doc.transaction_date,
			"mode_of_payment": mpe.payment_method,
			"party_type": "Customer",
			"party": doc.customer,
			"party_name": doc.customer_name,
			"paid_from": frappe.db.get_value("Company", doc.company, ["default_receivable_account"]),
			"paid_to": mpe.account,
			"paid_amount": mpe.amount,
			"base_paid_amount": mpe.amount,
			"received_amount": mpe.amount,
			"received_amount": mpe.amount,
			"base_received_amount": mpe.amount,
			"reference_no": doc.name,
			"reference_date": doc.transaction_date,
			"delivery_payment_transaction_id": mpe.name,
			"references": [{
				"reference_doctype": "Sales Order",
				"reference_name": doc.name,
				"due_date": doc.transaction_date,
				"total_amount": doc.rounded_total,
				"outstanding_amount": doc.rounded_total,
				"allocated_amount": mpe.amount,
			}],
			})
			pe.insert(ignore_permissions=True,ignore_if_duplicate=True,ignore_links=True,ignore_mandatory=True)
			pe.save()
			pe.submit()
			payment_entry_count += 1
	url = get_url("/app/payment-entry")
	frappe.msgprint(_("{0} <b><a href={1}>Payment Entry</a></b> Created").format(payment_entry_count,url))

def publish_message(doc):
	for d in doc.multiple_payment:
		if d.create_payment_entry_on_so != frappe.db.get_value("Mode of Payment",d.payment_method,"create_payment_entry_on_so"):
			frappe.msgprint(_('Mode of Payment setting changes detected in <b>Row : {0}</b> for Mode of Payment <b>{1}</b>  \
			<br><br>Old changes will not be overrite with new changes.').format(d.idx,d.payment_method))	