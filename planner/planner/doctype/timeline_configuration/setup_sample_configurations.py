import frappe
from frappe import _
from datetime import datetime, timedelta

def create_timeline_configurations():
    """Create proper timeline configurations for job card planning"""
    
    try:
        # Create Workstation → Work Order configuration for Job Card Planning
        if not frappe.db.exists("Timeline Configuration", "workstation-work-order"):
            workstation_config = frappe.get_doc({
                "doctype": "Timeline Configuration",
                "name": "workstation-work-order",
                "configuration_name": "Job Card Planning",
                "description": "Plan and schedule work orders across workstations to create job cards",
                "row_doctype": "Workstation",
                "block_doctype": "Work Order",
                "row_to_block_field": "workstation",
                "block_to_date_field": "planned_start_date",
                "date_range_end_field": "planned_end_date",
                "row_label_field": "workstation_name",
                "block_label_field": "production_item",
                "block_status_field": "status",
                "block_priority_field": "priority",
                "block_duration_field": "expected_time",
                "is_active": 1
            })
            workstation_config.insert()
            print(f"Created configuration: {workstation_config.name}")
        
        # Create User → Atlas Task configuration (if Atlas Task exists)
        if frappe.db.exists("DocType", "Atlas Task"):
            if not frappe.db.exists("Timeline Configuration", "user-atlas-task"):
                user_task_config = frappe.get_doc({
                    "doctype": "Timeline Configuration",
                    "name": "user-atlas-task",
                    "configuration_name": "Team Task Planning",
                    "description": "Assign and track Atlas Tasks across team members by due date",
                    "row_doctype": "User",
                    "block_doctype": "Atlas Task",
                    "row_to_block_field": "_assign",
                    "block_to_date_field": "exp_start_date",
                    "date_range_end_field": "exp_end_date",
                    "row_label_field": "full_name",
                    "block_label_field": "subject",
                    "block_status_field": "status",
                    "block_priority_field": "priority",
                    "is_active": 1
                })
                user_task_config.insert()
                print(f"Created configuration: {user_task_config.name}")
        
        frappe.db.commit()
        print("Timeline configurations created successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error creating timeline configurations: {str(e)}")
        raise

def create_sample_workstations():
    """Create sample workstations for job card planning"""
    
    try:
        workstations = [
            {
                "workstation_name": "CNC Machine 1",
                "workstation_type": "CNC",
                "description": "High precision CNC machine for metal cutting"
            },
            {
                "workstation_name": "Assembly Line A",
                "workstation_type": "Assembly",
                "description": "Main assembly line for product assembly"
            },
            {
                "workstation_name": "Quality Check Station",
                "workstation_type": "QC",
                "description": "Quality control and inspection station"
            },
            {
                "workstation_name": "Packaging Unit",
                "workstation_type": "Packaging",
                "description": "Product packaging and finishing"
            }
        ]
        
        for ws_data in workstations:
            if not frappe.db.exists("Workstation", ws_data["workstation_name"]):
                ws = frappe.get_doc({
                    "doctype": "Workstation",
                    **ws_data
                })
                ws.insert()
                print(f"Created workstation: {ws.name}")
        
        frappe.db.commit()
        print("Sample workstations created successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error creating workstations: {str(e)}")
        raise

def create_sample_work_orders():
    """Create sample work orders for job card planning"""
    
    try:
        # First, create some sample items if they don't exist
        sample_items = [
            {"item_code": "WIDGET-A", "item_name": "Widget A", "item_group": "Products"},
            {"item_code": "WIDGET-B", "item_name": "Widget B", "item_group": "Products"},
            {"item_code": "WIDGET-C", "item_name": "Widget C", "item_group": "Products"}
        ]
        
        for item_data in sample_items:
            if not frappe.db.exists("Item", item_data["item_code"]):
                item = frappe.get_doc({
                    "doctype": "Item",
                    **item_data
                })
                item.insert()
                print(f"Created item: {item.item_code}")
        
        # Create work orders
        work_orders = [
            {
                "production_item": "WIDGET-A",
                "qty": 100,
                "description": "Production of Widget A - Batch 001",
                "planned_start_date": datetime.now().date(),
                "planned_end_date": datetime.now().date() + timedelta(days=2),
                "status": "Not Started",
                "priority": "High"
            },
            {
                "production_item": "WIDGET-B",
                "qty": 50,
                "description": "Production of Widget B - Batch 002",
                "planned_start_date": datetime.now().date() + timedelta(days=1),
                "planned_end_date": datetime.now().date() + timedelta(days=3),
                "status": "Not Started",
                "priority": "Medium"
            },
            {
                "production_item": "WIDGET-C",
                "qty": 75,
                "description": "Quality check for Widget C",
                "planned_start_date": datetime.now().date() + timedelta(days=2),
                "planned_end_date": datetime.now().date() + timedelta(days=2),
                "status": "Not Started",
                "priority": "Low"
            }
        ]
        
        for wo_data in work_orders:
            # Check if work order with same production item and workstation exists
            existing_wo = frappe.db.exists("Work Order", {
                "production_item": wo_data["production_item"],
            })
            
            if not existing_wo:
                wo = frappe.get_doc({
                    "doctype": "Work Order",
                    **wo_data
                })
                wo.insert()
                print(f"Created work order: {wo.name}")
        
        frappe.db.commit()
        print("Sample work orders created successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error creating work orders: {str(e)}")
        raise

