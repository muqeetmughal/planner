# Copyright (c) 2024, ONFUSE AG and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TaskDependsOn(Document):
    def validate(self):
        if self.task:
            if not frappe.db.exists("Atlas Task", self.task):
                frappe.throw(frappe._("Task {0} does not exist").format(self.task))
