frappe.ui.form.on('HQ Master', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Stockists'), function() {
				frappe.set_route('List', 'Stockist Master', {
					'hq': frm.doc.name
				});
			});
			
			frm.add_custom_button(__('View Sales Report'), function() {
				frappe.set_route('query-report', 'HQ Wise Sales', {
					'hq': frm.doc.name
				});
			});
		}
	},
	
	team: function(frm) {
		if (frm.doc.team) {
			frappe.db.get_value('Team Master', frm.doc.team, 'region', (r) => {
				frm.set_value('region', r.region);
			});
		}
	}
});
