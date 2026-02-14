---
layout: default
title: "5. Market Data"
nav_order: 5
parent: Chapters
has_children: true
---

# Chapter 5: Market Data Feeds

## Introduction

Deutsche Boerse's T7 trading architecture provides four distinct market data feeds, each optimized for specific use cases and latency requirements. Understanding the characteristics, tradeoffs, and optimal applications of these feeds is a critical architectural decision that directly impacts system performance, operational costs, and data quality.

The four feeds available are:
- **EOBI (Enhanced Order Book Interface)**: Native binary protocol optimized for ultra-low latency
- **EMDI (Enhanced Market Data Interface)**: FIX/FAST-based feed with moderate latency and standardized encoding
- **MDI (Market Data Interface)**: Aggregated feed for low-bandwidth monitoring and retail distribution
- **RDI (Reference Data Interface)**: Static instrument and configuration data published before market open

All feeds are distributed via UDP multicast with live-live redundancy through Side A and Side B channels. This architecture ensures resilience against network failures while maintaining deterministic latency profiles. The choice of feed directly affects connection infrastructure requirements, colocation decisions, and licensing costs.

## Feed Comparison Matrix

| Aspect | EOBI | EMDI | MDI | RDI |
|--------|------|------|-----|-----|
| **Protocol** | Native Binary | FIX/FAST | FIX/FAST | FIX/FAST |
| **Transport** | UDP Multicast | UDP Multicast | UDP Multicast/TCP | UDP Multicast |
| **Latency** | Lowest (~4 µs faster than EMDI) | Medium | Higher | N/A (static) |
| **Order Book Depth** | Full (unrestricted) | 15 levels (Eurex) / 10 levels (Xetra) | Top-of-book only | N/A |
| **Update Granularity** | Every order/quote change | Snapshots + Incremental | Aggregated snapshots | Static reference |
| **Network Requirements** | 10 GbE CoLo only | High bandwidth | Low bandwidth | High bandwidth |
| **Monthly Pricing (EUR)** | 7,200 | 5,200-6,000 | Lower | Free (registration required) |
| **Primary Use Case** | HFT, market making | Algorithmic trading | Retail, monitoring | System configuration |

## Feed Details

### EOBI - Enhanced Order Book Interface

EOBI represents Deutsche Boerse's lowest-latency market data offering, designed specifically for high-frequency trading and market-making strategies. It uses a proprietary native binary protocol that eliminates the parsing overhead associated with text-based encodings.

**Key Characteristics:**
- Publishes every order book modification as it occurs in the matching engine
- Unrestricted order book depth visibility
- Approximately 4 microseconds faster than EMDI due to binary encoding and minimal transformation
- Requires dedicated 10 GbE connectivity available only in colocation facilities
- Higher monthly subscription cost (EUR 7,200) reflects premium latency advantage

EOBI is mandatory for participants pursuing latency-sensitive strategies where every microsecond matters. The full depth visibility enables sophisticated order book analytics and liquidity detection algorithms.

For detailed protocol specifications, message formats, and implementation guidance, see [EOBI Deep Dive](eobi.md).

### EMDI - Enhanced Market Data Interface

EMDI provides a balance between performance and standardization, using the industry-standard FIX protocol with FAST compression. This makes it accessible to firms with existing FIX infrastructure while maintaining competitive latency.

**Key Characteristics:**
- FIX/FAST encoding enables compatibility with standard market data handlers
- 15 levels of depth on Eurex products, 10 levels on Xetra
- Snapshot plus incremental update model for efficient synchronization
- Approximately 4 microseconds slower than EOBI
- Available both in colocation and via remote connectivity
- Monthly pricing ranges from EUR 5,200 to EUR 6,000 depending on product coverage

EMDI is the preferred choice for algorithmic trading firms that need substantial order book depth but can tolerate single-digit microsecond latency differences. The standardized protocol reduces development time and enables faster integration.

For detailed protocol specifications, message formats, and implementation guidance, see [EMDI Deep Dive](emdi.md).

### MDI - Market Data Interface

MDI serves as the aggregated feed for participants who prioritize bandwidth efficiency over granular updates. It provides top-of-book quotes and trade information without the full order book reconstruction overhead.

**Key Characteristics:**
- FIX/FAST encoding with aggregated updates
- Top-of-book (best bid/offer) visibility only
- Significantly lower bandwidth requirements
- Available via UDP multicast or TCP for remote connections
- Lower subscription costs suitable for retail distribution
- Higher latency acceptable for non-latency-sensitive applications

MDI is optimal for market surveillance, retail trading platforms, charting applications, and any system where full order book depth is unnecessary. The reduced data volume lowers infrastructure costs and simplifies processing requirements.

For detailed protocol specifications, message formats, and implementation guidance, see [MDI Deep Dive](mdi.md).

