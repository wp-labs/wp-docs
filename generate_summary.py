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
            title = extract_title(item)
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
    for title, link in sorted(files, key=lambda x: x[1]):
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