@frappe.whitelist()
def create_job_card_from_work_order(work_order_name, workstation_name=None):
    """Create a job card from a work order assigned to a workstation"""
    
    try:
        # Get the work order
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        # Use provided workstation or the one from work order
        target_workstation = workstation_name
        
        if not target_workstation:
            frappe.throw(_("Workstation is required to create a job card"))
        
        # Check if job card already exists for this work order and workstation
        existing_job_card = frappe.db.exists("Job Card", {
            "work_order": work_order_name,
            "workstation": target_workstation
        })
        
        if existing_job_card:
            return {
                "success": False,
                "message": f"Job Card already exists: {existing_job_card}",
                "job_card": existing_job_card
            }
        
        # Create new job card
        job_card = frappe.get_doc({
            "doctype": "Job Card",
            "work_order": work_order_name,
            "workstation": target_workstation,
            "production_item": work_order.production_item,
            "item_name": work_order.get("item_name", ""),
            "qty": work_order.qty,
            "description": work_order.description or f"Job Card for {work_order.production_item}",
            "planned_start_date": work_order.planned_start_date,
            "planned_end_date": work_order.planned_end_date,
            "status": "Open",
            "priority": work_order.get("priority", "Medium")
        })
        
        job_card.insert()
        
        # Update work order status if needed
        if work_order.status == "Not Started":
            work_order.status = "In Process"
            work_order.save()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Job Card created successfully: {job_card.name}",
            "job_card": job_card.name,
            "work_order": work_order_name,
            "workstation": target_workstation
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error creating job card: {str(e)}")
        return {
            "success": False,
            "message": f"Error creating job card: {str(e)}"
        }

@frappe.whitelist()
def assign_work_order_to_workstation(work_order_name, workstation_name, planned_start_date=None):
    """Assign a work order to a workstation and optionally create job card"""
    
    try:
        # Get the work order
        work_order = frappe.get_doc("Work Order", work_order_name)
        
        # Create a new job card with the provided workstation and work order
        
        # work_order.workstation = workstation_name
        
        # Update planned start date if provided
        if planned_start_date:
            work_order.planned_start_date = planned_start_date
        
        work_order.save()
        
        # Optionally create job card
        job_card_result = create_job_card_from_work_order(work_order_name, workstation_name)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Work Order {work_order_name} assigned to {workstation_name}",
            "work_order": work_order_name,
            "workstation": workstation_name,
            "job_card_result": job_card_result
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error assigning work order to workstation: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

@frappe.whitelist()
def get_workstation_work_orders(workstation_name, start_date=None, end_date=None):
    """Get all work orders assigned to a specific workstation"""
    
    try:
        #filters = {"workstation": workstation_name}
        filters = {} 
        if start_date and end_date:
            filters["planned_start_date"] = ["between", [start_date, end_date]]
        
        work_orders = frappe.get_all(
            "Work Order",
            filters=filters,
            fields=[
                "name", "production_item", "qty", "description",
                "planned_start_date", "planned_end_date", "status", "priority"
            ],
            order_by="planned_start_date asc"
        )
        
        return {
            "success": True,
            "workstation": workstation_name,
            "work_orders": work_orders,
            "count": len(work_orders)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting workstation work orders: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

def setup_job_card_system():
    """Complete setup for job card system"""
    
    print("Setting up Job Card System...")
    
    # Create timeline configurations
    create_timeline_configurations()
    
    # Create sample workstations
    create_sample_workstations()
    
    # Create sample work orders
    create_sample_work_orders()
    
    print("Job Card System setup completed!")

if __name__ == "__main__":
    setup_job_card_system()