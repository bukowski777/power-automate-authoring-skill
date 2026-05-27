#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_RUN_AFTER_STATUSES = {"Succeeded", "Failed", "Skipped", "TimedOut"}

REF_PATTERNS = {
    "outputs": re.compile(r"outputs\('([^']+)'\)"),
    "body": re.compile(r"body\('([^']+)'\)"),
    "result": re.compile(r"result\('([^']+)'\)"),
    "variables": re.compile(r"variables\('([^']+)'\)"),
}

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
GUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
SECRET_PATTERN = re.compile(
    r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b|"
    r"\b(?:api[-_ ]?key|client[-_ ]?secret|password|secret)\b\s*[:=]\s*[^\s,}\"']{8,}",
    re.IGNORECASE,
)
ALLOWED_URL_PREFIXES = ("https://schema.management.azure.com/",)
LOGGING_VARIABLES = {"varLogBusinessKey", "varLogSourceItemId", "varLogSourceFileName"}


@dataclass
class WorkflowDiagnostics:
    errors: list[str]
    warnings: list[str]


def extract_definition(data: dict[str, Any]) -> dict[str, Any]:
    definition = data.get("properties", {}).get("definition")
    if isinstance(definition, dict):
        return definition
    definition = data.get("definition")
    if isinstance(definition, dict):
        return definition
    return data


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from walk_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk_strings(nested)


def iter_action_collections(actions: dict[str, Any]):
    yield actions
    for action in actions.values():
        if not isinstance(action, dict):
            continue
        nested_actions = action.get("actions")
        if isinstance(nested_actions, dict):
            yield from iter_action_collections(nested_actions)
        for branch_key in ("else", "default"):
            branch = action.get(branch_key)
            if isinstance(branch, dict) and isinstance(branch.get("actions"), dict):
                yield from iter_action_collections(branch["actions"])
        cases = action.get("cases")
        if isinstance(cases, dict):
            for case in cases.values():
                if isinstance(case, dict) and isinstance(case.get("actions"), dict):
                    yield from iter_action_collections(case["actions"])


def collect_action_names(actions: dict[str, Any]) -> set[str]:
    action_names: set[str] = set()
    for collection in iter_action_collections(actions):
        action_names.update(collection.keys())
    return action_names


def collect_initialized_variables(actions: dict[str, Any]) -> set[str]:
    variables: set[str] = set()
    for collection in iter_action_collections(actions):
        for action in collection.values():
            if not isinstance(action, dict) or action.get("type") != "InitializeVariable":
                continue
            inputs = action.get("inputs", {})
            if not isinstance(inputs, dict):
                continue
            input_variables = inputs.get("variables", [])
            if isinstance(input_variables, list):
                for variable in input_variables:
                    if isinstance(variable, dict) and isinstance(variable.get("name"), str):
                        variables.add(variable["name"])
            if isinstance(inputs.get("name"), str):
                variables.add(inputs["name"])
    return variables


def collect_initialized_variables_from_action(action: dict[str, Any]) -> set[str]:
    if action.get("type") == "InitializeVariable":
        return collect_initialized_variables({"__current__": action})
    nested_actions = action.get("actions")
    if isinstance(nested_actions, dict):
        return collect_initialized_variables(nested_actions)
    return set()


def validate_run_after(actions: dict[str, Any], errors: list[str]) -> None:
    for collection in iter_action_collections(actions):
        same_level_names = set(collection.keys())
        for action_name, action in collection.items():
            if not isinstance(action, dict):
                continue
            run_after = action.get("runAfter", {})
            if not isinstance(run_after, dict):
                errors.append(f"{action_name}: runAfter must be an object")
                continue
            for dependency, statuses in run_after.items():
                if dependency not in same_level_names:
                    errors.append(f"{action_name}: runAfter references missing action/scope: {dependency}")
                if not isinstance(statuses, list):
                    errors.append(f"{action_name}: runAfter statuses for {dependency} must be a list")
                    continue
                for status in statuses:
                    if status not in VALID_RUN_AFTER_STATUSES:
                        errors.append(f"{action_name}: invalid runAfter status: {status}")


def validate_expression_references(
    definition: dict[str, Any],
    action_names: set[str],
    variable_names: set[str],
    errors: list[str],
) -> None:
    all_text = "\n".join(walk_strings(definition))
    for ref_type, pattern in REF_PATTERNS.items():
        for ref in sorted(set(pattern.findall(all_text))):
            if ref_type == "variables":
                if ref not in variable_names:
                    errors.append(
                        f"Expression variables('{ref}') references missing initialized variable"
                    )
                continue
            if ref not in action_names:
                errors.append(f"Expression {ref_type}('{ref}') references missing action/scope")


