import frappe
from frappe.model.document import Document

class StockistMaster(Document):
    def before_save(self):
        # autoname (S0001) is ready here
        if not self.stockist_code:
            self.stockist_code = self.name
