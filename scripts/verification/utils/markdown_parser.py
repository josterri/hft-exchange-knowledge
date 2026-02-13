"""Markdown parsing utilities for link extraction and validation."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class URLReference:
    """Reference to an external URL found in markdown."""
    url: str
    line_number: int
    context_text: str
    link_text: str


@dataclass
class InternalLink:
    """Reference to an internal markdown file."""
    target_path: str
    anchor: str
    line_number: int
    link_text: str


def extract_urls(file_path: Path) -> List[URLReference]:
    """Extract all external URLs from a markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        List of URLReference objects
    """
    urls = []

    # Regex patterns
    markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    bare_url_pattern = re.compile(r'https?://[^\s<>\[\]]+')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return urls

    for line_num, line in enumerate(lines, start=1):
        # Find markdown links [text](url)
        for match in markdown_link_pattern.finditer(line):
            link_text = match.group(1)
            url = match.group(2)

            # Skip anchors and relative paths
            if url.startswith('#'):
                continue
            if not url.startswith('http'):
                continue

            # Get context (trim whitespace)
            context = line.strip()
            if len(context) > 100:
                context = context[:97] + "..."

            urls.append(URLReference(
                url=url,
                line_number=line_num,
                context_text=context,
                link_text=link_text
            ))

        # Find bare URLs (not already in markdown links)
        # Remove markdown links from line first
        line_without_md_links = markdown_link_pattern.sub('', line)

        for match in bare_url_pattern.finditer(line_without_md_links):
            url = match.group(0)

            # Get context
            context = line.strip()
            if len(context) > 100:
                context = context[:97] + "..."

            urls.append(URLReference(
                url=url,
                line_number=line_num,
                context_text=context,
                link_text=url
            ))

    return urls


def extract_internal_links(file_path: Path) -> List[InternalLink]:
    """Extract all internal markdown links from a file.

    Args:
        file_path: Path to markdown file

    Returns:
        List of InternalLink objects
    """
    links = []
    markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return links

    for line_num, line in enumerate(lines, start=1):
        for match in markdown_link_pattern.finditer(line):
            link_text = match.group(1)
            target = match.group(2)

            # Skip external URLs
            if target.startswith('http'):
                continue

            # Skip pure anchors (unless they're the only thing)
            if target.startswith('#'):
                links.append(InternalLink(
                    target_path="",
                    anchor=target[1:],
                    line_number=line_num,
                    link_text=link_text
                ))
                continue

            # Parse path and anchor
            if '#' in target:
                path_part, anchor_part = target.split('#', 1)
                anchor = anchor_part
            else:
                path_part = target
                anchor = ""

            # Only include links to .md files
            if not path_part.endswith('.md'):
                continue

            links.append(InternalLink(
                target_path=path_part,
                anchor=anchor,
                line_number=line_num,
                link_text=link_text
            ))

    return links


def extract_headings(file_path: Path) -> List[str]:
    """Extract all markdown headings as GitHub-style anchors.

    Args:
        file_path: Path to markdown file

    Returns:
        List of anchor strings (lowercase, hyphens, no special chars)
    """
    headings = []
    heading_pattern = re.compile(r'^#+\s+(.+)$')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return headings

    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            heading_text = match.group(1)

            # Convert to GitHub-style anchor
            # 1. Lowercase
            anchor = heading_text.lower()
            # 2. Remove special characters (keep alphanumeric, spaces, hyphens)
            anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
            # 3. Replace spaces with hyphens
            anchor = re.sub(r'\s+', '-', anchor)
            # 4. Remove multiple consecutive hyphens
            anchor = re.sub(r'-+', '-', anchor)
            # 5. Strip leading/trailing hyphens
            anchor = anchor.strip('-')

            if anchor:
                headings.append(anchor)

    return headings


def get_all_markdown_files(repo_root: Path) -> List[Path]:
    """Find all markdown files in repository.

    Args:
        repo_root: Root directory of repository

    Returns:
        List of Path objects for all .md files
    """
    markdown_files = []

    # Directories to exclude
    exclude_dirs = {'.omc', '.git', 'node_modules', '__pycache__', '.venv', 'venv'}

    for md_file in repo_root.rglob('*.md'):
        # Check if any parent directory is in exclude list
        if any(part in exclude_dirs for part in md_file.parts):
            continue

        markdown_files.append(md_file)

    return sorted(markdown_files)
