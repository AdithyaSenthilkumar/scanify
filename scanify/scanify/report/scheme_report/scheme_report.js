frappe.query_reports["Scheme Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "approval_status",
			"label": __("Approval Status"),
			"fieldtype": "Select",
			"options": "\nPending\nApproved\nRejected"
		},
		{
			"fieldname": "region",
			"label": __("Region"),
			"fieldtype": "Link",
			"options": "Region Master"
		},
		{
			"fieldname": "team",
			"label": __("Team"),
			"fieldtype": "Link",
			"options": "Team Master"
		},
		{
			"fieldname": "doctor_code",
			"label": __("Doctor"),
			"fieldtype": "Link",
			"options": "Doctor Master"
		},
		{
			"fieldname": "stockist_code",
			"label": __("Stockist"),
			"fieldtype": "Link",
			"options": "Stockist Master"
		}
	]
};
