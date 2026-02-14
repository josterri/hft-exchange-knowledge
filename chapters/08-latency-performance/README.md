---
layout: default
title: "8. Latency & Performance"
nav_order: 8
parent: Chapters
---

# Chapter 8: Latency & Performance

## Introduction

Latency represents the fundamental competitive advantage in high-frequency trading on Deutsche Boerse's T7 platform. The difference between a profitable market-making operation and an unprofitable one can be measured in single-digit microseconds. Understanding T7's latency characteristics, throughput capacity, measurement infrastructure, and performance evolution is essential for participants designing systems that compete effectively in modern electronic markets.

This chapter examines T7's latency metrics from network ingress to market data distribution, explores the timestamp infrastructure that enables sub-nanosecond precision, analyzes throughput capacity under extreme conditions, and traces the architectural improvements that have reduced latency while increasing determinism. By understanding these performance characteristics, participants can optimize their trading infrastructure, evaluate connectivity options, and design strategies that leverage T7's performance envelope.

## Latency Metrics

### Order Request to Response Latency

The median latency for order request to response via Partition-Specific (PS) gateways measures less than 55 microseconds (µs). This metric captures the round-trip time from when an order enters the gateway until the matching engine's acknowledgment or execution report returns to the participant. As of 2019 baseline measurements, the overall median latency from timestamp t_3n (gateway entry) to t_4 (matching engine receipt) measured 56 µs across all products. For high-frequency sessions on options, the median reached 54 µs, while futures high-frequency sessions achieved 53 µs. *(Source: [T7 High-speed Trading Solution](https://deutsche-boerse.com/dbg-en/our-company/insights-corporate-en/T7-high-speed-trading-solution-for-derivatives-and-cash-products-1621640))*

This sub-60-microsecond performance positions T7 among the world's lowest-latency exchange platforms, comparable to major US futures exchanges and significantly faster than many equity trading venues.

### Order to Market Data Latency

