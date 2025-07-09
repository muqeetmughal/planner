import frappe
from frappe import _
from frappe.utils import getdate, get_datetime, now_datetime, add_days, get_time
from datetime import datetime, timedelta
import json

@frappe.whitelist()
def get_assignees(department=None, company=None):
    """Get list of employees/assignees for the planner"""
    try:
        filters = {"status": "Active"}

        if department:
            filters["department"] = department
        if company:
            filters["company"] = company

        employees = frappe.get_all(
            "Employee",
            filters=filters,
            fields=[
                "name", "employee_name as full_name", "department",
                "designation", "company", "image", "user_id",
                "cell_number", "personal_email"
            ],
            order_by="employee_name"
        )

        # Add workload statistics for each employee
        for employee in employees:
            employee["workload_stats"] = get_employee_workload_stats(employee["name"])

        return employees

    except Exception as e:
        frappe.log_error(f"Error in get_assignees: {str(e)}")
        frappe.throw(_("Failed to fetch assignees: {0}").format(str(e)))

@frappe.whitelist()
def get_assignments(start_date, end_date, department=None, company=None):
    """Get task assignments for the specified date range"""
    try:
        filters = {
            "date": ["between", [start_date, end_date]]
        }

        if department:
            filters["assignee_department"] = department
        if company:
            filters["company"] = company

        assignments = frappe.get_all(
            "Task Assignment",
            filters=filters,
            fields=[
                "name", "task", "assignee", "date", "start_time", "end_time",
                "status", "notes", "duration", "task_name", "assignee_name",
                "assignee_department", "task_priority", "task_project",
                "creation", "modified"
            ],
            order_by="date, start_time"
        )

        # Enrich with additional task and assignee details
        for assignment in assignments:
            # Get task details
            if assignment.get("task"):
                task_doc = frappe.get_cached_doc("Task", assignment["task"])
                assignment["task_doc"] = {
                    "name": task_doc.name,
                    "subject": task_doc.subject,
                    "description": task_doc.description,
                    "priority": task_doc.priority,
                    "status": task_doc.status,
                    "project": task_doc.project,
                    "expected_time": task_doc.expected_time or 0
                }

            # Calculate actual duration if not set
            if not assignment.get("duration") and assignment.get("start_time") and assignment.get("end_time"):
                start_dt = get_datetime(f"{assignment['date']} {assignment['start_time']}")
                end_dt = get_datetime(f"{assignment['date']} {assignment['end_time']}")
                assignment["duration"] = (end_dt - start_dt).total_seconds() / 3600

        return assignments

    except Exception as e:
        frappe.log_error(f"Error in get_assignments: {str(e)}")
        frappe.throw(_("Failed to fetch assignments: {0}").format(str(e)))

@frappe.whitelist()
def get_filters():
    """Get available filter options for departments and companies"""
    try:
        departments = frappe.get_all(
            "Department",
            filters={"disabled": 0},
            fields=["name"],
            order_by="name"
        )

        companies = frappe.get_all(
            "Company",
            filters={"disabled": 0},
            fields=["name"],
            order_by="name"
        )

        return {
            "departments": [d["name"] for d in departments],
            "companies": [c["name"] for c in companies]
        }

    except Exception as e:
        frappe.log_error(f"Error in get_filters: {str(e)}")
        return {"departments": [], "companies": []}

@frappe.whitelist()
def search_tasks(query, assignee=None, date=None, include_unassigned=False):
    """Search for tasks that can be assigned"""
    try:
        filters = {
            "status": ["in", ["Open", "Working", "Pending Review"]]
        }

        # Only add subject filter if query is provided and not wildcard
        if query and query.strip() and query != "*":
            filters["subject"] = ["like", f"%{query}%"]

        # Optionally filter by assignee's existing tasks
        if assignee:
            # Get tasks already assigned to this person
            assigned_tasks = frappe.get_all(
                "Task Assignment",
                filters={"assignee": assignee},
                fields=["task"],
                pluck="task"
            )
            if assigned_tasks:
                filters["name"] = ["not in", assigned_tasks]

        tasks = frappe.get_all(
            "Task",
            filters=filters,
            fields=[
                "name", "subject", "description", "priority", "status",
                "project", "expected_time", "creation", "modified"
            ],
            order_by="priority desc, creation desc",
            limit=20
        )

        # If include_unassigned is True, also get tasks without any assignments
        if include_unassigned:
            # Get all task IDs that have assignments
            assigned_task_ids = frappe.get_all(
                "Task Assignment",
                fields=["task"],
                pluck="task"
            )

            # Get unassigned tasks
            unassigned_filters = {
                "status": ["in", ["Open", "Working", "Pending Review"]]
            }

            # Only add subject filter if query is provided and not wildcard
            if query and query.strip() and query != "*":
                unassigned_filters["subject"] = ["like", f"%{query}%"]

            if assigned_task_ids:
                unassigned_filters["name"] = ["not in", assigned_task_ids]

            unassigned_tasks = frappe.get_all(
                "Task",
                filters=unassigned_filters,
                fields=[
                    "name", "subject", "description", "priority", "status",
                    "project", "expected_time", "creation", "modified"
                ],
                order_by="priority desc, creation desc",
                limit=10
            )

            # Add unassigned flag to distinguish them
            for task in unassigned_tasks:
                task["assignee"] = None
                task["is_unassigned"] = True

            # Combine and remove duplicates
            all_tasks = tasks + unassigned_tasks
            seen = set()
            unique_tasks = []
            for task in all_tasks:
                if task["name"] not in seen:
                    seen.add(task["name"])
                    unique_tasks.append(task)

            return unique_tasks[:20]  # Limit to 20 total

        return tasks

    except Exception as e:
        frappe.log_error(f"Error in search_tasks: {str(e)}")
        return []

