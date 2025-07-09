#!/usr/bin/env python3

import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TimelineSystemValidator:
    """Comprehensive validator for the dynamic timeline system"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "api_tests": [],
            "frontend_tests": [],
            "integration_tests": [],
            "performance_tests": [],
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        self.start_time = datetime.now()

    def log_result(self, test_type, test_name, success, message="", details=None):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }

        self.results[test_type].append(result)

        status = "✓" if success else "✗"
        print(f"{status} {test_name}: {message}")

        if not success:
            self.results["errors"].append(f"{test_name}: {message}")

    def validate_api_structure(self):
        """Validate API file structure and imports"""
        print("\n=== API Structure Validation ===")

        # Check if API files exist
        api_files = [
            "planner/planner/api/__init__.py",
            "planner/planner/api/timeline_data.py",
            "planner/planner/api/roster.py"
        ]

        for file_path in api_files:
            if os.path.exists(file_path):
                self.log_result("api_tests", f"File exists: {file_path}", True)
            else:
                self.log_result("api_tests", f"File missing: {file_path}", False)

        # Check API __init__.py content
        init_file = "planner/planner/api/__init__.py"
        if os.path.exists(init_file):
            with open(init_file, 'r') as f:
                content = f.read()
                if "get_timeline_data" in content and "update_block_assignment" in content:
                    self.log_result("api_tests", "API functions properly exported", True)
                else:
                    self.log_result("api_tests", "API functions not properly exported", False)

    def validate_frontend_structure(self):
        """Validate frontend component structure"""
        print("\n=== Frontend Structure Validation ===")

        # Check if frontend components exist
        frontend_files = [
            "frontend/src/components/Timeline/DynamicTimeline.vue",
            "frontend/src/components/Timeline/DynamicTimelineGrid.vue",
            "frontend/src/components/Timeline/DynamicTimelineBlock.vue",
            "frontend/src/components/Timeline/DynamicBlockDetails.vue",
            "frontend/src/components/Timeline/ConfigurationSelector.vue",
            "frontend/src/components/shared/Toast.vue",
            "frontend/src/composables/useToast.js",
            "frontend/src/pages/DynamicTimelinePage.vue"
        ]

        for file_path in frontend_files:
            if os.path.exists(file_path):
                self.log_result("frontend_tests", f"Component exists: {file_path}", True)
            else:
                self.log_result("frontend_tests", f"Component missing: {file_path}", False)

    def validate_doctype_structure(self):
        """Validate DocType structure"""
        print("\n=== DocType Structure Validation ===")

        # Check if Timeline Configuration DocType exists
        doctype_files = [
            "planner/planner/doctype/timeline_configuration/timeline_configuration.json",
            "planner/planner/doctype/timeline_configuration/timeline_configuration.py",
            "planner/planner/doctype/timeline_configuration/setup_sample_configurations.py"
        ]

        for file_path in doctype_files:
            if os.path.exists(file_path):
                self.log_result("integration_tests", f"DocType file exists: {file_path}", True)
            else:
                self.log_result("integration_tests", f"DocType file missing: {file_path}", False)

    def validate_api_functions(self):
        """Validate API function signatures"""
        print("\n=== API Function Validation ===")

        try:
            # Import the API module
            from planner.planner.api.timeline_data import (
                get_timeline_data,
                update_block_assignment,
                get_timeline_configurations,
                create_sample_workstation_configuration
            )

            # Check function signatures
            import inspect

            # Validate get_timeline_data
            sig = inspect.signature(get_timeline_data)
            expected_params = ['configuration_name', 'start_date', 'end_date', 'filters']
            actual_params = list(sig.parameters.keys())

            if all(param in actual_params for param in expected_params):
                self.log_result("api_tests", "get_timeline_data signature correct", True)
            else:
                self.log_result("api_tests", "get_timeline_data signature incorrect", False)

            # Validate update_block_assignment
            sig = inspect.signature(update_block_assignment)
            expected_params = ['block_doctype', 'block_name', 'new_row_assignment', 'new_date', 'config_name']
            actual_params = list(sig.parameters.keys())

            if all(param in actual_params for param in expected_params):
                self.log_result("api_tests", "update_block_assignment signature correct", True)
            else:
                self.log_result("api_tests", "update_block_assignment signature incorrect", False)

        except ImportError as e:
            self.log_result("api_tests", "Failed to import API functions", False, str(e))
        except Exception as e:
            self.log_result("api_tests", "Error validating API functions", False, str(e))

    def validate_frontend_imports(self):
        """Validate frontend component imports"""
        print("\n=== Frontend Import Validation ===")

        # Check key frontend files for proper imports
        files_to_check = [
            ("frontend/src/components/Timeline/DynamicTimeline.vue", ["frappe-ui", "useToast"]),
            ("frontend/src/components/Timeline/ConfigurationSelector.vue", ["frappe-ui", "useToast"]),
            ("frontend/src/components/shared/Toast.vue", ["frappe-ui"]),
            ("frontend/src/composables/useToast.js", ["frappe-ui"]),
            ("frontend/src/App.vue", ["Toast.vue"])
        ]

        for file_path, expected_imports in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    missing_imports = []
                    for import_item in expected_imports:
                        if import_item not in content:
                            missing_imports.append(import_item)

                    if not missing_imports:
                        self.log_result("frontend_tests", f"Imports correct in {file_path}", True)
                    else:
                        self.log_result("frontend_tests", f"Missing imports in {file_path}: {missing_imports}", False)
            else:
                self.log_result("frontend_tests", f"File not found: {file_path}", False)

    def validate_test_system(self):
        """Validate test system"""
        print("\n=== Test System Validation ===")

        test_files = [
            "planner/planner/tests/test_timeline_api.py"
        ]

        for file_path in test_files:
            if os.path.exists(file_path):
                self.log_result("integration_tests", f"Test file exists: {file_path}", True)

                # Check if test file has proper structure
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "class TestTimelineAPI" in content and "unittest" in content:
                        self.log_result("integration_tests", f"Test structure correct in {file_path}", True)
                    else:
                        self.log_result("integration_tests", f"Test structure incorrect in {file_path}", False)
            else:
                self.log_result("integration_tests", f"Test file missing: {file_path}", False)

    def validate_configuration_system(self):
        """Validate configuration system"""
        print("\n=== Configuration System Validation ===")

        try:
            # Check if we can import configuration functions
            from planner.planner.doctype.timeline_configuration.timeline_configuration import (
                get_available_configurations,
                validate_configuration_fields,
                setup_sample_configurations
            )

            self.log_result("integration_tests", "Configuration functions importable", True)

            # Check setup_sample_configurations
            from planner.planner.doctype.timeline_configuration.setup_sample_configurations import (
                create_timeline_configurations,
                setup_job_card_system
            )

            self.log_result("integration_tests", "Sample configuration functions importable", True)

        except ImportError as e:
            self.log_result("integration_tests", "Failed to import configuration functions", False, str(e))
        except Exception as e:
            self.log_result("integration_tests", "Error validating configuration system", False, str(e))

    def validate_documentation(self):
        """Validate documentation"""
        print("\n=== Documentation Validation ===")

        doc_files = [
            "DYNAMIC_TIMELINE_ENHANCEMENTS.md",
            "README.md"
        ]

        for file_path in doc_files:
            if os.path.exists(file_path):
                self.log_result("integration_tests", f"Documentation exists: {file_path}", True)
            else:
                self.log_result("integration_tests", f"Documentation missing: {file_path}", False)

    def performance_check(self):
        """Basic performance validation"""
        print("\n=== Performance Validation ===")

        # Check file sizes (large files might indicate issues)
        large_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.vue', '.js', '.py')):
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    if size > 100000:  # 100KB
                        large_files.append((filepath, size))

        if large_files:
            self.log_result("performance_tests", "Large files detected", False,
                          f"Files over 100KB: {large_files}")
        else:
            self.log_result("performance_tests", "No unusually large files", True)

        # Check for potential memory leaks (basic check)
        vue_files = []
        for root, dirs, files in os.walk('frontend/src'):
            for file in files:
                if file.endswith('.vue'):
                    vue_files.append(os.path.join(root, file))

        memory_issues = []
        for vue_file in vue_files:
            with open(vue_file, 'r') as f:
                content = f.read()
                # Check for common memory leak patterns
                if 'setInterval' in content and 'clearInterval' not in content:
                    memory_issues.append(f"{vue_file}: setInterval without clearInterval")
                if 'setTimeout' in content and content.count('setTimeout') > 5:
                    memory_issues.append(f"{vue_file}: Many setTimeout calls")

        if memory_issues:
            self.log_result("performance_tests", "Potential memory issues", False,
                          f"Issues: {memory_issues}")
        else:
            self.log_result("performance_tests", "No obvious memory issues", True)

    def validate_security(self):
        """Basic security validation"""
        print("\n=== Security Validation ===")

        # Check for potential security issues
        security_issues = []

        # Check Python files for unsafe patterns
        python_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        for py_file in python_files:
            with open(py_file, 'r') as f:
                content = f.read()
                # Check for potentially unsafe patterns
                if 'eval(' in content:
                    security_issues.append(f"{py_file}: Uses eval()")
                if 'exec(' in content:
                    security_issues.append(f"{py_file}: Uses exec()")
                if 'ignore_permissions=True' in content:
                    # This is sometimes necessary but should be noted
                    pass

        # Check JavaScript files for XSS vulnerabilities
        js_files = []
        for root, dirs, files in os.walk('frontend/src'):
            for file in files:
                if file.endswith(('.js', '.vue')):
                    js_files.append(os.path.join(root, file))

        for js_file in js_files:
            with open(js_file, 'r') as f:
                content = f.read()
                if 'innerHTML' in content and 'v-html' not in content:
                    security_issues.append(f"{js_file}: Direct innerHTML usage")

        if security_issues:
            self.log_result("integration_tests", "Security issues found", False,
                          f"Issues: {security_issues}")
        else:
            self.log_result("integration_tests", "No obvious security issues", True)

    def generate_summary(self):
        """Generate validation summary"""
        print("\n=== Validation Summary ===")

        total_tests = sum(len(tests) for tests in [
            self.results["api_tests"],
            self.results["frontend_tests"],
            self.results["integration_tests"],
            self.results["performance_tests"]
        ])

        passed_tests = sum(
            len([t for t in tests if t["success"]])
            for tests in [
                self.results["api_tests"],
                self.results["frontend_tests"],
                self.results["integration_tests"],
                self.results["performance_tests"]
            ]
        )

        failed_tests = total_tests - passed_tests

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "duration": str(datetime.now() - self.start_time),
            "timestamp": datetime.now().isoformat()
        }

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        print(f"Duration: {self.results['summary']['duration']}")

        if self.results["errors"]:
            print(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  - {error}")

        if self.results["warnings"]:
            print(f"\nWarnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")

    def save_report(self, filename="timeline_validation_report.json"):
        """Save validation report to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {filename}")

    def run_all_validations(self):
        """Run all validation checks"""
        print("Dynamic Timeline System Validation")
        print("=" * 50)

        # Structure validations
        self.validate_api_structure()
        self.validate_frontend_structure()
        self.validate_doctype_structure()

        # Functional validations
        self.validate_api_functions()
        self.validate_frontend_imports()
        self.validate_test_system()
        self.validate_configuration_system()

        # Quality validations
        self.validate_documentation()
        self.performance_check()
        self.validate_security()

        # Generate summary
        self.generate_summary()

        # Save report
        self.save_report()

        # Return success status
        return self.results["summary"]["success_rate"] >= 80.0


def main():
    """Main validation function"""
    validator = TimelineSystemValidator()

    try:
        success = validator.run_all_validations()

        if success:
            print("\n🎉 Dynamic Timeline System validation PASSED!")
            print("The system is ready for use.")
            return 0
        else:
            print("\n❌ Dynamic Timeline System validation FAILED!")
            print("Please review the errors above and fix them before proceeding.")
            return 1

    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
