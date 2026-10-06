#!/usr/bin/env python3
"""Validate, document, publish, and verify organization profile READMEs."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config" / "profile-targets.json"
DEFAULT_SUPPORT_TIERS = ROOT / "config" / "support-tiers.json"
DEFAULT_GENERATED_DOC = ROOT / "DOCS" / "generated" / "profile-targets.md"
SOURCE_BLOB_URL = (
    "https://github.com/Interested-Deving-1896/Interested-Deving-1896/blob/main"
)
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SUPPORT_TIERS_START = "<!-- SUPPORT-TIERS:START -->"
SUPPORT_TIERS_END = "<!-- SUPPORT-TIERS:END -->"
OPERATIONAL_TIER_FORBIDDEN_TERMS = (
    "assassination",
    "black market",
    "covert",
    "criminal",
    "dead drop",
    "fictional",
    "intelligence payroll",
    "money laundering",
    "protection racket",
    "shadow economy",
)


class ProfileError(RuntimeError):
    """Raised for invalid configuration, content, or publication state."""


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"cannot read manifest {path}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ProfileError("profile manifest schema_version must be 1")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ProfileError("profile manifest requires a non-empty profiles mapping")

    for key, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ProfileError(f"profiles.{key} must be an object")
        for field in (
            "title",
            "source",
            "policy_source",
            "policy_destination",
            "lore_source",
            "lore_destination",
            "repository_payload",
            "required_identity",
            "destinations",
        ):
            if not profile.get(field):
                raise ProfileError(f"profiles.{key}.{field} is required")
        policy_destination = profile["policy_destination"]
        if not isinstance(policy_destination, dict):
            raise ProfileError(f"profiles.{key}.policy_destination must be an object")
        for field in ("repository", "path", "branch"):
            if not policy_destination.get(field):
                raise ProfileError(
                    f"profiles.{key}.policy_destination.{field} is required"
                )
        lore_destination = profile["lore_destination"]
        if not isinstance(lore_destination, dict):
            raise ProfileError(f"profiles.{key}.lore_destination must be an object")
        for field in ("repository", "path", "branch"):
            if not lore_destination.get(field):
                raise ProfileError(
                    f"profiles.{key}.lore_destination.{field} is required"
                )
        payload = profile["repository_payload"]
        if not isinstance(payload, dict):
            raise ProfileError(f"profiles.{key}.repository_payload must be an object")
        for field in ("repository", "branch"):
            if not payload.get(field):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.{field} is required"
                )
        if payload["repository"] != policy_destination["repository"]:
            raise ProfileError(
                f"profiles.{key}.repository_payload must target the named README repo"
            )
        roots = payload.get("roots")
        files = payload.get("files")
        if not isinstance(roots, list) or not roots:
            raise ProfileError(
                f"profiles.{key}.repository_payload.roots must be non-empty"
            )
        if not isinstance(files, list) or not files:
            raise ProfileError(
                f"profiles.{key}.repository_payload.files must be non-empty"
            )
        profile_prefix = f"profiles/{key}/"
        for position, root in enumerate(roots):
            if not isinstance(root, dict):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.roots[{position}] must be an object"
                )
            source = root.get("source")
            destination = root.get("path")
            if not isinstance(source, str) or not source.startswith(profile_prefix):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.roots[{position}].source "
                    f"must be below {profile_prefix}"
                )
            if not isinstance(destination, str):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.roots[{position}].path "
                    "must be a string"
                )
            validate_destination_path(destination, allow_empty=True)
        for position, item in enumerate(files):
            if not isinstance(item, dict):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.files[{position}] must be an object"
                )
            source = item.get("source")
            destination = item.get("path")
            if not isinstance(source, str) or not source.startswith(profile_prefix):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.files[{position}].source "
                    f"must be below {profile_prefix}"
                )
            if not isinstance(destination, str):
                raise ProfileError(
                    f"profiles.{key}.repository_payload.files[{position}].path "
                    "must be a string"
                )
            validate_destination_path(destination)
        if not isinstance(profile["destinations"], list):
            raise ProfileError(f"profiles.{key}.destinations must be a list")
        for destination in profile["destinations"]:
            if not isinstance(destination, dict):
                raise ProfileError(f"profiles.{key}.destinations contains a non-object")
            for field in ("repository", "path", "branch"):
                if not destination.get(field):
                    raise ProfileError(
                        f"profiles.{key}.destinations.{field} is required"
                    )

    shared = data.get("shared_automation")
    if not isinstance(shared, dict):
        raise ProfileError("profile manifest requires shared_automation")
    sources = shared.get("sources")
    destinations = shared.get("destinations")
    if not isinstance(sources, list) or not sources:
        raise ProfileError("shared_automation.sources must be a non-empty list")
    if not isinstance(destinations, list) or not destinations:
        raise ProfileError("shared_automation.destinations must be a non-empty list")
    for source in sources:
        if not isinstance(source, str) or not source.startswith(
            (".github/", "scripts/")
        ):
            raise ProfileError(
                "shared automation sources must be paths below .github/ or scripts/"
            )
    for destination in destinations:
        if not isinstance(destination, dict):
            raise ProfileError("shared_automation.destinations contains a non-object")
        for field in ("profile", "repository", "branch"):
            if not destination.get(field):
                raise ProfileError(
                    f"shared_automation.destinations.{field} is required"
                )
        if destination["profile"] not in profiles:
            raise ProfileError(
                "shared_automation destination references unknown profile: "
                f"{destination['profile']}"
            )
    return data


def read_support_tiers(path: Path) -> dict[str, Any]:
    """Read and validate factual support-tier configuration."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"cannot read support tiers {path}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ProfileError("support tiers schema_version must be 1")
    source = data.get("source_of_truth")
    if not isinstance(source, dict):
        raise ProfileError("support tiers require source_of_truth")
    for field in ("name", "collective_url", "contribution_options_url", "authority"):
        if not isinstance(source.get(field), str) or not source[field].strip():
            raise ProfileError(f"support tiers source_of_truth.{field} is required")

    boundaries = data.get("content_boundaries")
    if not isinstance(boundaries, dict):
        raise ProfileError("support tiers require content_boundaries")
    if boundaries.get("classification") != "factual-operational":
        raise ProfileError("support tiers must be classified factual-operational")
    if boundaries.get("fictional_lore_generated") is not False:
        raise ProfileError("support tiers must not generate fictional lore")
    if not isinstance(boundaries.get("rule"), str) or not boundaries["rule"].strip():
        raise ProfileError("support tiers content_boundaries.rule is required")

    fields = data.get("required_tier_metadata")
    if not isinstance(fields, list) or not fields:
        raise ProfileError("support tiers require required_tier_metadata")
    field_keys: set[str] = set()
    for position, field in enumerate(fields):
        if not isinstance(field, dict):
            raise ProfileError(
                f"support tiers required_tier_metadata[{position}] must be an object"
            )
        for name in ("key", "label", "description"):
            if not isinstance(field.get(name), str) or not field[name].strip():
                raise ProfileError(
                    f"support tiers required_tier_metadata[{position}].{name} is required"
                )
        if field["key"] in field_keys:
            raise ProfileError(f"duplicate support-tier metadata key: {field['key']}")
        field_keys.add(field["key"])

    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ProfileError("support tiers require profiles")
    readmes: set[str] = set()
    for key, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ProfileError(f"support tiers profiles.{key} must be an object")
        for name in ("identity", "readme", "scope_statement"):
            if not isinstance(profile.get(name), str) or not profile[name].strip():
                raise ProfileError(f"support tiers profiles.{key}.{name} is required")
        if not isinstance(profile.get("include_metadata_template"), bool):
            raise ProfileError(
                f"support tiers profiles.{key}.include_metadata_template must be boolean"
            )
        readme = profile["readme"]
        if readme in readmes:
            raise ProfileError(f"duplicate support-tier README target: {readme}")
        readmes.add(readme)
        families = profile.get("families")
        if not isinstance(families, list) or not families:
            raise ProfileError(f"support tiers profiles.{key}.families must be non-empty")
        family_keys: set[str] = set()
        for position, family in enumerate(families):
            if not isinstance(family, dict):
                raise ProfileError(
                    f"support tiers profiles.{key}.families[{position}] must be an object"
                )
            for name in ("key", "label", "purpose"):
                if not isinstance(family.get(name), str) or not family[name].strip():
                    raise ProfileError(
                        f"support tiers profiles.{key}.families[{position}].{name} "
                        "is required"
                    )
            if family["key"] in family_keys:
                raise ProfileError(
                    f"duplicate support-tier family key in profiles.{key}: "
                    f"{family['key']}"
                )
            family_keys.add(family["key"])

    operational_values = [
        source["name"],
        source["authority"],
        *(field["label"] for field in fields),
        *(field["description"] for field in fields),
    ]
    for profile in profiles.values():
        operational_values.append(profile["scope_statement"])
        for family in profile["families"]:
            operational_values.extend((family["label"], family["purpose"]))
    operational_text = "\n".join(operational_values).casefold()
    for term in OPERATIONAL_TIER_FORBIDDEN_TERMS:
        if term in operational_text:
            raise ProfileError(
                "support-tier operational data contains fictional or unsafe term: "
                f"{term!r}"
            )
    return data


