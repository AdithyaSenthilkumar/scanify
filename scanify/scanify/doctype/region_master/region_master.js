frappe.ui.form.on('Region Master', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Teams'), function() {
				frappe.set_route('List', 'Team Master', {
					'region': frm.doc.name
				});
			});
		}
	}
});
