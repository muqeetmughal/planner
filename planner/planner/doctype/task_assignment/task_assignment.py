# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_datetime, time_diff_in_hours, now_datetime
from datetime import datetime, timedelta

class TaskAssignment(Document):
    def validate(self):
        self.validate_time_range()
        self.validate_date()
        self.validate_conflicts()
        self.calculate_duration()
        self.set_derived_fields()
    
    def before_save(self):
        self.set_system_fields()
    
    def validate_time_range(self):
        """Validate that end time is after start time"""
        if self.start_time and self.end_time:
            start_dt = get_datetime(f"{self.date} {self.start_time}")
            end_dt = get_datetime(f"{self.date} {self.end_time}")
            
            if end_dt <= start_dt:
                frappe.throw("End time must be after start time")
    
    def validate_date(self):
        """Validate assignment date"""
        if self.date:
            assignment_date = getdate(self.date)
            if assignment_date < getdate():
                frappe.msgprint("Assignment date is in the past", alert=True)
    
    def validate_conflicts(self):
        """Check for time conflicts with existing assignments"""
        if not (self.assignee and self.date and self.start_time and self.end_time):
            return
            
        # Get existing assignments for the same assignee and date
        filters = {
            "assignee": self.assignee,
            "date": self.date,
            "docstatus": ["!=", 2]  # Exclude cancelled documents
        }
        
        if not self.is_new():
            filters["name"] = ["!=", self.name]
        
        existing_assignments = frappe.get_all(
            "Task Assignment",
            filters=filters,
            fields=["name", "start_time", "end_time", "task_name"]
        )
        
        if existing_assignments:
            start_dt = get_datetime(f"{self.date} {self.start_time}")
            end_dt = get_datetime(f"{self.date} {self.end_time}")
            
            for assignment in existing_assignments:
                existing_start = get_datetime(f"{self.date} {assignment['start_time']}")
                existing_end = get_datetime(f"{self.date} {assignment['end_time']}")
                
                # Check for overlap
                if start_dt < existing_end and end_dt > existing_start:
                    frappe.throw(
                        f"Time conflict with existing assignment: {assignment['task_name']} "
                        f"({assignment['start_time']} - {assignment['end_time']})"
                    )
    
    def calculate_duration(self):
        """Calculate assignment duration in hours"""
        if self.start_time and self.end_time:
            start_dt = get_datetime(f"{self.date} {self.start_time}")
            end_dt = get_datetime(f"{self.date} {self.end_time}")
            self.duration = time_diff_in_hours(end_dt, start_dt)
    
    def set_derived_fields(self):
        """Set fields derived from linked documents"""
        if self.task:
            task_doc = frappe.get_cached_doc("Task", self.task)
            self.task_name = task_doc.subject
            self.task_priority = task_doc.priority
            self.task_project = task_doc.project
        
        if self.assignee:
            employee_doc = frappe.get_cached_doc("Employee", self.assignee)
            self.assignee_name = employee_doc.employee_name
            self.assignee_department = employee_doc.department
            self.company = employee_doc.company
    
    def set_system_fields(self):
        """Set system information fields"""
        if self.is_new():
            self.creation_details = f"Created by {frappe.session.user} on {now_datetime().strftime('%Y-%m-%d %H:%M')}"
        else:
            self.modified_details = f"Modified by {frappe.session.user} on {now_datetime().strftime('%Y-%m-%d %H:%M')}"
    
    def on_update(self):
        """Actions to perform after document update"""
        self.update_task_assignment_status()
        self.notify_assignee()
    
    def update_task_assignment_status(self):
        """Update the linked task's assignment status"""
        if self.task and self.status in ["Active", "Completed"]:
            task_doc = frappe.get_doc("Task", self.task)
            
            # Check if task should be marked as assigned
            if self.status == "Active" and task_doc.status == "Open":
                task_doc.status = "Working"
                task_doc.save(ignore_permissions=True)
            
            # Update task assignee if not already set
            if not task_doc.assigned_to and self.assignee:
                employee_doc = frappe.get_cached_doc("Employee", self.assignee)
                if employee_doc.user_id:
                    task_doc.assigned_to = employee_doc.user_id
                    task_doc.save(ignore_permissions=True)
    
    def notify_assignee(self):
        """Send notification to assignee about the assignment"""
        if self.assignee and self.is_new():
            employee_doc = frappe.get_cached_doc("Employee", self.assignee)
            if employee_doc.user_id:
                # Create notification
                notification = frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": f"New Task Assignment: {self.task_name}",
                    "email_content": f"""
                        <p>You have been assigned a new task:</p>
                        <ul>
                            <li><strong>Task:</strong> {self.task_name}</li>
                            <li><strong>Date:</strong> {frappe.format(self.date, 'Date')}</li>
                            <li><strong>Time:</strong> {self.start_time} - {self.end_time}</li>
                            <li><strong>Duration:</strong> {self.duration} hours</li>
                        </ul>
                        {f'<p><strong>Notes:</strong> {self.notes}</p>' if self.notes else ''}
                    """,
                    "document_type": "Task Assignment",
                    "document_name": self.name,
                    "for_user": employee_doc.user_id,
                    "type": "Assignment"
                })
                notification.insert(ignore_permissions=True)
    
    def get_workload_summary(self):
        """Get workload summary for the assignee on the assignment date"""
        if not (self.assignee and self.date):
            return {}
        
        # Get all assignments for the assignee on the same date
        assignments = frappe.get_all(
            "Task Assignment",
            filters={
                "assignee": self.assignee,
                "date": self.date,
                "docstatus": ["!=", 2]
            },
            fields=["duration", "status", "task_priority"]
        )
        
        total_hours = sum(a.get("duration", 0) for a in assignments)
        high_priority_count = len([a for a in assignments if a.get("task_priority") in ["High", "Urgent"]])
        
        return {
            "total_assignments": len(assignments),
            "total_hours": total_hours,
            "high_priority_tasks": high_priority_count,
            "utilization_percentage": min((total_hours / 8) * 100, 100) if total_hours else 0
        }