def repository_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ProfileError(f"path escapes repository root: {relative}") from exc
    return candidate


def validate_destination_path(path: str, allow_empty: bool = False) -> None:
    """Reject absolute or parent-traversing paths in remote payload mappings."""
    if not path and allow_empty:
        return
    candidate = PurePosixPath(path)
    if not path or candidate.is_absolute() or ".." in candidate.parts:
        raise ProfileError(f"invalid repository payload destination path: {path!r}")


def profile_payload_files(
    key: str, profile: dict[str, Any]
) -> list[tuple[Path, str]]:
    """Expand one profile's explicit files and directory roots deterministically."""
    payload = profile["repository_payload"]
    expanded: list[tuple[Path, str]] = []
    for root in payload["roots"]:
        source_root = repository_path(root["source"])
        if not source_root.is_dir():
            raise ProfileError(f"profile payload root is not a directory: {root['source']}")
        prefix = PurePosixPath(root["path"])
        for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
            relative = PurePosixPath(source.relative_to(source_root).as_posix())
            destination = (prefix / relative).as_posix()
            validate_destination_path(destination)
            expanded.append((source, destination))
    for item in payload["files"]:
        source = repository_path(item["source"])
        if not source.is_file():
            raise ProfileError(f"profile payload file does not exist: {item['source']}")
        expanded.append((source, item["path"]))

    seen: set[str] = set()
    for _, destination in expanded:
        if destination in seen:
            raise ProfileError(
                f"profiles.{key}.repository_payload maps duplicate path: {destination}"
            )
        seen.add(destination)
    return expanded


