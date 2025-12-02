# scanify/api.py (UPDATED with NULL SAFETY)
import frappe
import json
from frappe import _
from frappe.utils import flt, nowdate, add_months, get_first_day
import requests
import os

@frappe.whitelist()
def extract_stockist_statement(doc_name, file_url):
	"""Extract stockist statement data using Gemini AI"""
	try:
		doc = frappe.get_doc("Stockist Statement", doc_name)
		doc.extracted_data_status = "In Progress"
		doc.save()
		frappe.db.commit()
		
		if not file_url:
			frappe.throw("No file uploaded")
		
		# Get file content
		file_path = frappe.get_site_path('public', file_url.replace('/files/', ''))
		
		# Call Gemini API (you'll need to implement this based on your setup)
		extracted_data = call_gemini_extraction(file_path, doc.stockist_code)
		
		if extracted_data and len(extracted_data) > 0:
			# Clear existing items
			doc.items = []
			
			# Add extracted items
			for item_data in extracted_data:
				doc.append("items", {
					"product_code": item_data.get("product_code"),
					"opening_qty": flt(item_data.get("opening_qty", 0)),
					"purchase_qty": flt(item_data.get("purchase_qty", 0)),
					"sales_qty": flt(item_data.get("sales_qty", 0)),
					"return_qty": flt(item_data.get("return_qty", 0)),
					"misc_out_qty": flt(item_data.get("misc_out_qty", 0)),
				})
			
			doc.extracted_data_status = "Completed"
			doc.extraction_notes = "Data extracted successfully using AI"
			doc.calculate_closing_and_totals()
			doc.save()
			frappe.db.commit()
			
			return True
		else:
			doc.extracted_data_status = "Failed"
			doc.extraction_notes = "No data extracted or file format not recognized"
			doc.save()
			frappe.db.commit()
			return False
			
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Gemini Extraction Error")
		if frappe.db.exists("Stockist Statement", doc_name):
			doc = frappe.get_doc("Stockist Statement", doc_name)
			doc.extracted_data_status = "Failed"
			doc.extraction_notes = str(e)
			doc.save()
			frappe.db.commit()
		return False

def call_gemini_extraction(file_path, stockist_code):
	"""
	Call Gemini AI API to extract data from the statement file
	This is a placeholder - you need to implement actual Gemini API call
	"""
	# Get product list for the stockist
	products = frappe.get_all("Product Master", 
		fields=["product_code", "product_name", "pack", "pts"],
		filters={"status": "Active"})
	
	# Placeholder: Return empty list for now
	# TODO: Implement actual Gemini API integration
	frappe.msgprint(
		"Gemini extraction needs to be implemented with your API key. "
		"For now, please enter data manually.",
		indicator='orange'
	)
	
	return []

@frappe.whitelist()
def fetch_previous_month_closing(stockist_code, current_month):
	"""Fetch previous month's closing balance to set as opening balance"""
	try:
		from dateutil.relativedelta import relativedelta
		
		if not stockist_code or not current_month:
			return []
		
		current_date = frappe.utils.getdate(current_month)
		previous_month = current_date - relativedelta(months=1)
		previous_month_first = get_first_day(previous_month)
		
		# Find previous month's statement
		prev_statement = frappe.db.get_value("Stockist Statement", {
			"stockist_code": stockist_code,
			"statement_month": previous_month_first,
			"docstatus": 1
		}, "name")
		
		if not prev_statement:
			frappe.msgprint("No previous month statement found", indicator='orange')
			return []
		
		# Get items from previous statement
		prev_items = frappe.get_all("Stockist Statement Item",
			filters={"parent": prev_statement},
			fields=["product_code", "product_name", "pack", "closing_qty", "pts", "closing_value"])
		
		return prev_items or []
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Fetch Previous Month Error")
		return []
@frappe.whitelist()
def reroute_scheme_request(doc_name, comments):
    try:
        doc = frappe.get_doc("Scheme Request", doc_name)
        
        if doc.approval_status == "Rerouted":
            frappe.throw("Scheme request already rerouted")
        
        doc.approval_status = "Rerouted"
        doc.append("approval_log", {
            "approver": frappe.session.user,
            "approval_level": "Manager",
            "action": "Rerouted",
            "action_date": nowdate(),
            "comments": comments or "Rerouted for revision"
        })
        
        doc.save()
        frappe.db.commit()
        
        send_scheme_notification(doc, "Rerouted", comments)
        
        return True
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reroute Scheme Error")
        frappe.throw(str(e))

@frappe.whitelist()
def approve_scheme_request(doc_name, comments):
	"""Approve a scheme request"""
	try:
		doc = frappe.get_doc("Scheme Request", doc_name)
		
		if doc.approval_status == "Approved":
			frappe.throw("Scheme request already approved")
		
		doc.approval_status = "Approved"
		doc.append("approval_log", {
			"approver": frappe.session.user,
			"approval_level": "Manager",
			"action": "Approved",
			"action_date": nowdate(),
			"comments": comments or "Approved"
		})
		
		doc.save()
		frappe.db.commit()
		
		# Send notification
		send_scheme_notification(doc, "Approved", comments)
		
		return True
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Approve Scheme Error")
		frappe.throw(str(e))

@frappe.whitelist()
def reject_scheme_request(doc_name, comments):
	"""Reject a scheme request"""
	try:
		doc = frappe.get_doc("Scheme Request", doc_name)
		
		if doc.approval_status == "Rejected":
			frappe.throw("Scheme request already rejected")
		
		doc.approval_status = "Rejected"
		doc.append("approval_log", {
			"approver": frappe.session.user,
			"approval_level": "Manager",
			"action": "Rejected",
			"action_date": nowdate(),
			"comments": comments or "Rejected"
		})
		
		doc.save()
		frappe.db.commit()
		
		# Send notification
		send_scheme_notification(doc, "Rejected", comments)
		
		return True
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Reject Scheme Error")
		frappe.throw(str(e))

