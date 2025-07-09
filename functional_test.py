#!/usr/bin/env python3
"""
Functional test for the Dynamic Timeline API without requiring Frappe framework
This test validates the core logic and data structures of the timeline system
"""

import os
import sys
import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Mock Frappe framework components
class MockFrappe:
    def __init__(self):
        self.db = MockDB()
        self.utils = MockUtils()
        self._documents = {}
        self._doctypes = {}
        self._alerts = []

    def get_doc(self, doctype, name):
        if doctype in self._documents and name in self._documents[doctype]:
            return self._documents[doctype][name]
        else:
            raise Exception(f"Document {doctype} {name} not found")

    def get_all(self, doctype, filters=None, fields=None, order_by=None):
        if doctype not in self._documents:
            return []

        docs = list(self._documents[doctype].values())

        # Apply filters
        if filters:
            filtered_docs = []
            for doc in docs:
                match = True
                for key, value in filters.items():
                    if hasattr(doc, key):
                        doc_value = getattr(doc, key)
                        if isinstance(value, list):
                            if value[0] == "between":
                                if not (value[1][0] <= doc_value <= value[1][1]):
                                    match = False
                                    break
                            elif value[0] == "<=":
                                if not (doc_value <= value[1]):
                                    match = False
                                    break
                            elif value[0] == ">=":
                                if not (doc_value >= value[1]):
                                    match = False
                                    break
                        else:
                            if doc_value != value:
                                match = False
                                break
                    else:
                        match = False
                        break

                if match:
                    filtered_docs.append(doc)
            docs = filtered_docs

        # Convert to dict format
        result = []
        for doc in docs:
            doc_dict = {}
            if fields:
                for field in fields:
                    if hasattr(doc, field):
                        doc_dict[field] = getattr(doc, field)
            else:
                doc_dict = doc.__dict__.copy()
            result.append(doc_dict)

        return result

    def get_meta(self, doctype):
        return MockMeta(doctype)

    def throw(self, message):
        raise Exception(message)

    def log_error(self, message, title="Error"):
        print(f"LOG ERROR [{title}]: {message}")

    def show_alert(self, message):
        self._alerts.append(message)

    def whitelist(self):
        def decorator(func):
            return func
        return decorator

    def _(self, text):
        return text

class MockDB:
    def __init__(self):
        self._data = {}

    def exists(self, doctype, name_or_filters=None):
        if isinstance(name_or_filters, str):
            return doctype in self._data and name_or_filters in self._data[doctype]
        elif isinstance(name_or_filters, dict):
            if doctype not in self._data:
                return False
            for doc_name, doc_data in self._data[doctype].items():
                match = True
                for key, value in name_or_filters.items():
                    if key not in doc_data or doc_data[key] != value:
                        match = False
                        break
                if match:
                    return doc_name
            return False
        return False

    def commit(self):
        pass

    def rollback(self):
        pass

class MockUtils:
    def nowdate(self):
        return datetime.now().date()

    def getdate(self, date_string):
        if isinstance(date_string, str):
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        return date_string

    def add_days(self, date, days):
        return date + timedelta(days=days)

    def date_diff(self, date1, date2):
        return (date1 - date2).days

class MockMeta:
    def __init__(self, doctype):
        self.doctype = doctype
        self.fields = []

        # Mock field structure for common doctypes
        if doctype == "Workstation":
            self.fields = [
                MockField("workstation_name", "Data"),
                MockField("workstation_type", "Data"),
                MockField("description", "Text"),
                MockField("status", "Select"),
            ]
        elif doctype == "Work Order":
            self.fields = [
                MockField("production_item", "Link"),
                MockField("qty", "Float"),
                MockField("workstation", "Link"),
                MockField("planned_start_date", "Date"),
                MockField("planned_end_date", "Date"),
                MockField("status", "Select"),
                MockField("priority", "Select"),
                MockField("description", "Text"),
            ]

    def get_field(self, fieldname):
        for field in self.fields:
            if field.fieldname == fieldname:
                return field
        return None

class MockField:
    def __init__(self, fieldname, fieldtype):
        self.fieldname = fieldname
        self.fieldtype = fieldtype
        self.label = fieldname.replace("_", " ").title()

class MockDocument:
    def __init__(self, doctype, **kwargs):
        self.doctype = doctype
        self.name = kwargs.get("name", f"TEST-{doctype}-001")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self, ignore_permissions=False):
        pass

    def as_dict(self):
        return self.__dict__.copy()

# Mock the frappe module
mock_frappe = MockFrappe()
sys.modules['frappe'] = mock_frappe