def validate_markdown(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path.relative_to(ROOT)}: cannot read file: {exc}"]

    relative = path.relative_to(ROOT)
    h1_count = sum(1 for line in content.splitlines() if line.startswith("# "))
    if path.name == "SUMMARY.md":
        if h1_count < 1:
            errors.append(f"{relative}: expected at least one H1")
    elif h1_count != 1:
        errors.append(f"{relative}: expected exactly one H1, found {h1_count}")

    fence: tuple[str, int] | None = None
    for number, line in enumerate(content.splitlines(), start=1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if not match:
            continue
        marker = match.group(1)
        if fence is None:
            fence = (marker[0], len(marker))
        elif marker[0] == fence[0] and len(marker) >= fence[1]:
            fence = None
    if fence is not None:
        errors.append(f"{relative}: unclosed fenced code block")

    for match in LINK_PATTERN.finditer(content):
        target = match.group(1).strip().strip("<>").split()[0]
        if not target or re.match(r"^(?:[a-z]+:|#|/)", target, re.IGNORECASE):
            continue
        local = urllib.parse.unquote(target.split("#", 1)[0].split("?", 1)[0])
        resolved = (path.parent / local).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"{relative}: link escapes repository root: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{relative}: missing local link target: {target}")
    return errors


def support_tier_block(config: dict[str, Any], profile: dict[str, Any]) -> str:
    """Render one factual operational README block from structured data."""
    source = config["source_of_truth"]
    lines = [
        SUPPORT_TIERS_START,
        f"The [{source['name']}]({source['collective_url']}) connects transparent",
        "contributions to named public purposes. Its",
        f"[current contribution options]({source['contribution_options_url']}) remain",
        "the source of truth for live offerings.",
        "",
        profile["scope_statement"],
        "A tier is a contribution purpose—not a rank, entitlement, governance role,",
        "security clearance, or access level.",
    ]
    if profile["include_metadata_template"]:
        lines.extend(
            [
                "",
                "### Required tier metadata",
                "",
                "| Field | Required description |",
                "|---|---|",
            ]
        )
        for field in config["required_tier_metadata"]:
            lines.append(f"| {field['label']} | {field['description']} |")

    lines.extend(
        [
            "",
            "### Contribution-purpose summary",
            "",
            "| Tier family | Supported public work |",
            "|---|---|",
        ]
    )
    for family in profile["families"]:
        lines.append(f"| {family['label']} | {family['purpose']} |")
    lines.extend(
        [
            "",
            source["authority"],
            "A contribution expresses support for the stated purpose; it does not",
            "purchase governance authority or guarantee delivery of a proposal, service,",
            "or benefit.",
            "",
            "This factual operational block is generated from the canonical structured",
            "support-tier configuration.",
            "Fictional tier narratives remain exclusively under `characters/lore/`.",
            SUPPORT_TIERS_END,
        ]
    )
    return "\n".join(lines)


