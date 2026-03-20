#!/usr/bin/env python3
"""Sync documentation from multiple upstream repositories into this repo."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
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


def sync_tree(
    src_root: Path,
    dest_root: Path,
    ignore_patterns: list[str],
    dry_run: bool,
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
                shutil.copy2(src_path, dest_path)
            continue

        if file_hash(src_path) == file_hash(dest_path):
            skipped += 1
            continue

        print(f"M  {dest_path}")
        updated += 1
        if not dry_run:
            shutil.copy2(src_path, dest_path)

    return created, updated, skipped


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

    print(f"=== Syncing {source_name} ===")
    for mapping in source.get("mappings", []):
        src_dir = source_root / mapping["from"]
        dest_dir = (repo_root / mapping["to"]).resolve()
        print(f"  {src_dir} -> {dest_dir}")
        created, updated, skipped = sync_tree(src_dir, dest_dir, ignore_patterns, dry_run)
        print(
            f"  summary: created={created} updated={updated} skipped={skipped}"
        )
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
