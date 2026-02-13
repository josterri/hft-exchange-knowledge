#!/usr/bin/env python3
"""
run_all.py - Daily Verification Pipeline Orchestrator

Runs all verification checks sequentially and generates a unified report.
Designed for daily GitHub Actions execution and manual local runs.

Exit Codes:
    0: PASS - All checks passed
    1: WARNINGS - Minor issues detected
    2: ACTION REQUIRED - Critical issues detected
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import all verification modules
try:
    from check_links import LinkChecker
    from check_crossrefs import CrossRefValidator
    from check_facts import FactChecker
    from monitor_circulars import CircularMonitor
    from generate_report import ReportGenerator
except ImportError as e:
    print(f"ERROR: Failed to import verification modules: {e}", file=sys.stderr)
    print("Ensure all verification scripts are in the same directory.", file=sys.stderr)
    sys.exit(2)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_checks_argument(checks_arg: str) -> List[str]:
    """
    Parse the --checks argument into a list of check names.

    Args:
        checks_arg: Comma-separated string or 'all'

    Returns:
        List of check names

    Raises:
        ValueError: If invalid check name provided
    """
    valid_checks = {'links', 'crossrefs', 'facts', 'circulars'}

    if checks_arg.lower() == 'all':
        return list(valid_checks)

    requested = [c.strip().lower() for c in checks_arg.split(',')]
    invalid = set(requested) - valid_checks

    if invalid:
        raise ValueError(f"Invalid check names: {', '.join(invalid)}. "
                        f"Valid options: {', '.join(valid_checks)}, all")

    return requested


def determine_repo_root(script_path: Path) -> Path:
    """
    Determine repository root (2 levels up from script location).

    Args:
        script_path: Path to this script

    Returns:
        Path to repository root
    """
    # scripts/verification/run_all.py -> repo root is 2 levels up
    return script_path.parent.parent.parent


def load_config(config_path: Optional[Path], script_dir: Path) -> Dict:
    """
    Load configuration file.

    Args:
        config_path: Explicit path to config, or None for auto-detect
        script_dir: Directory containing this script

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
    """
    if config_path is None:
        config_path = script_dir / 'config.yaml'

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_check(
    check_name: str,
    config: Dict,
    repo_root: Path,
    output_dir: Path,
    registry_path: Optional[Path],
    dry_run: bool,
    logger: logging.Logger
) -> Tuple[Optional[Dict], float]:
    """
    Run a single verification check.

    Args:
        check_name: Name of check to run
        config: Configuration dictionary
        repo_root: Repository root path
        output_dir: Directory for output files
        registry_path: Path to fact registry (for facts check)
        dry_run: Whether to skip HTTP requests
        logger: Logger instance

    Returns:
        Tuple of (result_dict, elapsed_time_seconds)
    """
    start_time = time.time()
    result = None

    try:
        if check_name == 'links':
            logger.info("Running URL validation...")
            checker = LinkChecker(config=config, repo_root=repo_root, registry_path=registry_path)
            result = checker.run()
            output_file = output_dir / 'links_result.json'

        elif check_name == 'crossrefs':
            logger.info("Running cross-reference validation...")
            validator = CrossRefValidator(config=config, repo_root=repo_root)
            result = validator.run()
            output_file = output_dir / 'crossrefs_result.json'

        elif check_name == 'facts':
            logger.info("Running fact verification...")
            if registry_path is None:
                logger.warning("No registry path provided for fact checking, skipping")
                return None, time.time() - start_time
            checker = FactChecker(
                config=config,
                repo_root=repo_root,
                registry_path=registry_path
            )
            result = checker.run()
            output_file = output_dir / 'facts_result.json'

        elif check_name == 'circulars':
            logger.info("Running circular monitoring...")
            state_dir = Path(__file__).parent / '.state'
            monitor = CircularMonitor(
                config=config,
                state_dir=state_dir
            )
            result = monitor.run()
            output_file = output_dir / 'circulars_result.json'

        else:
            logger.error(f"Unknown check: {check_name}")
            return None, time.time() - start_time

        # Write result to JSON file
        if result is not None:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Wrote results to {output_file}")

    except Exception as e:
        logger.error(f"Check '{check_name}' failed with exception: {e}", exc_info=True)
        result = None

    elapsed = time.time() - start_time
    logger.info(f"Check '{check_name}' completed in {elapsed:.2f}s")

    return result, elapsed


def determine_overall_status(results: Dict[str, Optional[Dict]]) -> str:
    """
    Determine overall pipeline status from check results.

    Args:
        results: Dictionary of check results

    Returns:
        Status string: 'PASS', 'WARNINGS', or 'ACTION REQUIRED'
    """
    has_critical = False
    has_warnings = False

    for check_name, result in results.items():
        if result is None:
            has_critical = True
            continue

        status = result.get('status', 'UNKNOWN')
        if status == 'ACTION REQUIRED':
            has_critical = True
        elif status == 'WARNINGS':
            has_warnings = True

    if has_critical:
        return 'ACTION REQUIRED'
    elif has_warnings:
        return 'WARNINGS'
    else:
        return 'PASS'


def print_summary(
    results: Dict[str, Optional[Dict]],
    timings: Dict[str, float],
    total_time: float,
    report_path: Path,
    logger: logging.Logger
) -> None:
    """
    Print execution summary to stdout.

    Args:
        results: Dictionary of check results
        timings: Dictionary of execution times per check
        total_time: Total elapsed time
        report_path: Path to generated report
        logger: Logger instance
    """
    print("\n" + "="*50)
    print("=== Verification Pipeline Complete ===")
    print("="*50)

    mins, secs = divmod(int(total_time), 60)
    print(f"Total time: {mins:02d}:{secs:02d}")
    print()

    # Per-check summaries
    if 'links' in results:
        r = results['links']
        if r:
            total = r.get('summary', {}).get('total_urls', 0)
            failures = r.get('summary', {}).get('failures', 0)
            print(f"Links: {total} checked, {failures} failures")

    if 'crossrefs' in results:
        r = results['crossrefs']
        if r:
            total = r.get('summary', {}).get('total_refs', 0)
            broken = r.get('summary', {}).get('broken', 0)
            print(f"CrossRefs: {total} checked, {broken} broken")

    if 'facts' in results:
        r = results['facts']
        if r:
            total = r.get('summary', {}).get('total_facts', 0)
            issues = r.get('summary', {}).get('issues', 0)
            print(f"Facts: {total} checked, {issues} issues")

    if 'circulars' in results:
        r = results['circulars']
        if r:
            sources = r.get('summary', {}).get('sources_checked', 0)
            new_relevant = r.get('summary', {}).get('new_relevant', 0)
            print(f"Circulars: {sources} sources, {new_relevant} new relevant")

    print()
    overall = determine_overall_status(results)
    print(f"Overall: {overall}")
    print(f"Report: {report_path}")
    print("="*50)


def get_exit_code(overall_status: str) -> int:
    """
    Determine exit code from overall status.

    Args:
        overall_status: Overall pipeline status

    Returns:
        Exit code (0, 1, or 2)
    """
    if overall_status == 'PASS':
        return 0
    elif overall_status == 'WARNINGS':
        return 1
    else:
        return 2


def main() -> int:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Daily Verification Pipeline for hft-exchange-knowledge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run all checks
  %(prog)s --checks links                     # URL validation only
  %(prog)s --checks links,crossrefs           # Multiple checks
  %(prog)s --dry-run                          # Parse without HTTP requests
  %(prog)s --verbose --output-dir ./results   # Verbose with custom output
        """
    )

    parser.add_argument(
        '--checks',
        default='all',
        help='Checks to run: all, links, crossrefs, facts, circulars (comma-separated)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('reports'),
        help='Directory for result files (default: reports)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to config.yaml (default: auto-detect)'
    )
    parser.add_argument(
        '--registry',
        type=Path,
        help='Path to fact_registry.yaml (default: auto-detect)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse markdown and build lists, but skip HTTP requests'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Parse checks argument
        checks_to_run = parse_checks_argument(args.checks)
        logger.info(f"Checks to run: {', '.join(checks_to_run)}")

        # Determine paths
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent
        repo_root = determine_repo_root(script_path)

        logger.info(f"Repository root: {repo_root}")
        logger.info(f"Script directory: {script_dir}")

        # Load configuration
        config = load_config(args.config, script_dir)
        logger.info("Configuration loaded")

        # Determine registry path
        registry_path = args.registry
        if registry_path is None and 'facts' in checks_to_run:
            registry_path = script_dir / 'fact_registry.yaml'
            if not registry_path.exists():
                logger.warning(f"Registry not found at {registry_path}")
                registry_path = None

        # Create output directory
        output_dir = args.output_dir
        if not output_dir.is_absolute():
            output_dir = repo_root / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Run checks sequentially
        pipeline_start = time.time()
        results = {}
        timings = {}

        for check_name in checks_to_run:
            result, elapsed = run_check(
                check_name=check_name,
                config=config,
                repo_root=repo_root,
                output_dir=output_dir,
                registry_path=registry_path,
                dry_run=args.dry_run,
                logger=logger
            )
            results[check_name] = result
            timings[check_name] = elapsed

        total_time = time.time() - pipeline_start

        # Generate unified report
        logger.info("Generating unified report...")
        try:
            report_gen = ReportGenerator(
                config=config,
                output_dir=output_dir
            )
            exit_code = report_gen.run(
                links_result=results.get('links', {}),
                crossrefs_result=results.get('crossrefs', {}),
                facts_result=results.get('facts', {}),
                circulars_result=results.get('circulars', {})
            )
            report_path = output_dir / 'latest-report.md'
            logger.info(f"Report generated: {report_path}")
        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            report_path = output_dir / 'latest-report.md'

        # Determine overall status
        overall_status = determine_overall_status(results)

        # Print summary to stdout
        print_summary(results, timings, total_time, report_path, logger)

        # Return appropriate exit code
        return get_exit_code(overall_status)

    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        return 2


if __name__ == '__main__':
    sys.exit(main())
