import frappe
from frappe.model.document import Document

class ScanifySettings(Document):
    def validate(self):
        """Validate Gemini settings"""
        if self.enable_gemini:
            # Validate API key is provided
            api_key = self.get_password("gemini_api_key")
            if not api_key:
                frappe.throw("Please provide Gemini API Key to enable AI extraction")
            
            # Validate model name
            if not self.gemini_model_name:
                self.gemini_model_name = "gemini-2.5-flash"
    
    def on_update(self):
        """Clear cache when settings are updated"""
        frappe.cache().delete_value("gemini_settings")