### RDI - Reference Data Interface

RDI provides the static instrument definitions, trading calendar information, and system configuration data required to interpret all other market data feeds. It is published before market open and whenever instrument parameters change.

**Key Characteristics:**
- Contains instrument master data, trading schedules, contract specifications
- Published via UDP multicast before each trading session
- Free of charge but requires registration
- Essential for all trading participants regardless of chosen market data feed
- Updates distributed whenever corporate actions or contract parameters change

Every production system must consume RDI to maintain accurate instrument mappings, understand tick sizes, validate order parameters, and track lifecycle events such as expiry and settlement.

For detailed protocol specifications, message formats, and implementation guidance, see [RDI Deep Dive](rdi.md).

## Distribution Architecture

All T7 market data feeds are generated directly from the matching engine process, ensuring the lowest possible latency between order execution and market data publication. Since the Release 12.0 consolidation, both EOBI and EMDI are integrated within the matching engine process itself, eliminating any intermediate processing delays.

**Network Infrastructure:**
- Dedicated 10 Gigabit Ethernet market data network, physically separate from the transaction network
- UDP multicast delivery for efficient one-to-many distribution
- IGMPv2 protocol for multicast group management and subscription control
- Each instrument or instrument group assigned to specific multicast addresses

**Redundancy Model:**
- Live-live Side A and Side B channels transmit identical data on separate multicast groups
- Both sides independently generated from matching engine state
- Sequence numbers embedded in every message enable gap detection
- Participants subscribe to both sides and perform sequence number validation
- No failover delay—both feeds always active

This architecture ensures resilience against network failures, switch failures, or multicast group issues without introducing failover latency or complex state management.

## Recovery and Synchronization

Market data feeds transmitted via UDP multicast are inherently unreliable—packets may be lost, duplicated, or reordered by network infrastructure. T7 provides multiple mechanisms to detect and recover from data loss:

**EOBI Recovery:**
- Dedicated snapshot channel provides full order book state at regular intervals
- Sequence numbers in every message enable gap detection
- Participants maintain local sequence counters and request retransmission when gaps detected
- Replay Service available for historical data recovery

**EMDI Synchronization:**
- Snapshot plus incremental update model
- Initial snapshot message provides complete order book state
- Subsequent incremental messages contain only changes
- Sequence numbers enable detection of missing incremental updates
- Automatic resynchronization via new snapshot when gap exceeds threshold

**MDI and RDI:**
- Lower update frequency reduces packet loss probability
- Snapshot-based delivery simplifies recovery
- TCP option available for MDI when reliability more critical than latency

Robust market data handlers must implement gap detection, retransmission requests, and snapshot-based recovery to maintain data integrity under all network conditions.

## Feed Selection Guide

Choosing the appropriate market data feed requires analyzing your trading strategy, latency requirements, infrastructure capabilities, and budget constraints:

**Choose EOBI when:**
- Strategy is latency-sensitive (HFT, market making, arbitrage)
- Full order book depth required for liquidity analysis
- Colocation infrastructure already deployed
- Premium pricing justified by strategy profitability

**Choose EMDI when:**
- Algorithmic trading with moderate latency tolerance (sub-millisecond acceptable)
- Standardized FIX infrastructure preferred for faster integration
- 10-15 level depth sufficient for strategy requirements
- Remote connectivity acceptable

**Choose MDI when:**
- Top-of-book quotes sufficient for strategy
- Bandwidth costs or processing overhead must be minimized
- Retail distribution or market surveillance use case
- Latency not critical to strategy performance

**Choose RDI:**
- Always required regardless of other feeds selected
- Provides essential instrument metadata for all systems

Many participants consume multiple feeds: RDI for reference data, EOBI or EMDI for real-time trading, and MDI for backup monitoring or retail distribution.

## Commercial Data Products

Deutsche Boerse offers pre-packaged commercial data products that bundle specific market data content for common use cases:

**Xetra Products:**
- **Xetra Core**: Netted pre-trade data plus un-netted trade data (Level 1/Level 2)
- **Xetra Ultra**: Un-netted pre-trade data plus un-netted trade data, up to 10 best bid/ask levels

**Eurex Products:**
- **Eurex Core**: Best bid/ask up to depth 15, last traded price, volumes
- **Eurex Ultra**: Un-netted pre-trade data with up to 15 levels of depth

**Delayed Data:**
- MiFIR-compliant delayed market data available free of charge
- 15-minute delay from real-time publication
- Suitable for informational websites, non-trading applications

These commercial products simplify licensing by bundling permissions, but direct feed subscriptions offer greater flexibility for custom deployments.

---

[Previous: Chapter 4 - Trading Interfaces](../04-trading-interfaces/README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [Next: Chapter 6 - Order Types & Matching](../06-order-types-matching/README.md)
