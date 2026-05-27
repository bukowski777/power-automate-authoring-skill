import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT_DIR = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT_DIR / "scripts" / "validate-workflow-json.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_workflow_json", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_workflow(tmp_path, actions):
    path = tmp_path / "workflow.json"
    path.write_text(
        json.dumps({"properties": {"definition": {"actions": actions}}}),
        encoding="utf-8",
    )
    return path


class WorkflowJsonValidatorTest(unittest.TestCase):
    def test_valid_workflow_passes(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "Initialize_business_key": {
                        "type": "InitializeVariable",
                        "inputs": {
                            "variables": [
                                {"name": "varLogBusinessKey", "type": "string", "value": "INV-001"}
                            ]
                        },
                    },
                    "TRY_Process": {"type": "Scope", "actions": {}},
                    "Compose_summary": {
                        "type": "Compose",
                        "inputs": "@concat(outputs('TRY_Process'), variables('varLogBusinessKey'))",
                        "runAfter": {"TRY_Process": ["Succeeded"]},
                    },
                },
            )

            self.assertEqual(validator.validate_workflow(path), 0)

    def test_reports_missing_runafter_target_and_invalid_status(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "Compose_summary": {
                        "type": "Compose",
                        "runAfter": {"Missing_action": ["Cancelled"]},
                    }
                },
            )

            result = validator.collect_workflow_errors(path)

            self.assertIn(
                "Compose_summary: runAfter references missing action/scope: Missing_action",
                result,
            )
            self.assertIn("Compose_summary: invalid runAfter status: Cancelled", result)

    def test_reports_missing_expression_action_reference(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "Compose_summary": {
                        "type": "Compose",
                        "inputs": "@body('Missing_action')",
                    }
                },
            )

            self.assertIn(
                "Expression body('Missing_action') references missing action/scope",
                validator.collect_workflow_errors(path),
            )

    def test_reports_missing_variable_reference(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "Compose_summary": {
                        "type": "Compose",
                        "inputs": "@variables('varMissing')",
                    }
                },
            )

            self.assertIn(
                "Expression variables('varMissing') references missing initialized variable",
                validator.collect_workflow_errors(path),
            )

    def test_reports_hardcoded_sensitive_values_as_warnings_by_default(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "Call_http": {
                        "type": "Http",
                        "inputs": {
                            "uri": "https://contoso.example/api/orders",
                            "headers": {"Authorization": "Bearer " + "abcdefghijklmnopqrstuvwxyz"},
                            "to": "ops@example.com",
                            "tenant": "00000000-0000-0000-0000-000000000000",
                        },
                    }
                },
            )

            diagnostics = validator.collect_workflow_diagnostics(path)

            self.assertEqual([], diagnostics.errors)
            self.assertIn(
                "Hardcoded URL detected: https://contoso.example/api/orders",
                diagnostics.warnings,
            )
            self.assertIn("Hardcoded email address detected: ops@example.com", diagnostics.warnings)
            self.assertIn(
                "Hardcoded GUID-like identifier detected: 00000000-0000-0000-0000-000000000000",
                diagnostics.warnings,
            )
            self.assertIn("Secret-like value detected", diagnostics.warnings)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(0, validator.validate_workflow(path))
                self.assertEqual(1, validator.validate_workflow(path, strict=True))
            self.assertIn("WARN:", stderr.getvalue())

    def test_warns_when_catch_logging_variable_is_initialized_inside_try(self):
        validator = load_validator()
        with TemporaryDirectory() as tmp:
            path = write_workflow(
                Path(tmp),
                {
                    "TRY_Process": {
                        "type": "Scope",
                        "actions": {
                            "Initialize_log_key": {
                                "type": "InitializeVariable",
                                "inputs": {
                                    "variables": [
                                        {
                                            "name": "varLogBusinessKey",
                                            "type": "string",
                                            "value": "INV-001",
                                        }
                                    ]
                                },
                            }
                        },
                    },
                    "CATCH_Process": {
                        "type": "Scope",
                        "runAfter": {"TRY_Process": ["Failed", "TimedOut"]},
                        "actions": {
                            "Compose_catch_log_payload": {
                                "type": "Compose",
                                "inputs": "@variables('varLogBusinessKey')",
                            }
                        },
                    },
                },
            )

            diagnostics = validator.collect_workflow_diagnostics(path)

            self.assertEqual([], diagnostics.errors)
            self.assertIn(
                "CATCH_Process: logging variable varLogBusinessKey is initialized inside TRY_Process; initialize it before TRY_Process",
                diagnostics.warnings,
            )


if __name__ == "__main__":
    unittest.main()
