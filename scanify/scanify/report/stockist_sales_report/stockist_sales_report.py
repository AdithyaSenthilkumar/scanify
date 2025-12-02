import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "stockist_code",
			"label": _("Stockist Code"),
			"fieldtype": "Link",
			"options": "Stockist Master",
			"width": 120
		},
		{
			"fieldname": "stockist_name",
			"label": _("Stockist Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "hq",
			"label": _("HQ"),
			"fieldtype": "Link",
			"options": "HQ Master",
			"width": 120
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
			"fieldname": "statement_month",
			"label": _("Month"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "opening_value",
			"label": _("Opening Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "purchase_value",
			"label": _("Purchase Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "sales_value",
			"label": _("Sales Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "closing_value",
			"label": _("Closing Value"),
			"fieldtype": "Currency",
			"width": 120
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			ss.stockist_code,
			ss.stockist_name,
			ss.hq,
			ss.team,
			ss.region,
			ss.statement_month,
			ss.total_opening_value as opening_value,
			ss.total_purchase_value as purchase_value,
			ss.total_sales_value as sales_value,
			ss.total_closing_value as closing_value
		FROM 
			`tabStockist Statement` ss
		WHERE 
			ss.docstatus = 1
			{conditions}
		ORDER BY 
			ss.statement_month DESC, ss.stockist_name
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("from_date"):
		conditions += " AND ss.statement_month >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND ss.statement_month <= %(to_date)s"
	
	if filters.get("stockist_code"):
		conditions += " AND ss.stockist_code = %(stockist_code)s"
	
	if filters.get("hq"):
		conditions += " AND ss.hq = %(hq)s"
	
	if filters.get("team"):
		conditions += " AND ss.team = %(team)s"
	
	if filters.get("region"):
		conditions += " AND ss.region = %(region)s"
	
	return conditions
