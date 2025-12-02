# scanify/scanify/report/hq_wise_sales/hq_wise_sales.py
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
			"fieldname": "hq",
			"label": _("HQ"),
			"fieldtype": "Link",
			"options": "HQ Master",
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
			"fieldname": "total_stockists",
			"label": _("Total Stockists"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "opening_value",
			"label": _("Opening Value (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "purchase_value",
			"label": _("Purchase Value (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "sales_value",
			"label": _("Sales Value (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "closing_value",
			"label": _("Closing Value (₹ Lakhs)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			ss.hq,
			ss.team,
			ss.region,
			COUNT(DISTINCT ss.stockist_code) as total_stockists,
			SUM(ss.total_opening_value) / 100000 as opening_value,
			SUM(ss.total_purchase_value) / 100000 as purchase_value,
			SUM(ss.total_sales_value) / 100000 as sales_value,
			SUM(ss.total_closing_value) / 100000 as closing_value
		FROM 
			`tabStockist Statement` ss
		WHERE 
			ss.docstatus = 1
			{conditions}
		GROUP BY 
			ss.hq, ss.team, ss.region
		ORDER BY 
			sales_value DESC
	""", filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = ""
	
	if filters.get("from_date"):
		conditions += " AND ss.statement_month >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND ss.statement_month <= %(to_date)s"
	
	if filters.get("hq"):
		conditions += " AND ss.hq = %(hq)s"
	
	if filters.get("team"):
		conditions += " AND ss.team = %(team)s"
	
	if filters.get("region"):
		conditions += " AND ss.region = %(region)s"
	
	return conditions

def get_chart_data(data):
	if not data:
		return None
	
	labels = [d.get("hq") for d in data[:10]]  # Top 10 HQs
	sales = [d.get("sales_value") for d in data[:10]]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Sales Value (₹ Lakhs)",
					"values": sales
				}
			]
		},
		"type": "bar",
		"height": 300
	}
