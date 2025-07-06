# Copyright (c) 2025, ONFUSE AG and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_days, date_diff
from frappe import _
import json

@frappe.whitelist()
def get_timeline_data(configuration_name, start_date=None, end_date=None, filters=None):
	"""Get dynamic timeline data based on configuration"""
	try:
		# Get configuration
		config = frappe.get_doc("Timeline Configuration", configuration_name)
		if not config.is_active:
			frappe.throw(_("Timeline Configuration is not active"))
		
		# Parse filters
		if isinstance(filters, str):
			filters = json.loads(filters) if filters else {}
		elif not filters:
			filters = {}
		
		# Set default date range if not provided
		if not start_date:
			start_date = frappe.utils.nowdate()
		if not end_date:
			end_date = add_days(start_date, 30)  # Default 30-day range
		
		# Get row entities (e.g., Workstations)
		rows = get_row_entities(config, filters)
		
		# Get block entities (e.g., Work Orders)
		blocks = get_block_entities(config, start_date, end_date, filters)
		
		return {
			"success": True,
			"config": {
				"name": config.name,
				"configuration_name": config.configuration_name,
				"description": config.description,
				"row_doctype": config.row_doctype,
				"block_doctype": config.block_doctype,
				"field_mappings": {
					"row_to_block_field": config.row_to_block_field,
					"block_to_date_field": config.block_to_date_field,
					"row_label_field": config.row_label_field,
					"block_label_field": config.block_label_field,
					"block_color_field": config.block_color_field,
					"date_range_start_field": config.date_range_start_field,
					"date_range_end_field": config.date_range_end_field,
					"block_duration_field": config.block_duration_field,
					"block_status_field": config.block_status_field,
					"block_priority_field": config.block_priority_field
				}
			},
			"rows": rows,
			"blocks": blocks,
			"date_range": {
				"start_date": start_date,
				"end_date": end_date
			}
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Timeline Data Error")
		return {
			"success": False,
			"error": str(e),
			"rows": [],
			"blocks": [],
			"config": None
		}

def get_row_entities(config, filters=None):
	"""Get row entities based on configuration"""
	try:
		# Build filters for row doctype
		row_filters = {}
		if filters and filters.get("row_filters"):
			row_filters.update(filters["row_filters"])
		
		# Get required fields
		fields = ["name", config.row_label_field]
		
		# Add additional fields that might be useful
		row_meta = frappe.get_meta(config.row_doctype)
		additional_fields = ["status", "department", "company", "disabled"]
		for field in additional_fields:
			if row_meta.get_field(field):
				fields.append(field)
		
		# Remove duplicates
		fields = list(set(fields))
		
		# Get row entities
		rows = frappe.get_all(
			config.row_doctype,
			filters=row_filters,
			fields=fields,
			order_by=config.row_label_field
		)
		
		# Format row data
		formatted_rows = []
		for row in rows:
			formatted_row = {
				"id": row.name,
				"name": row.name,
				"label": row.get(config.row_label_field) or row.name,
				"doctype": config.row_doctype
			}
			
			# Add additional fields
			for field in fields:
				if field not in ["name", config.row_label_field]:
					formatted_row[field] = row.get(field)
			
			formatted_rows.append(formatted_row)
		
		return formatted_rows
		
	except Exception as e:
		frappe.log_error(f"Error getting row entities: {str(e)}", "Timeline Row Entities Error")
		return []

def get_block_entities(config, start_date, end_date, filters=None):
	"""Get block entities based on configuration and date range"""
	try:
		# Build filters for block doctype
		block_filters = {}
		if filters and filters.get("block_filters"):
			block_filters.update(filters["block_filters"])
		
		# Add date range filter
		date_field = config.block_to_date_field
		if config.date_range_start_field and config.date_range_end_field:
			# Handle date range blocks
			block_filters.update({
				config.date_range_start_field: ["<=", end_date],
				config.date_range_end_field: [">=", start_date]
			})
		else:
			# Handle single date blocks
			block_filters.update({
				date_field: ["between", [start_date, end_date]]
			})
		
		# Get required fields
		fields = [
			"name", 
			config.row_to_block_field, 
			config.block_to_date_field,
			config.block_label_field
		]
		
		# Add optional fields if they exist
		optional_fields = [
			config.block_color_field,
			config.date_range_start_field,
			config.date_range_end_field,
			config.block_duration_field,
			config.block_status_field,
			config.block_priority_field
		]
		
		for field in optional_fields:
			if field:
				fields.append(field)
		
		# Add common useful fields
		block_meta = frappe.get_meta(config.block_doctype)
		additional_fields = ["status", "priority", "progress", "description", "owner", "creation", "modified"]
		for field in additional_fields:
			if block_meta.get_field(field) and field not in fields:
				fields.append(field)
		
		# Remove duplicates and None values
		fields = list(set([f for f in fields if f]))
		
		# Get block entities
		blocks = frappe.get_all(
			config.block_doctype,
			filters=block_filters,
			fields=fields,
			order_by=f"{config.block_to_date_field} asc"
		)
		
		# Format block data
		formatted_blocks = []
		for block in blocks:
			formatted_block = {
				"id": block.name,
				"name": block.name,
				"label": block.get(config.block_label_field) or block.name,
				"doctype": config.block_doctype,
				"row_id": block.get(config.row_to_block_field),
				"date": block.get(config.block_to_date_field)
			}
			
			# Add date range if available
			if config.date_range_start_field and config.date_range_end_field:
				formatted_block["start_date"] = block.get(config.date_range_start_field)
				formatted_block["end_date"] = block.get(config.date_range_end_field)
			
			# Add optional fields
			if config.block_duration_field:
				formatted_block["duration"] = block.get(config.block_duration_field) or 0
			
			if config.block_status_field:
				formatted_block["status"] = block.get(config.block_status_field)
			
			if config.block_priority_field:
				formatted_block["priority"] = block.get(config.block_priority_field)
			
			if config.block_color_field:
				formatted_block["color"] = block.get(config.block_color_field)
			
			# Add other useful fields
			for field in ["progress", "description", "owner", "creation", "modified"]:
				if field in fields:
					formatted_block[field] = block.get(field)
			
			formatted_blocks.append(formatted_block)
		
		return formatted_blocks
		
	except Exception as e:
		frappe.log_error(f"Error getting block entities: {str(e)}", "Timeline Block Entities Error")
		return []

@frappe.whitelist()
def update_block_assignment(block_doctype, block_name, new_row_assignment, new_date=None, config_name=None):
	"""Update block assignment to a different row or date"""
	try:
		# Get the block document
		block_doc = frappe.get_doc(block_doctype, block_name)
		
		# Get configuration if provided
		config = None
		if config_name:
			config = frappe.get_doc("Timeline Configuration", config_name)
		
		# Update row assignment
		if new_row_assignment and config:
			setattr(block_doc, config.row_to_block_field, new_row_assignment)
		
		# Update date if provided
		if new_date and config:
			setattr(block_doc, config.block_to_date_field, getdate(new_date))
		
		# Save the document
		block_doc.save(ignore_permissions=True)
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Block assignment updated successfully",
			"block": block_doc.as_dict()
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Block Assignment Error")
		return {
			"success": False,
			"error": str(e)
		}

@frappe.whitelist()
def get_timeline_configurations():
	"""Get available timeline configurations for selection"""
	try:
		from planner.planner.doctype.timeline_configuration.timeline_configuration import get_available_configurations
		return get_available_configurations()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Timeline Configurations Error")
		return []

@frappe.whitelist()
def create_sample_workstation_configuration():
	"""Create sample configuration for Workstation -> Work Order timeline"""
	try:
		# Check if configuration already exists
		if frappe.db.exists("Timeline Configuration", "workstation-work-order"):
			return {
				"success": True,
				"message": "Configuration already exists",
				"name": "workstation-work-order"
			}
		
		# Create the configuration
		config = frappe.get_doc({
			"doctype": "Timeline Configuration",
			"configuration_name": "Job Card Planning",
			"description": "Plan Work Orders across Workstations for Job Card scheduling",
			"is_active": 1,
			"row_doctype": "Workstation",
			"block_doctype": "Work Order",
			"row_to_block_field": "workstation",
			"block_to_date_field": "planned_start_date",
			"row_label_field": "workstation_name",
			"block_label_field": "production_item",
			"block_color_field": "status",
			"date_range_start_field": "planned_start_date",
			"date_range_end_field": "planned_end_date",
			"block_duration_field": "expected_time",
			"block_status_field": "status",
			"block_priority_field": "priority"
		})
		
		config.insert(ignore_permissions=True)
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Sample configuration created successfully",
			"name": config.name
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Sample Configuration Error")
		return {
			"success": False,
			"error": str(e)
		}