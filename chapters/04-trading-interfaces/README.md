# Chapter 4: Trading Interfaces

## Introduction

Deutsche Boerse's T7 trading platform provides multiple trading interfaces to accommodate diverse participant needs, ranging from ultra-low latency high-frequency trading to traditional institutional order flow. Each interface represents a strategic architectural choice that balances latency performance, protocol complexity, development effort, and operational flexibility. Understanding these interfaces and their technical characteristics is fundamental for any participant designing connectivity to Eurex derivatives markets or Xetra cash equities.

This chapter examines the trading interface landscape available on T7, comparing performance characteristics, session types, protocol specifications, and use cases for each connectivity option. The choice of trading interface directly impacts latency, message throughput, development complexity, and operational infrastructure requirements, making it one of the most critical architectural decisions for trading firms.

## Interface Landscape

T7 provides three primary trading interfaces, each optimized for different participant profiles and trading requirements:

| Interface | Protocol | Latency | Max TPS | Typical Use Case |
|-----------|----------|---------|---------|------------------|
| ETI (Enhanced Trading Interface) | Proprietary binary | Lowest (<55 µs order-to-response) | 250 (HF Ultra) | HFT, market making, proprietary trading |
| FIX Gateway | FIX 4.2 / 4.4 | Moderate (protocol translation overhead) | LF rates | Traditional institutional, buy-side |
| T7 GUI | HTTPS/Web | Highest (manual interaction) | Manual rates | Manual trading, monitoring, administration |

The latency values shown represent median order request-to-response times under optimal conditions. Actual latency depends on network connectivity, co-location status, session type, and system load. The maximum transactions per second (TPS) values reflect the highest throughput session types available for each interface.

## ETI (Enhanced Trading Interface) Overview

The Enhanced Trading Interface (ETI) represents T7's native, high-performance trading protocol. ETI is a proprietary binary protocol designed for maximum performance, providing the lowest-latency access path to T7 matching engines.

### Protocol Characteristics

