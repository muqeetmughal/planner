# Copyright (c) 2025, ONFUSE AG and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import getdate, add_days, nowdate
from planner.planner.api.timeline_data import (
    get_timeline_data,
    update_block_assignment,
    get_timeline_configurations,
    create_sample_workstation_configuration
)

class TestTimelineAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests"""
        cls.setup_test_data()

    @classmethod
    def tearDownClass(cls):
        """Clean up test data after all tests"""
        cls.cleanup_test_data()

    @classmethod
    def setup_test_data(cls):
        """Create test workstations, work orders, and timeline configuration"""
        frappe.db.begin()

        try:
            # Create test workstations
            cls.workstations = []
            for i in range(1, 4):
                workstation_name = f"Test Workstation {i}"
                if not frappe.db.exists("Workstation", workstation_name):
                    workstation = frappe.get_doc({
                        "doctype": "Workstation",
                        "workstation_name": workstation_name,
                        "workstation_type": "Testing",
                        "description": f"Test workstation {i} for timeline testing"
                    })
                    workstation.insert(ignore_permissions=True)
                    cls.workstations.append(workstation.name)
                else:
                    cls.workstations.append(workstation_name)

            # Create test items
            cls.items = []
            for i in range(1, 4):
                item_code = f"TEST-ITEM-{i}"
                if not frappe.db.exists("Item", item_code):
                    item = frappe.get_doc({
                        "doctype": "Item",
                        "item_code": item_code,
                        "item_name": f"Test Item {i}",
                        "item_group": "Products",
                        "stock_uom": "Nos"
                    })
                    item.insert(ignore_permissions=True)
                    cls.items.append(item.item_code)
                else:
                    cls.items.append(item_code)

            # Create test work orders
            cls.work_orders = []
            for i, item in enumerate(cls.items):
                work_order = frappe.get_doc({
                    "doctype": "Work Order",
                    "production_item": item,
                    "qty": 100 * (i + 1),
                    "planned_start_date": add_days(nowdate(), i),
                    "planned_end_date": add_days(nowdate(), i + 2),
                    "status": "Not Started",
                    "priority": ["High", "Medium", "Low"][i % 3]
                })
                work_order.insert(ignore_permissions=True)
                cls.work_orders.append(work_order.name)

            # Create test timeline configuration
            cls.config_name = "test-workstation-work-order"
            if not frappe.db.exists("Timeline Configuration", cls.config_name):
                config = frappe.get_doc({
                    "doctype": "Timeline Configuration",
                    "name": cls.config_name,
                    "configuration_name": "Test Job Card Planning",
                    "description": "Test configuration for timeline API testing",
                    "row_doctype": "Workstation",
                    "block_doctype": "Work Order",
                    "row_to_block_field": "workstation",
                    "block_to_date_field": "planned_start_date",
                    "row_label_field": "workstation_name",
                    "block_label_field": "production_item",
                    "block_status_field": "status",
                    "block_priority_field": "priority",
                    "date_range_start_field": "planned_start_date",
                    "date_range_end_field": "planned_end_date",
                    "is_active": 1
                })
                config.insert(ignore_permissions=True)

            frappe.db.commit()

        except Exception as e:
            frappe.db.rollback()
            raise e

    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        try:
            frappe.db.begin()

            # Delete test work orders
            for work_order in cls.work_orders:
                if frappe.db.exists("Work Order", work_order):
                    frappe.delete_doc("Work Order", work_order, ignore_permissions=True)

            # Delete test items
            for item in cls.items:
                if frappe.db.exists("Item", item):
                    frappe.delete_doc("Item", item, ignore_permissions=True)

            # Delete test workstations
            for workstation in cls.workstations:
                if frappe.db.exists("Workstation", workstation):
                    frappe.delete_doc("Workstation", workstation, ignore_permissions=True)

            # Delete test configuration
            if frappe.db.exists("Timeline Configuration", cls.config_name):
                frappe.delete_doc("Timeline Configuration", cls.config_name, ignore_permissions=True)

            frappe.db.commit()

        except Exception as e:
            frappe.db.rollback()
            print(f"Error cleaning up test data: {e}")

    def test_get_timeline_configurations(self):
        """Test getting available timeline configurations"""
        configurations = get_timeline_configurations()

        self.assertIsInstance(configurations, list)

        # Check if our test configuration exists
        config_names = [config.get("name") for config in configurations]
        self.assertIn(self.config_name, config_names)

    def test_get_timeline_data_basic(self):
        """Test basic timeline data retrieval"""
        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=nowdate(),
            end_date=add_days(nowdate(), 7)
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("success"))
        self.assertIn("config", result)
        self.assertIn("rows", result)
        self.assertIn("blocks", result)
        self.assertIn("date_range", result)

        # Check configuration
        config = result["config"]
        self.assertEqual(config["name"], self.config_name)
        self.assertEqual(config["row_doctype"], "Workstation")
        self.assertEqual(config["block_doctype"], "Work Order")

        # Check rows (workstations)
        rows = result["rows"]
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)

        # Check blocks (work orders)
        blocks = result["blocks"]
        self.assertIsInstance(blocks, list)
        self.assertGreaterEqual(len(blocks), 0)

    def test_get_timeline_data_with_filters(self):
        """Test timeline data retrieval with filters"""
        filters = {
            "row_filters": {},
            "block_filters": {"status": "Not Started"}
        }

        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=nowdate(),
            end_date=add_days(nowdate(), 7),
            filters=filters
        )

        self.assertTrue(result.get("success"))

        # All returned blocks should have status "Not Started"
        blocks = result["blocks"]
        for block in blocks:
            self.assertEqual(block.get("status"), "Not Started")

    def test_update_block_assignment_basic(self):
        """Test basic block assignment update"""
        # Get a work order and workstation
        work_order_name = self.work_orders[0]
        workstation_name = self.workstations[0]
        new_date = add_days(nowdate(), 1)

        # Update assignment
        result = update_block_assignment(
            block_doctype="Work Order",
            block_name=work_order_name,
            new_row_assignment=workstation_name,
            new_date=new_date.strftime("%Y-%m-%d"),
            config_name=self.config_name
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("success"))
        self.assertIn("message", result)
        self.assertIn("block", result)

        # Verify the assignment was updated
        work_order = frappe.get_doc("Work Order", work_order_name)
        self.assertEqual(work_order.workstation, workstation_name)
        self.assertEqual(work_order.planned_start_date, new_date)

    def test_update_block_assignment_with_date_range(self):
        """Test block assignment update with date range handling"""
        work_order_name = self.work_orders[1]
        workstation_name = self.workstations[1]
        new_date = add_days(nowdate(), 2)

        # Get original work order data
        original_work_order = frappe.get_doc("Work Order", work_order_name)
        original_duration = (original_work_order.planned_end_date - original_work_order.planned_start_date).days

        # Update assignment
        result = update_block_assignment(
            block_doctype="Work Order",
            block_name=work_order_name,
            new_row_assignment=workstation_name,
            new_date=new_date.strftime("%Y-%m-%d"),
            config_name=self.config_name
        )

        self.assertTrue(result.get("success"))

        # Verify the assignment and date range were updated
        updated_work_order = frappe.get_doc("Work Order", work_order_name)
        self.assertEqual(updated_work_order.workstation, workstation_name)
        self.assertEqual(updated_work_order.planned_start_date, new_date)

        # Check that the duration is maintained
        new_duration = (updated_work_order.planned_end_date - updated_work_order.planned_start_date).days
        self.assertEqual(new_duration, original_duration)

    def test_update_block_assignment_invalid_block(self):
        """Test block assignment update with invalid block"""
        result = update_block_assignment(
            block_doctype="Work Order",
            block_name="INVALID-WORK-ORDER",
            new_row_assignment=self.workstations[0],
            new_date=nowdate().strftime("%Y-%m-%d"),
            config_name=self.config_name
        )

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_create_sample_workstation_configuration(self):
        """Test creating sample workstation configuration"""
        # This should create or return existing configuration
        result = create_sample_workstation_configuration()

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("success"))
        self.assertIn("message", result)

        # Check that the configuration exists
        config_exists = frappe.db.exists("Timeline Configuration", "workstation-work-order")
        self.assertTrue(config_exists)

    def test_get_timeline_data_error_handling(self):
        """Test error handling in timeline data retrieval"""
        # Test with invalid configuration
        result = get_timeline_data(
            configuration_name="INVALID-CONFIG",
            start_date=nowdate(),
            end_date=add_days(nowdate(), 7)
        )

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertEqual(result["rows"], [])
        self.assertEqual(result["blocks"], [])

    def test_timeline_data_date_range_handling(self):
        """Test timeline data with different date ranges"""
        # Test with past dates (should return empty blocks)
        past_start = add_days(nowdate(), -10)
        past_end = add_days(nowdate(), -5)

        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=past_start.strftime("%Y-%m-%d"),
            end_date=past_end.strftime("%Y-%m-%d")
        )

        self.assertTrue(result.get("success"))
        self.assertEqual(len(result["blocks"]), 0)

        # Test with future dates
        future_start = add_days(nowdate(), 10)
        future_end = add_days(nowdate(), 15)

        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=future_start.strftime("%Y-%m-%d"),
            end_date=future_end.strftime("%Y-%m-%d")
        )

        self.assertTrue(result.get("success"))
        # Should have rows but no blocks in future date range
        self.assertGreater(len(result["rows"]), 0)

    def test_timeline_data_formatting(self):
        """Test that timeline data is properly formatted"""
        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=nowdate(),
            end_date=add_days(nowdate(), 7)
        )

        self.assertTrue(result.get("success"))

        # Check row formatting
        rows = result["rows"]
        for row in rows:
            self.assertIn("id", row)
            self.assertIn("name", row)
            self.assertIn("label", row)
            self.assertIn("doctype", row)
            self.assertEqual(row["doctype"], "Workstation")

        # Check block formatting
        blocks = result["blocks"]
        for block in blocks:
            self.assertIn("id", block)
            self.assertIn("name", block)
            self.assertIn("label", block)
            self.assertIn("doctype", block)
            self.assertIn("date", block)
            self.assertEqual(block["doctype"], "Work Order")

    def test_multiple_assignments_same_workstation(self):
        """Test assigning multiple work orders to the same workstation"""
        workstation_name = self.workstations[0]

        # Assign multiple work orders to the same workstation
        for i, work_order_name in enumerate(self.work_orders):
            result = update_block_assignment(
                block_doctype="Work Order",
                block_name=work_order_name,
                new_row_assignment=workstation_name,
                new_date=add_days(nowdate(), i).strftime("%Y-%m-%d"),
                config_name=self.config_name
            )
            self.assertTrue(result.get("success"))

        # Get timeline data and check that all work orders are assigned
        result = get_timeline_data(
            configuration_name=self.config_name,
            start_date=nowdate(),
            end_date=add_days(nowdate(), 7)
        )

        self.assertTrue(result.get("success"))

        # Count blocks assigned to our workstation
        assigned_blocks = [block for block in result["blocks"] if block.get("row_id") == workstation_name]
        self.assertEqual(len(assigned_blocks), len(self.work_orders))


def run_timeline_tests():
    """Run all timeline API tests"""
    import sys

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTimelineAPI)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run tests when executed directly
    success = run_timeline_tests()
    if not success:
        sys.exit(1)
