// Copyright (c) 2021, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer', {
	distribution_type: function(frm) {
		frm.set_value("sales_type","");
	}
});