def replace_managed_block(content: str, expected: str, path: Path) -> str:
    start_count = content.count(SUPPORT_TIERS_START)
    end_count = content.count(SUPPORT_TIERS_END)
    if start_count != 1 or end_count != 1:
        raise ProfileError(
            f"{path.relative_to(ROOT)}: expected exactly one support-tier marker pair"
        )
    start = content.index(SUPPORT_TIERS_START)
    end = content.index(SUPPORT_TIERS_END, start) + len(SUPPORT_TIERS_END)
    return content[:start] + expected + content[end:]


def generate_support_tiers(config: dict[str, Any], check: bool) -> None:
    """Generate or verify operational README sections without touching lore."""
    stale: list[str] = []
    for profile in config["profiles"].values():
        path = repository_path(profile["readme"])
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProfileError(f"cannot read support-tier target {path}: {exc}") from exc
        expected = support_tier_block(config, profile)
        updated = replace_managed_block(content, expected, path)
        if updated == content:
            print(f"Support tiers current: {path.relative_to(ROOT)}")
            continue
        stale.append(str(path.relative_to(ROOT)))
        if not check:
            path.write_text(updated, encoding="utf-8")
            print(f"Generated support tiers: {path.relative_to(ROOT)}")
    if check and stale:
        raise ProfileError(
            "generated support-tier content is stale: " + ", ".join(stale)
        )