@frappe.whitelist()
def create_assignment(task, assignee, date, start_time, end_time, notes=None):
    """Create a new task assignment"""
    try:
        # Validate inputs
        if not all([task, assignee, date, start_time, end_time]):
            frappe.throw(_("Missing required fields for assignment creation"))

        # Check for time conflicts
        conflicts = check_time_conflicts(assignee, date, start_time, end_time)
        if conflicts:
            frappe.throw(_("Time conflict with existing assignment: {0}").format(conflicts[0]["task_name"]))

        # Get task and assignee details
        task_doc = frappe.get_doc("Task", task)
        employee_doc = frappe.get_doc("Employee", assignee)

        # Calculate duration
        start_dt = get_datetime(f"{date} {start_time}")
        end_dt = get_datetime(f"{date} {end_time}")
        duration = (end_dt - start_dt).total_seconds() / 3600

        # Create assignment document
        assignment = frappe.get_doc({
            "doctype": "Task Assignment",
            "task": task,
            "task_name": task_doc.subject,
            "assignee": assignee,
            "assignee_name": employee_doc.employee_name,
            "assignee_department": employee_doc.department,
            "company": employee_doc.company,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "status": "Assigned",
            "notes": notes,
            "task_priority": task_doc.priority,
            "task_project": task_doc.project
        })

        assignment.insert()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Assignment created successfully"),
            "assignment_id": assignment.name
        }

    except Exception as e:
        frappe.log_error(f"Error in create_assignment: {str(e)}")
        frappe.throw(_("Failed to create assignment: {0}").format(str(e)))

@frappe.whitelist()
def update_assignment(name, task=None, assignee=None, date=None, start_time=None, end_time=None, notes=None):
    """Update an existing task assignment"""
    try:
        assignment = frappe.get_doc("Task Assignment", name)

        # Store original values for conflict checking
        original_assignee = assignment.assignee
        original_date = assignment.date
        original_start = assignment.start_time
        original_end = assignment.end_time

        # Update fields if provided
        if task and task != assignment.task:
            task_doc = frappe.get_doc("Task", task)
            assignment.task = task
            assignment.task_name = task_doc.subject
            assignment.task_priority = task_doc.priority
            assignment.task_project = task_doc.project

        if assignee and assignee != assignment.assignee:
            employee_doc = frappe.get_doc("Employee", assignee)
            assignment.assignee = assignee
            assignment.assignee_name = employee_doc.employee_name
            assignment.assignee_department = employee_doc.department
            assignment.company = employee_doc.company

        if date:
            assignment.date = date
        if start_time:
            assignment.start_time = start_time
        if end_time:
            assignment.end_time = end_time
        if notes is not None:
            assignment.notes = notes

        # Check for conflicts if time/date/assignee changed
        if (assignee and assignee != original_assignee) or \
           (date and date != original_date) or \
           (start_time and start_time != original_start) or \
           (end_time and end_time != original_end):

            conflicts = check_time_conflicts(
                assignment.assignee,
                assignment.date,
                assignment.start_time,
                assignment.end_time,
                exclude_assignment=name
            )
            if conflicts:
                frappe.throw(_("Time conflict with existing assignment: {0}").format(conflicts[0]["task_name"]))

        # Recalculate duration
        start_dt = get_datetime(f"{assignment.date} {assignment.start_time}")
        end_dt = get_datetime(f"{assignment.date} {assignment.end_time}")
        assignment.duration = (end_dt - start_dt).total_seconds() / 3600

        assignment.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Assignment updated successfully")
        }

    except Exception as e:
        frappe.log_error(f"Error in update_assignment: {str(e)}")
        frappe.throw(_("Failed to update assignment: {0}").format(str(e)))

