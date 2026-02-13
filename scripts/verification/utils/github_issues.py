"""
GitHub Issues formatter for verification pipeline.

Formats verification results into GitHub Issue bodies.
Note: Issue creation/update is handled by actions/github-script in the workflow.
This module provides formatting utilities.
"""

from typing import Optional
from datetime import datetime, timezone


def format_issue_title(date: Optional[str] = None) -> str:
    """Generate issue title for verification failures."""
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"[Verification] ACTION REQUIRED - {date}"


def format_issue_body(
    links_result: dict = None,
    crossrefs_result: dict = None,
    facts_result: dict = None,
    circulars_result: dict = None,
    run_url: str = "",
    run_number: int = 0,
) -> str:
    """Format verification results into a GitHub Issue body."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sections = []
    sections.append(f"## Daily Verification Pipeline - ACTION REQUIRED\n")
    sections.append(f"**Date:** {date}")
    if run_url:
        sections.append(f"**Run:** [#{run_number}]({run_url})")
    sections.append("")

    # Links summary
    if links_result:
        failures = links_result.get("failures", [])
        pdf_updates = links_result.get("pdf_updates", [])
        total = links_result.get("total_urls", 0)
        results = links_result.get("results", {})
        ok_count = results.get("OK", 0)
        sections.append(f"### URL Validation: {ok_count}/{total} OK")
        if failures:
            sections.append(f"**{len(failures)} broken links found:**")
            for f in failures[:10]:  # First 10
                sections.append(f"- `{f['url']}` ({f['status']}) in {f['locations'][0]['file']}:{f['locations'][0]['line']}")
            if len(failures) > 10:
                sections.append(f"  ... and {len(failures) - 10} more")
        if pdf_updates:
            sections.append(f"\n**{len(pdf_updates)} PDFs updated:**")
            for p in pdf_updates[:5]:
                sections.append(f"- `{p['url']}`")
        sections.append("")

    # Cross-refs summary
    if crossrefs_result:
        broken = crossrefs_result.get("broken", 0)
        total = crossrefs_result.get("total_internal_links", 0)
        sections.append(f"### Cross-References: {total - broken}/{total} valid")
        if broken:
            for f in crossrefs_result.get("failures", [])[:10]:
                sections.append(f"- `{f['source_file']}:{f['line']}` -> `{f['target']}`: {f['error']}")
        sections.append("")

    # Facts summary
    if facts_result:
        changed = facts_result.get("changed", 0)
        stale = facts_result.get("stale", 0)
        sections.append(f"### Fact Verification: {changed} changed, {stale} stale")
        for d in facts_result.get("details", []):
            if d.get("status") in ("CHANGED", "NOT_FOUND_IN_SOURCE", "NEEDS_UPDATE"):
                sections.append(f"- **{d['id']}**: {d.get('note', d['status'])}")
        sections.append("")

    # Circulars summary
    if circulars_result:
        new_relevant = circulars_result.get("new_relevant", 0)
        if new_relevant:
            sections.append(f"### New Relevant Circulars: {new_relevant}")
            for c in circulars_result.get("new_circulars", []):
                if c.get("is_relevant"):
                    sections.append(f"- **{c['title']}** ({c.get('date', 'no date')})")
                    sections.append(f"  Keywords: {', '.join(c.get('matched_keywords', []))}")
            sections.append("")

    sections.append("---")
    sections.append("*See full report in workflow artifacts or `reports/latest-report.md`*")

    return "\n".join(sections)


def format_webhook_payload(
    status: str,
    run_url: str = "",
    run_number: int = 0,
    failure_count: int = 0,
) -> dict:
    """Format a Slack-compatible webhook payload."""
    emoji = ":white_check_mark:" if status == "PASS" else ":warning:" if status == "WARNINGS" else ":x:"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    text = f"{emoji} Verification Pipeline: {status} ({date})"
    if failure_count:
        text += f" - {failure_count} issues found"

    payload = {
        "text": text,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Daily Verification Pipeline*\n"
                           f"Status: *{status}* {emoji}\n"
                           f"Date: {date}\n"
                           f"Issues: {failure_count}"
                }
            }
        ]
    }

    if run_url:
        payload["blocks"].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": f"View Run #{run_number}"},
                    "url": run_url
                }
            ]
        })

    return payload
