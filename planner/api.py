from frappe import _
from frappe.utils import now_datetime, get_datetime, getdate, add_days, date_diff
from .realtime import emit_task_update, emit_batch_update
from planner.services.workload_service import WorkloadService
from planner.services.task_service import TaskService
import frappe
import traceback

@frappe.whitelist(allow_guest=True)
def oauth_providers():
    """Get OAuth providers for authentication (required by frappe-ui)"""
    return []

@frappe.whitelist()
def verify_task_structure():
    """Verify Atlas Task doctype structure and required fields"""
    try:
        print("\n=== Verifying Atlas Task Structure ===")
        
        # Check if Atlas Task doctype exists
        if not frappe.db.exists("DocType", "Atlas Task"):
            print("ERROR: Atlas Task DocType does not exist!")
            return handle_api_error(
                Exception("Atlas Task DocType not found"),
                "Task Structure Error",
                {"doctype_exists": False}
            )
            
        # Get Atlas Task doctype fields
        task_meta = frappe.get_meta("Atlas Task")
        print("\nAtlas Task Fields:")
        field_info = []
        for field in task_meta.fields:
            print(f"- {field.fieldname} ({field.fieldtype})")
            field_info.append({
                "name": field.fieldname,
                "type": field.fieldtype
            })
            
        # Check required fields exist
        required_fields = [
            "name", "subject", "status", "priority", 
            "exp_start_date", "exp_end_date", "expected_time",
            "department", "_assign"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not task_meta.get_field(field):
                missing_fields.append(field)
                
        if missing_fields:
            print("\nMissing required fields:", missing_fields)
            return handle_api_error(
                Exception("Missing required fields"),
                "Task Structure Error",
                {
                    "doctype_exists": True,
                    "fields": field_info,
                    "missing_fields": missing_fields
                }
            )
            
        print("\nAll required fields present")
        return {
            "success": True,
            "message": "Atlas Task structure verified",
            "fields": field_info
        }
        
    except Exception as e:
        return handle_api_error(e, "Task Structure Error")

def handle_api_error(e, error_title, fallback_data=None):
    """Common error handling for API endpoints"""
    error_traceback = traceback.format_exc()
    frappe.log_error(error_traceback, error_title)
    print(f"ERROR: {error_title}: {str(e)}")
    print(f"Full traceback: {error_traceback}")
    
    if isinstance(e, frappe.PermissionError):
        exc_type = "PermissionError"
    elif isinstance(e, frappe.ValidationError):
        exc_type = "ValidationError"
    elif isinstance(e, frappe.DoesNotExistError):
        exc_type = "DoesNotExistError"
    elif isinstance(e, AttributeError):
        exc_type = "AttributeError"
    else:
        exc_type = e.__class__.__name__
    
    error_response = {
        "message": error_title,
        "_error_message": str(e),
        "error": str(e),
        "exc_type": exc_type,
        "traceback": error_traceback,
        "http_status_code": 500,
        "success": False,
        "data": fallback_data
    }
    
    frappe.clear_messages()
    frappe.local.response.http_status_code = 500
    frappe.local.response.error = True
    
    for key, value in error_response.items():
        setattr(frappe.local.response, key, value)
    
    return error_response

@frappe.whitelist()
def get_workload_data(department=None, start_date=None, end_date=None):
    """Get workload data for ClickUp-style workload view"""
    try:
        print("\n=== Workload Data Request ===")
        print(f"Department: {department}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        
        if not hasattr(WorkloadService, 'get_workload_data'):
            raise AttributeError("WorkloadService.get_workload_data method not found")
            
        workload_data = WorkloadService.get_workload_data(department, start_date, end_date)
        
        if not isinstance(workload_data, dict):
            workload_data = {
                "assignees": [],
                "tasks": [],
                "capacity_settings": {}
            }
        
        workload_data.setdefault("assignees", [])
        workload_data.setdefault("tasks", [])
        workload_data.setdefault("capacity_settings", {})
        
        print(f"\n=== Final Workload Data ===")
        print(f"Total Assignees: {len(workload_data['assignees'])}")
        print(f"Total Tasks: {len(workload_data['tasks'])}")
        
        return workload_data
        
    except Exception as e:
        try:
            fallback_data = {
                "assignees": WorkloadService.get_department_employees(department) if department else [],
                "tasks": [],
                "capacity_settings": WorkloadService.get_capacity_settings()
            }
        except Exception as fallback_error:
            print(f"Error getting fallback data: {str(fallback_error)}")
            fallback_data = {
                "assignees": [],
                "tasks": [],
                "capacity_settings": {
                    "default_hours_per_day": 8,
                    "default_days_per_week": 5
                }
            }
        
        return handle_api_error(e, "Workload Data Error", fallback_data)

def get_fallback_workload_data(department=None):
    """Get fallback workload data when WorkloadService fails"""
    try:
        print("Generating fallback workload data...")
        
        capacity_settings = {}
        try:
            if hasattr(WorkloadService, 'get_capacity_settings'):
                capacity_settings = WorkloadService.get_capacity_settings(department)
        except:
            capacity_settings = {
                "hours_per_day": 8,
                "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }
        
        assignees = []
        tasks = []
        
        try:
            employee_filters = {"status": "Active"}
            if department:
                employee_filters["department"] = department
                
            employees = frappe.get_all(
                "Employee",
                filters=employee_filters,
                fields=["name", "employee_name", "user_id", "department"],
                limit=50
            )
            
            for emp in employees:
                if emp.user_id:
                    assignees.append({
                        "id": emp.user_id,
                        "name": emp.employee_name or emp.name,
                        "email": emp.user_id,
                        "department": emp.department
                    })
            
            task_filters = {"status": ["in", ["Open", "Working"]]}
            if department:
                task_filters["department"] = department
                
            task_list = frappe.get_all(
                "Atlas Task",
                filters=task_filters,
                fields=[
                    "name", "subject", "status", "priority",
                    "exp_start_date", "exp_end_date", "expected_time",
                    "department", "_assign"
                ],
                limit=100
            )
            
            for task in task_list:
                assignee = get_primary_assignee(task)
                tasks.append({
                    "id": task.name,
                    "title": task.subject,
                    "status": task.status,
                    "priority": task.priority,
                    "start_date": task.exp_start_date,
                    "end_date": task.exp_end_date,
                    "estimated_hours": task.expected_time or 0,
                    "assignee": assignee,
                    "department": task.department
                })
                
        except Exception as data_error:
            print(f"Error getting fallback data: {str(data_error)}")
        
        print(f"Fallback data: {len(assignees)} assignees, {len(tasks)} tasks")
        
        return {
            "assignees": assignees,
            "tasks": tasks,
            "capacity_settings": capacity_settings
        }
        
    except Exception as e:
        print(f"Error in get_fallback_workload_data: {str(e)}")
        return {
            "assignees": [],
            "tasks": [],
            "capacity_settings": {
                "hours_per_day": 8,
                "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }
        }

@frappe.whitelist()
def create_atlas_task(task_data):
    """Create a new Atlas Task"""
    try:
        if not task_data:
            frappe.throw(_("Task data is required"))
            
        # Convert task_data from string to dict if needed
        if isinstance(task_data, str):
            task_data = frappe.parse_json(task_data)
            
        # Create task
        task = frappe.get_doc({
            "doctype": "Atlas Task",
            "naming_series": "TASK-.YYYY.-",
            "subject": task_data.get("subject"),
            "status": task_data.get("status", "Open"),
            "priority": task_data.get("priority", "Medium"),
            "department": task_data.get("department"),
            "exp_start_date": task_data.get("exp_start_date"),
            "exp_end_date": task_data.get("exp_end_date"),
            "expected_time": task_data.get("expected_time"),
            "progress": task_data.get("progress", 0),
            "_assign": task_data.get("_assign"),
            "description": task_data.get("description"),
            "color": task_data.get("color"),
            "is_milestone": task_data.get("is_milestone", 0)
        })
        
        task.insert()
        
        print(f"""
Created Atlas Task:
- Name: {task.name}
- Subject: {task.subject}
- Department: {task.department}
- Assigned to: {task._assign}
""")
        
        return {
            "success": True,
            "message": "Task created successfully",
            "task": task.as_dict()
        }
        
    except Exception as e:
        return handle_api_error(e, "Task Creation Error")

@frappe.whitelist()
def create_test_task():
    """Create a test Atlas Task for debugging"""
    try:
        verify_result = verify_task_structure()
        if not verify_result.get("success"):
            return verify_result
            
        departments = frappe.get_all("Department", fields=["name"])
        if not departments:
            return handle_api_error(
                Exception("No departments found"),
                "Test Task Creation Error",
                {"departments_exist": False}
            )
            
        department = departments[0].name
        
        employees = frappe.get_all(
            "Employee",
            filters={"department": department, "status": "Active"},
            fields=["name", "user_id", "employee_name"]
        )
        if not employees:
            return handle_api_error(
                Exception(f"No employees found in department {department}"),
                "Test Task Creation Error",
                {
                    "departments_exist": True,
                    "department": department,
                    "employees_exist": False
                }
            )
            
        employee = employees[0]
        
        task = frappe.get_doc({
            "doctype": "Atlas Task",
            "subject": "Test Task",
            "status": "Open",
            "priority": "Medium",
            "department": department,
            "_assign": frappe.as_json([employee.user_id]) if employee.user_id else None,
            "exp_start_date": frappe.utils.nowdate(),
            "exp_end_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
            "expected_time": 16,
            "description": f"Test task created for debugging purposes in department {department}"
        })
        task.insert()
        
        print(f"""
Created test task:
- Name: {task.name}
- Department: {task.department}
- Assigned to: {task._assign}
""")
        
        return {
            "success": True,
            "message": "Test task created successfully",
            "task": task.as_dict(),
            "metadata": {
                "department": department,
                "assignee": {
                    "id": employee.user_id,
                    "name": employee.employee_name,
                    "employee_id": employee.name
                }
            }
        }
        
    except Exception as e:
        return handle_api_error(
            e,
            "Test Task Creation Error",
            {
                "departments_exist": bool(departments),
                "department": department if 'department' in locals() else None,
                "employees_exist": bool(employees) if 'employees' in locals() else None
            }
        )

@frappe.whitelist()
def list_tasks():
    """List all Atlas Tasks in the system with their details"""
    try:
        tasks = frappe.get_all(
            "Atlas Task",
            fields=[
                "name", "subject", "status", "priority", "project",
                "exp_start_date", "exp_end_date", "expected_time",
                "department", "_assign", "owner", "creation"
            ],
            order_by="creation desc"
        )
        
        formatted_tasks = []
        for task in tasks:
            try:
                assignee = "Unassigned"
                if task._assign:
                    assigned_users = frappe.parse_json(task._assign)
                    if assigned_users and len(assigned_users) > 0:
                        assignee = assigned_users[0]
                
                formatted_tasks.append({
                    "id": task.name,
                    "title": task.subject,
                    "status": task.status,
                    "department": task.department,
                    "assignee": assignee,
                    "project": task.project,
                    "scheduled": bool(task.exp_start_date and task.exp_end_date),
                    "created_by": task.owner,
                    "created_at": task.creation
                })
            except Exception as e:
                print(f"Error formatting task {task.name}: {str(e)}")
                continue
        
        print(f"Found {len(tasks)} total tasks, {len(formatted_tasks)} formatted successfully")
        return {
            "total_count": len(tasks),
            "tasks": formatted_tasks
        }
        
    except Exception as e:
        print(f"Error listing tasks: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "List Tasks Error")
        return {"error": str(e), "total_count": 0, "tasks": []}

@frappe.whitelist()
def planner_get_backlog(searchtext=None, projectText=None):
    """Get Atlas Tasks for the backlog with enhanced search"""
    print(f"\n=== Planner Backlog Request ===") 
    try:
        filters = {
            "_assign": ["is", "null"],
        }
        
        if searchtext:
            filters.update({
                "subject": ["like", f"%{searchtext}%"]
            })
        
        if projectText:
            filters.update({
                "project": ["like", f"%{projectText}%"]
            })
        
        tasks = frappe.get_all(
            "Atlas Task",
            filters=filters,
            fields=[
                "name", "subject", "status", "priority", "project",
                "exp_start_date", "exp_end_date", "expected_time",
                "department", "color", "_assign"
            ],
            order_by="creation desc"
        )
        
        for task in tasks:
            task.color = get_task_color(task)
        
        return tasks
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Planner Backlog Error")
        return []

@frappe.whitelist()
def update_task(**kwargs):
    """Update Atlas Task with enhanced validation and real-time updates"""
    try:
        task_id = kwargs.get('task_id')
        updates = kwargs.get('updates')
        
        if not task_id:
            frappe.throw(_("Task ID is required"))
        
        task = frappe.get_doc("Atlas Task", task_id)
        
        valid_fields = [
            "status", "priority", "exp_start_date",
            "exp_end_date", "expected_time", "description"
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
        
        return task.as_dict()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Task Error")
        return {"error": str(e)}

@frappe.whitelist()
def batch_update_tasks(updates):
    """Update multiple Atlas Tasks in batch with real-time notifications"""
    try:
        if not updates:
            frappe.throw(_("No updates provided"))
        
        if hasattr(TaskService, 'batch_update_tasks'):
            updated_tasks = TaskService.batch_update_tasks(updates)
        else:
            updated_tasks = []
            for update in updates:
                result = update_task(update.get('task_id'), update.get('updates', {}))
                if 'error' not in result:
                    updated_tasks.append(result)
        
        return updated_tasks
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Batch Update Tasks Error")
        return {"error": str(e)}

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

def get_task_assignees(task):
    """Get detailed assignee information for Atlas Task"""
    assignees = []
    try:
        if task._assign:
            assigned_users = frappe.parse_json(task._assign)
            for user in assigned_users:
                user_info = frappe.get_cached_value(
                    "User",
                    user,
                    ["full_name", "user_image"],
                    as_dict=True
                )
                if user_info:
                    assignees.append({
                        "id": user,
                        "name": user_info.full_name,
                        "image": user_info.user_image
                    })
    except Exception as e:
        frappe.logger().error(f"Error getting task assignees: {str(e)}")
    
    return assignees

def get_primary_assignee(task):
    """Get the primary assignee from Atlas Task _assign field"""
    try:
        if task._assign:
            frappe.logger().debug(f"Task {task.name} _assign field: {task._assign}")
            assigned_users = frappe.parse_json(task._assign)
            frappe.logger().debug(f"Parsed assigned users: {assigned_users}")
            
            if assigned_users and len(assigned_users) > 0:
                assignee = assigned_users[0]
                user_exists = frappe.db.exists("User", assignee)
                if user_exists:
                    return assignee
                else:
                    frappe.logger().warning(f"Invalid user {assignee} assigned to task {task.name}")
            else:
                frappe.logger().debug(f"No users in _assign list for task {task.name}")
        else:
            frappe.logger().debug(f"No _assign field for task {task.name}")
    except Exception as e:
        frappe.logger().error(f"Error getting primary assignee for task {task.name}: {str(e)}")
    
    return "Unassigned"

@frappe.whitelist()
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
        
        try:
            task.save(ignore_version=True)
            frappe.db.commit()
        except frappe.TimestampMismatchError:
            task.reload()
            task.save(ignore_version=True)
            frappe.db.commit()
        
        emit_task_update(task)
        
        return {
            "success": True,
            "task": TaskService.format_task(task),
            "message": "Task moved successfully"
        }
        
    except Exception as e:
        frappe.logger().error(f"Error moving task: {str(e)}")
        return handle_api_error(e, "Move Task Error")
