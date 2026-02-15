#!/usr/bin/env python3
"""Generate and validate the Foundry-compatible OpenAPI artifact."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_FOUNDRY_SERVER_URL = "http://localhost:5000"
FOUNDRY_OPENAPI_VERSION = "3.0.3"
EXPECTED_OPERATIONS = {
    "/classify/ae-pc": "classifyAePc",
    "/classify/ae-category": "classifyAeCategory",
    "/classify/pc-category": "classifyPcCategory",
}
UNSUPPORTED_COMBINERS = {"anyOf", "oneOf", "allOf"}


def _to_json_content(content: dict[str, Any]) -> dict[str, Any]:
    if "application/json" in content:
        return {"application/json": deepcopy(content["application/json"])}
    if content:
        _, first_content = next(iter(content.items()))
        return {"application/json": deepcopy(first_content)}
    return {}


def _choose_response_code(responses: dict[str, Any]) -> str:
    if "200" in responses:
        return "200"
    two_xx = sorted(code for code in responses if code.startswith("2"))
    if two_xx:
        return two_xx[0]
    return sorted(responses)[0]


def _collect_schema_refs(node: Any, refs: set[str]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            refs.add(ref.rsplit("/", maxsplit=1)[-1])
        for value in node.values():
            _collect_schema_refs(value, refs)
        return

    if isinstance(node, list):
        for value in node:
            _collect_schema_refs(value, refs)


def _collect_combiners(node: Any, path: str = "$", issues: list[str] | None = None) -> list[str]:
    if issues is None:
        issues = []

    if isinstance(node, dict):
        for key, value in node.items():
            current_path = f"{path}.{key}"
            if key in UNSUPPORTED_COMBINERS:
                issues.append(current_path)
            _collect_combiners(value, path=current_path, issues=issues)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _collect_combiners(value, path=f"{path}[{index}]", issues=issues)

    return issues


def _normalize_operation(
    operation: dict[str, Any],
    operation_id: str,
    schemas: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "operationId": operation_id,
        "responses": {},
    }

    for key in ("summary", "description", "tags"):
        if key in operation:
            normalized[key] = deepcopy(operation[key])

    request_body = operation.get("requestBody")
    if isinstance(request_body, dict):
        request_copy = deepcopy(request_body)
        json_content = _to_json_content(request_copy.get("content", {}))
        if not json_content:
            raise ValueError(f"Operation {operation_id} has no request content")
        request_copy["content"] = json_content

        # Help Foundry generate better example payloads.
        # Foundry's function UI appears to prefer a media-type `example` over a
        # schema-level `example` behind a $ref.
        if schemas is not None:
            media = request_copy.get("content", {}).get("application/json")
            if isinstance(media, dict) and "example" not in media:
                schema = media.get("schema")
                if isinstance(schema, dict):
                    ref = schema.get("$ref")
                    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                        schema_name = ref.rsplit("/", maxsplit=1)[-1]
                        schema_obj = schemas.get(schema_name)
                        if isinstance(schema_obj, dict) and "example" in schema_obj:
                            media["example"] = deepcopy(schema_obj["example"])

        normalized["requestBody"] = request_copy

    responses = operation.get("responses")
    if not isinstance(responses, dict) or not responses:
        raise ValueError(f"Operation {operation_id} has no responses")

    response_code = _choose_response_code(responses)
    response_copy = deepcopy(responses[response_code])
    response_content = _to_json_content(response_copy.get("content", {}))
    if not response_content:
        response_content = {"application/json": {"schema": {"type": "object"}}}
    response_copy["content"] = response_content
    normalized["responses"] = {response_code: response_copy}

    return normalized


def build_foundry_openapi_spec(server_url: str = DEFAULT_FOUNDRY_SERVER_URL) -> dict[str, Any]:
    from src.api.app import app

    raw_spec = app.openapi()
    raw_paths = raw_spec.get("paths", {})
    raw_schemas = raw_spec.get("components", {}).get("schemas", {})

    filtered_paths: dict[str, Any] = {}
    for path, operation_id in EXPECTED_OPERATIONS.items():
        path_item = raw_paths.get(path)
        if not isinstance(path_item, dict) or "post" not in path_item:
            raise ValueError(f"Missing POST operation for required path: {path}")
        filtered_paths[path] = {
            "post": _normalize_operation(path_item["post"], operation_id, schemas=raw_schemas),
        }

    referenced_schemas: set[str] = set()
    _collect_schema_refs(filtered_paths, referenced_schemas)

    kept_schemas: dict[str, Any] = {}
    queue = sorted(referenced_schemas)
    while queue:
        schema_name = queue.pop(0)
        if schema_name in kept_schemas:
            continue
        schema = raw_schemas.get(schema_name)
        if not isinstance(schema, dict):
            raise ValueError(f"Missing schema referenced in operation: {schema_name}")
        schema_copy = deepcopy(schema)
        kept_schemas[schema_name] = schema_copy

        nested_refs: set[str] = set()
        _collect_schema_refs(schema_copy, nested_refs)
        for nested in sorted(nested_refs):
            if nested not in kept_schemas and nested not in queue:
                queue.append(nested)

    spec: dict[str, Any] = {
        "openapi": FOUNDRY_OPENAPI_VERSION,
        "info": {
            "title": raw_spec.get("info", {}).get("title", "DSPy Complaint Classifier API"),
            "version": raw_spec.get("info", {}).get("version", "0.0.0"),
            "description": raw_spec.get("info", {}).get(
                "description",
                "Foundry compute module contract for DSPy classifier routes.",
            ),
        },
        "servers": [{"url": server_url}],
        "paths": filtered_paths,
    }
    if kept_schemas:
        spec["components"] = {"schemas": kept_schemas}

    errors = validate_spec(spec, server_url=server_url)
    if errors:
        raise ValueError("Generated spec failed validation:\n- " + "\n- ".join(errors))
    return spec


def validate_spec(spec: dict[str, Any], server_url: str = DEFAULT_FOUNDRY_SERVER_URL) -> list[str]:
    errors: list[str] = []

    openapi_version = spec.get("openapi")
    if not isinstance(openapi_version, str) or not openapi_version.startswith("3.0"):
        errors.append(f"openapi must be 3.0.x, found: {openapi_version!r}")

    servers = spec.get("servers")
    if servers != [{"url": server_url}]:
        errors.append(f"servers must be exactly [{{'url': '{server_url}'}}]")

    paths = spec.get("paths")
    if not isinstance(paths, dict):
        errors.append("paths must be an object")
        return errors

    expected_paths = set(EXPECTED_OPERATIONS)
    actual_paths = set(paths)
    if actual_paths != expected_paths:
        errors.append(
            "paths must match required classify routes exactly: "
            f"expected {sorted(expected_paths)}, got {sorted(actual_paths)}"
        )

    for path, expected_operation_id in EXPECTED_OPERATIONS.items():
        path_item = paths.get(path)
        if not isinstance(path_item, dict):
            errors.append(f"path {path} must contain a path item object")
            continue

        methods = set(path_item)
        if methods != {"post"}:
            errors.append(f"path {path} must contain only POST; found {sorted(methods)}")
            continue

        operation = path_item["post"]
        if not isinstance(operation, dict):
            errors.append(f"path {path} POST operation must be an object")
            continue

        operation_id = operation.get("operationId")
        if operation_id != expected_operation_id:
            errors.append(f"path {path} operationId must be {expected_operation_id}, found {operation_id!r}")

        responses = operation.get("responses")
        if not isinstance(responses, dict) or len(responses) != 1:
            errors.append(f"path {path} must define exactly one response code")
            continue

        response_code, response_obj = next(iter(responses.items()))
        if not isinstance(response_obj, dict):
            errors.append(f"path {path} response {response_code} must be an object")
            continue

        content = response_obj.get("content")
        if not isinstance(content, dict) or set(content) != {"application/json"}:
            errors.append(f"path {path} response {response_code} must have only application/json content")

    combiner_paths = _collect_combiners(spec)
    if combiner_paths:
        errors.append("spec cannot contain anyOf/oneOf/allOf: " + ", ".join(combiner_paths))

    return errors


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Failed to read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"File {path} is not valid JSON: {exc}") from exc


def validate_image(
    image_ref: str,
    expected_spec: dict[str, Any],
    server_url: str = DEFAULT_FOUNDRY_SERVER_URL,
) -> list[str]:
    errors: list[str] = []

    if ":latest" in image_ref:
        errors.append("image tag must not be latest")

    result = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"docker image inspect failed for {image_ref}: {result.stderr.strip()}"]

    try:
        image_data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [f"docker image inspect output is not valid JSON: {exc}"]

    if not image_data:
        return [f"docker image inspect returned empty data for {image_ref}"]

    image = image_data[0]
    if image.get("Os") != "linux":
        errors.append(f"image os must be linux, found {image.get('Os')!r}")
    if image.get("Architecture") != "amd64":
        errors.append(f"image architecture must be amd64, found {image.get('Architecture')!r}")

    config = image.get("Config") or {}
    user = str(config.get("User") or "").strip()
    if not user:
        errors.append("image must set a non-root USER")
    else:
        uid_token = user.split(":", maxsplit=1)[0]
        if not uid_token.isdigit() or int(uid_token) <= 0:
            errors.append(f"image USER must include a positive numeric uid, found {user!r}")

    labels = config.get("Labels") or {}
    openapi_label = labels.get("server.openapi")
    if not openapi_label:
        errors.append("image label server.openapi is missing")
        return errors

    try:
        labeled_spec = json.loads(openapi_label)
    except json.JSONDecodeError as exc:
        errors.append(f"image label server.openapi is not valid JSON: {exc}")
        return errors

    spec_errors = validate_spec(labeled_spec, server_url=server_url)
    if spec_errors:
        errors.extend(f"server.openapi: {error}" for error in spec_errors)
    if labeled_spec != expected_spec:
        errors.append("server.openapi label JSON does not exactly match openapi.foundry.json")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-path",
        type=Path,
        default=Path("openapi.foundry.json"),
        help="Path to Foundry OpenAPI artifact.",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Regenerate spec from FastAPI before validating.",
    )
    parser.add_argument(
        "--image-ref",
        help="Optional image reference to validate metadata and labels.",
    )
    parser.add_argument(
        "--server-url",
        default=DEFAULT_FOUNDRY_SERVER_URL,
        help="Expected servers[0].url value in the Foundry OpenAPI contract.",
    )
    args = parser.parse_args()

    try:
        if args.generate:
            spec = build_foundry_openapi_spec(server_url=args.server_url)
            args.spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            print(f"Wrote Foundry OpenAPI spec: {args.spec_path}")
        else:
            spec = _load_json(args.spec_path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate_spec(spec, server_url=args.server_url)
    if args.image_ref:
        errors.extend(validate_image(args.image_ref, spec, server_url=args.server_url))

    if errors:
        print("Foundry validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Foundry validation passed.")
    if args.image_ref:
        print(f"Image metadata validated: {args.image_ref}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
