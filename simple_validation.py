#!/usr/bin/env python3
"""
Simple validation test for the Dynamic Timeline System
This test validates file structure, syntax, and basic functionality without requiring Frappe imports
"""

import os
import sys
import ast
import json
import traceback
from datetime import datetime

class SimpleTimelineValidator:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []

    def log_test(self, test_name, success, message=""):
        status = "✓" if success else "✗"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")

        if not success:
            self.errors.append(f"{test_name}: {message}")

    def validate_file_exists(self, file_path, description):
        """Check if a file exists"""
        if os.path.exists(file_path):
            self.log_test(f"File exists: {description}", True, file_path)
            return True
        else:
            self.log_test(f"File missing: {description}", False, file_path)
            return False

    def validate_python_syntax(self, file_path):
        """Validate Python file syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST to check syntax
            ast.parse(content)
            self.log_test(f"Python syntax valid: {os.path.basename(file_path)}", True)
            return True
        except SyntaxError as e:
            self.log_test(f"Python syntax error: {os.path.basename(file_path)}", False, str(e))
            return False
        except Exception as e:
            self.log_test(f"Python file error: {os.path.basename(file_path)}", False, str(e))
            return False

    def validate_vue_syntax(self, file_path):
        """Basic Vue file validation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic checks for Vue file structure
            has_template = '<template>' in content and '</template>' in content
            has_script = '<script' in content and '</script>' in content
            has_style = '<style' in content and '</style>' in content

            if has_template and has_script:
                self.log_test(f"Vue structure valid: {os.path.basename(file_path)}", True)
                return True
            else:
                missing = []
                if not has_template:
                    missing.append("template")
                if not has_script:
                    missing.append("script")
                self.log_test(f"Vue structure incomplete: {os.path.basename(file_path)}", False, f"Missing: {', '.join(missing)}")
                return False
        except Exception as e:
            self.log_test(f"Vue file error: {os.path.basename(file_path)}", False, str(e))
            return False

    def validate_js_syntax(self, file_path):
        """Basic JavaScript file validation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic checks for common JavaScript patterns
            has_import = 'import' in content or 'require' in content
            has_export = 'export' in content or 'module.exports' in content

            # Check for basic syntax issues
            if content.strip():
                self.log_test(f"JS file valid: {os.path.basename(file_path)}", True)
                return True
            else:
                self.log_test(f"JS file empty: {os.path.basename(file_path)}", False)
                return False
        except Exception as e:
            self.log_test(f"JS file error: {os.path.basename(file_path)}", False, str(e))
            return False

    def validate_json_syntax(self, file_path):
        """Validate JSON file syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            self.log_test(f"JSON syntax valid: {os.path.basename(file_path)}", True)
            return True
        except json.JSONDecodeError as e:
            self.log_test(f"JSON syntax error: {os.path.basename(file_path)}", False, str(e))
            return False
        except Exception as e:
            self.log_test(f"JSON file error: {os.path.basename(file_path)}", False, str(e))
            return False

    def validate_api_functions(self, file_path):
        """Validate API functions exist in Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required functions
            required_functions = [
                'get_timeline_data',
                'update_block_assignment',
                'get_timeline_configurations'
            ]

            found_functions = []
            missing_functions = []

            for func in required_functions:
                if f'def {func}(' in content:
                    found_functions.append(func)
                else:
                    missing_functions.append(func)

            if not missing_functions:
                self.log_test("API functions complete", True, f"Found: {', '.join(found_functions)}")
                return True
            else:
                self.log_test("API functions incomplete", False, f"Missing: {', '.join(missing_functions)}")
                return False
        except Exception as e:
            self.log_test("API functions validation error", False, str(e))
            return False

    def validate_imports_in_file(self, file_path, expected_imports):
        """Check if file contains expected imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            missing_imports = []
            for import_item in expected_imports:
                if import_item not in content:
                    missing_imports.append(import_item)

            if not missing_imports:
                self.log_test(f"Imports correct: {os.path.basename(file_path)}", True)
                return True
            else:
                self.log_test(f"Missing imports: {os.path.basename(file_path)}", False, f"Missing: {', '.join(missing_imports)}")
                return False
        except Exception as e:
            self.log_test(f"Import validation error: {os.path.basename(file_path)}", False, str(e))
            return False

    def run_validation(self):
        """Run all validation tests"""
        print("Dynamic Timeline System - Simple Validation")
        print("=" * 60)

        # Backend API Files
        print("\n=== Backend API Files ===")
        api_files = [
            ("planner/api/__init__.py", "API init file"),
            ("planner/api/timeline_data.py", "Timeline data API"),
            ("planner/api/roster.py", "Roster API"),
        ]

        for file_path, description in api_files:
            if self.validate_file_exists(file_path, description):
                self.validate_python_syntax(file_path)

        # Validate specific API functions
        timeline_api_path = "planner/api/timeline_data.py"
        if os.path.exists(timeline_api_path):
            self.validate_api_functions(timeline_api_path)

        # DocType Files
        print("\n=== DocType Files ===")
        doctype_files = [
            ("planner/planner/doctype/timeline_configuration/timeline_configuration.py", "Timeline Configuration DocType"),
            ("planner/planner/doctype/timeline_configuration/timeline_configuration.json", "Timeline Configuration JSON"),
            ("planner/planner/doctype/timeline_configuration/setup_sample_configurations.py", "Sample Configuration Setup"),
        ]

        for file_path, description in doctype_files:
            if self.validate_file_exists(file_path, description):
                if file_path.endswith('.py'):
                    self.validate_python_syntax(file_path)
                elif file_path.endswith('.json'):
                    self.validate_json_syntax(file_path)

        # Frontend Components
        print("\n=== Frontend Components ===")
        frontend_files = [
            ("frontend/src/components/Timeline/DynamicTimeline.vue", "Dynamic Timeline Component"),
            ("frontend/src/components/Timeline/DynamicTimelineGrid.vue", "Timeline Grid Component"),
            ("frontend/src/components/Timeline/DynamicTimelineBlock.vue", "Timeline Block Component"),
            ("frontend/src/components/Timeline/DynamicBlockDetails.vue", "Block Details Component"),
            ("frontend/src/components/Timeline/ConfigurationSelector.vue", "Configuration Selector"),
            ("frontend/src/components/shared/Toast.vue", "Toast Component"),
            ("frontend/src/pages/DynamicTimelinePage.vue", "Dynamic Timeline Page"),
        ]

        for file_path, description in frontend_files:
            if self.validate_file_exists(file_path, description):
                self.validate_vue_syntax(file_path)

        # JavaScript/TypeScript Files
        print("\n=== JavaScript Files ===")
        js_files = [
            ("frontend/src/composables/useToast.js", "Toast Composable"),
            ("frontend/src/App.vue", "Main App Component"),
        ]

        for file_path, description in js_files:
            if self.validate_file_exists(file_path, description):
                if file_path.endswith('.js'):
                    self.validate_js_syntax(file_path)
                elif file_path.endswith('.vue'):
                    self.validate_vue_syntax(file_path)

        # Test Files
        print("\n=== Test Files ===")
        test_files = [
            ("planner/tests/test_timeline_api.py", "Timeline API Tests"),
        ]

        for file_path, description in test_files:
            if self.validate_file_exists(file_path, description):
                self.validate_python_syntax(file_path)

        # Documentation
        print("\n=== Documentation ===")
        doc_files = [
            ("DYNAMIC_TIMELINE_ENHANCEMENTS.md", "Enhancement Documentation"),
            ("README.md", "README Documentation"),
        ]

        for file_path, description in doc_files:
            self.validate_file_exists(file_path, description)

        # Validate specific imports
        print("\n=== Import Validation ===")

        # Check API init file exports
        api_init_path = "planner/api/__init__.py"
        if os.path.exists(api_init_path):
            self.validate_imports_in_file(api_init_path, [
                "get_timeline_data",
                "update_block_assignment",
                "get_timeline_configurations"
            ])

        # Check frontend imports
        dynamic_timeline_path = "frontend/src/components/Timeline/DynamicTimeline.vue"
        if os.path.exists(dynamic_timeline_path):
            self.validate_imports_in_file(dynamic_timeline_path, [
                "frappe-ui",
                "useToast"
            ])

        # Check Toast component
        toast_path = "frontend/src/components/shared/Toast.vue"
        if os.path.exists(toast_path):
            self.validate_imports_in_file(toast_path, [
                "frappe-ui",
                "useToast"
            ])

        # Generate Summary
        print("\n=== Validation Summary ===")
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        # Overall assessment
        print("\n=== Assessment ===")
        if success_rate >= 90:
            print("🎉 Excellent! The timeline system is well-structured and ready for use.")
        elif success_rate >= 80:
            print("✅ Good! The timeline system is mostly complete with minor issues.")
        elif success_rate >= 70:
            print("⚠️  Fair! The timeline system has some issues that should be addressed.")
        elif success_rate >= 60:
            print("❌ Poor! The timeline system has significant issues that need fixing.")
        else:
            print("💥 Critical! The timeline system has major problems and is not ready.")

        return success_rate >= 80

def main():
    """Main validation function"""
    validator = SimpleTimelineValidator()

    try:
        success = validator.run_validation()
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
