// scanify/scanify/doctype/stockist_statement/stockist_statement.js
frappe.ui.form.on('Stockist Statement', {
	refresh: function(frm) {
		if (frm.doc.uploaded_file && frm.doc.extracted_data_status === 'Pending' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Extract Data with AI'), function() {
				extract_statement_data(frm);
			});
		}
		
		if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Fetch Previous Month Closing'), function() {
				fetch_previous_closing(frm);
			});
		}
		
		// Add custom button to view statement file
		if (frm.doc.uploaded_file) {
			frm.add_custom_button(__('View Uploaded File'), function() {
				window.open(frm.doc.uploaded_file, '_blank');
			});
		}
	},
	
	statement_month: function(frm) {
		if (frm.doc.statement_month) {
			// Auto-set from_date and to_date
			let month_date = frappe.datetime.str_to_obj(frm.doc.statement_month);
			let first_day = frappe.datetime.get_first_day_of_the_month(frm.doc.statement_month);
			let last_day = frappe.datetime.get_last_day_of_the_month(frm.doc.statement_month);
			
			frm.set_value('from_date', first_day);
			frm.set_value('to_date', last_day);
		}
	}
});

frappe.ui.form.on('Stockist Statement Item', {
	opening_qty: function(frm, cdt, cdn) {
		calculate_item_closing(frm, cdt, cdn);
	},
	
	purchase_qty: function(frm, cdt, cdn) {
		calculate_item_closing(frm, cdt, cdn);
	},
	
	sales_qty: function(frm, cdt, cdn) {
		calculate_item_closing(frm, cdt, cdn);
	},
	
	return_qty: function(frm, cdt, cdn) {
		calculate_item_closing(frm, cdt, cdn);
	},
	
	misc_out_qty: function(frm, cdt, cdn) {
		calculate_item_closing(frm, cdt, cdn);
	},
	
	product_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.product_code) {
			frappe.db.get_value('Product Master', row.product_code, ['product_name', 'pack', 'pts'], (r) => {
				frappe.model.set_value(cdt, cdn, 'product_name', r.product_name);
				frappe.model.set_value(cdt, cdn, 'pack', r.pack);
				frappe.model.set_value(cdt, cdn, 'pts', r.pts);
				calculate_item_closing(frm, cdt, cdn);
			});
		}
	}
});

function calculate_item_closing(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	// Closing = Opening + Purchase - Sales - Return - Misc Out
	let closing_qty = flt(row.opening_qty) + flt(row.purchase_qty) - flt(row.sales_qty) - flt(row.return_qty) - flt(row.misc_out_qty);
	frappe.model.set_value(cdt, cdn, 'closing_qty', closing_qty);
	
	// Closing Value = Closing Qty * PTS
	let closing_value = closing_qty * flt(row.pts);
	frappe.model.set_value(cdt, cdn, 'closing_value', closing_value);
	
	// Recalculate totals
	calculate_totals(frm);
}

function calculate_totals(frm) {
	let total_opening = 0;
	let total_purchase = 0;
	let total_sales = 0;
	let total_closing = 0;
	
	frm.doc.items.forEach(item => {
		total_opening += flt(item.opening_qty) * flt(item.pts);
		total_purchase += flt(item.purchase_qty) * flt(item.pts);
		total_sales += flt(item.sales_qty) * flt(item.pts);
		total_closing += flt(item.closing_value);
	});
	
	frm.set_value('total_opening_value', total_opening);
	frm.set_value('total_purchase_value', total_purchase);
	frm.set_value('total_sales_value', total_sales);
	frm.set_value('total_closing_value', total_closing);
}

function extract_statement_data(frm) {
	frappe.call({
		method: 'scanify.api.extract_stockist_statement',
		args: {
			doc_name: frm.doc.name,
			file_url: frm.doc.uploaded_file
		},
		freeze: true,
		freeze_message: __('Extracting data using AI...'),
		callback: function(r) {
			if (r.message) {
				frm.reload_doc();
				frappe.msgprint(__('Data extracted successfully!'));
			}
		}
	});
}

function fetch_previous_closing(frm) {
	frappe.call({
		method: 'scanify.api.fetch_previous_month_closing',
		args: {
			stockist_code: frm.doc.stockist_code,
			current_month: frm.doc.statement_month
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				// Clear existing items
				frm.clear_table('items');
				
				// Add items with opening balance
				r.message.forEach(item => {
					let row = frm.add_child('items');
					row.product_code = item.product_code;
					row.product_name = item.product_name;
					row.pack = item.pack;
					row.opening_qty = item.closing_qty;
					row.pts = item.pts;
					row.closing_qty = item.closing_qty;
					row.closing_value = item.closing_value;
				});
				
				frm.refresh_field('items');
				calculate_totals(frm);
				frappe.msgprint(__('Previous month closing balance loaded'));
			} else {
				frappe.msgprint(__('No previous month data found'));
			}
		}
	});
}
