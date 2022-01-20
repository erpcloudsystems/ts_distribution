// Copyright (c) 2021, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('External Vehicles', {
	refresh: function(frm) {
		frm.set_query("territory", function () {
			return {
				"filters": {
					"enabled": 1,
					"is_group": 0
				}
			};
		});

		frm.set_query("sub_territory", function () {
			return {
				"filters": {
					"parent_territory": frm.doc.territory,
					"enabled": 1
				}
			};
		});
	}
});
