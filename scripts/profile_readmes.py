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
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config" / "profile-targets.json"
DEFAULT_GENERATED_DOC = ROOT / "DOCS" / "generated" / "profile-targets.md"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


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
        for field in ("repository", "branch"):
            if not destination.get(field):
                raise ProfileError(
                    f"shared_automation.destinations.{field} is required"
                )
    return data


def repository_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ProfileError(f"path escapes repository root: {relative}") from exc
    return candidate


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


def validate(manifest: dict[str, Any]) -> None:
    errors: list[str] = []
    markdown_files = [ROOT / "README.md", *sorted((ROOT / "DOCS").rglob("*.md"))]

    for key, profile in manifest["profiles"].items():
        source = repository_path(profile["source"])
        policy_source = repository_path(profile["policy_source"])
        lore_source = repository_path(profile["lore_source"])
        markdown_files.append(source)
        markdown_files.append(lore_source)
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
                f"(../../{profile['source']}) | "
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
                f"| [`{source}`](../../{source}) | "
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
            f"(../../{profile['policy_source']}) | "
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
            f"(../../{profile['lore_source']}) | "
            f"[`{lore['repository']}:{lore['path']}`]"
            f"(https://github.com/{lore['repository']}/blob/{lore['branch']}/{lore['path']}) |"
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
) -> tuple[str, str | None]:
    encoded_path = urllib.parse.quote(path, safe="/")
    encoded_ref = urllib.parse.quote(branch, safe="")
    url = (
        f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
        f"?ref={encoded_ref}"
    )
    data = github_request("GET", url, token, allow_not_found=True)
    if not data:
        return "", None
    if data.get("type") != "file" or not data.get("sha"):
        raise ProfileError(f"remote target is not a file: {repository}:{path}")
    content = base64.b64decode(data.get("content", "")).decode("utf-8")
    return content, data["sha"]


def sync_profiles(
    manifest: dict[str, Any], token: str, check: bool, dry_run: bool
) -> None:
    if not token:
        raise ProfileError("PROFILE_SYNC_TOKEN or GH_TOKEN is required")

    drift = 0
    for profile in manifest["profiles"].values():
        source = repository_path(profile["source"])
        expected = source.read_text(encoding="utf-8")
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

            encoded_path = urllib.parse.quote(path, safe="/")
            url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
            github_request(
                "PUT",
                url,
                token,
                {
                    "message": "docs: synchronize organization profile",
                    "content": base64.b64encode(expected.encode()).decode(),
                    "branch": branch,
                    **({"sha": sha} if sha else {}),
                },
            )
            print(f"UPDATED {label}")

        policy_source = repository_path(profile["policy_source"])
        expected = policy_source.read_text(encoding="utf-8")
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
                encoded_path = urllib.parse.quote(path, safe="/")
                url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
                github_request(
                    "PUT",
                    url,
                    token,
                    {
                        "message": "ci: synchronize repository README policy",
                        "content": base64.b64encode(expected.encode()).decode(),
                        "branch": branch,
                        **({"sha": sha} if sha else {}),
                    },
                )
                print(f"UPDATED {label}")

        lore_source = repository_path(profile["lore_source"])
        expected = lore_source.read_text(encoding="utf-8")
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
                encoded_path = urllib.parse.quote(path, safe="/")
                url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
                github_request(
                    "PUT",
                    url,
                    token,
                    {
                        "message": "docs: synchronize organization-specific lore",
                        "content": base64.b64encode(expected.encode()).decode(),
                        "branch": branch,
                        **({"sha": sha} if sha else {}),
                    },
                )
                print(f"UPDATED {label}")

    for relative_source in manifest["shared_automation"]["sources"]:
        source = repository_path(relative_source)
        expected = source.read_text(encoding="utf-8")
        for destination in manifest["shared_automation"]["destinations"]:
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

            encoded_path = urllib.parse.quote(relative_source, safe="/")
            url = f"https://api.github.com/repos/{repository}/contents/{encoded_path}"
            github_request(
                "PUT",
                url,
                token,
                {
                    "message": "ci: synchronize shared repository automation",
                    "content": base64.b64encode(expected.encode()).decode(),
                    "branch": branch,
                    **({"sha": sha} if sha else {}),
                },
            )
            print(f"UPDATED {label}")

    if check and drift:
        raise ProfileError(f"{drift} downstream target(s) have drifted")
    if dry_run:
        print(f"Dry run complete: {drift} target(s) would be updated.")
    elif not check:
        print(f"Publication complete: {drift} target(s) updated.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    subparsers = result.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")

    docs = subparsers.add_parser("generate-docs")
    docs.add_argument("--output", type=Path, default=DEFAULT_GENERATED_DOC)
    docs.add_argument("--check", action="store_true")

    sync = subparsers.add_parser("sync")
    sync.add_argument("--check", action="store_true")
    sync.add_argument("--dry-run", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        manifest = read_manifest(args.manifest)
        if args.command == "validate":
            validate(manifest)
        elif args.command == "generate-docs":
            generate_docs(manifest, args.output, args.check)
        elif args.command == "sync":
            validate(manifest)
            token = os.environ.get("PROFILE_SYNC_TOKEN") or os.environ.get("GH_TOKEN", "")
            sync_profiles(manifest, token, args.check, args.dry_run)
        return 0
    except (OSError, ProfileError, UnicodeDecodeError) as exc:
        print(f"profile-readmes: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
