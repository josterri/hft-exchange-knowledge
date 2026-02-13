"""
Main report generator that reads verification result JSON files and produces a unified Markdown report.

This module combines results from URL validation, cross-reference checking, fact verification,
and circular monitoring into a comprehensive daily verification report with actionable insights.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.report_formatter import (
    format_circular_entries,
    format_crossref_failures,
    format_fact_issues,
    format_link_failures,
    format_metadata,
    format_summary_table,
    format_table,
    wrap_collapsible,
)


class ReportGenerator:
    """Generates unified verification reports from multiple checker results."""

    def __init__(self, config: dict, output_dir: Path):
        """
        Initialize the report generator.

        Args:
            config: Configuration dictionary with pipeline settings
            output_dir: Directory where reports will be written
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        links_result: dict,
        crossrefs_result: dict,
        facts_result: dict,
        circulars_result: dict,
    ) -> int:
        """
        Generate comprehensive report from all verification results.

        Args:
            links_result: URL validation results
            crossrefs_result: Cross-reference checking results
            facts_result: Fact verification results
            circulars_result: Circular monitoring results

        Returns:
            Exit code: 0=PASS, 1=WARNINGS, 2=ACTION REQUIRED
        """
        # Combine all results
        combined_results = {
            "links": links_result,
            "crossrefs": crossrefs_result,
            "facts": facts_result,
            "circulars": circulars_result,
        }

        # Determine overall status
        status, exit_code = self._determine_overall_status(combined_results)

        # Generate report content
        report_date = datetime.utcnow().strftime("%Y-%m-%d")
        report_content = self._build_report(combined_results, report_date, status)

        # Write latest report
        latest_report = self.output_dir / "latest-report.md"
        latest_report.write_text(report_content, encoding="utf-8")

        # Archive combined JSON results
        json_archive = self.output_dir / f"{report_date}.json"
        json_archive.write_text(
            json.dumps(combined_results, indent=2), encoding="utf-8"
        )

        print(f"Report generated: {latest_report}")
        print(f"JSON archive: {json_archive}")
        print(f"Overall status: {status} (exit code: {exit_code})")

        return exit_code

    def _determine_overall_status(self, results: dict) -> tuple[str, int]:
        """
        Determine overall verification status and exit code.

        Args:
            results: Combined results from all checkers

        Returns:
            Tuple of (status_string, exit_code)
        """
        # Check for critical failures
        links = results.get("links", {})
        crossrefs = results.get("crossrefs", {})
        facts = results.get("facts", {})
        circulars = results.get("circulars", {})

        # Critical: 404s, changed facts, broken cross-refs, needs_update
        link_failures = links.get("failures", [])
        critical_link_failures = [
            f
            for f in link_failures
            if f.get("status_code") in [404, 500, 502, 503, 504]
            or "domain" in f.get("error", "").lower()
            or "timeout" in f.get("error", "").lower()
        ]

        crossref_failures = crossrefs.get("failures", [])

        fact_details = facts.get("details", [])
        changed_facts = [f for f in fact_details if f.get("issue_type") == "changed"]
        needs_update_facts = [
            f for f in fact_details if f.get("issue_type") == "needs_update"
        ]

        # Check for any critical failures
        has_critical = (
            len(critical_link_failures) > 0
            or len(crossref_failures) > 0
            or len(changed_facts) > 0
            or len(needs_update_facts) > 0
        )

        if has_critical:
            return "ACTION REQUIRED", 2

        # Check for warnings
        redirect_failures = [
            f
            for f in link_failures
            if f.get("status_code") in [301, 302, 303, 307, 308]
        ]
        pdf_updates = [
            f for f in link_failures if "pdf" in f.get("error", "").lower()
        ]

        stale_facts = [f for f in fact_details if f.get("issue_type") == "stale"]
        approaching_facts = [
            f for f in fact_details if f.get("issue_type") == "approaching_deadline"
        ]

        new_circulars = circulars.get("new_circulars", [])

        has_warnings = (
            len(redirect_failures) > 0
            or len(pdf_updates) > 0
            or len(stale_facts) > 0
            or len(approaching_facts) > 0
            or len(new_circulars) > 0
        )

        if has_warnings:
            return "WARNINGS", 1

        # All good
        return "PASS", 0

    def _build_report(
        self, results: dict, report_date: str, overall_status: str
    ) -> str:
        """
        Build the complete Markdown report.

        Args:
            results: Combined verification results
            report_date: Date string for report header
            overall_status: Overall status string (PASS/WARNINGS/ACTION REQUIRED)

        Returns:
            Complete Markdown report content
        """
        report = f"# Daily Verification Report - {report_date}\n\n"

        # Summary section
        report += "## Summary\n\n"
        report += format_summary_table(results)
        report += f"\n## Overall Status: **{overall_status}**\n\n"
        report += "---\n\n"

        # Section 1: Broken Links
        link_failures = results.get("links", {}).get("failures", [])
        if link_failures:
            report += format_link_failures(link_failures)

            # Add collapsible section for all checked URLs
            all_urls = results.get("links", {}).get("checked_urls", [])
            if all_urls:
                url_list = "\n".join(
                    [f"- {url.get('url', '')} ({url.get('status_code', 'N/A')})" for url in all_urls]
                )
                report += wrap_collapsible(
                    f"All checked URLs ({len(all_urls)} total)", url_list
                )
                report += "\n"

        # Section 2: Cross-Reference Issues
        crossref_failures = results.get("crossrefs", {}).get("failures", [])
        if crossref_failures:
            report += format_crossref_failures(crossref_failures)

        # Section 3: Fact Verification Issues
        fact_details = results.get("facts", {}).get("details", [])
        if fact_details:
            report += format_fact_issues(fact_details)

        # Section 4: New Circulars
        new_circulars = results.get("circulars", {}).get("new_circulars", [])
        if new_circulars:
            report += format_circular_entries(new_circulars)

        # Section 5: Metadata
        metadata = self._build_metadata(results)
        report += format_metadata(metadata)

        return report

    def _build_metadata(self, results: dict) -> dict:
        """
        Build metadata dictionary from results and config.

        Args:
            results: Combined verification results

        Returns:
            Metadata dictionary
        """
        # Extract statistics
        link_stats = results.get("links", {}).get("statistics", {})
        fact_stats = results.get("facts", {}).get("statistics", {})
        crossref_stats = results.get("crossrefs", {}).get("statistics", {})
        circular_stats = results.get("circulars", {}).get("statistics", {})

        # Get run information from any result that has it
        run_date = None
        run_time = None

        for result in [
            results.get("links"),
            results.get("crossrefs"),
            results.get("facts"),
            results.get("circulars"),
        ]:
            if result and result.get("metadata"):
                metadata = result["metadata"]
                if not run_date:
                    run_date = metadata.get("run_date")
                if not run_time:
                    run_time = metadata.get("run_time")

        if not run_date:
            run_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return {
            "version": self.config.get("version", "1.0.0"),
            "run_date": run_date,
            "run_time": run_time or "N/A",
            "urls_checked": link_stats.get("total_unique_urls", 0),
            "facts_verified": fact_stats.get("total_facts", 0),
            "internal_links_checked": crossref_stats.get("total_references", 0),
            "circular_sources_checked": circular_stats.get("sources_checked", 0),
        }


