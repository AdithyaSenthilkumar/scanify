frappe.query_reports["Stockist Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -6),
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
			"options": "Team Master",
			"get_query": function() {
				let region = frappe.query_report.get_filter_value('region');
				if (region) {
					return {
						"filters": {
							"region": region
						}
					};
				}
			}
		},
		{
			"fieldname": "hq",
			"label": __("HQ"),
			"fieldtype": "Link",
			"options": "HQ Master",
			"get_query": function() {
				let team = frappe.query_report.get_filter_value('team');
				if (team) {
					return {
						"filters": {
							"team": team
						}
					};
				}
			}
		},
		{
			"fieldname": "stockist_code",
			"label": __("Stockist"),
			"fieldtype": "Link",
			"options": "Stockist Master",
			"get_query": function() {
				let hq = frappe.query_report.get_filter_value('hq');
				if (hq) {
					return {
						"filters": {
							"hq": hq
						}
					};
				}
			}
		}
	]
};
