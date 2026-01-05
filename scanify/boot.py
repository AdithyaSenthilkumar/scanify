import frappe

def boot_session(bootinfo):
    """Add custom boot info"""
    bootinfo.scanify_settings = {
        "company_name": frappe.db.get_single_value("Scanify Settings", "company_name") or "Stedman Pharmaceuticals",
        "company_logo": frappe.db.get_single_value("Scanify Settings", "company_logo") or "/assets/scanify/images/stedman_logo.png"
    }
    if frappe.session.user == "Guest":
        return
