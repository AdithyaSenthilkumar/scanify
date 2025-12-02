frappe.ui.form.on('Product Master', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage in Statements'), function() {
				frappe.set_route('query-report', 'Product Wise Sales', {
					'product_code': frm.doc.name
				});
			});
		}
	},
	
	mrp: function(frm) {
		if (frm.doc.mrp && !frm.doc.pts) {
			let suggested_pts = frm.doc.mrp * 0.69;
			frappe.msgprint(__('Suggested PTS (69% of MRP): ₹') + suggested_pts.toFixed(2));
		}
	}
});
