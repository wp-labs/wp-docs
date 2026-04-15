#!/usr/bin/env python3
"""
Generate mdbook SUMMARY.md with proper directory structure
"""

import os
import re
from pathlib import Path


def extract_title(file_path):
    """Extract title from markdown file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass

    # Fallback to filename with better formatting
    name = file_path.stem
    return name.replace("_", " ").replace("-", " ").title()


def shorten_summary_title(file_path, title):
    """Shorten long headings for sidebar readability without changing document titles."""
    shortened = title.strip()
    path_str = str(file_path).replace("\\", "/")

    # Drop long explanatory parentheticals commonly used for implementation notes.
    shortened = re.sub(r"（对齐[^）]+）", "", shortened)
    shortened = re.sub(r"\(aligned with [^)]+\)", "", shortened, flags=re.IGNORECASE)

    # Common documentation suffixes can be shorter in navigation.
    replacements = [
        ("运行时管理面使用说明", "运行时管理"),
        ("Remote Project Sync And Rule Reload SOP", "Project Sync SOP"),
        ("远程工程拉取与规则热更新 SOP", "工程热更新 SOP"),
        ("`wprescue` 与 rescue 数据使用指南", "`wprescue` 使用"),
        ("与 rescue 数据使用指南", "Rescue 使用"),
        ("And Rescue Data Usage", "Rescue Usage"),
        ("项目工具使用指南", "项目工具"),
        ("Sources Configuration Guide", "Sources Guide"),
        ("Sinks Configuration Guide", "Sinks Guide"),
        ("Configuration Guide", "配置指南"),
        ("Quick Reference", "速查"),
        ("排障指南（Troubleshooting）", "排障指南"),
        ("用户建议 Q&A（产品能力与配置体验）", "用户建议 Q&A"),
        ("Function and Topic Index", "函数索引"),
        ("函数与专题索引", "函数索引"),
        ("Field Functions 函数索引", "函数索引"),
        ("Case-Insensitive Static Dictionary Lookup", "Static Dict Lookup"),
        ("忽略大小写静态字典查表", "静态字典查表"),
        ("Prefix Filtering for Strings", "Prefix Filter"),
        ("结果反转包装函数", "结果反转"),
        ("表达式函数匹配", "函数匹配"),
        ("Processor 使用示例", "示例"),
        ("Complete Type System Example", "Type System Example"),
        ("Complete Feature Example", "Feature Example"),
        ("Semantic Dictionary Configuration", "Semantic Dictionary"),
        ("Connector Development Guide", "Connector Dev Guide"),
        ("Docs Aggregation Automation", "Docs Sync Automation"),
        ("Generator Usage", "Generator"),
        ("Runtime Usage", "Runtime"),
        ("CLI Usage Guide", "CLI"),
        ("功能与 CLI 使用指南", "功能与 CLI"),
        ("Product Overview", "产品概览"),
        ("Core Concepts Quick Reference", "核心概念"),
        ("Secure Variables and Environment Variables", "Secure Variables"),
        ("安全变量与环境变量", "安全变量"),
    ]
    for old, new in replacements:
        shortened = shortened.replace(old, new)

    # Function/examples pages read better in navigation without repetitive suffixes.
    if "/functions/" in path_str or "/examples/" in path_str:
        shortened = re.sub(r"\s*使用指南$", "", shortened)
        shortened = re.sub(r"\s*函数使用指南$", "", shortened)
        shortened = re.sub(r"\s*使用示例$", "", shortened)
        shortened = re.sub(r"\s*Function Usage Guide$", "", shortened, flags=re.IGNORECASE)
        shortened = re.sub(r"\s*Function Guide$", "", shortened, flags=re.IGNORECASE)
        shortened = re.sub(r"\s*Usage Guide$", "", shortened, flags=re.IGNORECASE)
        shortened = re.sub(r"\s*Example$", "", shortened, flags=re.IGNORECASE)

    # Release notes in sidebar can use shorter names.
    if "/00-release/" in path_str:
        m = re.match(r"^WarpParse\s+(\d+(?:\.\d+)*)", shortened, flags=re.IGNORECASE)
        if m:
            shortened = f"{m.group(1)} 更新说明"
        m = re.match(r"^(\d+(?:\.\d+)*)\s+Release Notes$", shortened, flags=re.IGNORECASE)
        if m:
            shortened = f"{m.group(1)} Release Notes"

    # Collapse leftover spacing after removals.
    shortened = re.sub(r"\s{2,}", " ", shortened).strip(" -:：")
    return shortened or title


def should_ignore(file_path):
    """Check if file should be ignored"""
    ignore_patterns = [
        "SUMMARY.md",
        "generate_*.py",
        ".git/",
        "target/",
        "node_modules/",
        "__pycache__/",
        "book/",
    ]

    path_str = str(file_path)
    for pattern in ignore_patterns:
        if re.search(pattern, path_str):
            return True
    return False


def get_directory_title(dirname, readme_path=None):
    """Get title for directory, try reading from README first"""
    # Try to get title from README.md first
    if readme_path and readme_path.exists():
        title = extract_title(readme_path)
        if title and title != readme_path.stem:
            return title

    # Fallback to predefined titles
    titles = {
        "adr": "Architecture Decision Records",
        "cli": "CLI Tools",
        "concepts": "Core Concepts",
        "config": "Configuration Guide",
        "decision": "Decision",
        "design": "Design Documents",
        "dev": "Developer Guide",
        "getting_started": "Getting Started",
        "getting-started": "Getting Started",
        "guides": "User Guides",
        "migration": "Migration Guides",
        "params": "Parameters Reference",
        "plugins": "Plugins",
        "reference": "Reference",
        "schemas": "Schemas",
        "sinks": "Sinks",
        "tasks": "Task Documents",
        "tools": "Tools",
        "usecases": "Use Cases",
        "user": "User Guide",
    }
    return titles.get(dirname, dirname.replace("_", " ").replace("-", " ").title())


def release_sort_key(path_obj):
    """Sort release notes by version descending."""
    stem = path_obj.stem
    parts = []
    for token in stem.split("."):
        try:
            parts.append(int(token))
        except ValueError:
            parts.append(-1)
    return tuple(parts)


def sort_summary_files(dir_path, files):
    """Sort files for SUMMARY generation."""
    rel_dir = dir_path.as_posix()
    if rel_dir.endswith("00-release"):
        return sorted(files, key=lambda x: release_sort_key(Path(x[1])), reverse=True)
    return sorted(files, key=lambda x: x[1])


def process_directory(dir_path, docs_root, indent_level=0, parent_has_header=True):
    """Recursively process directory and return summary lines"""
    lines = []
    indent = "  " * indent_level

    # Get relative path from docs root
    rel_path = dir_path.relative_to(docs_root)

    # Check if README.md exists
    readme_path = dir_path / "README.md"
    has_readme = readme_path.exists()

    # Get directory title
    dir_title = get_directory_title(dir_path.name, readme_path)

    # Only add directory header if it has a README (mdbook requires links for nested items)
    if has_readme:
        lines.append(f"{indent}- [{dir_title}]({rel_path}/README.md)")
        content_indent = indent + "  "
        current_has_header = True
    else:
        # No README, so we'll list content at current indent without a header
        content_indent = indent
        current_has_header = False

    # Collect files and subdirectories
    files = []
    subdirs = []

    for item in sorted(dir_path.iterdir(), key=lambda x: x.name.lower()):
        if should_ignore(item):
            continue

        if item.is_file() and item.suffix == ".md" and item.name != "README.md":
            title = shorten_summary_title(item, extract_title(item))
            link = item.relative_to(docs_root)
            files.append((title, str(link)))
        elif item.is_dir():
            # Check if directory has any markdown files
            has_md = any(
                f.suffix == ".md" for f in item.rglob("*.md") if not should_ignore(f)
            )
            if has_md:
                subdirs.append(item)

    # Add files in this directory (sorted by link/path for proper numerical order)
    for title, link in sort_summary_files(rel_path, files):
        lines.append(f"{content_indent}- [{title}]({link})")

    # Recursively process subdirectories
    for subdir in subdirs:
        subdir_readme = subdir / "README.md"
        if subdir_readme.exists():
            # Subdirectory has README, process normally
            lines.extend(
                process_directory(
                    subdir,
                    docs_root,
                    indent_level + (1 if has_readme else 0),
                    current_has_header,
                )
            )
        else:
            # Subdirectory has no README, inline its contents
            lines.extend(
                process_directory(
                    subdir, docs_root, indent_level + (1 if has_readme else 0), False
                )
            )

    return lines


def generate_fixed_summary(docs_root):
    """Generate proper mdbook SUMMARY.md with directory structure"""

    summary_lines = ["# Summary", ""]

    # Root level files (excluding README.md as it's the index)
    root_files = []
    for file in sorted(docs_root.glob("*.md"), key=lambda x: x.name):
        if not should_ignore(file) and file.name != "README.md":
            title = extract_title(file)
            link = file.name
            root_files.append((title, link))

    # Add root files
    if root_files:
        for title, link in root_files:
            summary_lines.append(f"- [{title}]({link})")
        summary_lines.append("")

    # Find all top-level directories
    directories = []
    for item in sorted(docs_root.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir() and not should_ignore(item):
            # Check if directory has markdown files
            has_md = any(
                f.suffix == ".md" for f in item.rglob("*.md") if not should_ignore(f)
            )
            if has_md:
                directories.append(item)

    # Process each top-level directory recursively
    for dir_path in directories:
        lines = process_directory(
            dir_path, docs_root, indent_level=0, parent_has_header=False
        )
        summary_lines.extend(lines)
        summary_lines.append("")

    return "\n".join(summary_lines)


def main():
    """Main function"""
    base_dir = Path(__file__).parent

    for lang_dir in ["docs-zh", "docs-en"]:
        docs_root = base_dir / lang_dir
        if not docs_root.exists():
            print(f"Skipping {lang_dir}: directory not found")
            continue

        summary_content = generate_fixed_summary(docs_root)

        # Write SUMMARY.md
        summary_path = docs_root / "SUMMARY.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_content)

        print(f"Generated {summary_path}")
        print("-" * 40)
        print(summary_content)
        print()


if __name__ == "__main__":
    main()