def send_scheme_notification(doc, action, comments):
	"""Send email notification for scheme request approval/rejection"""
	try:
		subject = f"Scheme Request {doc.name} - {action}"
		message = f"""
		<p>Dear {doc.requested_by},</p>
		<p>Your scheme request {doc.name} has been <strong>{action}</strong>.</p>
		<p><strong>Doctor:</strong> {doc.doctor_name or 'N/A'} ({doc.doctor_code or 'N/A'})</p>
		<p><strong>Stockist:</strong> {doc.stockist_name or 'N/A'}</p>
		<p><strong>Total Value:</strong> ₹{flt(doc.total_scheme_value or 0):,.2f}</p>
		<p><strong>Comments:</strong> {comments or 'None'}</p>
		<p>Please check the system for more details.</p>
		"""
		
		frappe.sendmail(
			recipients=[doc.requested_by],
			subject=subject,
			message=message
		)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Send Notification Error")
# scanify/api.py - Add these methods

@frappe.whitelist()
def search_doctors(search_term):
	"""Search doctors by name or place"""
	try:
		search_term = f"%{search_term}%"
		
		doctors = frappe.db.sql("""
			SELECT 
				name,
				doctor_code,
				doctor_name,
				place,
				specialization,
				hospital_clinic,
				city_pool,
				team,
				region
			FROM `tabDoctor Master`
			WHERE status = 'Active'
			AND (
				doctor_name LIKE %(search_term)s
				OR place LIKE %(search_term)s
				OR doctor_code LIKE %(search_term)s
			)
			ORDER BY doctor_name
			LIMIT 20
		""", {"search_term": search_term}, as_dict=True)
		
		return doctors or []
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Doctor Search Error")
		return []
# scanify/api.py - Add this method

@frappe.whitelist()
def get_stockists_by_team(team):
	"""Get all active stockists for a team"""
	try:
		stockists = frappe.get_all("Stockist Master",
			filters={
				"team": team,
				"status": "Active"
			},
			fields=["name", "stockist_code", "stockist_name", "city", "hq"],
			order_by="stockist_name"
		)
		return stockists or []
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Stockists Error")
		return []

@frappe.whitelist()
def search_stockists(search_term, team=None):
	"""Search stockists by name or city, optionally filter by team"""
	try:
		search_term = f"%{search_term}%"
		
		conditions = "status = 'Active'"
		
		if team:
			conditions += f" AND team = '{team}'"
		
		stockists = frappe.db.sql(f"""
			SELECT 
				name,
				stockist_code,
				stockist_name,
				city,
				hq,
				team,
				region
			FROM `tabStockist Master`
			WHERE {conditions}
			AND (
				stockist_name LIKE %(search_term)s
				OR city LIKE %(search_term)s
				OR stockist_code LIKE %(search_term)s
			)
			ORDER BY stockist_name
			LIMIT 20
		""", {"search_term": search_term}, as_dict=True)
		
		return stockists or []
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Stockist Search Error")
		return []

@frappe.whitelist()
def get_dashboard_data():
	"""Get dashboard KPI data with null safety"""
	try:
		# Total stockists
		total_stockists = frappe.db.count("Stockist Master", {"status": "Active"}) or 0
		
		# Total schemes this month
		from frappe.utils import get_first_day, get_last_day, today
		first_day = get_first_day(today())
		last_day = get_last_day(today())
		
		total_schemes = frappe.db.count("Scheme Request", {
			"application_date": ["between", [first_day, last_day]]
		}) or 0
		
		pending_schemes = frappe.db.count("Scheme Request", {
			"approval_status": "Pending",
			"application_date": ["between", [first_day, last_day]]
		}) or 0
		
		approved_schemes = frappe.db.count("Scheme Request", {
			"approval_status": "Approved",
			"application_date": ["between", [first_day, last_day]]
		}) or 0
		
		# Total scheme value this month
		result = frappe.db.sql("""
			SELECT COALESCE(SUM(total_scheme_value), 0) as total
			FROM `tabScheme Request`
			WHERE application_date BETWEEN %s AND %s
			AND approval_status = 'Approved'
		""", (first_day, last_day), as_dict=True)
		
		total_scheme_value = flt(result[0].total) if result and result[0] else 0
		
		# Statements processed this month
		statements_processed = frappe.db.count("Stockist Statement", {
			"statement_month": ["between", [first_day, last_day]],
			"docstatus": 1
		}) or 0
		
		return {
			"total_stockists": total_stockists,
			"total_schemes": total_schemes,
			"pending_schemes": pending_schemes,
			"approved_schemes": approved_schemes,
			"total_scheme_value": total_scheme_value,
			"statements_processed": statements_processed
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Dashboard Data Error")
		return {
			"total_stockists": 0,
			"total_schemes": 0,
			"pending_schemes": 0,
			"approved_schemes": 0,
			"total_scheme_value": 0,
			"statements_processed": 0
		}
@frappe.whitelist()
def upload_company_logo():
	"""Upload company logo"""
	return {
		"message": "Upload your logo to /public/files/stedman_logo.png"
	}

@frappe.whitelist()
def get_workspace_settings():
	"""Get workspace settings including logo"""
	logo_path = frappe.db.get_single_value("Scanify Settings", "company_logo")
	if not logo_path:
		logo_path = "/files/stedman_logo.png"  # default
	
	return {
		"logo": logo_path,
		"company_name": "Stedman Pharmaceuticals"
	}
