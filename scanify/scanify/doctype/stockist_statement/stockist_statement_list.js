// scanify/scanify/doctype/stockist_statement/stockist_statement_list.js
frappe.listview_settings['Stockist Statement'] = {
	add_fields: ["extracted_data_status", "total_sales_value", "stockist_name"],
	get_indicator: function(doc) {
		if (doc.docstatus === 1) {
			return [__("Submitted"), "green", "docstatus,=,1"];
		} else if (doc.extracted_data_status === "Completed") {
			return [__("Data Extracted"), "blue", "extracted_data_status,=,Completed"];
		} else if (doc.extracted_data_status === "Failed") {
			return [__("Extraction Failed"), "red", "extracted_data_status,=,Failed"];
		} else if (doc.extracted_data_status === "In Progress") {
			return [__("Processing"), "orange", "extracted_data_status,=,In Progress"];
		} else {
			return [__("Draft"), "gray", "docstatus,=,0"];
		}
	},
	onload: function(listview) {
		listview.page.add_inner_button(__("Bulk Extract Data"), function() {
			let selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__("Please select statements to extract"));
				return;
			}
			
			frappe.confirm(
				__("Extract data for {0} statements?", [selected.length]),
				() => {
					selected.forEach(doc => {
						frappe.call({
							method: 'scanify.api.extract_stockist_statement',
							args: {
								doc_name: doc.name,
								file_url: doc.uploaded_file
							}
						});
					});
					frappe.msgprint(__("Extraction started for selected statements"));
				}
			);
		});
	}
};
