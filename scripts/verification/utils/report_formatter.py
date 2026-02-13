"""
Utility module for formatting verification results into Markdown tables and sections.

This module provides functions to format various verification results (URL validation,
cross-references, fact checking, circular monitoring) into well-structured Markdown
output with tables, collapsible sections, and summary views.
"""

from typing import Any


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """
    Create a Markdown table from headers and rows.

    Args:
        headers: List of column header strings
        rows: List of row data, where each row is a list of cell values

    Returns:
        Formatted Markdown table string
    """
    if not headers or not rows:
        return ""

    # Header row
    table = "| " + " | ".join(headers) + " |\n"

    # Separator row
    table += "|" + "|".join(["-------" for _ in headers]) + "|\n"

    # Data rows
    for row in rows:
        # Ensure all values are strings and escape pipe characters
        escaped_row = [str(cell).replace("|", "\\|") for cell in row]
        table += "| " + " | ".join(escaped_row) + " |\n"

    return table


def format_summary_table(results: dict) -> str:
    """
    Create the top-level summary table with Status column (PASS/WARN/FAIL).

    Args:
        results: Dictionary containing all verification results with keys:
                 'links', 'crossrefs', 'facts', 'circulars'

    Returns:
        Formatted Markdown summary table
    """
    headers = ["Check", "Status", "Details"]
    rows = []

    # URL Validation
    links = results.get("links", {})
    link_stats = links.get("statistics", {})
    total_urls = link_stats.get("total_unique_urls", 0)
    failed_urls = link_stats.get("failed_urls", 0)
    redirect_urls = link_stats.get("redirects", 0)
    pdf_updates = link_stats.get("pdf_updates", 0)

    if failed_urls > 0:
        link_status = "FAIL"
    elif redirect_urls > 0 or pdf_updates > 0:
        link_status = "WARN"
    else:
        link_status = "PASS"

    link_details = f"{total_urls - failed_urls}/{total_urls} URLs OK"
    if failed_urls > 0:
        link_details += f", {failed_urls} failures"
    if redirect_urls > 0:
        link_details += f", {redirect_urls} redirects"
    if pdf_updates > 0:
        link_details += f", {pdf_updates} PDF updates"

    rows.append(["URL Validation", link_status, link_details])

    # Cross-References
    crossrefs = results.get("crossrefs", {})
    crossref_stats = crossrefs.get("statistics", {})
    total_refs = crossref_stats.get("total_references", 0)
    valid_refs = crossref_stats.get("valid_references", 0)

    if valid_refs == total_refs and total_refs > 0:
        crossref_status = "PASS"
    elif total_refs == 0:
        crossref_status = "PASS"
    else:
        crossref_status = "FAIL"

    crossref_details = f"{valid_refs}/{total_refs} links valid"
    rows.append(["Cross-References", crossref_status, crossref_details])

    # Fact Verification
    facts = results.get("facts", {})
    fact_stats = facts.get("statistics", {})
    total_facts = fact_stats.get("total_facts", 0)
    verified = fact_stats.get("verified", 0)
    changed = fact_stats.get("changed", 0)
    stale = fact_stats.get("stale", 0)
    needs_update = fact_stats.get("needs_update", 0)

    if changed > 0 or needs_update > 0:
        fact_status = "FAIL"
    elif stale > 0:
        fact_status = "WARN"
    else:
        fact_status = "PASS"

    fact_details = f"{verified} verified"
    if changed > 0:
        fact_details += f", {changed} changed"
    if stale > 0:
        fact_details += f", {stale} stale"
    if needs_update > 0:
        fact_details += f", {needs_update} need update"

    rows.append(["Fact Verification", fact_status, fact_details])

    # Circular Monitor
    circulars = results.get("circulars", {})
    circular_stats = circulars.get("statistics", {})
    new_relevant = circular_stats.get("new_relevant_circulars", 0)

    if new_relevant > 0:
        circular_status = "ACTION"
        circular_details = f"{new_relevant} new relevant circulars"
    else:
        circular_status = "INFO"
        circular_details = "No new relevant circulars"

    rows.append(["Circular Monitor", circular_status, circular_details])

    return format_table(headers, rows)