def validate(manifest: dict[str, Any], support_tiers: dict[str, Any]) -> None:
    errors: list[str] = []
    markdown_files = [ROOT / "README.md", *sorted((ROOT / "DOCS").rglob("*.md"))]

    tier_profiles = support_tiers["profiles"]
    expected_tier_profiles = {"source", *manifest["profiles"]}
    if set(tier_profiles) != expected_tier_profiles:
        errors.append(
            "support-tier profiles must match source plus publication profiles: "
            f"expected {sorted(expected_tier_profiles)}, got {sorted(tier_profiles)}"
        )
    source_tiers = tier_profiles.get("source", {})
    if source_tiers.get("readme") != "README.md":
        errors.append("support-tier source profile must target README.md")

    for key, profile in manifest["profiles"].items():
        source = repository_path(profile["source"])
        policy_source = repository_path(profile["policy_source"])
        lore_source = repository_path(profile["lore_source"])
        markdown_files.append(source)
        markdown_files.append(lore_source)
        tier_profile = tier_profiles.get(key, {})
        if tier_profile.get("readme") != profile["source"]:
            errors.append(
                f"support-tier profiles.{key}.readme must equal {profile['source']!r}"
            )
        if tier_profile.get("identity") != profile["required_identity"]:
            errors.append(
                f"support-tier profiles.{key}.identity must equal "
                f"{profile['required_identity']!r}"
            )
        try:
            content = source.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{profile['source']}: cannot read template: {exc}")
            continue

        if profile["required_identity"] not in content:
            errors.append(
                f"{profile['source']}: missing required identity "
                f"{profile['required_identity']!r}"
            )
        lowered = content.casefold()
        for forbidden in profile.get("forbidden_identity", []):
            if forbidden.casefold() in lowered:
                errors.append(
                    f"{profile['source']}: forbidden identity present: {forbidden!r}"
                )

        destinations = profile["destinations"]
        if len(destinations) != 2:
            errors.append(
                f"profiles.{key}: expected one named README repo and one .github "
                f"profile destination, found {len(destinations)}"
            )
        try:
            policy = json.loads(policy_source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{profile['policy_source']}: cannot read policy: {exc}")
        else:
            required = policy.get("identity", {}).get("required", [])
            if profile["required_identity"] not in required:
                errors.append(
                    f"{profile['policy_source']}: policy does not require "
                    f"{profile['required_identity']!r}"
                )

        try:
            lore = lore_source.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{profile['lore_source']}: cannot read lore: {exc}")
        else:
            if profile["required_identity"] not in lore:
                errors.append(
                    f"{profile['lore_source']}: missing required identity "
                    f"{profile['required_identity']!r}"
                )
            lowered_lore = lore.casefold()
            for forbidden in profile.get("forbidden_identity", []):
                if forbidden.casefold() in lowered_lore:
                    errors.append(
                        f"{profile['lore_source']}: forbidden identity present: "
                        f"{forbidden!r}"
                    )

        try:
            payload_files = profile_payload_files(key, profile)
        except ProfileError as exc:
            errors.append(str(exc))
            payload_files = []
        for payload_source, payload_destination in payload_files:
            if (
                payload_source.suffix.casefold() == ".md"
                and not payload_destination.startswith(".github/")
            ):
                markdown_files.append(payload_source)
            if payload_source.suffix.casefold() not in {
                ".md",
                ".json",
                ".toml",
                ".svg",
                ".yml",
                ".yaml",
            }:
                continue
            try:
                payload_text = payload_source.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(
                    f"{payload_source.relative_to(ROOT)}: cannot read payload text: {exc}"
                )
                continue
            lowered_payload = payload_text.casefold()
            for forbidden in profile.get("forbidden_identity", []):
                if forbidden.casefold() in lowered_payload:
                    errors.append(
                        f"{payload_source.relative_to(ROOT)}: forbidden identity "
                        f"present in repository payload: {forbidden!r}"
                    )

    portable_identities = {"Interested-Deving-1896"}
    portable_identities.update(
        profile["required_identity"] for profile in manifest["profiles"].values()
    )
    for relative_source in manifest["shared_automation"]["sources"]:
        source = repository_path(relative_source)
        try:
            content = source.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relative_source}: cannot read shared automation: {exc}")
            continue
        for identity in portable_identities:
            if identity.casefold() in content.casefold():
                errors.append(
                    f"{relative_source}: shared automation hard-codes identity "
                    f"{identity!r}"
                )

    seen: set[Path] = set()
    for path in markdown_files:
        if path in seen:
            continue
        seen.add(path)
        errors.extend(validate_markdown(path))

    try:
        generate_support_tiers(support_tiers, check=True)
    except ProfileError as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise ProfileError(f"validation failed with {len(errors)} error(s)")
    print(f"Validated {len(seen)} Markdown files and all profile identities.")


