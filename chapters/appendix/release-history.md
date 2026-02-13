# Appendix: T7 Release History

## Overview

The T7 trading platform represents Deutsche Börse's continuous evolution toward ultra-low latency electronic trading. Since its initial launch in December 2012, T7 has undergone systematic enhancement through biannual releases, each addressing specific performance, regulatory, or capacity requirements. For HFT participants, understanding this release history provides crucial context for architectural decisions, timing system upgrades, and anticipating future capabilities.

This appendix chronicles the major T7 releases and their significance for high-frequency trading operations.

## T7 Major Release Timeline

| Release | Date | Key Features for HFT |
|---------|------|---------------------|
| **T7 1.0** | Dec 2012 | Initial T7 launch on Eurex, replacing legacy Eurex system. Introduced modern microservice architecture with separate order book management per product. Baseline latency ~50-100 µs. |
| **T7 2.0** | Jun 2013 | Xetra migration to T7 platform, consolidating cash and derivatives markets on unified technology stack. Market data standardization across asset classes. |
| **T7 3.0** | 2014 | Enhanced market data distribution. EOBI (Enhanced Order Book Interface) introduction providing UDP multicast market data with improved granularity and lower latency than legacy protocols. |
| **T7 5.0** | 2015 | Symmetric Multi-Processing (SMP) introduction, enabling parallel order book processing across multiple CPU cores. Partitioning scheme introduced to isolate high-volume products. Performance improvements reducing minimum latency to ~20-30 µs range. |
| **T7 6.0** | Nov 2016 | MiFID II preparation features including algorithmic order flagging support. Enhanced order routing capabilities. Pre-trade risk controls enhanced for regulatory compliance. |
| **T7 7.0** | Jun 2017 | Full MiFID II compliance deployment. RTS 25 timestamp synchronization requirements (100 µs accuracy). Order-to-trade ratio monitoring tools. Transaction reporting enhancements. |
| **T7 8.0** | Dec 2018 | Post-MiFID II operational enhancements. Performance optimizations following regulatory implementation. Enhanced monitoring and surveillance capabilities. |
| **T7 9.0** | Nov 2019 | **FIX LF (Low Latency FIX) introduction**, replacing legacy FIX Gateway with modern FIX 5.0 SP2 implementation. Partition structure improvements increasing capacity per partition. Enhanced market maker protection schemes. |
| **T7 10.0** | Nov 2020 | TSL (Trade Size Limit) enhancements providing finer-grained risk controls. New partition structure supporting increased product density. Latency improvements to ~10-15 µs minimum range. |
| **T7 10.1** | Jun 2021 | **PS Gateway consolidation with matching engine** on same physical server, eliminating inter-server network hops and reducing latency by ~5-8 µs. TSL Clearing Member controls for enhanced risk management. Session management improvements. |
| **T7 11.0** | Nov 2021 | Significant performance optimizations across order processing pipeline. Capacity increases supporting higher message rates per partition. Memory architecture improvements reducing cache misses. |
| **T7 11.1** | Jun 2022 | ETI password encryption security enhancements. Short Code solution 2.0 providing improved product identification for algorithmic trading. Order routing optimizations. |
| **T7 12.0** | Nov 2023 | **EOBI and EMDI publisher integration into matching engine process**, eliminating separate publisher process and reducing market data latency by ~4 µs. Unified order request types simplifying protocol usage. MOV (Minimum Order Value) enhancements supporting risk controls. |
| **T7 12.1** | Jun 2024 | **Static volatility interruptions** (activated Jul 8, 2024) providing predictable circuit breaker behavior. Partition expansion from 5 to 6 partitions supporting capacity growth. **Xetra Midpoint** launch (Dec 2024) for continuous midpoint matching. |
| **T7 13.0** | May 2024 | Further performance optimizations in matching engine core logic. Improved order book update efficiency. Enhanced session management reducing reconnection latency. |
| **T7 13.1** | Nov 2024 | **Tech Refresh 2024**: Hardware upgrade to latest Intel Xeon Scalable processors. PTP synchronization improvements achieving 4-5 ns RMS jitter (down from ~10 ns). Capacity upgrades supporting 2x message throughput. Memory bandwidth improvements. |
| **T7 14.0** | Nov 2025 | **SMP enhancements with Cross Partition (CP) mode becoming default** (Dec 1, 2025), enabling automatic load balancing across partitions. New ETI order entry request types (CreateOrderRequest, ModifyOrderRequest) replacing legacy formats. ESU (Entry Service Unit) passive/aggressive traffic split for improved latency predictability. |
| **T7 14.1** | May 2026 (planned) | **TLS 1.2 decommissioning** (TLS 1.3 only) for enhanced security. **Mandatory migration** to new ETI order request types. Quote Request Solution supporting RFQ workflows. Auction Volume Discovery mechanism for institutional block trading. |

## Key Architectural Milestones

### Phase 1: Platform Foundation (2012-2014)
**Initial T7 deployment** replaced Deutsche Börse's legacy trading systems with a modern, scalable architecture. The migration from the legacy Eurex system to T7 1.0 in December 2012 represented a fundamental shift toward microservice-based design, with separate order book managers per product and centralized risk management.

The **Xetra migration** to T7 2.0 in June 2013 unified cash and derivatives markets on a single technology platform, enabling consistent market data protocols and cross-asset strategies.