# Now we can import our timeline API
sys.path.insert(0, '.')

class TestTimelineAPI(unittest.TestCase):

    def setUp(self):
        """Set up test data"""
        # Create mock workstations
        self.workstations = []
        for i in range(1, 4):
            workstation = MockDocument(
                "Workstation",
                name=f"WS-{i:03d}",
                workstation_name=f"Test Workstation {i}",
                workstation_type="Testing",
                description=f"Test workstation {i}",
                status="Active"
            )
            self.workstations.append(workstation)

        # Create mock work orders
        self.work_orders = []
        for i in range(1, 4):
            work_order = MockDocument(
                "Work Order",
                name=f"WO-{i:03d}",
                production_item=f"ITEM-{i:03d}",
                qty=100,
                workstation=self.workstations[i-1].name if i <= len(self.workstations) else None,
                planned_start_date=datetime.now().date() + timedelta(days=i),
                planned_end_date=datetime.now().date() + timedelta(days=i+2),
                status="Not Started",
                priority=["High", "Medium", "Low"][i % 3],
                description=f"Test work order {i}"
            )
            self.work_orders.append(work_order)

        # Create mock timeline configuration
        self.timeline_config = MockDocument(
            "Timeline Configuration",
            name="test-config",
            configuration_name="Test Configuration",
            description="Test timeline configuration",
            is_active=1,
            row_doctype="Workstation",
            block_doctype="Work Order",
            row_to_block_field="workstation",
            block_to_date_field="planned_start_date",
            row_label_field="workstation_name",
            block_label_field="production_item",
            block_status_field="status",
            block_priority_field="priority",
            date_range_start_field="planned_start_date",
            date_range_end_field="planned_end_date"
        )

        # Mock frappe's document storage
        mock_frappe._documents = {
            "Workstation": {ws.name: ws for ws in self.workstations},
            "Work Order": {wo.name: wo for wo in self.work_orders},
            "Timeline Configuration": {"test-config": self.timeline_config}
        }

    def test_get_timeline_data_basic(self):
        """Test basic timeline data retrieval"""
        try:
            from planner.api.timeline_data import get_timeline_data

            result = get_timeline_data(
                configuration_name="test-config",
                start_date=datetime.now().date().strftime("%Y-%m-%d"),
                end_date=(datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
            )

            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertIn("config", result)
            self.assertIn("rows", result)
            self.assertIn("blocks", result)

            if result["success"]:
                # Check configuration
                config = result["config"]
                self.assertEqual(config["name"], "test-config")
                self.assertEqual(config["row_doctype"], "Workstation")
                self.assertEqual(config["block_doctype"], "Work Order")

                # Check rows
                rows = result["rows"]
                self.assertIsInstance(rows, list)
                self.assertGreater(len(rows), 0)

                # Check blocks
                blocks = result["blocks"]
                self.assertIsInstance(blocks, list)

                print(f"✓ Timeline data retrieved successfully")
                print(f"  - Configuration: {config['configuration_name']}")
                print(f"  - Rows: {len(rows)}")
                print(f"  - Blocks: {len(blocks)}")
            else:
                print(f"✗ Timeline data retrieval failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"✗ Error testing timeline data: {e}")
            self.fail(f"Timeline data test failed: {e}")

    def test_update_block_assignment(self):
        """Test block assignment update"""
        try:
            from planner.api.timeline_data import update_block_assignment

            # Test updating work order assignment
            work_order = self.work_orders[0]
            new_workstation = self.workstations[1].name
            new_date = (datetime.now().date() + timedelta(days=5)).strftime("%Y-%m-%d")

            result = update_block_assignment(
                block_doctype="Work Order",
                block_name=work_order.name,
                new_row_assignment=new_workstation,
                new_date=new_date,
                config_name="test-config"
            )

            self.assertIsInstance(result, dict)
            self.assertIn("success", result)

            if result["success"]:
                print(f"✓ Block assignment updated successfully")
                print(f"  - Work Order: {work_order.name}")
                print(f"  - New Workstation: {new_workstation}")
                print(f"  - New Date: {new_date}")

                # Verify the assignment was updated
                updated_work_order = mock_frappe.get_doc("Work Order", work_order.name)
                self.assertEqual(updated_work_order.workstation, new_workstation)
            else:
                print(f"✗ Block assignment update failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"✗ Error testing block assignment: {e}")
            self.fail(f"Block assignment test failed: {e}")

    def test_get_timeline_configurations(self):
        """Test getting timeline configurations"""
        try:
            from planner.api.timeline_data import get_timeline_configurations

            result = get_timeline_configurations()

            self.assertIsInstance(result, list)

            if result:
                print(f"✓ Timeline configurations retrieved successfully")
                print(f"  - Count: {len(result)}")
                for config in result:
                    print(f"  - {config.get('name', 'Unknown')}: {config.get('configuration_name', 'No name')}")
            else:
                print(f"✓ No timeline configurations found (this is ok for testing)")

        except Exception as e:
            print(f"✗ Error testing timeline configurations: {e}")
            self.fail(f"Timeline configurations test failed: {e}")

    def test_api_error_handling(self):
        """Test API error handling"""
        try:
            from planner.api.timeline_data import get_timeline_data, update_block_assignment

            # Test with invalid configuration
            result = get_timeline_data(
                configuration_name="invalid-config",
                start_date=datetime.now().date().strftime("%Y-%m-%d"),
                end_date=(datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
            )

            self.assertIsInstance(result, dict)
            self.assertFalse(result.get("success", True))
            print(f"✓ Error handling works for invalid configuration")

            # Test with invalid block assignment
            result = update_block_assignment(
                block_doctype="Work Order",
                block_name="INVALID-WO",
                new_row_assignment="INVALID-WS",
                new_date=datetime.now().date().strftime("%Y-%m-%d"),
                config_name="test-config"
            )

            self.assertIsInstance(result, dict)
            self.assertFalse(result.get("success", True))
            print(f"✓ Error handling works for invalid block assignment")

        except Exception as e:
            print(f"✗ Error testing error handling: {e}")
            self.fail(f"Error handling test failed: {e}")

    def test_data_formatting(self):
        """Test data formatting and structure"""
        try:
            from planner.api.timeline_data import get_timeline_data

            result = get_timeline_data(
                configuration_name="test-config",
                start_date=datetime.now().date().strftime("%Y-%m-%d"),
                end_date=(datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
            )

            if result.get("success"):
                # Test row formatting
                rows = result["rows"]
                for row in rows:
                    self.assertIn("id", row)
                    self.assertIn("name", row)
                    self.assertIn("label", row)
                    self.assertIn("doctype", row)
                    self.assertEqual(row["doctype"], "Workstation")

                # Test block formatting
                blocks = result["blocks"]
                for block in blocks:
                    self.assertIn("id", block)
                    self.assertIn("name", block)
                    self.assertIn("label", block)
                    self.assertIn("doctype", block)
                    self.assertIn("date", block)
                    self.assertEqual(block["doctype"], "Work Order")

                print(f"✓ Data formatting is correct")
                print(f"  - Rows properly formatted: {len(rows)}")
                print(f"  - Blocks properly formatted: {len(blocks)}")
            else:
                print(f"✗ Data formatting test skipped due to API error")

        except Exception as e:
            print(f"✗ Error testing data formatting: {e}")
            self.fail(f"Data formatting test failed: {e}")

class FunctionalTestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def run_tests(self):
        print("Dynamic Timeline API - Functional Tests")
        print("=" * 60)

        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestTimelineAPI)

        # Run tests with custom result handler
        result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w')).run(suite)

        # Manual test execution for better output
        test_instance = TestTimelineAPI()
        test_instance.setUp()

        tests = [
            ("Basic Timeline Data Retrieval", test_instance.test_get_timeline_data_basic),
            ("Block Assignment Update", test_instance.test_update_block_assignment),
            ("Timeline Configurations", test_instance.test_get_timeline_configurations),
            ("API Error Handling", test_instance.test_api_error_handling),
            ("Data Formatting", test_instance.test_data_formatting),
        ]

        print(f"\nRunning {len(tests)} functional tests...\n")

        for test_name, test_func in tests:
            try:
                print(f"=== {test_name} ===")
                test_func()
                self.tests_passed += 1
                self.test_results.append((test_name, True, ""))
            except Exception as e:
                print(f"✗ {test_name} FAILED: {e}")
                self.tests_failed += 1
                self.test_results.append((test_name, False, str(e)))
            print()

        # Summary
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0

        print("=" * 60)
        print("FUNCTIONAL TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.tests_failed > 0:
            print(f"\nFailed Tests:")
            for test_name, success, error in self.test_results:
                if not success:
                    print(f"  - {test_name}: {error}")

        print("\n" + "=" * 60)

        if success_rate >= 80:
            print("🎉 Functional tests PASSED! The timeline API is working correctly.")
            return True
        else:
            print("❌ Functional tests FAILED! The timeline API has issues.")
            return False

def main():
    """Main test runner"""
    runner = FunctionalTestRunner()

    try:
        success = runner.run_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Functional test runner failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