def format_link_failures(failures: list[dict]) -> str:
    """
    Format broken links section with Critical (404/errors) and Warning (redirects/PDF updates) subsections.

    Args:
        failures: List of failed link dictionaries with keys:
                  'url', 'status_code', 'error', 'file', 'line', 'link_text'

    Returns:
        Formatted Markdown section with tables
    """
    if not failures:
        return ""

    # Separate critical from warnings
    critical = []
    warnings = []

    for failure in failures:
        status_code = failure.get("status_code")
        error = failure.get("error", "")

        # Critical: 404, 5xx, domain errors, timeouts
        if (status_code in [404, 500, 502, 503, 504] or
            "domain" in error.lower() or
            "timeout" in error.lower() or
            "connection" in error.lower()):
            critical.append(failure)
        # Warning: 3xx redirects, PDF updates
        elif status_code in [301, 302, 303, 307, 308] or "pdf" in error.lower():
            warnings.append(failure)
        else:
            critical.append(failure)  # Default to critical

    output = "## Section 1: Broken Links\n\n"

    # Critical section
    if critical:
        output += "### Critical (404 / Domain Error / Server Error)\n\n"
        headers = ["URL", "Referenced In", "Line", "Link Text", "Suggested Action"]
        rows = []

        for item in critical:
            url = item.get("url", "")
            file_path = item.get("file", "")
            line = str(item.get("line", ""))
            link_text = item.get("link_text", "")
            status = item.get("status_code", "")
            error = item.get("error", "")

            # Suggest action based on error type
            if status == 404:
                action = "Remove or replace link"
            elif "domain" in error.lower():
                action = "Verify domain or remove link"
            elif status in [500, 502, 503, 504]:
                action = "Retry later or find alternative"
            else:
                action = "Investigate and fix"

            rows.append([url, file_path, line, link_text, action])

        output += format_table(headers, rows) + "\n"

    # Warning section
    if warnings:
        output += "### Warning (Redirects / Updated PDFs)\n\n"
        headers = ["URL", "Referenced In", "Line", "Status", "Action"]
        rows = []

        for item in warnings:
            url = item.get("url", "")
            file_path = item.get("file", "")
            line = str(item.get("line", ""))
            status = item.get("status_code", "")
            error = item.get("error", "")

            # Determine status and action
            if status in [301, 302, 303, 307, 308]:
                status_text = f"Redirect ({status})"
                action = "Update to final URL"
            elif "pdf" in error.lower():
                status_text = "PDF updated"
                action = "Review PDF content changes"
            else:
                status_text = str(status)
                action = "Review"

            rows.append([url, file_path, line, status_text, action])

        output += format_table(headers, rows) + "\n"

    return output


def format_crossref_failures(failures: list[dict]) -> str:
    """
    Format cross-reference issues table.

    Args:
        failures: List of broken cross-reference dictionaries with keys:
                  'source_file', 'line', 'target', 'error'

    Returns:
        Formatted Markdown section with table
    """
    if not failures:
        return ""

    output = "## Section 2: Cross-Reference Issues\n\n"
    headers = ["Source File", "Line", "Target", "Error", "Suggested Action"]
    rows = []

    for item in failures:
        source = item.get("source_file", "")
        line = str(item.get("line", ""))
        target = item.get("target", "")
        error = item.get("error", "")

        # Suggest action based on error type
        if "not found" in error.lower():
            action = "Create missing section or update reference"
        elif "ambiguous" in error.lower():
            action = "Make reference more specific"
        else:
            action = "Fix reference syntax"

        rows.append([source, line, target, error, action])

    output += format_table(headers, rows) + "\n"
    return output