**EOBI introduction** in T7 3.0 (2014) provided HFT participants with UDP multicast market data offering superior latency characteristics compared to legacy TCP-based protocols.

### Phase 2: Performance & Scalability (2015-2018)
**SMP (Symmetric Multi-Processing) introduction** in T7 5.0 (2015) represented a pivotal architectural enhancement. By enabling parallel processing across multiple CPU cores through partitioning, SMP dramatically improved throughput capacity while maintaining deterministic latency. This allowed high-volume products to be isolated on dedicated partitions, preventing cross-product interference.

**MiFID II compliance** (T7 6.0-8.0, 2016-2018) introduced regulatory features including algorithmic order flagging, RTS 25 timestamp synchronization (100 µs accuracy requirement), and enhanced surveillance capabilities. While primarily regulatory-driven, these releases established infrastructure still relevant for HFT operations today.

### Phase 3: Latency Optimization (2019-2023)
**FIX LF (Low Latency FIX) launch** in T7 9.0 (November 2019) replaced the legacy FIX Gateway with a modern FIX 5.0 SP2 implementation offering significantly lower latency and improved session management. This provided an alternative protocol to ETI for participants requiring FIX compatibility.

**PS Gateway consolidation** in T7 10.1 (June 2021) eliminated a critical latency bottleneck by co-locating the participant gateway with the matching engine on the same physical server. This removed inter-server network hops, reducing round-trip latency by approximately 5-8 µs.

**EOBI/EMDI integration into matching engine process** in T7 12.0 (November 2023) represented another major architectural refinement. By eliminating the separate market data publisher process and generating EOBI messages directly within the matching engine, Deutsche Börse reduced market data latency by approximately 4 µs—a substantial improvement for latency-sensitive strategies.

### Phase 4: Modern Platform (2024-2026)
**Tech Refresh 2024** (T7 13.1, November 2024) brought comprehensive hardware upgrades including latest-generation Intel Xeon processors, improved memory subsystems, and enhanced PTP synchronization achieving 4-5 ns RMS jitter. Combined with software optimizations, this enabled **minimum reaction times below 3 µs** for optimal conditions.

**CoLo 2.0 network infrastructure** deployment (2024-2025) upgraded interconnect fabric with higher bandwidth switches and improved PTP distribution, supporting the platform's evolution toward sub-microsecond latency targets.

**SMP Cross Partition (CP) mode becoming default** in T7 14.0 (December 2025) represents a maturation of the partitioning architecture, enabling automatic load balancing while maintaining latency predictability. The new ETI order request types introduced in this release provide cleaner protocol semantics and improved processing efficiency.

**TLS 1.3 mandatory migration** in T7 14.1 (May 2026) reflects ongoing security modernization while maintaining performance through hardware-accelerated cryptography.

## Performance Evolution

T7's performance trajectory demonstrates systematic latency reduction through architectural refinement:

| Period | Typical Minimum Latency | Key Enablers |
|--------|------------------------|--------------|
| **2012-2014** | 50-100 µs | Initial architecture, single-core processing |
| **2015-2016** | 20-30 µs | SMP introduction, partitioning |
| **2017-2019** | 10-20 µs | Software optimizations, FIX LF launch |
| **2020-2021** | 8-12 µs | PS Gateway consolidation |
| **2022-2023** | 5-8 µs | EOBI integration, matching engine optimizations |
| **2024-present** | 2.5-5 µs | Tech Refresh 2024, hardware upgrades, software refinements |

**Current state** (T7 13.1/14.0, 2024-2025): Under optimal conditions with low order book depth and favorable partition load, minimum gateway-to-gateway reaction times below 3 µs are achievable. Typical latency for most trading scenarios ranges 5-10 µs, with median latency around 8-12 µs depending on product complexity and order type.

**Critical insight for HFT participants**: Latency improvements have increasingly derived from **architectural refinements** (PS Gateway consolidation, EOBI integration, SMP enhancements) rather than raw hardware upgrades. Understanding these architectural changes enables participants to optimize strategies around T7's specific design characteristics.

## Release Cadence & Planning

Deutsche Börse maintains a **biannual release schedule**:
- **Major releases** (November): Significant features, architectural changes, capacity upgrades
- **Minor releases** (May/June): Enhancements, optimizations, regulatory updates

**Implications for HFT participants**:
- **Testing windows**: 3-4 weeks pre-production testing before each release
- **Backward compatibility**: Generally maintained for at least two release cycles
- **Mandatory migrations**: Communicated 12+ months in advance (e.g., TLS 1.3, new ETI request types)
- **Performance testing**: Pre-release performance metrics published for capacity planning

**Recommended practice**: Maintain compatibility with current and next release to ensure smooth transitions during production upgrades.

## Looking Forward

Future T7 development priorities (based on public roadmap communications):
- **Sub-microsecond latency targets**: Continued optimization toward sub-1 µs minimum latency for specific scenarios
- **Enhanced capacity**: Supporting higher message rates per partition as algorithmic trading volumes grow
- **FPGA acceleration**: Potential hardware offload for specific matching engine functions
- **Market data compression**: Improved EOBI efficiency for bandwidth optimization
- **Risk control granularity**: Finer-grained pre-trade controls with minimal latency impact

The T7 platform's evolutionary trajectory demonstrates Deutsche Börse's commitment to maintaining competitive latency while supporting increasing capacity and regulatory requirements. For HFT participants, staying informed about release schedules and architectural roadmaps enables proactive adaptation to platform capabilities.

[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
