import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, getdate
from ..realtime import emit_task_update, emit_batch_update

class TaskService:
    @staticmethod
    def get_all_tasks(department=None, start_date=None, end_date=None):
        """Get all Atlas Tasks with optional department and date filters"""
        try:
            filters = {}
            
            if department:
                filters["department"] = department
                
            if start_date:
                filters["exp_start_date"] = [">=", start_date]
            if end_date:
                filters["exp_end_date"] = ["<=", end_date]
                
            print(f"\n=== Getting Atlas Tasks ===")
            print(f"Filters: {filters}")
            
            tasks = frappe.get_all(
                "Atlas Task",
                filters=filters,
                fields=[
                    "name", "subject", "status", "priority",
                    "exp_start_date", "exp_end_date", "expected_time",
                    "department", "_assign", "project", "description",
                    "color", "progress"
                ],
                order_by="creation desc"
            )
            
            print(f"Found {len(tasks)} tasks")
            if not tasks:
                print("Checking if Atlas Task doctype exists...")
                if not frappe.db.exists("DocType", "Atlas Task"):
                    print("ERROR: Atlas Task DocType does not exist!")
                else:
                    print("Atlas Task DocType exists but no tasks found")
                    
            formatted_tasks = [TaskService.format_task(task) for task in tasks]
            print(f"Formatted {len(formatted_tasks)} tasks successfully")
            
            return formatted_tasks
            
        except Exception as e:
            frappe.logger().error(f"Error getting tasks: {str(e)}")
            return []

    @staticmethod
    def get_task(task_id):
        """Get a single Atlas Task by ID"""
        try:
            task = frappe.get_doc("Atlas Task", task_id)
            return TaskService.format_task(task)
        except Exception as e:
            frappe.logger().error(f"Error getting task {task_id}: {str(e)}")
            return None

    @staticmethod
    def update_task(task_id, updates):
        """Update an Atlas Task"""
        try:
            if not task_id:
                frappe.throw(_("Task ID is required"))
            
            task = frappe.get_doc("Atlas Task", task_id)
            
            valid_fields = [
                "status", "priority", "exp_start_date",
                "exp_end_date", "expected_time", "description",
                "progress", "color"
            ]
            
            for field, value in updates.items():
                if field not in valid_fields:
                    frappe.throw(_(f"Invalid field: {field}"))
                
                setattr(task, field, value)
            
            task.modified = now_datetime()
            task.save()
            
            try:
                emit_task_update(task)
            except:
                pass
            
            return TaskService.format_task(task)
            
        except Exception as e:
            frappe.logger().error(f"Error updating task {task_id}: {str(e)}")
            raise

    @staticmethod
    def batch_update_tasks(updates):
        """Update multiple Atlas Tasks in batch"""
        try:
            if not updates:
                frappe.throw(_("No updates provided"))
            
            updated_tasks = []
            for update in updates:
                task_id = update.get('task_id')
                changes = update.get('changes', {})
                
                if task_id and changes:
                    try:
                        updated_task = TaskService.update_task(task_id, changes)
                        if updated_task:
                            updated_tasks.append(updated_task)
                    except Exception as task_error:
                        frappe.logger().error(f"Error updating task {task_id}: {str(task_error)}")
                        continue
            
            if updated_tasks:
                try:
                    emit_batch_update(updated_tasks)
                except:
                    pass
            
            return updated_tasks
            
        except Exception as e:
            frappe.logger().error(f"Error in batch update: {str(e)}")
            raise

    @staticmethod
    def move_task(task_id, assignee_id=None, start_date=None, end_date=None):
        """Move Atlas Task to different assignee or schedule"""
        try:
            if not task_id:
                frappe.throw(_("Task ID is required"))
            
            task = frappe.get_doc("Atlas Task", task_id)
            
            if assignee_id:
                if assignee_id == "unassigned":
                    task._assign = None
                else:
                    employee = frappe.get_value("Employee", {"user_id": assignee_id}, "name")
                    if employee:
                        task._assign = frappe.as_json([assignee_id])
                    else:
                        frappe.throw(_("Invalid assignee"))
            
            if start_date:
                task.exp_start_date = getdate(start_date)
            if end_date:
                task.exp_end_date = getdate(end_date)
            
            task.save(ignore_version=True)
            frappe.db.commit()
            
            try:
                emit_task_update(task)
            except:
                pass
            
            return {
                "success": True,
                "task": TaskService.format_task(task),
                "message": "Task moved successfully"
            }
            
        except Exception as e:
            frappe.logger().error(f"Error moving task {task_id}: {str(e)}")
            raise

    @staticmethod
    def format_task(task):
        """Format Atlas Task for API response"""
        try:
            assignee = "Unassigned"
            if task._assign:
                assigned_users = frappe.parse_json(task._assign)
                if assigned_users and len(assigned_users) > 0:
                    assignee = assigned_users[0]
            
            return {
                "id": task.name,
                "title": task.subject,
                "status": task.status,
                "priority": task.priority,
                "department": task.department,
                "project": task.project,
                "description": task.description,
                "startDate": task.exp_start_date,
                "endDate": task.exp_end_date,
                "estimatedHours": task.expected_time,
                "assignee": assignee,
                "color": task.color or TaskService.get_task_color(task),
                "progress": task.progress or 0
            }
            
        except Exception as e:
            frappe.logger().error(f"Error formatting task {task.name}: {str(e)}")
            return None

    @staticmethod
    def get_task_color(task):
        """Get color based on Atlas Task status and priority"""
        status_colors = {
            "Completed": "#10B981",  # green
            "Working": "#3B82F6",    # blue
            "Overdue": "#EF4444",    # red
            "Open": "#6B7280"        # gray
        }
        
        priority_colors = {
            "High": "#DC2626",       # red
            "Medium": "#F59E0B",     # amber
            "Low": "#10B981"         # green
        }
        
        return status_colors.get(task.status) or priority_colors.get(task.priority) or "#6B7280"