@frappe.whitelist()
def delete_assignment(assignment_id):
    """Delete a task assignment"""
    try:
        frappe.delete_doc("Task Assignment", assignment_id)
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Assignment deleted successfully")
        }

    except Exception as e:
        frappe.log_error(f"Error in delete_assignment: {str(e)}")
        frappe.throw(_("Failed to delete assignment: {0}").format(str(e)))

@frappe.whitelist()
def move_assignment(assignment_id, new_date, new_assignee):
    """Move an assignment to a new date and/or assignee"""
    try:
        assignment = frappe.get_doc("Task Assignment", assignment_id)

        # Check for conflicts at new location
        conflicts = check_time_conflicts(
            new_assignee,
            new_date,
            assignment.start_time,
            assignment.end_time,
            exclude_assignment=assignment_id
        )
        if conflicts:
            frappe.throw(_("Time conflict at destination: {0}").format(conflicts[0]["task_name"]))

        # Update assignment
        if new_assignee != assignment.assignee:
            employee_doc = frappe.get_doc("Employee", new_assignee)
            assignment.assignee = new_assignee
            assignment.assignee_name = employee_doc.employee_name
            assignment.assignee_department = employee_doc.department
            assignment.company = employee_doc.company

        assignment.date = new_date
        assignment.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Assignment moved successfully")
        }

    except Exception as e:
        frappe.log_error(f"Error in move_assignment: {str(e)}")
        frappe.throw(_("Failed to move assignment: {0}").format(str(e)))

def check_time_conflicts(assignee, date, start_time, end_time, exclude_assignment=None):
    """Check for time conflicts with existing assignments"""
    try:
        filters = {
            "assignee": assignee,
            "date": date
        }

        if exclude_assignment:
            filters["name"] = ["!=", exclude_assignment]

        existing_assignments = frappe.get_all(
            "Task Assignment",
            filters=filters,
            fields=["name", "start_time", "end_time", "task_name"]
        )

        start_dt = get_datetime(f"{date} {start_time}")
        end_dt = get_datetime(f"{date} {end_time}")

        conflicts = []
        for assignment in existing_assignments:
            existing_start = get_datetime(f"{date} {assignment['start_time']}")
            existing_end = get_datetime(f"{date} {assignment['end_time']}")

            # Check for overlap
            if start_dt < existing_end and end_dt > existing_start:
                conflicts.append(assignment)

        return conflicts

    except Exception as e:
        frappe.log_error(f"Error in check_time_conflicts: {str(e)}")
        return []

def get_employee_workload_stats(employee):
    """Get workload statistics for an employee"""
    try:
        # Get assignments for current week
        today = getdate()
        week_start = add_days(today, -today.weekday())
        week_end = add_days(week_start, 6)

        assignments = frappe.get_all(
            "Task Assignment",
            filters={
                "assignee": employee,
                "date": ["between", [week_start, week_end]]
            },
            fields=["duration", "status"]
        )

        total_hours = sum(a.get("duration", 0) for a in assignments)
        active_assignments = len([a for a in assignments if a.get("status") == "Active"])

        return {
            "weekly_hours": total_hours,
            "active_assignments": active_assignments,
            "utilization": min((total_hours / 40) * 100, 100) if total_hours else 0
        }

    except Exception as e:
        frappe.log_error(f"Error in get_employee_workload_stats: {str(e)}")
        return {
            "weekly_hours": 0,
            "active_assignments": 0,
            "utilization": 0
        }

@frappe.whitelist()
def create_task(subject, description=None, priority="Medium", expected_time=0, project=None, department=None):
    """Create a new task that can be assigned"""
    try:
        # Validate inputs
        if not subject:
            frappe.throw(_("Task subject is required"))

        # Get current user's employee record for department if not provided
        if not department:
            employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "department")
            if employee:
                department = employee

        # Create task document
        task = frappe.get_doc({
            "doctype": "Task",
            "subject": subject,
            "description": description,
            "priority": priority,
            "expected_time": expected_time,
            "project": project,
            "status": "Open"
        })

        task.insert()
        frappe.db.commit()

        return {
            "success": True,
            "message": _("Task created successfully"),
            "task": {
                "name": task.name,
                "subject": task.subject,
                "description": task.description,
                "priority": task.priority,
                "expected_time": task.expected_time,
                "project": task.project,
                "status": task.status
            }
        }

    except Exception as e:
        frappe.log_error(f"Error in create_task: {str(e)}")
        frappe.throw(_("Failed to create task: {0}").format(str(e)))

@frappe.whitelist()
def get_projects():
    """Get list of active projects for task creation"""
    try:
        projects = frappe.get_all(
            "Project",
            filters={"status": "Open"},
            fields=["name", "project_name"],
            order_by="project_name"
        )

        # Filter out projects with null/empty names
        valid_projects = []
        for project in projects:
            if project.get("name") and project.get("project_name"):
                valid_projects.append(project)

        return valid_projects

    except Exception as e:
        frappe.log_error(f"Error in get_projects: {str(e)}")
        return []

