import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Scheme ID"),
			"fieldtype": "Link",
			"options": "Scheme Request",
			"width": 130
		},
		{
			"fieldname": "application_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "doctor_code",
			"label": _("Doctor Code"),
			"fieldtype": "Link",
			"options": "Doctor Master",
			"width": 100
		},
		{
			"fieldname": "doctor_name",
			"label": _("Doctor Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "doctor_place",
			"label": _("Place"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "stockist_code",
			"label": _("Stockist Code"),
			"fieldtype": "Link",
			"options": "Stockist Master",
			"width": 110
		},
		{
			"fieldname": "stockist_name",
			"label": _("Stockist Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "team",
			"label": _("Team"),
			"fieldtype": "Link",
			"options": "Team Master",
			"width": 120
		},
		{
			"fieldname": "region",
			"label": _("Region"),
			"fieldtype": "Link",
			"options": "Region Master",
			"width": 120
		},
		{
			"fieldname": "total_scheme_value",
			"label": _("Scheme Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "approval_status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "requested_by",
			"label": _("Requested By"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			name,
			application_date,
			doctor_code,
			doctor_name,
			doctor_place,
			stockist_code,
			stockist_name,
			team,
			region,
			total_scheme_value,
			approval_status,
			requested_by
		FROM 
			`tabScheme Request`
		WHERE 
			1=1
			{conditions}
		ORDER BY 
			application_date DESC
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("from_date"):
		conditions += " AND application_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND application_date <= %(to_date)s"
	
	if filters.get("approval_status"):
		conditions += " AND approval_status = %(approval_status)s"
	
	if filters.get("team"):
		conditions += " AND team = %(team)s"
	
	if filters.get("region"):
		conditions += " AND region = %(region)s"
	
	if filters.get("doctor_code"):
		conditions += " AND doctor_code = %(doctor_code)s"
	
	if filters.get("stockist_code"):
		conditions += " AND stockist_code = %(stockist_code)s"
	
	return conditions