def load_results(results_dir: Path) -> tuple[dict, dict, dict, dict]:
    """
    Load all verification result JSON files from a directory.

    Args:
        results_dir: Directory containing result JSON files

    Returns:
        Tuple of (links_result, crossrefs_result, facts_result, circulars_result)

    Note:
        Missing files are handled gracefully with empty placeholder dictionaries.
    """
    results_dir = Path(results_dir)

    # Default empty structures
    empty_links = {
        "failures": [],
        "checked_urls": [],
        "statistics": {
            "total_unique_urls": 0,
            "failed_urls": 0,
            "redirects": 0,
            "pdf_updates": 0,
        },
    }

    empty_crossrefs = {
        "failures": [],
        "statistics": {"total_references": 0, "valid_references": 0},
    }

    empty_facts = {
        "details": [],
        "statistics": {
            "total_facts": 0,
            "verified": 0,
            "changed": 0,
            "stale": 0,
            "needs_update": 0,
        },
    }

    empty_circulars = {
        "new_circulars": [],
        "statistics": {"sources_checked": 0, "new_relevant_circulars": 0},
    }

    # Try to load each file
    def load_json_safe(file_path: Path, default: dict) -> dict:
        if file_path.exists():
            try:
                return json.loads(file_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")
                return default
        else:
            print(f"Warning: File not found: {file_path}, using empty result")
            return default

    links_result = load_json_safe(
        results_dir / "links-result.json", empty_links
    )
    crossrefs_result = load_json_safe(
        results_dir / "crossrefs-result.json", empty_crossrefs
    )
    facts_result = load_json_safe(
        results_dir / "facts-result.json", empty_facts
    )
    circulars_result = load_json_safe(
        results_dir / "circulars-result.json", empty_circulars
    )

    return links_result, crossrefs_result, facts_result, circulars_result


def main():
    """CLI entry point for report generation."""
    parser = argparse.ArgumentParser(
        description="Generate unified verification report from checker results"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/verification.yaml"),
        help="Path to configuration file (default: config/verification.yaml)",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("."),
        help="Directory containing result JSON files (default: current directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory to write reports to (default: reports/)",
    )

    args = parser.parse_args()

    # Load configuration
    config = {}
    if args.config.exists():
        try:
            import yaml

            config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: Could not load config from {args.config}: {e}")
            config = {"version": "1.0.0"}
    else:
        print(f"Warning: Config file not found: {args.config}, using defaults")
        config = {"version": "1.0.0"}

    # Load results
    print(f"Loading results from {args.results_dir}...")
    links, crossrefs, facts, circulars = load_results(args.results_dir)

    # Generate report
    generator = ReportGenerator(config, args.output_dir)
    exit_code = generator.run(links, crossrefs, facts, circulars)

    return exit_code


if __name__ == "__main__":
    exit(main())
