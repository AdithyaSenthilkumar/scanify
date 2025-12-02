# scanify/scanify/report/team_wise_sales/team_wise_sales.py
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		{
			"fieldname": "team",
			"label": _("Team"),
			"fieldtype": "Link",
			"options": "Team Master",
			"width": 150
		},
		{
			"fieldname": "region",
			"label": _("Region"),
			"fieldtype": "Link",
			"options": "Region Master",
			"width": 150
		},
		{
			"fieldname": "total_stockists",
			"label": _("Total Stockists"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "total_sales",
			"label": _("Total Sales (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "avg_per_stockist",
			"label": _("Avg Per Stockist (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			ss.team,
			ss.region,
			COUNT(DISTINCT ss.stockist_code) as total_stockists,
			SUM(ss.total_sales_value) / 100000 as total_sales,
			(SUM(ss.total_sales_value) / COUNT(DISTINCT ss.stockist_code)) / 100000 as avg_per_stockist
		FROM 
			`tabStockist Statement` ss
		WHERE 
			ss.docstatus = 1
			{conditions}
		GROUP BY 
			ss.team, ss.region
		ORDER BY 
			total_sales DESC
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("from_date"):
		conditions += " AND ss.statement_month >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND ss.statement_month <= %(to_date)s"
	
	if filters.get("team"):
		conditions += " AND ss.team = %(team)s"
	
	if filters.get("region"):
		conditions += " AND ss.region = %(region)s"
	
	return conditions

def get_chart_data(data):
	labels = [d.get("team") for d in data]
	sales = [d.get("total_sales") for d in data]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Total Sales (₹ Lakhs)",
					"values": sales
				}
			]
		},
		"type": "bar"
	}
