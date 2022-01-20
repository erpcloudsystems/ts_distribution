from __future__ import unicode_literals
import frappe
from frappe import msgprint, throw, _
from frappe.utils import flt, get_url, money_in_words
from frappe.contacts.doctype.address.address import get_address_display
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.model.document import Document
from erpnext.accounts.utils import reconcile_against_document
from erpnext.accounts.party import get_party_account

def validate(doc, method):
	sales_order = ""
	for so in doc.items:
		sales_order = so.sales_order

	payment_entries_against_order = frappe.db.sql("""
			select
				"Payment Entry" as reference_type, t1.name as reference_name,
				t1.remarks as remarks, t2.allocated_amount as amount, t2.name as reference_row,
				t2.reference_name as against_order, t1.posting_date
			from `tabPayment Entry` t1, `tabPayment Entry Reference` t2
			where
				t1.name = t2.parent and t1.payment_type = "Receive"
				and t1.party_type = "Customer" and t1.party = %s and t1.docstatus = 1
				and t2.reference_doctype = "Sales Order" and t2.reference_name = %s
			order by t1.posting_date desc
		""",(doc.customer,sales_order), as_dict=1)

	doc.advances = []
	for d in payment_entries_against_order:
		advance = doc.append("advances",{})
		advance.reference_type = "Payment Entry"
		advance.reference_name = d.reference_name
		advance.remarks = d.remarks
		advance.advance_amount = d.amount
		advance.allocated_amount = d.amount
		advance.reference_row = d.reference_row

def on_submit(doc, method):
	publish_message(doc)
	validate_stock(doc)
	if len(doc.multiple_payment) > 0:
		create_multi_payment_entry(doc)

	if doc.distribution_type == "Direct Sales":
		make_delivery_note(doc.name)	

def create_multi_payment_entry(doc):
	payment_entry_count =  0
	for mpe in doc.multiple_payment:
		if (mpe.amount > 0 and 
			mpe.payment_method and 
			mpe.create_payment_entry_on_delivery == 1):
			pe = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": "Receive",
			"company": doc.company,
			"cost_center": doc.cost_center,
			"posting_date": doc.posting_date,
			"mode_of_payment": mpe.payment_method,
			"party_type": "Customer",
			"party": doc.customer,
			"party_name": doc.customer_name,
			"paid_from": doc.debit_to,
			"paid_to": mpe.account,
			"paid_amount": mpe.amount,
			"base_paid_amount": mpe.amount,
			"received_amount": mpe.amount,
			"received_amount": mpe.amount,
			"base_received_amount": mpe.amount,
			"reference_no": doc.name,
			"reference_date": doc.posting_date,
			"delivery_payment_transaction_id": mpe.name,
			"references": [{
				"reference_doctype": "Sales Invoice",
				"reference_name": doc.name,
				"due_date": doc.due_date,
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
	doc.reload()

def publish_message(doc):
	for d in doc.multiple_payment:
		if d.create_payment_entry_on_delivery != frappe.db.get_value("Mode of Payment",d.payment_method,"create_payment_entry_on_delivery"):
			frappe.msgprint(_('Mode of Payment setting changes detected in <b>Row : {0}</b> for Mode of Payment <b>{1}</b>  \
			<br><br>Old changes will not be overrite with new changes.').format(d.idx,d.payment_method))

def validate_stock(doc):
	for d in doc.items:
		balance_qty = frappe.db.get_value('Bin',{'item_code':d.item_code,'warehouse':d.warehouse},'actual_qty') or 0.0
		deficiency = flt(balance_qty - d.qty)
		if balance_qty < d.qty:
			msg = _("{0} units of {1} needed in {2} to complete this transaction.").format(
					abs(deficiency), frappe.get_desk_link('Item', d.item_code),
					frappe.get_desk_link('Warehouse', d.warehouse))
			frappe.throw(msg)

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = flt(source_doc.qty) - flt(source_doc.delivered_qty)
		target_doc.stock_qty = target_doc.qty * flt(source_doc.conversion_factor)

		target_doc.base_amount = target_doc.qty * flt(source_doc.base_rate)
		target_doc.amount = target_doc.qty * flt(source_doc.rate)

	doclist = get_mapped_doc("Sales Invoice", source_name, 	{
		"Sales Invoice": {
			"doctype": "Delivery Note",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Invoice Item": {
			"doctype": "Delivery Note Item",
			"field_map": {
				"name": "si_detail",
				"parent": "against_sales_invoice",
				"serial_no": "serial_no",
				"sales_order": "against_sales_order",
				"so_detail": "so_detail",
				"cost_center": "cost_center"
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.delivered_by_supplier!=1
		},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges",
			"add_if_empty": True
		},
		"Sales Team": {
			"doctype": "Sales Team",
			"field_map": {
				"incentives": "incentives"
			},
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	doclist.insert(ignore_permissions=True, ignore_mandatory=True)
	doclist.save(ignore_permissions=True)
	doclist.submit()
	url = get_url("/app/delivery-note")
	frappe.msgprint(_("<b><a href={0}>Delivery Note</a></b> Created").format(url))