def generated_document(manifest: dict[str, Any]) -> str:
    lines = [
        "# Organization README publication targets",
        "",
        "This page is generated from `config/profile-targets.json`. The two",
        "organization templates are independent identities; the personal profile",
        "README is not copied into either organization.",
        "",
        "| Profile | Canonical template | Destination repository | Destination file |",
        "|---|---|---|---|",
    ]
    for profile in manifest["profiles"].values():
        for destination in profile["destinations"]:
            repository = destination["repository"]
            path = destination["path"]
            lines.append(
                f"| {profile['title']} | [`{profile['source']}`]"
                f"({SOURCE_BLOB_URL}/{profile['source']}) | "
                f"[`{repository}`](https://github.com/{repository}) | `{path}` |"
            )
    lines.extend(
        [
            "",
            "Publication validates identity boundaries before making any update.",
            "Drift verification compares each remote file byte-for-byte with its",
            "canonical organization template.",
            "",
            "## Shared automation targets",
            "",
            "The following portable files are mirrored unchanged to both organization",
            "README repositories. They derive repository identity at runtime.",
            "",
            "| Canonical file | Destination repository |",
            "|---|---|",
        ]
    )
    for source in manifest["shared_automation"]["sources"]:
        for destination in manifest["shared_automation"]["destinations"]:
            repository = destination["repository"]
            lines.append(
                f"| [`{source}`]({SOURCE_BLOB_URL}/{source}) | "
                f"[`{repository}`](https://github.com/{repository}) |"
            )
    lines.extend(
        [
            "",
            "## Repository-specific README policies",
            "",
            "Each named README repository receives its own policy; policies are not",
            "copied across organization boundaries.",
            "",
            "| Organization | Canonical policy | Destination |",
            "|---|---|---|",
        ]
    )
    for profile in manifest["profiles"].values():
        policy = profile["policy_destination"]
        lines.append(
            f"| {profile['title']} | [`{profile['policy_source']}`]"
            f"({SOURCE_BLOB_URL}/{profile['policy_source']}) | "
            f"[`{policy['repository']}:{policy['path']}`]"
            f"(https://github.com/{policy['repository']}/blob/{policy['branch']}/{policy['path']}) |"
        )
    lines.extend(
        [
            "",
            "## Organization-specific fictional lore",
            "",
            "Each named README repository receives a Stewardship Ledger variant",
            "written only for that repository's identity. Detailed fiction remains",
            "outside the operational organization profile README.",
            "",
            "| Organization | Canonical lore | Destination |",
            "|---|---|---|",
        ]
    )
    for profile in manifest["profiles"].values():
        lore = profile["lore_destination"]
        lines.append(
            f"| {profile['title']} | [`{profile['lore_source']}`]"
            f"({SOURCE_BLOB_URL}/{profile['lore_source']}) | "
            f"[`{lore['repository']}:{lore['path']}`]"
            f"(https://github.com/{lore['repository']}/blob/{lore['branch']}/{lore['path']}) |"
        )
    lines.extend(
        [
            "",
            "## Organization-specific repository payloads",
            "",
            "Documentation sites, community-health files, and preview assets are",
            "published only to their matching named README repository.",
            "",
            "| Organization | Canonical roots | Explicit files | Destination |",
            "|---|---:|---:|---|",
        ]
    )
    for profile in manifest["profiles"].values():
        payload = profile["repository_payload"]
        roots = ", ".join(f"`{root['source']}`" for root in payload["roots"])
        repository = payload["repository"]
        lines.append(
            f"| {profile['title']} | {roots} | {len(payload['files'])} | "
            f"[`{repository}`](https://github.com/{repository}) |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_docs(manifest: dict[str, Any], output: Path, check: bool) -> None:
    expected = generated_document(manifest)
    if check:
        actual = output.read_text(encoding="utf-8") if output.exists() else ""
        if actual != expected:
            raise ProfileError(f"generated documentation is stale: {output}")
        print(f"Generated documentation is current: {output.relative_to(ROOT)}")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Generated {output.relative_to(ROOT)}")


def github_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    allow_not_found: bool = False,
) -> dict[str, Any]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "Interested-Deving-1896-profile-publisher",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        if allow_not_found and exc.code == 404:
            return {}
        detail = exc.read().decode(errors="replace")
        raise ProfileError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProfileError(f"GitHub API {method} {url} failed: {exc}") from exc