The latency from order execution to market data publication on Xetra measures approximately 40 µs in the median. This metric represents the time between when a match occurs in the Matching Engine and when the resulting market data message appears on EOBI (Enhanced Order Book Interface) or EMDI (Enhanced Market Data Interface) feeds. The sub-40-microsecond market data latency ensures that participants receiving market data feeds observe executions with minimal delay, supporting algorithmic strategies that depend on rapid market data processing for signal generation and order decision logic. *(Source: [T7 Open Day 2019 Presentation](https://www.deutsche-boerse.com/resource/blob/1637232/da0ae611905acda0d7502260903a0835/data/Open-Day-2019_T7-Latency-Roadmap_Andreas-Lohr_final.pdf))*

### EOBI vs ETI Response Latency

A critical architectural characteristic of T7 is that EOBI market data is published before ETI (Enhanced Trading Interface) execution responses reach the order originator. In production measurements from 13 February 2025, EOBI market data was in the median 1.5 µs faster than ETI responses. This timing relationship reflects T7's "public data first" principle: market participants observing EOBI feeds see order book changes and executions before the participant who submitted the order receives their private execution report. *(Source: [Insights into Trading System Dynamics - March 2025](https://www.eurex.com/resource/blob/48918/4f724c9415d2731cfb27295db6269c9c/data/presentation-insights-into-trading-system-dynamics.pdf))*

EOBI send times are typically measured before gateway send time of responses, ensuring that public market transparency precedes private execution notification. This design prevents information asymmetries where order originators would possess execution knowledge before the broader market observes price changes.

### Minimum Reaction Time

T7's minimum reaction time—the fastest observed latency between measurement points t_9d (EOBI network TAP outbound) and t_3a (network TAP inbound)—measures 2,787 nanoseconds (ns), or approximately 2.8 µs. This figure represents the theoretical minimum latency achievable under optimal conditions with minimal queueing, contention, or processing overhead. Around 10 trading participants demonstrate reaction times of less than 2,830 ns for the most actively traded products, indicating the presence of highly optimized trading systems capable of detecting market data changes and submitting orders within single-digit microseconds. *(Source: [Insights into Trading System Dynamics - March 2025](https://www.eurex.com/resource/blob/48918/4f724c9415d2731cfb27295db6269c9c/data/presentation-insights-into-trading-system-dynamics.pdf))*

These sub-3-microsecond reaction times encompass the entire cycle of receiving EOBI market data, processing the message, making a trading decision, constructing an order message, and transmitting it to the exchange. Achieving such performance requires kernel bypass networking (DPDK or similar), in-memory processing, optimized trading logic, and co-located infrastructure.

### Gateway Latency Differences

Different gateway types introduce varying latency characteristics based on their routing architecture and processing requirements.

**PS Gateway Latency**: Partition-Specific gateways provide the lowest-latency access path to T7. Since H1 2021, PS gateways have been co-located with matching engines on the same physical server, eliminating inter-server network hops and reducing latency by several microseconds. This consolidation creates the shortest possible path from network interface to matching logic. *(Source: [T7 Architecture Factsheet](https://deutsche-boerse.com/resource/blob/320052/a4d10931561b1cdeb0a68f177826f785/Factsheet_T7-data.pdf))*

**LF Gateway Latency**: Low-Frequency (LF) gateways, which provide multi-partition access through a single session, historically introduced approximately 75 µs of additional latency compared to PS gateways. However, recent performance optimizations have dramatically reduced this gap. As of January 2025, LF gateways add approximately 12 µs compared to PS gateways for same-partition requests. For cross-partition requests (operations requiring coordination across partitions), latency has decreased from approximately 45 µs in January 2025 to approximately 1 µs after optimization. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

These improvements make LF gateways increasingly viable for participants requiring multi-partition access without the operational complexity of managing multiple PS gateway connections.

**Redundancy Link Latency**: The redundancy link connecting Room A and Room B for failover purposes introduces more than 50 µs of additional latency when active. Under normal operations, this link carries state replication traffic without affecting trading latency. However, if the primary network path between rooms fails, the redundancy link serves as an emergency backup, introducing this latency penalty. Participants should account for increased latency during redundancy link usage when designing failover strategies. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

## Throughput and Capacity

### Peak Message Rate

T7 demonstrated its capacity to handle extreme message volumes in June 2024, achieving a peak message rate of 201,000 messages per second across the entire platform. Within this aggregate rate:

- **Eurex derivatives**: 118,000 messages/second (recorded on March 13, 2024)
- **Xetra cash equities**: 92,000 messages/second (recorded on April 16, 2024)

These figures represent actual production loads during high-volatility trading conditions, demonstrating T7's ability to sustain performance under stress. The platform's capacity headroom ensures that even during exceptional market events (macroeconomic announcements, volatility spikes, index rebalancing), participants experience consistent latency and throughput. *(Source: [T7 Architecture Factsheet](https://deutsche-boerse.com/resource/blob/320052/a4d10931561b1cdeb0a68f177826f785/Factsheet_T7-data.pdf))*

### Daily Transaction Capacity

T7 supports over 320 million transactions per day across all connected trading venues. This capacity encompasses order submissions, modifications, cancellations, executions, and market data events. On April 7, 2025, T7 processed 1.25 billion daily requests, a significant increase from 857 million in 2023. This volume distributed as:

- **Eurex**: 460 million requests
- **Xetra**: 759 million requests

The growth in request volumes reflects increased algorithmic trading activity, market maker competition, and expanded product offerings. T7's ability to scale to 1.25 billion daily requests without degradation demonstrates the robustness of its partition-based architecture and processing infrastructure. *(Source: [T7 Architecture Factsheet](https://deutsche-boerse.com/resource/blob/320052/a4d10931561b1cdeb0a68f177826f785/Factsheet_T7-data.pdf))*

### Per-Session Throughput Limits

T7 enforces per-session throughput limits based on session type to manage load distribution and ensure fair access:

| Session Type | Maximum Throughput |
|--------------|-------------------|
| HF Full | 150 transactions/second (TPS) |
| HF Light | 50 transactions/second (TPS) |
| LF Sessions | Lower than HF (exact limits vary by configuration) |

These limits apply per session, allowing participants to scale capacity by establishing multiple sessions. High-frequency market makers typically establish multiple HF Full sessions to accommodate their order flow requirements. *(Source: T7 Enhanced Trading Interface specification)*

### Partition-Level Message Rates

Individual partitions within T7 handle substantial message volumes. In April 2025, one Xetra partition reached 20,000 messages per second, compared to 14,000 messages/second in the same period of 2024. This 43% year-over-year increase reflects growing trading activity and highlights the importance of Deutsche Boerse's dynamic product redistribution across partitions to maintain balanced load. *(Source: [T7 Architecture Factsheet](https://deutsche-boerse.com/resource/blob/320052/a4d10931561b1cdeb0a68f177826f785/Factsheet_T7-data.pdf))*

## Timestamp Precision and Infrastructure

T7 provides participants with access to multiple high-precision timestamps for every order, execution, and market data event. This timestamp infrastructure enables precise latency measurement, regulatory compliance, and forensic analysis of trading activity.

### Timestamp Measurement Points

T7 captures timestamps at multiple points in the order processing pipeline, identified by standardized codes:

| Timestamp Code | Location | Description |
|----------------|----------|-------------|
| t_3a | Network TAP inbound | Packet arrival at gateway network interface (entry point) |
| t_3d | Network TAP outbound | Packet departure from gateway network interface (exit point) |
| t_3n | Gateway processing entry | Order message entry into gateway application logic |
| t_4 | Matching engine receipt | Order arrival at matching engine |
| t_5 | Matching engine output | Execution result generation |
| t_7 | Market data generation | Market data message creation |
| t_8 | Market data send | Market data message transmission to distribution layer |
| t_9 | EOBI send | EOBI message transmission to network |
| t_9d | Network TAP for EOBI outbound | EOBI packet departure at network interface |

Passive network TAPs at three strategic locations capture every packet entering and leaving the system, providing independent verification of message timing. These TAPs operate without introducing latency or packet loss, ensuring accurate measurement without affecting trading operations. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

### Timestamp Precision Levels

**Nanosecond Resolution**: T7 provides timestamps with sub-nanosecond resolution. Network timestamps (t_3a, t_3d, t_9d) are synchronized using White Rabbit technology with approximately 1 ns quality. Packets are timestamped with sub-nanosecond resolution and nanosecond accuracy, enabling precise latency analysis and regulatory reporting. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

**High Precision Timestamp (HPT) Service**: Participants can access the High Precision Timestamp service, which provides timestamps t_3a, t_3d, and t_9d for their orders and market data messages. This service enables participants to measure their own end-to-end latency, identify bottlenecks in their processing pipelines, and verify Deutsche Boerse's published latency statistics. *(Source: [Deutsche Boerse Time Services](https://www.deutsche-boerse.com/dbg-en/markets-services/ps-technology/ps-7-market-technology/ps-n7/ps-connectivity-services-time-services))*

**ETI Timestamp Fields**: The Enhanced Trading Interface includes specific timestamp fields for regulatory and operational purposes:

- **RequestTime (Field 5979)**: Client-provided timestamp indicating when the order was created
- **TrdRegTSPrevTimePriority**: Previous trade reporting timestamp for priority determination
- **TrdRegTSTimePriority**: Trade reporting timestamp for MiFID II compliance

These fields support participants in meeting their regulatory timestamp obligations. *(Source: ETI Specification)*

### Time Synchronization Technologies

**Precision Time Protocol (PTP)**: T7 originally used PTP (IEEE 1588) for time synchronization, achieving ±50 ns standard accuracy. After the 2024 technology refresh, PTP accuracy improved to 4-5 ns RMS consistently. This improvement resulted from server hardware upgrades and the implementation of a hybrid PTP + SyncE (Synchronous Ethernet) architecture. *(Source: [Tech Refresh 2024](https://www.deutsche-boerse.com/resource/blob/4126486/21cc046dd9eea5655f2b7ce17500f673/data/Tech%20Refreshes.pdf))*

**White Rabbit**: White Rabbit technology, developed at CERN for particle physics experiments, provides sub-nanosecond time synchronization accuracy (less than 1 ns). Deutsche Boerse employs White Rabbit for network timestamp capture at TAP points, ensuring that measurements of participant latency and system processing time achieve the highest possible precision. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

**GPS Time Signal**: Deutsche Boerse's time services include GPS time signals with sub-microsecond accuracy, providing a globally synchronized time reference for participants' trading infrastructure. This service enables participants to synchronize their own trading servers, market data processors, and logging systems with exchange time, ensuring consistency in timestamp analysis and regulatory reporting. *(Source: [Deutsche Boerse Time Services](https://www.deutsche-boerse.com/dbg-en/markets-services/ps-technology/ps-7-market-technology/ps-n7/ps-connectivity-services-time-services))*

### MiFID II Timestamp Requirements

Under MiFID II regulations, high-frequency trading firms must maintain timestamp precision of at least 100 µs for order lifecycle events. T7's nanosecond-level timestamp precision exceeds this requirement by more than five orders of magnitude, providing participants with significant compliance headroom. The availability of multiple timestamps (t_3a, t_3n, t_4, etc.) enables participants to demonstrate precise order timing for regulatory audits and best execution reporting. *(Source: MiFID II Regulatory Technical Standards)*

## Latency Evolution and Improvements

T7's latency performance has improved continuously through architectural optimizations, hardware upgrades, and protocol enhancements. Understanding this evolution provides insight into Deutsche Boerse's commitment to maintaining competitive latency while increasing system capacity and determinism.

### Technology Refresh 2024

In 2024, Deutsche Boerse executed a comprehensive technology refresh of T7's infrastructure, delivering multiple performance improvements:

**Network Architecture Migration**: The system migrated from InfiniBand to Ethernet networking. While InfiniBand provided low latency, Ethernet's maturity, commodity availability, and industry standardization enabled greater flexibility and cost efficiency without sacrificing performance. The migration maintained latency profiles while improving network manageability. *(Source: [Tech Refresh 2024](https://www.deutsche-boerse.com/resource/blob/4126486/21cc046dd9eea5655f2b7ce17500f673/data/Tech%20Refreshes.pdf))*

**Server Hardware Upgrade**: Matching engine servers were upgraded from dual 12-core processors to dual 32-core processors. This increase in core count enabled greater parallelization of matching logic, risk checking, and market data generation, improving throughput without increasing latency. The new processors also feature larger cache sizes and higher clock speeds, reducing per-instruction latency. *(Source: [Tech Refresh 2024](https://www.deutsche-boerse.com/resource/blob/4126486/21cc046dd9eea5655f2b7ce17500f673/data/Tech%20Refreshes.pdf))*

**NUMA Optimization**: The gateway, matching engine, and market data publisher processes now fit within a single NUMA (Non-Uniform Memory Access) domain. This co-location within a single memory domain eliminates cross-NUMA memory access latency, reducing cache coherency overhead and improving processing determinism. NUMA optimization is particularly important for high-frequency workloads where microsecond-level latency variations can affect strategy performance. *(Source: [Tech Refresh 2024](https://www.deutsche-boerse.com/resource/blob/4126486/21cc046dd9eea5655f2b7ce17500f673/data/Tech%20Refreshes.pdf))*

**Time Synchronization Enhancement**: The hybrid PTP + SyncE implementation improved clock synchronization accuracy from ±50 ns to 4-5 ns RMS. This improvement ensures that timestamp measurements across distributed system components maintain nanosecond-level consistency, enhancing latency measurement precision and supporting fair market access. *(Source: [Tech Refresh 2024](https://www.deutsche-boerse.com/resource/blob/4126486/21cc046dd9eea5655f2b7ce17500f673/data/Tech%20Refreshes.pdf))*

### Key Release Milestones

**Release 6.0**: Introduced partition-specific FIFO gateways, creating dedicated entry points for each partition. This change eliminated queueing contention across partitions, improving latency determinism and enabling participants to optimize connectivity for their specific product focus. *(Source: T7 Release Notes)*

**Release 7.0**: Extended EOBI coverage to all Eurex products, providing participants with a unified, low-latency market data interface across derivatives markets. This release also established PS gateways as the single low-latency entry point for high-frequency participants, clarifying connectivity architecture and simplifying optimization strategies. *(Source: T7 Release Notes)*

**H1 2021 Co-Location**: The consolidation of PS gateways with matching engines on the same physical server represented a pivotal architectural change, eliminating inter-server network latency and reducing order processing latency by several microseconds. This optimization specifically benefits high-frequency participants using PS gateway connections. *(Source: [T7 High-speed Trading Solution](https://deutsche-boerse.com/dbg-en/our-company/insights-corporate-en/T7-high-speed-trading-solution-for-derivatives-and-cash-products-1621640))*

**Release 14.0 (November 2025)**: Introduced Sponsored Access functionality, enabling brokers to offer their clients direct market access while maintaining control over risk management. This release also included TLS 1.3 support alongside existing TLS 1.2 connectivity. TLS 1.2 will be decommissioned in simulation environments on March 13, 2026, and in production on April 27, 2026 (Release 14.1), requiring participants to upgrade their encryption implementations. *(Source: T7 Release Notes)*

**Release 14.1 (May 2026 - Planned)**: Will introduce five new ETI order management requests with optimized field layouts designed specifically for latency reduction. By streamlining message structures and eliminating unnecessary fields, these new requests will reduce serialization overhead and network transmission time, providing additional microsecond-level latency improvements. *(Source: T7 Roadmap)*

### Latency Roadmap Philosophy

Deutsche Boerse's latency roadmap emphasizes two complementary goals: reducing absolute latency and improving latency determinism. As stated in Deutsche Boerse's public presentations, "Low and deterministic latency means reduced risk for customers." The target is constant low latency, especially under high load conditions, rather than simply achieving the lowest possible latency under ideal conditions. *(Source: [T7 Open Day 2023 - Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

This philosophy drives architectural decisions:

- **More deterministic network infrastructure**: Adoption of 10 Gbit/s latency-optimized networks with minimal jitter
- **FIFO processing guarantees**: Partition-specific gateways process orders strictly in arrival order
- **Single low-latency entry point**: PS gateways provide a clearly defined, optimized path for high-frequency participants
- **Load balancing**: Dynamic product redistribution across partitions prevents any single partition from becoming a bottleneck

These design principles ensure that participants can depend on consistent latency profiles when designing strategies, reducing the risk of unexpected latency spikes that could result in adverse selection or missed trading opportunities.

## Determinism and Fairness

### CoLo 2.0 Latency-Optimized Network

The Co-Location 2.0 (CoLo 2.0) infrastructure provides a highly deterministic 10 Gbit/s network environment designed to ensure equal network access for all co-located participants. The network architecture eliminates latency variance between participants' racks and the matching engines, creating a "level playing field" where competitive advantage derives from algorithmic sophistication and execution efficiency rather than from preferential network placement. *(Source: [Cash Market Co-location Services](https://www.cashmarket.deutsche-boerse.com/cash-en/Data-Tech/Technology/co-location-services))*

### FIFO Processing Guarantees

T7's partition-specific FIFO processing model ensures that orders arriving at a gateway are processed in strict temporal sequence. Earlier orders receive priority over later orders at the same price level, regardless of the participant submitting them. This deterministic processing model supports fairness principles and enables participants to design strategies that depend on predictable execution behavior. *(Source: T7 Architecture documentation)*

### No Artificial Delays or Speed Bumps

T7 does not implement artificial delays, speed bumps, or order processing throttles designed to slow down high-frequency trading. All orders are processed as rapidly as possible in arrival sequence, without intentional delays. This design contrasts with some trading venues that introduce deliberate latency mechanisms to discourage certain trading strategies. Deutsche Boerse's approach reflects a commitment to efficient price discovery and market liquidity provision, recognizing that high-frequency market makers contribute to tight spreads and deep order books. *(Source: [T7 Latency Roadmap](https://www.deutsche-boerse.com/resource/blob/3690194/fe6b01b1e14800eb40374a95516debf2/data/Open%20Day%202023%20-%20Presentation,%20T7-Latency%20Roadmap.pdf))*

### Public Data First Principle

T7's "public data first" principle ensures that EOBI market data reflecting order book changes and executions is published before execution reports reach the originating participant. As documented earlier, EOBI messages are in the median 1.5 µs faster than ETI execution responses. This architectural guarantee prevents information asymmetries and ensures that all market participants, regardless of their connectivity status or subscription choices, observe the same market state simultaneously. *(Source: [Insights into Trading System Dynamics - March 2025](https://www.eurex.com/resource/blob/48918/4f724c9415d2731cfb27295db6269c9c/data/presentation-insights-into-trading-system-dynamics.pdf))*

### Equal Network Access for Co-Located Participants

All co-located participants connect to PS gateways through infrastructure designed to provide equal latency. Network cable lengths, switch configurations, and routing policies are standardized to eliminate preferential access. This equality ensures that smaller participants can compete effectively with larger institutions, supporting market diversity and competition. *(Source: [Cash Market Co-location Services](https://www.cashmarket.deutsche-boerse.com/cash-en/Data-Tech/Technology/co-location-services))*

## Monitoring and Transparency

### High Precision Timestamp File Service

Deutsche Boerse provides participants with access to High Precision Timestamp files containing timestamps t_3a (network TAP inbound), t_3d (network TAP outbound), and t_9d (EOBI network TAP outbound) for their trading activity. Participants can use these files to:

- **Measure end-to-end latency**: Calculate the time from market data observation (t_9d) to order submission (t_3a)
- **Identify internal bottlenecks**: Detect delays in their own trading infrastructure by comparing their internal timestamps with exchange timestamps
- **Verify Deutsche Boerse's latency metrics**: Independently confirm published latency statistics
- **Support regulatory compliance**: Demonstrate precise order timing for MiFID II and other regulatory reporting requirements

The HPT service enables participants to continuously monitor their latency performance and identify degradation or unexpected delays that could affect strategy profitability. *(Source: [Deutsche Boerse Time Services](https://www.deutsche-boerse.com/dbg-en/markets-services/ps-technology/ps-7-market-technology/ps-n7/ps-connectivity-services-time-services))*

### Published Latency Statistics

Deutsche Boerse regularly publishes latency statistics at Open Day presentations and through public documentation. These statistics include median latencies, percentile distributions, and minimum observed latencies across different market segments and session types. This transparency enables participants to:

- **Benchmark their infrastructure**: Compare their observed latencies against exchange-published figures
- **Evaluate connectivity options**: Assess the latency impact of different gateway types and session configurations
- **Plan infrastructure investments**: Determine whether additional optimization (such as upgrading to PS gateways or implementing kernel bypass networking) would provide meaningful latency improvements

The publication of latency statistics represents Deutsche Boerse's commitment to transparency and supports informed decision-making by market participants. *(Source: [T7 Open Day 2019 Presentation](https://www.deutsche-boerse.com/resource/blob/1637232/da0ae611905acda0d7502260903a0835/data/Open-Day-2019_T7-Latency-Roadmap_Andreas-Lohr_final.pdf))*

### Time Services

Deutsche Boerse offers comprehensive time services to support participants' infrastructure synchronization requirements:

**GPS Time Signal**: Provides sub-microsecond accuracy time reference for participants' trading servers, market data processors, and logging systems. GPS synchronization ensures global time consistency across geographically distributed trading operations.

**PTP/White Rabbit Distribution**: Participants can receive PTP or White Rabbit time signals directly from Deutsche Boerse's infrastructure, eliminating the need for independent GPS receivers and ensuring alignment with exchange time references.

These services enable participants to maintain nanosecond-level time synchronization with T7, supporting precise latency measurement, regulatory compliance, and coordinated trading across multiple venues. *(Source: [Deutsche Boerse Time Services](https://www.deutsche-boerse.com/dbg-en/markets-services/ps-technology/ps-7-market-technology/ps-n7/ps-connectivity-services-time-services))*

## Optimization Strategies for Participants

### Co-Location Placement

Co-locating trading infrastructure at Equinix FR2 Frankfurt represents the single most effective latency optimization. By eliminating wide-area network latency (typically 10-50 milliseconds for European connections), co-location reduces round-trip order latency to tens of microseconds. For strategies sensitive to microsecond-level latency (market making, statistical arbitrage, latency arbitrage), co-location is effectively mandatory for competitiveness.

### PS Gateway vs LF Gateway Selection

Participants should evaluate their trading patterns when selecting gateway types:

**Choose PS Gateways when:**
- Trading focuses on products within a single partition
- Latency requirements are critical (every microsecond matters)
- Message rates exceed 50 TPS per product group
- Strategy depends on sub-40-microsecond execution latency

**Choose LF Gateways when:**
- Trading spans multiple partitions
- Operational simplicity is prioritized over lowest possible latency
- Additional 12 µs latency is acceptable for multi-partition access
- Strategy does not require sub-60-microsecond execution

Given the recent improvements reducing LF gateway latency to approximately 12 µs overhead, more participants may find LF gateways suitable for their needs, particularly when trading across multiple product groups.

### Kernel Bypass Networking

Participants achieving sub-3-microsecond reaction times (as observed in T7's minimum reaction time statistics) employ kernel bypass networking technologies such as DPDK (Data Plane Development Kit) or Solarflare OpenOnload. These technologies eliminate operating system overhead in network packet processing, reducing application-to-network latency from tens of microseconds to hundreds of nanoseconds. Kernel bypass requires specialized development expertise but provides essential performance for ultra-low latency strategies.

### Market Data Processing Optimization

Subscribing to EOBI provides the lowest-latency market data feed, with EOBI messages published before ETI execution responses. Participants should prioritize EOBI processing over EMDI when latency is critical, as EOBI's streamlined message format and publication sequence provide microsecond-level advantages. Optimizing EOBI parsing, multicast reception, and message handling can reduce signal detection latency and improve overall strategy performance.

### Session and Connection Management

Establishing multiple sessions enables participants to scale throughput and implement redundancy:

- **Multiple PS gateway sessions**: Distribute order flow across multiple sessions to overcome per-session 150 TPS limits
- **Dual-side connectivity**: Connect to both Side A and Side B infrastructure for failover capability
- **Market Reset handling**: Implement rapid order resubmission logic to minimize downtime after Market Reset events

Effective session management ensures that participants maintain performance during normal operations and recover rapidly from system disruptions.

## Conclusion

T7's latency and performance characteristics represent the culmination of continuous architectural evolution, hardware optimization, and operational refinement. With median order-to-response latencies below 55 µs, order-to-market-data latencies around 40 µs, and minimum reaction times approaching 2.8 µs, T7 provides a competitive platform for high-frequency trading strategies across cash equities and derivatives markets.

The platform's throughput capacity—supporting peak message rates exceeding 201,000 messages/second and daily transaction volumes over 1.25 billion requests—ensures that performance remains consistent even during extreme market conditions. The timestamp infrastructure, featuring nanosecond-level precision via White Rabbit and PTP synchronization, enables precise latency measurement and regulatory compliance.

Deutsche Boerse's commitment to deterministic latency, reflected in FIFO processing guarantees, CoLo 2.0 infrastructure, and the "public data first" principle, supports market fairness and provides participants with predictable execution behavior. The continuous latency improvements—from LF gateway optimization to PS gateway co-location with matching engines—demonstrate an ongoing focus on maintaining T7's competitiveness in the global landscape of ultra-low latency trading venues.

For participants designing trading infrastructure, understanding T7's latency envelope, timestamp measurement points, throughput limits, and optimization opportunities is essential for achieving competitive execution speeds. The following chapter will examine risk controls and pre-trade checks, which operate within this microsecond-level latency budget while providing comprehensive market protection and participant safety mechanisms.

---

[Previous: Chapter 7 - Market Models & Microstructure](../07-market-models/README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [Next: Chapter 9 - Risk Controls](../09-risk-controls/README.md)
