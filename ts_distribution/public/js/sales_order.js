// Copyright (c) 2021, Tech Station and contributors
// For license information, please see license.txt

cur_frm.add_fetch('payment_method',  'create_payment_entry_on_so',  'create_payment_entry_on_so');
cur_frm.add_fetch('payment_method',  'create_payment_entry_on_delivery',  'create_payment_entry_on_delivery');
cur_frm.add_fetch('item_code',  'shipping_discount',  'shipping_discount');

frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		frm.set_query("payment_method", "multiple_payment", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Mode of Payment', 'name', 'not in', "Paid,Gift"],
				]
			};
		});

		frm.set_query("account", "multiple_payment", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				query: "ts_distribution.utils.account.getAccount",
				filters: {
					'name': d.payment_method,
					'company': frm.doc.company
				}
			};
		});

		frm.set_query("customer_driver", function () {
			return {
				"filters": {
					"customer": frm.doc.customer,
				}
			};
		});

		update_multipayment_status(frm);
	},
	distribution_type: function(frm) {
		frm.set_value("transportation_vehicle","");
		frm.set_value("vehicle_type","");
		frappe.db.get_value(frm.doc.distribution_type, frm.doc.sales_type, "warehouse", (r) => {
				frm.set_value("set_warehouse",r.warehouse);
		});
	},
	transportation_vehicle: function(frm) {
		frm.set_value("vehicle_type","");
		set_total_discount(frm);
	},
	customer: function(frm) {
		if (frm.doc.customer && frm.doc.company) {
			frappe.call({
				method: "ts_distribution.hook.sales_order.getCredit_Limit",
				args: {
					customer: frm.doc.customer,
					company: frm.doc.company
				},
				callback: function (r) {
					if(r.message){
						frm.set_value("customer_credit_limit", r.message);
					}
					else{
						frm.set_value("customer_credit_limit", 0);
					}
				}
			});
		}
	},
	fetch_advance_payment: function (frm) {
		set_advance_entries(frm);
	},
	before_save: function (frm) {
		if(frm.doc.docstatus === 0){
			set_totals(frm);
		}
	},
});

frappe.ui.form.on("Sales Order Item", {
	"rate": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	},
	"qty": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	},
	"shipping_discount": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	},
	"total_shipping_discount": function (frm, cdt, cdn) {
		set_total_discount(frm);
	}
});

frappe.ui.form.on("TD Multiple Payment", {
	"payment_method": function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.payment_method) {
			frappe.call({
				"method": "ts_distribution.utils.account.getDefaultAccount",
				args: {
					method: d.payment_method,
					company: frm.doc.company
				},
				callback: function (r) {
					frappe.model.set_value(d.doctype, d.name, "account", r.message);
				}
			});

		}
	},
	"amount": function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var paid_amount = 0;
		var unpaid_amount = 0;
		var multiple_payment = frm.doc.multiple_payment;

		for (var i in multiple_payment) {
			if(multiple_payment[i].create_payment_entry_on_so  == 1){
				paid_amount = paid_amount + multiple_payment[i].amount;
			}
			if(multiple_payment[i].create_payment_entry_on_so === 0){
				unpaid_amount = unpaid_amount + multiple_payment[i].amount;
			}	
		}
			frm.set_value("paid_amount", paid_amount);
			frm.set_value("unpaid_amount", unpaid_amount);
			set_totals(frm);
			frm.refresh_fields();

		if((paid_amount + unpaid_amount + frm.doc.advance_amount_adjusted) > frm.doc.rounded_total){
			frappe.model.set_value(d.doctype, d.name, "amount", 0.0);
			frappe.throw(__("Payment amount can not be higher then rounded total <b>"+frm.doc.rounded_total+"</b>"));
		}
	},
	"multiple_payment_remove": function (frm, cdt, cdn) {
		var paid_amount = 0;
		var unpaid_amount = 0;
		var multiple_payment = frm.doc.multiple_payment;

		for (var i in multiple_payment) {
			if(multiple_payment[i].create_payment_entry_on_so  == 1){
				paid_amount = paid_amount + multiple_payment[i].amount;
			}
			if(multiple_payment[i].create_payment_entry_on_so === 0){
				unpaid_amount = unpaid_amount + multiple_payment[i].amount;
			}
		}
			frm.set_value("paid_amount", paid_amount);
			frm.set_value("unpaid_amount", unpaid_amount);
			set_totals(frm);
			frm.refresh_fields();
	}
});

