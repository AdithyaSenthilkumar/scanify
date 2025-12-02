frappe.query_reports["Team Wise Sales"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_start(),
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
		}
	]
};
