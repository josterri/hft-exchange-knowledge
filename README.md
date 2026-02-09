# Deutsche Boerse HFT Exchange Knowledge Base

A comprehensive, open-source tutorial and reference guide for understanding Deutsche Boerse Group's trading technology infrastructure -- covering the T7 trading platform, trading interfaces (ETI, FIX), market data feeds (EOBI, EMDI, MDI, RDI), co-location services, latency characteristics, market models, risk controls, and regulatory framework.

## Who Is This For?

- **Quantitative traders** evaluating Deutsche Boerse as a trading venue
- **Trading system developers** building connectivity to Xetra or Eurex
- **Fintech professionals** seeking to understand European exchange infrastructure
- **Students and researchers** studying market microstructure

## Source Policy

All content in this repository is sourced **exclusively** from publicly available Deutsche Boerse Group websites:

- [deutsche-boerse.com](https://www.deutsche-boerse.com)
- [eurex.com](https://www.eurex.com)
- [xetra.com](https://www.xetra.com)
- [cashmarket.deutsche-boerse.com](https://www.cashmarket.deutsche-boerse.com)
- [eurexchange.com](https://www.eurexchange.com)
- [developer.deutsche-boerse.com](https://developer.deutsche-boerse.com)

No proprietary, non-public, or third-party information is included.

## How to Use This Repository

Start with Chapter 1 for an overview of Deutsche Boerse Group, then progress through the chapters sequentially. Each chapter builds on previous knowledge. Use the appendix for quick reference and terminology lookup.

See [Table of Contents](TABLE_OF_CONTENTS.md) for the full chapter listing.

## Note on "HTP"

This tutorial covers what is commonly referred to as "high-throughput" trading at Deutsche Boerse. There is no specific protocol called "HTP" (High-Throughput Protocol) in Deutsche Boerse's documentation. The actual high-throughput trading stack consists of:

- **ETI (Enhanced Trading Interface)** -- native binary protocol for low-latency order entry
- **EOBI (Enhanced Order Book Interface)** -- lowest-latency full-depth market data feed
- **EMDI (Enhanced Market Data Interface)** -- aggregated depth-of-book market data

These interfaces are covered comprehensively in Chapters 4, 5, and 8.

## License

This work is licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All contributions must cite official Deutsche Boerse Group sources.