frappe.ui.form.on("TD Advance Customer Payment", {
	"adjust_amount": function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var total = 0;
		var advance = frm.doc.advance_customer_payment;

		if(d.adjust_amount > d.unallocated_amount){
			frappe.model.set_value(d.doctype, d.name, "adjust_amount", 0.0);
			frappe.throw(__("Adjust amount can not be higher then advance amount <b>"+d.unallocated_amount+"</b>"));
		}
		else{
			for (var i in advance) {
				total = total + advance[i].adjust_amount;
			}
				frm.set_value("advance_amount_adjusted", total);
				set_totals(frm);
				frm.refresh_fields();
		}
		if(total > frm.doc.rounded_total){
			frappe.model.set_value(d.doctype, d.name, "adjust_amount", 0.0);
			frappe.throw(__("Total advance adjust amount can not be higher then rounded total <b>"+frm.doc.rounded_total+"</b>"));
		}
	},
	"advance_customer_payment_remove": function (frm, cdt, cdn) {
		var total = 0;
		var advance = frm.doc.advance_customer_payment;

		for (var i in advance) {
			total = total + advance[i].adjust_amount;
		}
			frm.set_value("advance_amount_adjusted", total);
			frm.refresh_fields();
	}
});

function set_advance_entries(frm) {
	if(frm.doc.customer){
		frappe.call({
			"method": "ts_distribution.hook.sales_order.return_unallocated_amount",
			args: {
				customer: frm.doc.customer
			},
			callback: function (r) {
				if (r.message) {
					frm.doc.advance_customer_payment = [];
					for (var payment_entry in r.message) {
						var payment_entry = r.message[payment_entry]
						var a = frm.add_child("advance_customer_payment");
						a.payment_entry = payment_entry.name;
						a.payment_received_date = payment_entry.posting_date;
						a.payment_method = payment_entry.mode_of_payment;
						a.unallocated_amount = payment_entry.unallocated_amount;
						a.paid_to = payment_entry.paid_to;
					}
					frm.refresh_fields();
				}
			}
		});
	}
}

function set_discount(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if(row.rate && row.rate < row.shipping_discount){
		frappe.throw(__("Rate Can Not Be Lesser Then Shipping Discount <b>{0}.</b>",[row.shipping_discount]));
	}
	else{
		frappe.model.set_value(cdt, cdn, "total_shipping_discount", row.qty * row.shipping_discount);
	}
}

function set_total_discount(frm) {
	var total_discount = 0;
	var items = frm.doc.items;
	for (var i = 0; i < items.length; i++) {
		total_discount += items[i].total_shipping_discount;
	}
	if(frm.doc.distribution_type == "Indirect Sales" && frm.doc.transportation_vehicle == "Customer Vehicles"){
		frm.set_value("discount_amount", total_discount);
		frm.refresh_fields();
	}
	else{
		frm.set_value("discount_amount", 0.0);
		frm.refresh_fields();
	}
}

function set_totals(frm) {
	frm.set_value("outstanding_amount",frm.doc.rounded_total - (frm.doc.advance_amount_adjusted + frm.doc.paid_amount));
}

function update_multipayment_status(frm) {
	$.each(frm.doc.multiple_payment,  function(i,  d) {
		if(!frm.is_new() && d.payment_method){
		frappe.call({
			method: "ts_distribution.hook.sales_order.get_PaymentEntry_data",
			args: {
				order_no: frm.doc.name,
				mode_of_payment: d.payment_method,
				paid_amount: d.amount,
			},
			callback: function (r) {
				if (r.message == 1 && d.create_payment_entry_on_delivery === 0){
					d.status = "<span class=\"indicator-pill whitespace-nowrap green\"> <span>Paid</span></span>";
				}
				else{
					d.status = "<span class=\"indicator-pill whitespace-nowrap orange\"> <span>Unpaid</span></span>";
				}
				frm.refresh_fields();
			}
		});
		}
		if(d.create_payment_entry_on_delivery === 0 && d.create_payment_entry_on_so == 0){
			d.payment_stage = "<span class=\"indicator-pill whitespace-nowrap red\"><span>Payment Not Specified</span></span>";
		}
		if(d.create_payment_entry_on_delivery === 0 && d.create_payment_entry_on_so == 1){
			d.payment_stage = "<span class=\"indicator-pill whitespace-nowrap green\"><span>Advance Payment</span></span>";
		}
		if(d.create_payment_entry_on_delivery === 1 && d.create_payment_entry_on_so == 0){
			d.payment_stage = "<span class=\"indicator-pill whitespace-nowrap orange\"><span>Payment With Delivery</span></span>";
		}
	});
}