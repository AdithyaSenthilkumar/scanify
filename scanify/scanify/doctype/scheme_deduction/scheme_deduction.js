frappe.ui.form.on('Scheme Deduction', {
	refresh: function(frm) {
		// Add custom button for manual refresh
		if (frm.doc.docstatus === 0 && frm.doc.scheme_request && frm.doc.stockist_statement) {
			frm.add_custom_button(__('Reload Items'), function() {
				load_items(frm);
			}, __('Actions'));
		}
		
		// Set filters and queries
		set_scheme_query(frm);
		set_statement_filter(frm);
	},
	
	onload: function(frm) {
		set_scheme_query(frm);
	},
	
	scheme_request: function(frm) {
		if (frm.doc.scheme_request) {
			// Fetch scheme details
			frappe.db.get_value('Scheme Request', frm.doc.scheme_request, 
				['stockist_code', 'application_date', 'doctor_code'], (r) => {
				if (r) {
					frm.set_value('stockist_code', r.stockist_code);
					frm.set_value('scheme_date', r.application_date);
					frm.set_value('doctor_code', r.doctor_code);
					
					// Auto-load items if statement is also selected
					if (frm.doc.stockist_statement) {
						load_items(frm);
					}
				}
			});
		}
		
		set_statement_filter(frm);
	},
	
	stockist_statement: function(frm) {
		// Auto-load items when statement is selected
		if (frm.doc.scheme_request && frm.doc.stockist_statement) {
			load_items(frm);
		}
	},
	
	stockist_code: function(frm) {
		set_statement_filter(frm);
	}
});

frappe.ui.form.on('Scheme Deduction Item', {
	deduct_qty: function(frm, cdt, cdn) {
		calculate_item_value(frm, cdt, cdn);
	},
	
	pts: function(frm, cdt, cdn) {
		calculate_item_value(frm, cdt, cdn);
	}
});

function set_scheme_query(frm) {
	frm.set_query('scheme_request', function() {
		return {
			filters: {
				'docstatus': 1  // Only submitted schemes
			},
			query: 'scanify.scanify.doctype.scheme_deduction.scheme_deduction.get_scheme_requests',
			page_length: 20
		};
	});
}

function set_statement_filter(frm) {
	if (frm.doc.stockist_code) {
		frm.set_query('stockist_statement', function() {
			return {
				filters: {
					'stockist_code': frm.doc.stockist_code,
					'docstatus': ['!=', 2]  // Exclude cancelled
				},
				query: 'scanify.scanify.doctype.scheme_deduction.scheme_deduction.get_stockist_statements',
				page_length: 20
			};
		});
	}
}

function load_items(frm) {
	if (!frm.doc.scheme_request) {
		frappe.msgprint(__('Please select a Scheme Request first'));
		return;
	}
	
	if (!frm.doc.stockist_statement) {
		frappe.msgprint(__('Please select a Stockist Statement first'));
		return;
	}
	
	frappe.call({
		method: 'scanify.scanify.doctype.scheme_deduction.scheme_deduction.fetch_and_populate_items',
		args: {
			scheme_request: frm.doc.scheme_request,
			stockist_statement: frm.doc.stockist_statement
		},
		freeze: true,
		freeze_message: __('Loading scheme items...'),
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				frm.clear_table('items');
				
				r.message.forEach(item => {
					let row = frm.add_child('items');
					row.product_code = item.product_code;
					row.product_name = item.product_name;
					row.pack = item.pack;
					row.scheme_free_qty = item.scheme_free_qty;
					row.current_free_qty = item.current_free_qty;
					row.deduct_qty = item.deduct_qty;
					row.pts = item.pts;
					row.deducted_value = item.deducted_value;
				});
				
				frm.refresh_field('items');
				calculate_totals(frm);
				
				frappe.show_alert({
					message: __(`Loaded ${r.message.length} items from scheme`),
					indicator: 'green'
				});
			} else {
				frappe.msgprint(__('No items found in scheme request'));
			}
		},
		error: function(r) {
			frappe.msgprint({
				title: __('Error'),
				message: __('Failed to load items. Please try again.'),
				indicator: 'red'
			});
		}
	});
}

function calculate_item_value(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	row.deducted_value = flt(row.deduct_qty) * flt(row.pts);
	frm.refresh_field('items');
	calculate_totals(frm);
}

function calculate_totals(frm) {
	let total_qty = 0;
	let total_value = 0;
	
	if (frm.doc.items) {
		frm.doc.items.forEach(item => {
			total_qty += flt(item.deduct_qty);
			total_value += flt(item.deducted_value);
		});
	}
	
	frm.set_value('total_deducted_qty', total_qty);
	frm.set_value('total_deducted_value', total_value);
}
