import frappe
from frappe.model.document import Document

class DoctorMaster(Document):
    def before_save(self):
        # autoname (D0001) is available by the time before_save runs
        if not self.doctor_code:
            self.doctor_code = self.name
