frappe.ui.form.on('Team Master', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View HQs'), function() {
				frappe.set_route('List', 'HQ Master', {
					'team': frm.doc.name
				});
			});
			
			frm.add_custom_button(__('View Sales Report'), function() {
				frappe.set_route('query-report', 'Team Wise Sales', {
					'team': frm.doc.name
				});
			});
		}
	}
});
