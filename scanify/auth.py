import frappe

def on_session_creation(login_manager):
    """Redirect to Scanify dashboard after login"""
    if frappe.session.user != "Guest":
        frappe.local.response["home_page"] = "/app/scanify_dashboard"
