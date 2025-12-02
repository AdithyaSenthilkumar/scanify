import frappe
from frappe import _
from frappe.utils import flt

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
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "opening_value",
			"label": _("Opening Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "primary_value",
			"label": _("Primary Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "sales_before_scheme",
			"label": _("Sales Before Scheme"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "scheme_value",
			"label": _("Scheme Value"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "sales_after_scheme",
			"label": _("Sales After Scheme"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "scheme_impact_pct",
			"label": _("Scheme Impact %"),
			"fieldtype": "Percent",
			"width": 130
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
	
	# Get stockist statements
	statements = frappe.db.sql(f"""
		SELECT 
			ss.stockist_code,
			ss.stockist_name,
			ss.hq,
			ss.team,
			DATE_FORMAT(ss.statement_month, '%%b %%Y') as month,
			ss.total_opening_value as opening_value,
			ss.total_purchase_value as primary_value,
			ss.total_sales_value as sales_before_scheme,
			ss.total_closing_value as closing_value,
			ss.statement_month
		FROM 
			`tabStockist Statement` ss
		WHERE 
			ss.docstatus = 1
			{conditions}
		ORDER BY 
			ss.statement_month, ss.stockist_name
	""", filters, as_dict=1)
	
	# Get scheme values for each stockist/month
	for row in statements:
		scheme_value = get_scheme_value_for_month(
			row.stockist_code, 
			row.statement_month
		)
		row.scheme_value = scheme_value
		row.sales_after_scheme = flt(row.sales_before_scheme) - flt(scheme_value)
		
		# Calculate scheme impact percentage
		if flt(row.sales_before_scheme) > 0:
			row.scheme_impact_pct = (flt(scheme_value) / flt(row.sales_before_scheme)) * 100
		else:
			row.scheme_impact_pct = 0
	
	return statements

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

def get_scheme_value_for_month(stockist_code, statement_month):
	"""Get total approved scheme value for a stockist in a given month"""
	from frappe.utils import get_first_day, get_last_day
	
	first_day = get_first_day(statement_month)
	last_day = get_last_day(statement_month)
	
	result = frappe.db.sql("""
		SELECT SUM(total_scheme_value) as total
		FROM `tabScheme Request`
		WHERE stockist_code = %s
		AND application_date BETWEEN %s AND %s
		AND approval_status = 'Approved'
		AND docstatus = 1
	""", (stockist_code, first_day, last_day))
	
	return flt(result[0][0]) if result and result[0][0] else 0
