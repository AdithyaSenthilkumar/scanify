import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

class SchemeRequest(Document):
    def validate(self):
        self.calculate_total_scheme_value()
        self.validate_attachments()
    
    def calculate_total_scheme_value(self):
        total = 0
        
        if not self.items:
            self.total_scheme_value = 0
            return
            
        for item in self.items:
            rate = flt(item.special_rate or 0) if item.special_rate else flt(item.product_rate or 0)
            quantity = flt(item.quantity or 0)
            item.product_value = quantity * rate
            total += item.product_value
        
        self.total_scheme_value = total
    
    def validate_attachments(self):
        attachments = [
            self.proof_attachment_1,
            self.proof_attachment_2,
            self.proof_attachment_3,
            self.proof_attachment_4
        ]
        
        if not any(attachments):
            frappe.throw("At least one supporting document is required")
    
    def on_submit(self):
        if self.approval_status == "Approved":
            create_stock_adjustment(self)
        else:
            frappe.throw("Cannot submit scheme request without approval")

def create_stock_adjustment(doc):
    try:
        doc.append("approval_log", {
            "approver": frappe.session.user,
            "approval_level": "Final",
            "action": "Approved",
            "action_date": nowdate(),
            "comments": "Scheme approved and submitted"
        })
        doc.save()
        
        frappe.msgprint(
            f"Scheme request approved. Total value: ₹{flt(doc.total_scheme_value or 0):,.2f}",
            indicator='green'
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Stock Adjustment Error")