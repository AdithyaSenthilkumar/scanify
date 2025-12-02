// scanify/scanify/doctype/scheme_request/scheme_request_list.js
frappe.listview_settings['Scheme Request'] = {
	add_fields: ["approval_status", "total_scheme_value", "doctor_name", "stockist_name"],
	get_indicator: function(doc) {
		if (doc.approval_status === "Approved") {
			return [__("Approved"), "green", "approval_status,=,Approved"];
		} else if (doc.approval_status === "Rejected") {
			return [__("Rejected"), "red", "approval_status,=,Rejected"];
		} else {
			return [__("Pending"), "orange", "approval_status,=,Pending"];
		}
	},
	onload: function(listview) {
		if (frappe.user.has_role('Sales Manager') || frappe.user.has_role('System Manager')) {
			listview.page.add_inner_button(__("Bulk Approve"), function() {
				let selected = listview.get_checked_items();
				if (selected.length === 0) {
					frappe.msgprint(__("Please select scheme requests"));
					return;
				}
				
				frappe.prompt([
					{
						fieldname: 'comments',
						fieldtype: 'Small Text',
						label: 'Approval Comments',
						reqd: 1
					}
				], (values) => {
					selected.forEach(doc => {
						if (doc.approval_status === 'Pending') {
							frappe.call({
								method: 'scanify.api.approve_scheme_request',
								args: {
									doc_name: doc.name,
									comments: values.comments
								}
							});
						}
					});
					frappe.msgprint(__("Approval process started"));
					setTimeout(() => listview.refresh(), 2000);
				}, __('Bulk Approve Schemes'));
			});
		}
	}
};
