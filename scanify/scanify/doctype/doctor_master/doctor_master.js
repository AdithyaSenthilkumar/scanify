frappe.ui.form.on('Doctor Master', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Scheme History'), function() {
				frappe.set_route('List', 'Scheme Request', {
					'doctor_code': frm.doc.name
				});
			});
			
			frm.add_custom_button(__('Create Scheme Request'), function() {
				frappe.new_doc('Scheme Request', {
					'doctor_code': frm.doc.name
				});
			});
		}
	}
});
