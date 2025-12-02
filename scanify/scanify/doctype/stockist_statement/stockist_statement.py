# scanify/scanify/doctype/stockist_statement/stockist_statement.py
import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_months, get_first_day, get_last_day

class StockistStatement(Document):
	def validate(self):
		self.calculate_closing_and_totals()
		# Don't call validate_closing_balance here since it's already hooked
	
	def calculate_closing_and_totals(self):
		"""Calculate closing qty and values for each item and update totals"""
		total_opening = 0
		total_purchase = 0
		total_sales = 0
		total_closing = 0
		
		for item in self.items:
			# NULL SAFETY: Convert all to float with default 0
			opening = flt(item.opening_qty or 0)
			purchase = flt(item.purchase_qty or 0)
			sales = flt(item.sales_qty or 0)
			return_qty = flt(item.return_qty or 0)
			misc_out = flt(item.misc_out_qty or 0)
			pts = flt(item.pts or 0)
			
			# Closing Qty = Opening + Purchase - Sales - Return - Misc Out
			item.closing_qty = opening + purchase - sales - return_qty - misc_out
			
			# Closing Value = Closing Qty * PTS
			item.closing_value = flt(item.closing_qty) * pts
			
			# Calculate totals
			total_opening += opening * pts
			total_purchase += purchase * pts
			total_sales += sales * pts
			total_closing += flt(item.closing_value)
		
		self.total_opening_value = total_opening
		self.total_purchase_value = total_purchase
		self.total_sales_value = total_sales
		self.total_closing_value = total_closing
	
	def on_submit(self):
		"""After submission, update next month's opening balance"""
		update_next_month_opening(self)

# Remove this function from being called in validate() - it's hooked in hooks.py
def validate_closing_balance(doc, method=None):
	"""Validate that closing balance matches formula - HOOK VERSION"""
	if not doc.items:
		return
		
	for item in doc.items:
		opening = flt(item.opening_qty or 0)
		purchase = flt(item.purchase_qty or 0)
		sales = flt(item.sales_qty or 0)
		return_qty = flt(item.return_qty or 0)
		misc_out = flt(item.misc_out_qty or 0)
		
		calculated_closing = opening + purchase - sales - return_qty - misc_out
		actual_closing = flt(item.closing_qty or 0)
		
		if abs(calculated_closing - actual_closing) > 0.01:
			frappe.msgprint(
				f"Warning: Closing qty mismatch for {item.product_name or 'Unknown Product'}: "
				f"Expected {calculated_closing}, Got {actual_closing}",
				indicator='orange'
			)

def update_next_month_opening(doc, method=None):
	"""Update next month's opening balance with this month's closing - HOOK VERSION"""
	try:
		from dateutil.relativedelta import relativedelta
		
		if not doc.statement_month:
			return
		
		# Calculate next month
		next_month_date = doc.statement_month + relativedelta(months=1)
		next_month_first = get_first_day(next_month_date)
		
		# Check if next month's statement exists
		next_statement = frappe.db.exists("Stockist Statement", {
			"stockist_code": doc.stockist_code,
			"statement_month": next_month_first,
			"docstatus": 0
		})
		
		if next_statement:
			next_doc = frappe.get_doc("Stockist Statement", next_statement)
			
			# Update opening balances
			for item in doc.items:
				if not item.product_code:
					continue
					
				for next_item in next_doc.items:
					if next_item.product_code == item.product_code:
						next_item.opening_qty = flt(item.closing_qty or 0)
						break
			
			next_doc.calculate_closing_and_totals()
			next_doc.save()
			frappe.msgprint(f"Next month's opening balance updated for {next_doc.name}")
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Next Month Opening Error")