@frappe.whitelist()
def get_assignment_conflicts(assignee, date, start_time, end_time, exclude_assignment=None):
    """Check for assignment conflicts for given parameters"""
    filters = {
        "assignee": assignee,
        "date": date,
        "docstatus": ["!=", 2]
    }
    
    if exclude_assignment:
        filters["name"] = ["!=", exclude_assignment]
    
    existing_assignments = frappe.get_all(
        "Task Assignment",
        filters=filters,
        fields=["name", "start_time", "end_time", "task_name", "status"]
    )
    
    conflicts = []
    if existing_assignments:
        start_dt = get_datetime(f"{date} {start_time}")
        end_dt = get_datetime(f"{date} {end_time}")
        
        for assignment in existing_assignments:
            existing_start = get_datetime(f"{date} {assignment['start_time']}")
            existing_end = get_datetime(f"{date} {assignment['end_time']}")
            
            # Check for overlap
            if start_dt < existing_end and end_dt > existing_start:
                conflicts.append({
                    "assignment_id": assignment["name"],
                    "task_name": assignment["task_name"],
                    "start_time": assignment["start_time"],
                    "end_time": assignment["end_time"],
                    "status": assignment["status"]
                })
    
    return conflicts

@frappe.whitelist()
def get_assignee_workload(assignee, start_date, end_date):
    """Get workload statistics for an assignee over a date range"""
    assignments = frappe.get_all(
        "Task Assignment",
        filters={
            "assignee": assignee,
            "date": ["between", [start_date, end_date]],
            "docstatus": ["!=", 2]
        },
        fields=["date", "duration", "status", "task_priority"]
    )
    
    # Group by date
    daily_workload = {}
    total_hours = 0
    high_priority_count = 0
    
    for assignment in assignments:
        date_str = str(assignment["date"])
        duration = assignment.get("duration", 0)
        
        if date_str not in daily_workload:
            daily_workload[date_str] = {
                "total_hours": 0,
                "assignment_count": 0,
                "high_priority_count": 0
            }
        
        daily_workload[date_str]["total_hours"] += duration
        daily_workload[date_str]["assignment_count"] += 1
        
        if assignment.get("task_priority") in ["High", "Urgent"]:
            daily_workload[date_str]["high_priority_count"] += 1
            high_priority_count += 1
        
        total_hours += duration
    
    # Calculate working days (exclude weekends)
    working_days = 0
    current_date = getdate(start_date)
    end_date_obj = getdate(end_date)
    
    while current_date <= end_date_obj:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            working_days += 1
        current_date += timedelta(days=1)
    
    avg_daily_hours = total_hours / working_days if working_days else 0
    utilization = (avg_daily_hours / 8) * 100 if avg_daily_hours else 0
    
    return {
        "daily_workload": daily_workload,
        "summary": {
            "total_hours": total_hours,
            "total_assignments": len(assignments),
            "high_priority_tasks": high_priority_count,
            "working_days": working_days,
            "avg_daily_hours": avg_daily_hours,
            "utilization_percentage": min(utilization, 100)
        }
    }

@frappe.whitelist()
def bulk_assign_tasks(assignments_data):
    """Create multiple task assignments in bulk"""
    try:
        assignments_data = frappe.parse_json(assignments_data)
        created_assignments = []
        errors = []
        
        for assignment_data in assignments_data:
            try:
                assignment = frappe.get_doc({
                    "doctype": "Task Assignment",
                    **assignment_data
                })
                assignment.insert()
                created_assignments.append(assignment.name)
            except Exception as e:
                errors.append({
                    "assignment_data": assignment_data,
                    "error": str(e)
                })
        
        frappe.db.commit()
        
        return {
            "success": True,
            "created_count": len(created_assignments),
            "created_assignments": created_assignments,
            "errors": errors
        }
        
    except Exception as e:
        frappe.log_error(f"Error in bulk_assign_tasks: {str(e)}")
        frappe.throw(f"Failed to create bulk assignments: {str(e)}")