def validate_hardcoded_values(definition: dict[str, Any], warnings: list[str]) -> None:
    seen_warnings: set[str] = set()
    for text in walk_strings(definition):
        for url in URL_PATTERN.findall(text):
            if not url.startswith(ALLOWED_URL_PREFIXES):
                seen_warnings.add(f"Hardcoded URL detected: {url}")
        for email in EMAIL_PATTERN.findall(text):
            seen_warnings.add(f"Hardcoded email address detected: {email}")
        for guid in GUID_PATTERN.findall(text):
            seen_warnings.add(f"Hardcoded GUID-like identifier detected: {guid}")
        if SECRET_PATTERN.search(text):
            seen_warnings.add("Secret-like value detected")
    warnings.extend(sorted(seen_warnings))


def collect_initialized_variables_before(actions: dict[str, Any], action_name: str) -> set[str]:
    variables: set[str] = set()
    for current_name, action in actions.items():
        if current_name == action_name:
            break
        if isinstance(action, dict):
            variables.update(collect_initialized_variables_from_action(action))
    return variables


def validate_catch_logging_variables(actions: dict[str, Any], warnings: list[str]) -> None:
    for catch_name, catch_action in actions.items():
        if not isinstance(catch_action, dict):
            continue
        run_after = catch_action.get("runAfter", {})
        if not isinstance(run_after, dict):
            continue
        try_dependencies = [name for name in run_after if name in actions and name.startswith("TRY_")]
        if not try_dependencies:
            continue

        catch_text = "\n".join(walk_strings(catch_action))
        used_logging_variables = LOGGING_VARIABLES.intersection(
            REF_PATTERNS["variables"].findall(catch_text)
        )
        if not used_logging_variables:
            continue

        for try_name in try_dependencies:
            before_try_variables = collect_initialized_variables_before(actions, try_name)
            try_action = actions.get(try_name)
            initialized_inside_try = (
                collect_initialized_variables_from_action(try_action)
                if isinstance(try_action, dict)
                else set()
            )
            for variable_name in sorted(used_logging_variables):
                if variable_name in before_try_variables:
                    continue
                if variable_name in initialized_inside_try:
                    warnings.append(
                        f"{catch_name}: logging variable {variable_name} is initialized inside {try_name}; initialize it before {try_name}"
                    )
                else:
                    warnings.append(
                        f"{catch_name}: logging variable {variable_name} is not initialized before {try_name}"
                    )


def collect_workflow_diagnostics(path: Path) -> WorkflowDiagnostics:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return WorkflowDiagnostics(errors=[f"Invalid JSON: {exc}"], warnings=[])

    if not isinstance(data, dict):
        return WorkflowDiagnostics(errors=["Workflow JSON root must be an object"], warnings=[])

    definition = extract_definition(data)
    actions = definition.get("actions", {})
    if not isinstance(actions, dict):
        return WorkflowDiagnostics(
            errors=["Workflow definition actions must be an object"],
            warnings=[],
        )

    errors: list[str] = []
    warnings: list[str] = []
    action_names = collect_action_names(actions)
    variable_names = collect_initialized_variables(actions)

    validate_run_after(actions, errors)
    validate_expression_references(definition, action_names, variable_names, errors)
    validate_hardcoded_values(definition, warnings)
    validate_catch_logging_variables(actions, warnings)

    return WorkflowDiagnostics(errors=errors, warnings=warnings)


def collect_workflow_errors(path: Path) -> list[str]:
    return collect_workflow_diagnostics(path).errors


def validate_workflow(path: Path, strict: bool = False) -> int:
    diagnostics = collect_workflow_diagnostics(path)
    for error in diagnostics.errors:
        print(f"ERROR: {path}: {error}", file=sys.stderr)
    for warning in diagnostics.warnings:
        print(f"WARN: {path}: {warning}", file=sys.stderr)
    if diagnostics.errors:
        return 1
    if strict and diagnostics.warnings:
        return 1
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate common Power Automate workflow JSON authoring hazards."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings, such as hardcoded URLs or emails, as failures.",
    )
    parser.add_argument("workflow", nargs="+", type=Path, help="Workflow JSON file to validate")
    args = parser.parse_args(argv)

    exit_code = 0
    for workflow_path in args.workflow:
        exit_code |= validate_workflow(workflow_path, strict=args.strict)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