**Binary Protocol with FIX Semantics**: ETI employs a custom binary encoding format while maintaining semantic alignment with FIX 5.0 Service Pack 2 (SP2). This design provides the performance advantages of binary serialization (compact message size, minimal parsing overhead) while leveraging familiar FIX semantics for field definitions and message structures. Participants familiar with FIX workflows can map their business logic to ETI with relative ease, despite the different wire format. *(Source: [Eurex ETI Documentation](https://www.eurex.com))*

**Little-Endian Byte Ordering**: ETI messages use little-endian byte ordering (least significant byte first), matching x86/x64 processor architectures. This alignment eliminates byte-swapping overhead on the predominant server platforms used for algorithmic trading, contributing to lower processing latency. *(Source: [ETI Technical Specification](https://www.eurex.com))*

**TemplateID-Based Message Identification**: Each ETI message type is identified by a unique TemplateID field in the message header. Participants use TemplateID to route incoming messages to appropriate handlers and to construct outgoing messages with the correct structure. This template-based approach enables efficient message dispatch and validation. *(Source: [ETI Message Structure](https://www.eurex.com))*

**Asynchronous Message-Based Interface**: ETI operates as an asynchronous protocol where participants can send multiple requests without waiting for responses. The matching engine processes orders in FIFO sequence and returns responses asynchronously. This design supports maximum throughput and allows participants to pipeline order submissions for optimal performance. *(Source: [ETI Protocol Overview](https://www.eurex.com))*

### Session Types and Throughput

ETI supports multiple session types differentiated by maximum throughput, partition access, and pricing. As of T7 Release 14.0, the following session types are available:

**High-Frequency Light (HF Light)**
- Maximum throughput: 50 transactions per second (TPS)
- Partition access: Single partition via PS gateway
- Monthly fee: EUR 250 per session
- Use case: Entry-level HF trading, strategies with moderate message rates, or participants testing HF infrastructure before scaling to higher-throughput sessions. *(Source: [Eurex Pricing](https://www.eurex.com))*

**High-Frequency Full (HF Full)**
- Maximum throughput: 150 transactions per second (TPS)
- Partition access: Single partition via PS gateway
- Monthly fee: EUR 500 per session
- Use case: Active market making, high-frequency trading strategies with substantial order flow. *(Source: [Eurex Pricing](https://www.eurex.com))*

**High-Frequency Ultra (HF Ultra)**
- Maximum throughput: 250 transactions per second (TPS)
- Partition access: Single partition via PS gateway
- Monthly fee: EUR 1,000 per session
- Use case: Ultra-high-frequency market making, quote-driven strategies generating maximum message rates. *(Source: [Eurex Pricing](https://www.eurex.com))*

**Low-Frequency (LF)**
- Maximum throughput: Moderate (exact limit not published but significantly lower than HF sessions)
- Partition access: Multi-partition via LF gateway
- Monthly fee: Lower cost structure (fees vary by service configuration)
- Use case: Buy-side participants, multi-partition trading strategies, back-office systems requiring access to all partitions without managing multiple HF sessions. *(Source: [Eurex Pricing](https://www.eurex.com))*

**Back-Office**
- Throughput: Administrative operations (drop copy, risk events, trade confirmations)
- Partition access: Multi-partition
- Use case: Subset of LF functionality focused on post-trade and risk management workflows rather than active order entry. *(Source: [ETI Session Types](https://www.eurex.com))*

### Maximum ETI Sessions Per Participant

Since June 2024, T7 supports a maximum of 600 ETI trading sessions per participant. This limit provides substantial capacity for large trading organizations operating multiple strategies, desks, or algorithmic systems, while ensuring that system resources are allocated fairly across all participants. Participants requiring more than 600 concurrent sessions must coordinate with Deutsche Boerse to evaluate infrastructure capacity and potential accommodations. *(Source: [Eurex ETI Session Limits](https://www.eurex.com))*

### Transport and Security

**TCP/IP with TLS 1.3 Encryption**: ETI sessions operate over TCP/IP connections with mandatory TLS 1.3 encryption. TLS 1.3 provides confidentiality, integrity, and forward secrecy for all messages transmitted between participants and T7 infrastructure. TLS 1.3's performance improvements over earlier TLS versions (reduced handshake latency, optimized cipher suites) minimize encryption overhead, ensuring that security does not significantly impact latency. *(Source: [ETI Security](https://www.eurex.com))*

**TLS 1.2 Decommissioning**: Deutsche Boerse plans to decommission TLS 1.2 support with T7 Release 14.1 (scheduled for May 18, 2026). After this date, only TLS 1.3 will be supported for ETI connections. Participants must ensure their trading systems support TLS 1.3 and complete migration before the decommissioning date to avoid connectivity interruptions. *(Source: [Eurex Technical Notices](https://www.eurex.com))*

### Detailed ETI Coverage

For comprehensive technical details on ETI protocol structure, message flows, session lifecycle management, and implementation guidance, see [ETI Deep Dive](eti.md).

## FIX Gateway Overview

The FIX Gateway provides an alternative trading interface for participants preferring industry-standard FIX (Financial Information eXchange) protocol connectivity. FIX Gateway support was introduced in T7 Release 10.0 (March 2021), expanding T7's accessibility to participants with existing FIX infrastructure.

### Protocol Support

FIX Gateway supports two widely deployed FIX versions:

**FIX 4.2**: The most widely deployed FIX version globally, supported by virtually all FIX-enabled trading systems and order management systems (OMS). FIX 4.2 provides core order entry, execution reporting, and session management functionality. *(Source: [FIX Trading Community](https://www.fixtrading.org))*

**FIX 4.4**: An evolution of FIX 4.2 with additional message types, enhanced precision for decimal fields, and improved extensibility. FIX 4.4 supports more complex order types and market data structures compared to FIX 4.2. *(Source: [FIX Trading Community](https://www.fixtrading.org))*

Participants select the FIX version during session configuration based on their trading system capabilities and business requirements.

### Protocol Translation Architecture

FIX Gateway operates as a protocol translation layer, converting FIX messages to ETI binary format before routing them to T7 matching engines. This translation occurs at the gateway layer and adds minimal latency overhead. The architecture flow is as follows:

1. Participant sends FIX order message (e.g., NewOrderSingle) to FIX Gateway
2. FIX Gateway validates FIX message structure and maps fields to ETI equivalents
3. FIX Gateway constructs ETI binary message and routes to appropriate PS gateway (via LF gateway infrastructure)
4. PS gateway forwards ETI message to matching engine
5. Matching engine processes order and generates ETI response
6. FIX Gateway receives ETI response and translates back to FIX format
7. FIX Gateway sends FIX execution report to participant

This bidirectional translation ensures that participants interact exclusively with FIX protocol while T7 maintains its native ETI processing internally. *(Source: [T7 FIX Gateway Architecture](https://www.eurex.com))*

### Performance Characteristics

**Latency Overhead**: FIX Gateway introduces protocol translation overhead compared to native ETI connections. The translation process adds latency due to FIX parsing, field mapping, and ETI message construction. While Deutsche Boerse has optimized the translation layer, participants should expect higher latency compared to native ETI connections. Exact latency differences vary based on message complexity and system load. *(Source: [T7 FIX Gateway Performance](https://www.eurex.com))*

**Routing via LF Gateways**: FIX sessions route through LF gateways to reach PS gateways, inheriting the latency characteristics of LF gateway infrastructure. Recent performance improvements to LF gateways (reducing cross-partition latency to approximately 1 microsecond) have improved FIX Gateway latency, making it more competitive for medium-frequency trading strategies. *(Source: [T7 Gateway Performance](https://www.eurex.com))*

**Throughput**: FIX sessions support LF throughput rates, making them suitable for traditional buy-side trading, algorithmic strategies with moderate message rates, and institutional order flow. FIX sessions are not recommended for high-frequency market making or strategies requiring HF session throughput. *(Source: [T7 FIX Gateway](https://www.eurex.com))*

### Use Cases

**Existing FIX Infrastructure**: Participants with established FIX-based order management systems, execution management systems, or multi-asset trading platforms can connect to T7 without developing custom ETI adapters. This accelerates time-to-market and reduces development costs.

**Industry-Standard Protocol Preference**: Some institutional participants mandate FIX protocol usage for consistency across trading venues, operational simplicity, and vendor independence. FIX Gateway enables these participants to access T7 markets while maintaining their FIX-centric architecture.

**Multi-Venue Connectivity**: Participants connecting to multiple global exchanges often prefer FIX protocol for consistency. Using FIX for T7 connectivity aligns with their broader connectivity architecture, simplifying configuration management, monitoring, and troubleshooting.

### Detailed FIX Gateway Coverage

For detailed information on FIX message specifications, session management, field mappings to ETI, and implementation examples, see [FIX Gateway Deep Dive](fix-gateway.md).

## T7 GUI (Graphical User Interface)

T7 GUI provides web-based trading interfaces for manual trading, order monitoring, risk management, and administrative operations. The GUI is not designed for algorithmic or high-frequency trading but serves critical operational and oversight roles.

### Available GUI Applications

**Eurex Trader GUI**: Web-based trading interface for Eurex derivatives markets, supporting manual order entry, quote submission, order book visualization, and portfolio monitoring. Eurex Trader GUI is suitable for discretionary traders, risk managers, and operations staff requiring human-readable market views. *(Source: [Eurex Trader GUI](https://www.eurex.com))*

**T7 Admin GUI**: Administrative interface for managing ETI sessions, configuring risk parameters (Advanced Risk Protection, Post-Trade Risk limits), viewing drop copy messages, and accessing trade confirmations. T7 Admin GUI provides operational control for participant administrators and compliance officers. *(Source: [T7 Admin GUI](https://www.eurex.com))*

### Access and Technology

**Protocol**: HTTPS (HTTP over TLS) with web browser access
**Latency**: High (manual interaction involves human response times, rendering delays, and network round-trips)
**Suitable for**: Manual trading, order monitoring, risk management, operational administration

T7 GUI applications do not expose APIs for automated trading and are explicitly designed for human-operated workflows.

### Pricing

T7 GUI access is available in two pricing models:

**Included with Existing Connectivity**: Participants with ETI or FIX Gateway connectivity receive T7 GUI access at no additional cost as part of their connectivity package.

**Standalone GUI Access**: Participants requiring only GUI access (without algorithmic trading connectivity) pay EUR 310 per month for GUI-only connectivity. This pricing supports manual traders, back-office operations, and risk oversight teams that do not require programmatic order entry. *(Source: [Deutsche Boerse Pricing](https://www.deutsche-boerse.com))*

## Interface Selection Guide

Selecting the appropriate trading interface is a strategic decision influenced by latency requirements, development resources, existing infrastructure, and trading strategy characteristics.

### Choose ETI High-Frequency (HF) When:

- **Ultra-low latency is critical**: Market making, arbitrage, or statistical strategies where microsecond advantages impact profitability
- **High message rates are required**: Strategies generating hundreds or thousands of orders per second
- **Co-located at Equinix FR2**: HF sessions deliver maximum value when combined with co-location, eliminating wide-area network latency
- **Willing to implement binary protocol**: Development team has expertise to implement custom ETI protocol stack or integrate with third-party ETI libraries

### Choose ETI Low-Frequency (LF) When:

- **Multi-partition access needed**: Trading strategies span multiple product groups across different partitions
- **Moderate latency acceptable**: Strategies do not require sub-100-microsecond latency and can tolerate LF gateway overhead
- **Simpler session management preferred**: Operating a single LF session is operationally simpler than managing multiple partition-specific HF sessions
- **Lower cost structure desired**: LF sessions typically cost less than multiple HF sessions for multi-partition access

### Choose FIX Gateway When:

- **Existing FIX infrastructure in place**: Order management systems, execution management systems, or vendor platforms already support FIX protocol
- **Industry-standard protocol required**: Institutional mandates or operational policies require FIX connectivity
- **Moderate latency acceptable**: Trading strategies can accommodate additional latency from protocol translation
- **Faster time-to-market needed**: Leveraging existing FIX implementation reduces development effort compared to implementing custom ETI stack

### Choose T7 GUI When:

- **Manual trading only**: Discretionary traders operating without automated strategies
- **Monitoring and administration**: Risk managers, compliance officers, or operations staff requiring read-only or limited operational control
- **Low-volume operations**: Trading frequencies measured in orders per hour or day rather than orders per second

## Session Architecture Summary

Understanding how different session types connect to T7 infrastructure clarifies latency characteristics and architectural trade-offs.

**ETI HF Sessions**: Connect directly to Partition-Specific (PS) gateways, which are co-located with matching engines on the same physical server (as of H1 2021). This architecture provides the shortest possible path from network interface to matching logic, delivering <55 microsecond median order-to-response latency. *(Source: [T7 Architecture](https://www.eurex.com))*

**ETI LF Sessions**: Connect to Low-Frequency (LF) gateways, which route messages to appropriate PS gateways based on target partition. LF gateways introduce approximately 12 microseconds of additional latency for same-side requests compared to direct PS gateway connections. Cross-partition operations (coordinating across multiple partitions) add approximately 1 microsecond. *(Source: [T7 Gateway Performance](https://www.eurex.com))*

**FIX Sessions**: Terminate at FIX gateways, which translate FIX messages to ETI binary format and route through LF gateway infrastructure to PS gateways. This architecture introduces both protocol translation overhead and LF gateway routing latency. *(Source: [T7 FIX Gateway](https://www.eurex.com))*

**Back-Office Sessions**: Similar to LF sessions, Back-Office sessions connect to LF gateways but are restricted to administrative message types (drop copy, risk events, trade confirmations) rather than full order entry functionality. *(Source: [ETI Session Types](https://www.eurex.com))*

## Additional Services via ETI

Beyond standard order entry and execution, ETI provides access to specialized trading services and workflows available on T7.

### Trade Entry Services (TES)

Trade Entry Services enable participants to report off-exchange trades for clearing through Eurex Clearing. TES supports block trades, exchange-for-physical (EFP) transactions, and other pre-negotiated trades that require clearing but occur outside the central limit order book. TES messages use ETI protocol with specialized message types for trade reporting. *(Source: [Eurex TES](https://www.eurex.com))*

### SRQS (Selective Request for Quote)

SRQS enables participants to request quotes from designated liquidity providers for specific instruments. This request-for-quote workflow is particularly useful for less liquid instruments or large orders where soliciting competitive quotes improves execution quality. SRQS operates via ETI messaging, with request and response flows integrated into the ETI protocol. *(Source: [Eurex SRQS](https://www.eurex.com))*

**Eurex EnLight**: The SRQS implementation for Eurex derivatives, providing request-for-quote functionality across fixed income, equity index, and commodity derivatives.

**Xetra EnLight**: The SRQS implementation for Xetra cash equities, enabling quote solicitation for less liquid stocks or large block trades.

### CLIP (Client Liquidity Improvement Process)

CLIP is a derivatives-only workflow that enables participants to execute large orders with minimal market impact by matching against internal client liquidity before accessing the central order book. CLIP operates via specialized ETI message types and is subject to size thresholds and regulatory requirements. CLIP is not available for cash equities on Xetra. *(Source: [Eurex CLIP](https://www.eurex.com))*

### Strategy Creation

T7 supports multi-leg instruments for derivatives, allowing participants to create custom option strategies (e.g., spreads, straddles, combinations) as single tradable instruments. Strategy creation uses ETI messages to define leg ratios, prices, and execution conditions. Once created, strategies trade as unified instruments with single order book and execution semantics. *(Source: [Eurex Strategy Trading](https://www.eurex.com))*

### Risk Management via ETI

Participants configure pre-trade risk limits directly via ETI messaging, enabling dynamic adjustment of Advanced Risk Protection (ARP) parameters, Post-Trade Risk (PTR) thresholds, and trading limits. This real-time risk management capability allows participants to adapt risk controls intraday based on market conditions, position changes, or strategy requirements. *(Source: [Eurex Risk Management](https://www.eurex.com))*

Risk management functions are available via HF sessions for latency-sensitive risk control updates, ensuring that risk parameter changes propagate to matching engines with minimal delay.

## Encryption and Security

All T7 trading interfaces implement robust encryption and authentication mechanisms to protect order data confidentiality and prevent unauthorized access.

### TLS 1.3 Mandatory Encryption

TLS 1.3 is mandatory for all ETI connections as of current T7 releases. TLS 1.3 provides:

- **Confidentiality**: All messages encrypted during transmission, preventing eavesdropping
- **Integrity**: Cryptographic message authentication codes (MACs) ensure messages are not tampered with in transit
- **Forward secrecy**: Session keys are ephemeral and cannot be recovered even if long-term keys are compromised
- **Performance**: TLS 1.3 reduces handshake latency compared to TLS 1.2, minimizing connection establishment overhead

TLS 1.2 support will be decommissioned with T7 Release 14.1 (May 18, 2026), requiring all participants to migrate to TLS 1.3. *(Source: [Deutsche Boerse Security](https://www.deutsche-boerse.com))*

### Password Encryption

ETI session logon messages include encrypted password fields using public key cryptography. Deutsche Boerse provides a public key certificate, and participants encrypt their passwords using this public key before transmission. This ensures that passwords are never transmitted in plaintext, even before TLS session establishment. *(Source: [ETI Security](https://www.eurex.com))*

### Session-Level Authentication

Each ETI session authenticates using participant credentials (username, password, session ID). Deutsche Boerse validates credentials at session logon and rejects unauthorized connection attempts. Session credentials are assigned during participant onboarding and can be managed via Deutsche Boerse's participant administration portal. *(Source: [ETI Session Management](https://www.eurex.com))*

FIX Gateway sessions use FIX protocol authentication mechanisms (Logon message with username and password fields), with similar encryption and validation procedures.

## Conclusion

Deutsche Boerse's trading interface landscape provides flexible connectivity options tailored to diverse participant needs. ETI delivers ultra-low latency and maximum throughput for high-frequency trading, while FIX Gateway offers industry-standard connectivity for institutional participants with existing FIX infrastructure. T7 GUI serves operational and administrative requirements for manual trading and risk management.

Understanding the performance characteristics, protocol specifications, and architectural trade-offs of each interface enables participants to make informed connectivity decisions aligned with their latency requirements, development resources, and trading strategies. The choice between native ETI binary protocol and FIX translation, between partition-specific HF sessions and multi-partition LF sessions, and between co-located and remote connectivity fundamentally shapes the performance envelope and operational complexity of a participant's trading infrastructure.

The following chapters will build on this interface foundation, exploring market data protocols (EOBI, EMDI, MDI, RDI), order types and matching logic, and latency optimization techniques for participants seeking maximum performance from T7 connectivity.

---

[Previous: Chapter 3 - Network Infrastructure & Co-Location](../03-network-infrastructure/README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [Next: Chapter 5 - Market Data Feeds](../05-market-data/README.md)