def remote_file(
    repository: str, path: str, branch: str, token: str
) -> tuple[bytes, str | None]:
    encoded_path = urllib.parse.quote(path, safe="/")
    encoded_ref = urllib.parse.quote(branch, safe="")
    url = (
        f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
        f"?ref={encoded_ref}"
    )
    data = github_request("GET", url, token, allow_not_found=True)
    if not data:
        return b"", None
    if data.get("type") != "file" or not data.get("sha"):
        raise ProfileError(f"remote target is not a file: {repository}:{path}")
    content = base64.b64decode(data.get("content", ""))
    return content, data["sha"]


def commit_files(
    repository: str,
    branch: str,
    files: list[tuple[str, bytes]],
    token: str,
) -> None:
    """Commit a set of managed files atomically to one destination branch."""
    encoded_branch = urllib.parse.quote(branch, safe="")
    ref = github_request(
        "GET",
        f"https://api.github.com/repos/{repository}/git/ref/heads/{encoded_branch}",
        token,
    )
    head_sha = ref.get("object", {}).get("sha")
    if not head_sha:
        raise ProfileError(f"cannot resolve destination branch: {repository}:{branch}")
    commit = github_request(
        "GET",
        f"https://api.github.com/repos/{repository}/git/commits/{head_sha}",
        token,
    )
    base_tree = commit.get("tree", {}).get("sha")
    if not base_tree:
        raise ProfileError(f"cannot resolve destination tree: {repository}:{branch}")

    tree_entries: list[dict[str, str]] = []
    for path, content in sorted(files):
        blob = github_request(
            "POST",
            f"https://api.github.com/repos/{repository}/git/blobs",
            token,
            {
                "content": base64.b64encode(content).decode(),
                "encoding": "base64",
            },
        )
        if not blob.get("sha"):
            raise ProfileError(f"cannot create destination blob: {repository}:{path}")
        tree_entries.append(
            {"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]}
        )

    tree = github_request(
        "POST",
        f"https://api.github.com/repos/{repository}/git/trees",
        token,
        {"base_tree": base_tree, "tree": tree_entries},
    )
    new_commit = github_request(
        "POST",
        f"https://api.github.com/repos/{repository}/git/commits",
        token,
        {
            "message": "chore: synchronize managed README repository content",
            "tree": tree["sha"],
            "parents": [head_sha],
        },
    )
    github_request(
        "PATCH",
        f"https://api.github.com/repos/{repository}/git/refs/heads/{encoded_branch}",
        token,
        {"sha": new_commit["sha"], "force": False},
    )
    print(f"COMMITTED {repository}:{branch} ({len(files)} file(s))")


def sync_profiles(
    manifest: dict[str, Any],
    token: str,
    check: bool,
    dry_run: bool,
    selected_profile: str | None,
) -> None:
    if not token:
        raise ProfileError("PROFILE_SYNC_TOKEN or GH_TOKEN is required")

    profiles = manifest["profiles"]
    if selected_profile:
        if selected_profile not in profiles:
            raise ProfileError(f"unknown profile selected for sync: {selected_profile}")
        selected_profiles = {selected_profile: profiles[selected_profile]}
    else:
        selected_profiles = profiles

    drift = 0
    pending_updates: dict[tuple[str, str], dict[str, bytes]] = {}

    def queue_update(repository: str, branch: str, path: str, content: bytes) -> None:
        destination = pending_updates.setdefault((repository, branch), {})
        existing = destination.get(path)
        if existing is not None and existing != content:
            raise ProfileError(
                f"conflicting managed content for destination: {repository}:{path}"
            )
        destination[path] = content

    for profile_key, profile in selected_profiles.items():
        source = repository_path(profile["source"])
        expected = source.read_bytes()
        for destination in profile["destinations"]:
            repository = destination["repository"]
            path = destination["path"]
            branch = destination["branch"]
            actual, sha = remote_file(repository, path, branch, token)
            label = f"{repository}:{path}"
            if actual == expected:
                print(f"CURRENT {label}")
                continue

            drift += 1
            print(f"DRIFT {label}")
            if check or dry_run:
                continue

            queue_update(repository, branch, path, expected)
            print(f"QUEUED {label}")

        policy_source = repository_path(profile["policy_source"])
        expected = policy_source.read_bytes()
        destination = profile["policy_destination"]
        repository = destination["repository"]
        path = destination["path"]
        branch = destination["branch"]
        actual, sha = remote_file(repository, path, branch, token)
        label = f"{repository}:{path}"
        if actual == expected:
            print(f"CURRENT {label}")
        else:
            drift += 1
            print(f"DRIFT {label}")
            if not check and not dry_run:
                queue_update(repository, branch, path, expected)
                print(f"QUEUED {label}")

        lore_source = repository_path(profile["lore_source"])
        expected = lore_source.read_bytes()
        destination = profile["lore_destination"]
        repository = destination["repository"]
        path = destination["path"]
        branch = destination["branch"]
        actual, sha = remote_file(repository, path, branch, token)
        label = f"{repository}:{path}"
        if actual == expected:
            print(f"CURRENT {label}")
        else:
            drift += 1
            print(f"DRIFT {label}")
            if not check and not dry_run:
                queue_update(repository, branch, path, expected)
                print(f"QUEUED {label}")

        payload = profile["repository_payload"]
        repository = payload["repository"]
        branch = payload["branch"]
        for payload_source, path in profile_payload_files(profile_key, profile):
            expected = payload_source.read_bytes()
            actual, sha = remote_file(repository, path, branch, token)
            label = f"{repository}:{path}"
            if actual == expected:
                print(f"CURRENT {label}")
                continue

            drift += 1
            print(f"DRIFT {label}")
            if check or dry_run:
                continue

            queue_update(repository, branch, path, expected)
            print(f"QUEUED {label}")

    for relative_source in manifest["shared_automation"]["sources"]:
        source = repository_path(relative_source)
        expected = source.read_bytes()
        for destination in manifest["shared_automation"]["destinations"]:
            if selected_profile and destination["profile"] != selected_profile:
                continue
            repository = destination["repository"]
            branch = destination["branch"]
            actual, sha = remote_file(repository, relative_source, branch, token)
            label = f"{repository}:{relative_source}"
            if actual == expected:
                print(f"CURRENT {label}")
                continue

            drift += 1
            print(f"DRIFT {label}")
            if check or dry_run:
                continue

            queue_update(repository, branch, relative_source, expected)
            print(f"QUEUED {label}")

    if not check and not dry_run:
        for (repository, branch), files in sorted(pending_updates.items()):
            commit_files(repository, branch, list(files.items()), token)

    if check and drift:
        raise ProfileError(f"{drift} downstream target(s) have drifted")
    if dry_run:
        print(f"Dry run complete: {drift} target(s) would be updated.")
    elif not check:
        print(
            f"Publication complete: {drift} target(s) updated in "
            f"{len(pending_updates)} commit(s)."
        )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    result.add_argument("--support-tiers", type=Path, default=DEFAULT_SUPPORT_TIERS)
    subparsers = result.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")

    docs = subparsers.add_parser("generate-docs")
    docs.add_argument("--output", type=Path, default=DEFAULT_GENERATED_DOC)
    docs.add_argument("--check", action="store_true")

    tiers = subparsers.add_parser("generate-tiers")
    tiers.add_argument("--check", action="store_true")

    sync = subparsers.add_parser("sync")
    sync.add_argument("--check", action="store_true")
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument(
        "--profile",
        help="publish only one configured profile and its shared automation target",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        manifest = read_manifest(args.manifest)
        support_tiers = read_support_tiers(args.support_tiers)
        if args.command == "validate":
            validate(manifest, support_tiers)
        elif args.command == "generate-docs":
            generate_docs(manifest, args.output, args.check)
        elif args.command == "generate-tiers":
            generate_support_tiers(support_tiers, args.check)
        elif args.command == "sync":
            validate(manifest, support_tiers)
            token = os.environ.get("PROFILE_SYNC_TOKEN") or os.environ.get("GH_TOKEN", "")
            sync_profiles(manifest, token, args.check, args.dry_run, args.profile)
        return 0
    except (OSError, ProfileError, UnicodeDecodeError) as exc:
        print(f"profile-readmes: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
