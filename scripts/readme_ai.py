#!/usr/bin/env python3
"""Create opt-in README drafts through an OpenAI-compatible chat endpoint."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def strip_markdown_fence(value: str) -> str:
    match = re.fullmatch(r"\s*```(?:markdown|md)?\s*\n(.*?)\n```\s*", value, re.DOTALL)
    return match.group(1) if match else value.strip()


def completion(endpoint: str, token: str, payload: dict[str, Any]) -> str:
    if not endpoint.startswith("https://"):
        raise RuntimeError("README_AI_ENDPOINT must be an HTTPS URL")
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "portable-readme-maintenance",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"AI endpoint returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"AI endpoint request failed: {exc}") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("AI endpoint response has no choices[0].message.content") from exc
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("AI endpoint returned an empty draft")
    return strip_markdown_fence(content) + "\n"


def build_prompt(
    mode: str,
    readme: str,
    policy: dict[str, Any],
    language: str,
    instructions: str,
) -> str:
    identity = policy.get("identity", {})
    required = identity.get("required", [])
    forbidden = identity.get("forbidden", [])
    headings = policy.get("required_headings", [])
    managed = policy.get("managed_blocks", {})
    boundaries = (
        "Return only complete Markdown, without a surrounding code fence. "
        f"Preserve these identity strings exactly: {required}. "
        f"Do not introduce these identity strings: {forbidden}. "
        "Preserve every README-AUTO marker and the complete content between its "
        f"start and end markers exactly. Managed blocks: {list(managed)}. "
        "Do not invent project claims, links, people, metrics, or status."
    )
    if mode == "translate":
        task = (
            f"Translate the reader-facing prose into language code {language!r}. "
            "Keep URLs, code, badges, HTML comments, product names, repository names, "
            "and identity strings unchanged."
        )
    else:
        task = (
            "Improve clarity, navigation, accessibility, and concision while retaining "
            f"all factual meaning. Keep these heading texts present: {headings}."
        )
    if instructions.strip():
        task += f" Additional maintainer instructions: {instructions.strip()}"
    return f"{boundaries}\n\n{task}\n\nSOURCE README:\n{readme}"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mode", choices=("translate", "draft"))
    result.add_argument("--readme", type=Path, default=Path("README.md"))
    result.add_argument("--policy", type=Path, default=Path("config/readme-policy.json"))
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--language", default="")
    result.add_argument("--instructions", default="")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        endpoint = os.environ.get("README_AI_ENDPOINT", "").strip()
        token = os.environ.get("README_AI_TOKEN", "").strip()
        if not endpoint or not token:
            raise RuntimeError(
                "AI generation requires README_AI_ENDPOINT and README_AI_TOKEN"
            )
        if args.mode == "translate" and not re.fullmatch(
            r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})?", args.language
        ):
            raise RuntimeError("translation language must be a valid short language tag")

        policy = load_json(args.policy)
        configured_languages = policy.get("translation_languages", [])
        if (
            args.mode == "translate"
            and configured_languages
            and args.language not in configured_languages
        ):
            raise RuntimeError(
                f"language {args.language!r} is not enabled by the README policy"
            )
        readme = args.readme.read_text(encoding="utf-8")
        ai = policy.get("ai", {})
        model = os.environ.get("README_AI_MODEL", "").strip() or ai.get("model")
        if not isinstance(model, str) or not model:
            raise RuntimeError("README AI model is not configured")

        draft = completion(
            endpoint,
            token,
            {
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a documentation editor. Follow identity and "
                            "managed-content constraints exactly."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_prompt(
                            args.mode,
                            readme,
                            policy,
                            args.language,
                            args.instructions,
                        ),
                    },
                ],
            },
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(draft, encoding="utf-8")
        print(f"Generated proposal: {args.output}")
        return 0
    except (OSError, RuntimeError, UnicodeDecodeError) as exc:
        print(f"readme-ai: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
