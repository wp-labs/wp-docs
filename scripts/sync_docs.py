#!/usr/bin/env python3
"""Sync documentation from multiple upstream repositories into this repo."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync aggregated documentation from configured upstream sources."
    )
    parser.add_argument(
        "--config",
        default="docs-sources.json",
        help="Path to the sync configuration file.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Sync only the named source. Can be provided multiple times.",
    )
    parser.add_argument(
        "--workdir",
        default=".cache/docs-sync",
        help="Working directory used for temporary git checkouts.",
    )
    parser.add_argument(
        "--prefer-local",
        action="store_true",
        help="Use local_path when it exists before falling back to git clone.",
    )
    parser.add_argument(
        "--local-override",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Override a source root for local development.",
    )
    parser.add_argument(
        "--git-token-env",
        help="Environment variable that stores a token for cloning private repositories.",
    )
    parser.add_argument(
        "--generate-summary",
        action="store_true",
        help="Run generate_summary.py after sync finishes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned changes without writing files.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_overrides(items: list[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Invalid --local-override value: {item!r}")
        name, raw_path = item.split("=", 1)
        overrides[name.strip()] = Path(raw_path).expanduser().resolve()
    return overrides


def resolve_path(base: Path, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    rendered = " ".join(cmd)
    print(f"$ {rendered}")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def git_env(token_env_name: str | None) -> tuple[dict[str, str] | None, list[str]]:
    if not token_env_name:
        return None, []

    token = os.environ.get(token_env_name)
    if not token:
        return None, []

    env = os.environ.copy()
    return env, ["-c", f"http.extraheader=AUTHORIZATION: bearer {token}"]


def prepare_git_checkout(
    source: dict,
    source_name: str,
    checkout_root: Path,
    token_env_name: str | None,
) -> Path:
    repo = source.get("repo")
    if not repo:
        raise SystemExit(f"Source {source_name!r} does not define repo or local_path")

    ref = source.get("ref", "main")
    checkout_dir = checkout_root / source_name
    env, git_prefix = git_env(token_env_name)

    if (checkout_dir / ".git").exists():
        run(["git", *git_prefix, "fetch", "--depth", "1", "origin", ref], cwd=checkout_dir, env=env)
        run(["git", "checkout", "--force", "FETCH_HEAD"], cwd=checkout_dir, env=env)
        run(["git", "clean", "-fdx"], cwd=checkout_dir, env=env)
    else:
        checkout_dir.parent.mkdir(parents=True, exist_ok=True)
        run(
            ["git", *git_prefix, "clone", "--depth", "1", "--branch", ref, repo, str(checkout_dir)],
            env=env,
        )

    checkout_subdir = source.get("checkout_subdir", "")
    return (checkout_dir / checkout_subdir).resolve()


def resolve_source_root(
    source: dict,
    config_dir: Path,
    workdir: Path,
    prefer_local: bool,
    local_overrides: dict[str, Path],
    token_env_name: str | None,
) -> Path:
    source_name = source["name"]

    if source_name in local_overrides:
        root = local_overrides[source_name]
        print(f"Using local override for {source_name}: {root}")
        return root

    local_path = resolve_path(config_dir, source.get("local_path"))
    if prefer_local and local_path and local_path.exists():
        print(f"Using local source for {source_name}: {local_path}")
        return local_path

    if local_path and not source.get("repo"):
        if not local_path.exists():
            raise SystemExit(f"Local source for {source_name!r} not found: {local_path}")
        return local_path

    git_root = prepare_git_checkout(source, source_name, workdir, token_env_name)
    print(f"Using git checkout for {source_name}: {git_root}")
    return git_root


def should_ignore(path: Path, patterns: list[str]) -> bool:
    rel = path.as_posix()
    name = path.name
    return any(fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern) for pattern in patterns)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


LANGUAGE_SWITCH_PATTERNS = [
    re.compile(r"^中文\s*\|\s*\[English\]\([^)]+\)\s*$"),
    re.compile(r"^\[中文\]\([^)]+\)\s*\|\s*English\s*$"),
]


def strip_language_switch_lines(text: str) -> str:
    lines = text.splitlines()
    rewritten_lines = [
        line
        for line in lines
        if not any(pattern.match(line.strip()) for pattern in LANGUAGE_SWITCH_PATTERNS)
    ]
    rewritten = "\n".join(rewritten_lines)
    if text.endswith("\n"):
        rewritten += "\n"
    return rewritten


def source_bytes(src_path: Path, strip_language_switch_headers: bool) -> bytes:
    if strip_language_switch_headers and src_path.suffix == ".md":
        text = src_path.read_text(encoding="utf-8")
        return strip_language_switch_lines(text).encode("utf-8")
    return src_path.read_bytes()


def file_bytes_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clear_tree(dest_root: Path, dry_run: bool) -> None:
    if not dest_root.exists():
        return

    print(f"X  {dest_root}")
    if dry_run:
        return

    shutil.rmtree(dest_root)


def sync_tree(
    src_root: Path,
    dest_root: Path,
    ignore_patterns: list[str],
    dry_run: bool,
    strip_language_switch_headers: bool = False,
) -> tuple[int, int, int]:
    created = 0
    updated = 0
    skipped = 0

    if not src_root.exists():
        raise SystemExit(f"Source directory not found: {src_root}")

    for src_path in sorted(src_root.rglob("*")):
        rel_path = src_path.relative_to(src_root)
        if should_ignore(rel_path, ignore_patterns):
            continue

        dest_path = dest_root / rel_path
        if src_path.is_dir():
            if dry_run:
                continue
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)

        if not dest_path.exists():
            print(f"A  {dest_path}")
            created += 1
            if not dry_run:
                if strip_language_switch_headers and src_path.suffix == ".md":
                    dest_path.write_bytes(source_bytes(src_path, True))
                else:
                    shutil.copy2(src_path, dest_path)
            continue

        src_bytes = source_bytes(src_path, strip_language_switch_headers)
        if file_bytes_hash(src_bytes) == file_hash(dest_path):
            skipped += 1
            continue

        print(f"M  {dest_path}")
        updated += 1
        if not dry_run:
            if strip_language_switch_headers and src_path.suffix == ".md":
                dest_path.write_bytes(src_bytes)
            else:
                shutil.copy2(src_path, dest_path)

    return created, updated, skipped


def sync_file(
    src_path: Path,
    dest_path: Path,
    dry_run: bool,
    strip_language_switch_headers: bool = False,
) -> str:
    if not src_path.exists():
        raise SystemExit(f"Source file not found: {src_path}")
    if not src_path.is_file():
        raise SystemExit(f"Source path is not a file: {src_path}")

    if not dry_run:
        dest_path.parent.mkdir(parents=True, exist_ok=True)

    if not dest_path.exists():
        print(f"A  {dest_path}")
        if not dry_run:
            if strip_language_switch_headers and src_path.suffix == ".md":
                dest_path.write_bytes(source_bytes(src_path, True))
            else:
                shutil.copy2(src_path, dest_path)
        return "created"

    src_bytes = source_bytes(src_path, strip_language_switch_headers)
    if file_bytes_hash(src_bytes) == file_hash(dest_path):
        return "skipped"

    print(f"M  {dest_path}")
    if not dry_run:
        if strip_language_switch_headers and src_path.suffix == ".md":
            dest_path.write_bytes(src_bytes)
        else:
            shutil.copy2(src_path, dest_path)
    return "updated"


def markdown_targets(target: Path) -> list[Path]:
    if target.is_file() and target.suffix == ".md":
        return [target]
    if target.is_dir():
        return sorted(target.rglob("*.md"))
    return []


def strip_language_switch_headers(target: Path, dry_run: bool) -> int:
    updated = 0

    for md_path in markdown_targets(target):
        original = md_path.read_text(encoding="utf-8")
        rewritten = strip_language_switch_lines(original)

        if rewritten == original:
            continue
        print(f"L  {md_path}")
        updated += 1
        if not dry_run:
            md_path.write_text(rewritten, encoding="utf-8")

    return updated


def rewrite_cross_language_links(
    dest_root: Path,
    counterpart_root: Path,
    expected_lang: str,
    dry_run: bool,
) -> int:
    updated = 0
    pattern = re.compile(r"\]\(((?:\.\./)+)(zh|en)/([^)#]+?)(#[^)]+)?\)")

    for md_path in sorted(dest_root.rglob("*.md")):
        original = md_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            lang = match.group(2)
            if lang != expected_lang:
                return match.group(0)

            rel_target = Path(match.group(3))
            anchor = match.group(4) or ""
            target = counterpart_root / rel_target
            if not target.exists():
                return match.group(0)

            rewritten = os.path.relpath(target, md_path.parent).replace(os.sep, "/")
            return f"]({rewritten}{anchor})"

        rewritten = pattern.sub(replace, original)
        if rewritten == original:
            continue

        print(f"R  {md_path}")
        updated += 1
        if not dry_run:
            md_path.write_text(rewritten, encoding="utf-8")

    return updated


def rewrite_file_contents(
    dest_root: Path,
    replacements: list[tuple[str, str]],
    dry_run: bool,
) -> int:
    updated = 0

    for md_path in sorted(dest_root.rglob("*.md")):
        original = md_path.read_text(encoding="utf-8")
        rewritten = original
        for old, new in replacements:
            rewritten = rewritten.replace(old, new)

        if rewritten == original:
            continue

        print(f"T  {md_path}")
        updated += 1
        if not dry_run:
            md_path.write_text(rewritten, encoding="utf-8")

    return updated


def sync_source(
    source: dict,
    repo_root: Path,
    config_dir: Path,
    workdir: Path,
    prefer_local: bool,
    local_overrides: dict[str, Path],
    token_env_name: str | None,
    default_ignore: list[str],
    dry_run: bool,
) -> None:
    source_name = source["name"]
    source_root = resolve_source_root(
        source,
        config_dir,
        workdir,
        prefer_local,
        local_overrides,
        token_env_name,
    )
    ignore_patterns = list(default_ignore) + list(source.get("ignore", []))
    mappings = source.get("mappings", [])
    file_mappings = source.get("files", [])
    strip_language_switch = source.get("strip_language_switch_headers", False)
    mapping_by_from = {mapping["from"]: mapping for mapping in mappings}

    print(f"=== Syncing {source_name} ===")
    transformed_targets: list[Path] = []

    file_counts = {"created": 0, "updated": 0, "skipped": 0}
    for file_mapping in file_mappings:
        src_file = source_root / file_mapping["from"]
        dest_file = (repo_root / file_mapping["to"]).resolve()
        print(f"  {src_file} -> {dest_file}")
        result = sync_file(src_file, dest_file, dry_run, strip_language_switch)
        file_counts[result] += 1
        transformed_targets.append(dest_file)

    if file_mappings:
        print(
            "  file summary: "
            f"created={file_counts['created']} "
            f"updated={file_counts['updated']} "
            f"skipped={file_counts['skipped']}"
        )

    for mapping in mappings:
        src_dir = source_root / mapping["from"]
        dest_dir = (repo_root / mapping["to"]).resolve()
        print(f"  {src_dir} -> {dest_dir}")
        if mapping.get("clean", False):
            clear_tree(dest_dir, dry_run)
        created, updated, skipped = sync_tree(
            src_dir,
            dest_dir,
            ignore_patterns,
            dry_run,
            strip_language_switch,
        )
        transformed_targets.append(dest_dir)
        print(
            f"  summary: created={created} updated={updated} skipped={skipped}"
        )
        if source.get("rewrite_cross_language_links", False):
            counterpart_lang = "en" if mapping["from"] == "zh" else "zh"
            counterpart_mapping = mapping_by_from.get(counterpart_lang)
            if counterpart_mapping:
                counterpart_root = (repo_root / counterpart_mapping["to"]).resolve()
                rewritten = rewrite_cross_language_links(
                    dest_dir,
                    counterpart_root,
                    counterpart_lang,
                    dry_run,
                )
                if rewritten:
                    print(f"  relinked cross-language refs: {rewritten}")
        replacements_by_lang = source.get("replace_text", {})
        replacements = [
            (item["from"], item["to"])
            for item in replacements_by_lang.get(mapping["from"], [])
        ]
        if replacements:
            rewritten = rewrite_file_contents(dest_dir, replacements, dry_run)
            if rewritten:
                print(f"  normalized text replacements: {rewritten}")
    if strip_language_switch:
        for target in transformed_targets:
            stripped = strip_language_switch_headers(target, dry_run)
            if stripped:
                print(f"  stripped language switch headers: {stripped}")
    print()


def maybe_generate_summary(repo_root: Path, dry_run: bool) -> None:
    if dry_run:
        print("Skipping SUMMARY generation in dry-run mode.")
        return
    run([sys.executable, "generate_summary.py"], cwd=repo_root)


def main() -> int:
    args = parse_args()

    config_path = Path(args.config).expanduser().resolve()
    config_dir = config_path.parent
    repo_root = config_dir
    workdir = resolve_path(repo_root, args.workdir)
    if workdir is None:
        raise SystemExit("Unable to resolve workdir")

    config = load_config(config_path)
    sources = config.get("sources", [])
    if not sources:
        raise SystemExit(f"No sources defined in {config_path}")

    selected = set(args.source)
    if selected:
        sources = [source for source in sources if source["name"] in selected]
        if not sources:
            raise SystemExit(f"No matching sources found for: {', '.join(sorted(selected))}")

    local_overrides = parse_overrides(args.local_override)
    default_ignore = list(config.get("source_defaults", {}).get("ignore", []))

    for source in sources:
        sync_source(
            source,
            repo_root=repo_root,
            config_dir=config_dir,
            workdir=workdir,
            prefer_local=args.prefer_local,
            local_overrides=local_overrides,
            token_env_name=args.git_token_env,
            default_ignore=default_ignore,
            dry_run=args.dry_run,
        )

    should_generate_summary = args.generate_summary or config.get(
        "default_generate_summary", False
    )
    if should_generate_summary:
        maybe_generate_summary(repo_root, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