@frappe.whitelist()
def get_task_templates():
    """Get common task templates for quick creation"""
    try:
        # This could be expanded to use a custom doctype for task templates
        # For now, return common task types
        templates = [
            {
                "name": "meeting",
                "subject": "Team Meeting",
                "description": "Regular team meeting",
                "priority": "Medium",
                "expected_time": 1
            },
            {
                "name": "review",
                "subject": "Code Review",
                "description": "Review code changes",
                "priority": "High",
                "expected_time": 2
            },
            {
                "name": "documentation",
                "subject": "Documentation",
                "description": "Update project documentation",
                "priority": "Low",
                "expected_time": 3
            },
            {
                "name": "training",
                "subject": "Training Session",
                "description": "Team training session",
                "priority": "Medium",
                "expected_time": 4
            },
            {
                "name": "planning",
                "subject": "Sprint Planning",
                "description": "Plan upcoming sprint tasks",
                "priority": "High",
                "expected_time": 2
            },
            {
                "name": "testing",
                "subject": "Testing",
                "description": "Test application functionality",
                "priority": "Medium",
                "expected_time": 3
            }
        ]

        return templates

    except Exception as e:
        frappe.log_error(f"Error in get_task_templates: {str(e)}")
        return []

@frappe.whitelist()
def quick_assign_task(task_name, assignee, date, start_time="09:00", end_time="17:00"):
    """Quick assignment of a task to an assignee"""
    try:
        # Validate inputs
        if not all([task_name, assignee, date]):
            frappe.throw(_("Missing required fields for quick assignment"))

        # Check if task exists
        if not frappe.db.exists("Task", task_name):
            frappe.throw(_("Task {0} does not exist").format(task_name))

        # Check if assignee exists
        if not frappe.db.exists("Employee", assignee):
            frappe.throw(_("Employee {0} does not exist").format(assignee))

        return create_assignment(
            task=task_name,
            assignee=assignee,
            date=date,
            start_time=start_time,
            end_time=end_time
        )

    except Exception as e:
        frappe.log_error(f"Error in quick_assign_task: {str(e)}")
        frappe.throw(_("Failed to assign task: {0}").format(str(e)))

@frappe.whitelist()
def get_workload_analytics(start_date, end_date, department=None, company=None):
    """Get workload analytics for the specified period"""
    try:
        filters = {
            "date": ["between", [start_date, end_date]]
        }

        if department:
            filters["assignee_department"] = department
        if company:
            filters["company"] = company

        assignments = frappe.get_all(
            "Task Assignment",
            filters=filters,
            fields=[
                "assignee", "assignee_name", "date", "duration",
                "status", "task_priority", "assignee_department"
            ]
        )

        # Group by assignee
        assignee_stats = {}
        for assignment in assignments:
            assignee = assignment["assignee"]
            if assignee not in assignee_stats:
                assignee_stats[assignee] = {
                    "name": assignment["assignee_name"],
                    "department": assignment["assignee_department"],
                    "total_hours": 0,
                    "assignments_count": 0,
                    "high_priority_tasks": 0,
                    "daily_breakdown": {}
                }

            stats = assignee_stats[assignee]
            stats["total_hours"] += assignment.get("duration", 0)
            stats["assignments_count"] += 1

            if assignment.get("task_priority") in ["High", "Urgent"]:
                stats["high_priority_tasks"] += 1

            # Daily breakdown
            date_str = str(assignment["date"])
            if date_str not in stats["daily_breakdown"]:
                stats["daily_breakdown"][date_str] = 0
            stats["daily_breakdown"][date_str] += assignment.get("duration", 0)

        return {
            "assignee_stats": assignee_stats,
            "summary": {
                "total_assignments": len(assignments),
                "total_hours": sum(a.get("duration", 0) for a in assignments),
                "avg_utilization": calculate_avg_utilization(assignee_stats)
            }
        }

    except Exception as e:
        frappe.log_error(f"Error in get_workload_analytics: {str(e)}")
        return {"assignee_stats": {}, "summary": {}}

def calculate_avg_utilization(assignee_stats):
    """Calculate average utilization across all assignees"""
    if not assignee_stats:
        return 0

    total_utilization = 0
    for stats in assignee_stats.values():
        # Assume 8 hours per day as standard
        working_days = len(stats["daily_breakdown"])
        standard_hours = working_days * 8
        utilization = (stats["total_hours"] / standard_hours * 100) if standard_hours else 0
        total_utilization += min(utilization, 100)

    return total_utilization / len(assignee_stats)