def format_fact_issues(details: list[dict]) -> str:
    """
    Format fact verification issues with subsections for Changed Values,
    Approaching Deadlines, Stale Facts.

    Args:
        details: List of fact issue dictionaries with keys:
                 'fact_id', 'category', 'issue_type', 'repository_value',
                 'source_value', 'file', 'line', 'effective_date', 'days_until'

    Returns:
        Formatted Markdown section with subsections and tables
    """
    if not details:
        return ""

    output = "## Section 3: Fact Verification Issues\n\n"

    # Categorize issues
    changed = []
    approaching = []
    stale = []
    needs_update = []

    for item in details:
        issue_type = item.get("issue_type", "")
        if issue_type == "changed":
            changed.append(item)
        elif issue_type == "approaching_deadline":
            approaching.append(item)
        elif issue_type == "stale":
            stale.append(item)
        elif issue_type == "needs_update":
            needs_update.append(item)

    # Changed Values
    if changed:
        output += "### Changed Values\n\n"
        headers = ["Fact ID", "Category", "Repository Value", "Source Value", "File", "Line"]
        rows = []

        for item in changed:
            rows.append([
                item.get("fact_id", ""),
                item.get("category", ""),
                str(item.get("repository_value", "")),
                str(item.get("source_value", "")),
                item.get("file", ""),
                str(item.get("line", ""))
            ])

        output += format_table(headers, rows) + "\n"

    # Approaching Deadlines
    if approaching:
        output += "### Approaching Deadlines\n\n"
        headers = ["Fact ID", "Date", "Days Until", "File", "Line"]
        rows = []

        for item in approaching:
            rows.append([
                item.get("fact_id", ""),
                str(item.get("effective_date", "")),
                str(item.get("days_until", "")),
                item.get("file", ""),
                str(item.get("line", ""))
            ])

        output += format_table(headers, rows) + "\n"

    # Stale Facts
    if stale:
        output += "### Stale Facts (>12 months since effective date)\n\n"
        headers = ["Fact ID", "Effective Date", "File", "Line"]
        rows = []

        for item in stale:
            rows.append([
                item.get("fact_id", ""),
                str(item.get("effective_date", "")),
                item.get("file", ""),
                str(item.get("line", ""))
            ])

        output += format_table(headers, rows) + "\n"

    # Needs Update
    if needs_update:
        output += "### Needs Update (date has passed)\n\n"
        headers = ["Fact ID", "Value", "File", "Line"]
        rows = []

        for item in needs_update:
            rows.append([
                item.get("fact_id", ""),
                str(item.get("repository_value", "")),
                item.get("file", ""),
                str(item.get("line", ""))
            ])

        output += format_table(headers, rows) + "\n"

    return output


def format_circular_entries(circulars: list[dict]) -> str:
    """
    Format new circulars table.

    Args:
        circulars: List of new circular dictionaries with keys:
                   'date', 'title', 'source', 'matched_keywords', 'potentially_affects'

    Returns:
        Formatted Markdown section with table
    """
    if not circulars:
        return ""

    output = "## Section 4: New Circulars / Announcements\n\n"
    headers = ["Date", "Title", "Source", "Matched Keywords", "Potentially Affects"]
    rows = []

    for item in circulars:
        date = str(item.get("date", ""))
        title = item.get("title", "")
        source = item.get("source", "")
        keywords = ", ".join(item.get("matched_keywords", []))
        affects = ", ".join(item.get("potentially_affects", []))

        rows.append([date, title, source, keywords, affects])

    output += format_table(headers, rows) + "\n"
    return output


def format_metadata(metadata: dict) -> str:
    """
    Format the verification metadata section.

    Args:
        metadata: Dictionary with keys:
                  'version', 'run_date', 'run_time', 'urls_checked',
                  'facts_verified', 'internal_links_checked', 'circular_sources_checked'

    Returns:
        Formatted Markdown metadata section
    """
    output = "## Section 5: Verification Metadata\n\n"

    output += f"- Pipeline version: {metadata.get('version', 'unknown')}\n"
    output += f"- Run date: {metadata.get('run_date', 'unknown')}\n"
    output += f"- Run time: {metadata.get('run_time', 'unknown')}\n"
    output += f"- URLs checked: {metadata.get('urls_checked', 0)} (unique)\n"
    output += f"- Facts verified: {metadata.get('facts_verified', 0)}\n"
    output += f"- Internal links checked: {metadata.get('internal_links_checked', 0)}\n"
    output += f"- Circular sources checked: {metadata.get('circular_sources_checked', 0)}\n"

    return output


def wrap_collapsible(title: str, content: str) -> str:
    """
    Wrap content in <details><summary> tags for collapsible sections.

    Args:
        title: Summary text shown when collapsed
        content: Content to show when expanded

    Returns:
        HTML details/summary block
    """
    return f"<details><summary>{title}</summary>\n\n{content}\n\n</details>\n"
