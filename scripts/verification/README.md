# Daily Verification Pipeline

Automated daily verification system for the [hft-exchange-knowledge](https://github.com/josterri/hft-exchange-knowledge) repository. Ensures all facts, numbers, links, and regulatory references remain correct and up-to-date.

## Overview

This pipeline runs daily via GitHub Actions (06:00 UTC) and checks:

1. **URL Validation** - All 350+ URLs across 33 markdown files are checked for availability, redirects, soft 404s, and PDF document changes
2. **Cross-Reference Validation** - All internal markdown links, anchors, TOC coverage, and back-links are verified
3. **Fact Verification** - Pricing, latency metrics, dates, and regulatory references are verified against source documents
4. **Circular Monitoring** - Deutsche Boerse/Eurex circular and announcement pages are monitored for new content affecting the repository

## Prerequisites

- Python 3.11+
- pip

## Installation

```bash
cd scripts/verification
pip install -r requirements.txt
```

## Usage

### Run Full Pipeline

```bash
python run_all.py
```

### Run Specific Checks

```bash
python run_all.py --checks links           # URL validation only
python run_all.py --checks crossrefs        # Cross-reference validation only
python run_all.py --checks facts            # Fact verification only
python run_all.py --checks circulars        # Circular monitoring only
python run_all.py --checks links,crossrefs  # Multiple checks
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--checks` | Checks to run (all, links, crossrefs, facts, circulars) | `all` |
| `--output-dir` | Directory for reports | `reports` |
| `--config` | Path to config.yaml | Auto-detect |
| `--registry` | Path to fact_registry.yaml | Auto-detect |
| `--verbose` | Enable verbose logging | Off |
| `--dry-run` | Parse files without HTTP requests | Off |

### Run via GitHub Actions

The pipeline runs automatically daily at 06:00 UTC. To trigger manually:

1. Go to Actions tab in the repository
2. Select "Daily Verification Pipeline"
3. Click "Run workflow"
4. Optionally select which checks to run

## Configuration

Edit `config.yaml` to customize:

- **approved_domains**: Deutsche Boerse domains to check against
- **rate_limits**: HTTP request rate per domain (default: 2 req/s)
- **retry**: Retry count and backoff settings
- **circular_sources**: URLs for circular/announcement monitoring
- **circular_keywords**: Keywords for filtering relevant circulars
- **notifications**: GitHub Issue and webhook settings

## Fact Registry

The `fact_registry.yaml` contains every verifiable fact in the repository.

### Schema

```yaml
- id: "pricing-eurex-colo-emdi-monthly"
  category: pricing          # urls|pricing|latency|session_limits|dates|contacts|regulatory
  value: "6000"
  unit: "EUR/month"
  file: "chapters/appendix/pricing-summary.md"
  line: 50
  context: "CoLo 2.0 EMDI | 6,000"
  source_url: "https://..."
  source_document: "Eurex Circular 104/25"
  effective_date: "2026-01-01"
  last_verified: "2026-02-13"
  verification_method: "manual"   # manual | automated | pdf_text_check
  pdf_text_extractable: null      # true | false | null
  notes: ""
```

### Adding New Facts

1. Run the registry builder to discover new candidates:
   ```bash
   python build_registry.py --scan-all --output fact_registry.yaml --merge
   ```
2. Review new entries (marked `verification_method: unreviewed`)
3. Set appropriate `verification_method` for each
4. Run verification to test: `python run_all.py --checks facts`

## Report Format

Reports are written to `reports/latest-report.md` (overwritten each run) and archived as `reports/YYYY-MM-DD.json`.

### Status Levels

| Status | Meaning | Exit Code |
|--------|---------|-----------|
| **PASS** | All checks passed | 0 |
| **WARNINGS** | Minor issues (redirects, approaching deadlines) | 1 |
| **ACTION REQUIRED** | Critical issues (broken links, changed facts) | 2 |

## Architecture

```
scripts/verification/
  run_all.py              # Orchestrator
  config.yaml             # Configuration
  requirements.txt        # Python dependencies
  fact_registry.yaml      # Verifiable facts database
  build_registry.py       # Semi-automated registry builder
  check_links.py          # URL validation
  check_crossrefs.py      # Internal link validation
  check_facts.py          # Fact verification
  monitor_circulars.py    # Circular monitoring
  generate_report.py      # Report generation
  .state/                 # Runtime state (gitignored)
  utils/
    __init__.py
    http_client.py        # Rate-limited HTTP client
    markdown_parser.py    # Markdown parsing utilities
    report_formatter.py   # Report formatting
    github_issues.py      # GitHub Issue formatting
```

## Troubleshooting

### Rate Limiting
Deutsche Boerse pages may rate-limit requests. The pipeline uses a conservative 2 req/s limit with exponential backoff. If you get persistent timeouts, try reducing the rate in `config.yaml`.

### PDF Parsing Failures
Some Deutsche Boerse PDFs use image-based content that cannot be text-extracted. These are marked `pdf_text_extractable: false` in the registry and fall back to content hash comparison.

### DNS Issues
All Deutsche Boerse domains resolve to the same CDN. If DNS fails, check your network connectivity.

### GitHub Actions Failures
If the pipeline fails in GitHub Actions but works locally, it may be due to IP-based rate limiting of GitHub-hosted runners. Consider using a self-hosted runner.

## Maintenance

- **New content added**: Update `fact_registry.yaml` with new facts and URLs
- **Annual price list update** (January): Pipeline detects via circular monitor; update pricing chapter and registry
- **T7 release**: Pipeline detects via circular monitor; update release history and affected chapters
- **Quarterly**: Update Python dependencies, review parsers, archive old reports

## License

Part of the [hft-exchange-knowledge](https://github.com/josterri/hft-exchange-knowledge) project. CC BY-SA 4.0.
