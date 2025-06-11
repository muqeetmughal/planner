import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today

class AtlasTask(Document):
    def validate(self):
        self.validate_dates()
        self.validate_progress()
        self.validate_status()
        self.update_depends_on()

    def validate_dates(self):
        if self.exp_start_date and self.exp_end_date:
            if getdate(self.exp_start_date) > getdate(self.exp_end_date):
                frappe.throw(_("Expected Start Date cannot be greater than Expected End Date"))

    def validate_progress(self):
        if self.progress is not None:
            if self.progress > 100:
                frappe.throw(_("Progress % cannot be more than 100"))
            elif self.progress == 100 and self.status != "Completed":
                self.status = "Completed"
                self.completed_on = frappe.utils.now()
                self.completed_by = frappe.session.user

    def validate_status(self):
        if self.status == "Completed":
            if not self.completed_on:
                self.completed_on = frappe.utils.now()
            if not self.completed_by:
                self.completed_by = frappe.session.user

    def update_depends_on(self):
        # 
        pass
