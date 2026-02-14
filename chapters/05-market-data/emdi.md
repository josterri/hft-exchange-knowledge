---
layout: default
title: "EMDI"
nav_order: 2
parent: "5. Market Data"
grand_parent: Chapters
---

# Enhanced Market Data Interface (EMDI)

The Enhanced Market Data Interface (EMDI) is Deutsche Boerse's medium-latency market data feed that combines standardized FIX protocol encoding with aggregated order book data. EMDI provides a balanced solution for firms requiring comprehensive market data without the complexity of ultra-low-latency implementations, offering price-level aggregated order books with depths up to 15 levels.

## Protocol Architecture

EMDI is built on industry-standard protocols, making it accessible to firms with existing market data infrastructure:

**Protocol Stack:**
- FIX 5.0 Service Pack 2 (FIX 5.0 SP2)
- FAST 1.1 and 1.2 (FIX Adapted for Streaming) encoding
- UDP multicast delivery for efficient distribution
- Standardized FIXML schema files for message validation

The use of standardized FIX/FAST protocols distinguishes EMDI from the proprietary EOBI format, allowing firms to leverage existing commercial and open-source libraries. Deutsche Boerse provides XML FAST template files supporting both FAST 1.1 and 1.2 versions, along with FIXML schema files for message structure validation.

**Architectural Integration:**

Since Release 12.0, EMDI has been fully consolidated into the Matching Engine (ME) process. This architectural change eliminated the separate Market Data Distributor (MDD) process, reducing the data path and improving latency characteristics. The consolidation means EMDI and EOBI now share source IP addresses for consolidated partitions, streamlining network configuration and reducing the latency gap between the two feeds.

## Data Content and Structure

EMDI delivers un-netted, price-level aggregated order book data with configurable depth:

**Order Book Depth:**
- Eurex markets: up to 15 price levels per side
- Xetra markets: up to 10 price levels per side
- Each level contains aggregated quantity at that price
- Both bid and ask sides transmitted

**Data Elements:**
- Aggregated quantities at each price level (not individual orders)
- Best bid and ask prices with depth
- Trade reports with price, quantity, and trade conditions
- Market statistics and trading session information
- Auction indicators and reference prices
- Instrument status updates

The aggregation model significantly reduces data volume compared to EOBI's order-by-order approach. While EOBI transmits every individual order add, modify, and delete, EMDI consolidates all orders at each price level into a single quantity figure. This makes EMDI more bandwidth-efficient but less granular for market microstructure analysis.

## Snapshot and Incremental Update Model

EMDI employs a dual-channel architecture separating complete state snapshots from real-time incremental updates:

**Snapshot Channel:**
- Provides complete order book state at regular intervals
- Transmitted on dedicated multicast group separate from incrementals
- Contains full depth for all subscribed instruments
- Snapshot cycle frequency configurable per product group
- Used for initial state acquisition and gap recovery

**Incremental Channel:**
- Real-time updates reflecting order book changes
- Minimal message size for efficiency
- Only transmits changed price levels, not entire book
- Sequential message numbering for gap detection

**Synchronization Mechanism:**

The synchronization between snapshots and incrementals relies on two critical sequence number fields:

- **MsgSeqNum**: Sequence number of the current message
- **LastMsgSeqNumProcessed**: In snapshots, indicates the last incremental update already reflected in the snapshot state

**Recovery Process:**

When a gap is detected in the incremental stream:

1. Request or wait for next snapshot message
2. Apply snapshot to establish known good state
3. Note the LastMsgSeqNumProcessed value from snapshot
4. Buffer any incrementals received during recovery
5. Apply buffered incrementals with MsgSeqNum > LastMsgSeqNumProcessed
6. Resume normal incremental processing

This model ensures data consistency while allowing efficient real-time updates during normal operation and reliable recovery during network disruptions or initial connection.

## Latency Characteristics

EMDI occupies the middle ground in Deutsche Boerse's market data latency spectrum:

**Relative Latency Positioning:**
- Faster than MDI (Request/Response interface)
- Slower than EOBI (ultra-low-latency feed)
- Suitable for algorithmic trading, not optimal for market making

**Release 12.0 Improvements:**

The consolidation of EMDI into the Matching Engine process in Release 12.0 delivered measurable latency improvements:

- Eliminated MDD process hop, reducing data path
- EMDI and EOBI now generated from same source process
- Shared source IP addresses for consolidated partitions
- Gap between EOBI and EMDI latency narrowed

While exact latency figures vary by product and network conditions, typical EMDI latency ranges from several hundred microseconds to low milliseconds from matching event to client receipt. This positions EMDI as appropriate for strategies operating on millisecond to sub-second timescales, but not for microsecond-sensitive high-frequency trading.

**Latency Contributors:**
- Aggregation processing within ME
- FIX/FAST encoding overhead
- Network transmission time
- Client-side FAST decoding

## Redundancy and Multicast Delivery

EMDI provides live-live redundancy through dual independent distribution paths:

**Side A and Side B:**
- Two complete, independent multicast streams
- Identical data transmitted simultaneously on both sides
- Separate multicast IP addresses and port numbers
- IGMPv2 protocol for multicast group management

**Client Implementation Pattern:**

Clients typically subscribe to both Side A and Side B simultaneously:

1. Receive messages from both sides in parallel
2. Process first message received for each sequence number
3. Discard duplicate when received from second side
4. Monitor both sides for health and failover capability

**Benefits:**
- Zero failover time (already receiving both sides)
- Protection against single network path failure
- Protection against single source server failure
- Ability to detect and diagnose network asymmetries

The live-live model eliminates the detection and switchover delay inherent in active-passive failover schemes, critical for maintaining continuous market data flow.

## Pricing and Commercial Terms

EMDI pricing reflects its position as a comprehensive, standards-based market data solution:

**Monthly Subscription Fees (CoLo 2.0 pricing):**

- **Xetra EMDI**: EUR 5,200 per month
- **Eurex EMDI**: EUR 6,000 per month
- **Combined Xetra EMDI + EOBI**: EUR 7,280 per month (bundled discount)

**Connection Rebates:**
- Eurex dual connection (Side A + Side B): EUR 750 rebate per connection
- Incentivizes proper redundant connection implementation

**Cost Comparison:**
- EMDI less expensive than EOBI as standalone product
- Combined EMDI + EOBI bundle offers cost efficiency
- MDI lower cost but request/response model limits use cases

The bundled pricing for EMDI + EOBI reflects common deployment patterns where firms use EMDI for algorithmic strategies and EOBI for latency-critical market making, allowing cost-effective access to both feeds.

## EMDI vs EOBI Comparison

Understanding the differences between EMDI and EOBI guides appropriate feed selection:

**Protocol and Implementation:**
- **EMDI**: Standardized FIX 5.0 SP2 with FAST encoding; commercial libraries available
- **EOBI**: Proprietary binary format; custom parser implementation required

**Data Granularity:**
- **EMDI**: Aggregated price-level quantities; total volume at each price
- **EOBI**: Individual order-by-order updates; every add, modify, delete visible

**Order Book Depth:**
- **EMDI**: Limited to 10 (Xetra) or 15 (Eurex) price levels
- **EOBI**: Full unlimited depth; entire order book visible

**Latency:**
- **EMDI**: Medium latency; hundreds of microseconds to low milliseconds
- **EOBI**: Ultra-low latency; tens of microseconds

**Data Volume:**
- **EMDI**: Lower message rate due to aggregation
- **EOBI**: Higher message rate; every order event transmitted

**Use Case Fit:**
- **EMDI**: Algorithmic trading, DMA systems, visualization, strategies not requiring microsecond latency
- **EOBI**: High-frequency trading, market making, strategies requiring full depth and minimal latency

**Implementation Effort:**
- **EMDI**: Lower; leverage existing FIX/FAST infrastructure and libraries
- **EOBI**: Higher; custom parser development and optimization required

## Use Cases and Target Applications

EMDI serves specific market participant profiles and strategy types:

**Algorithmic Trading Platforms:**
- Execution algorithms requiring market context
- Smart order routing based on consolidated depth
- VWAP, TWAP, and implementation shortfall strategies
- Strategies operating on second to sub-second timescales

**Direct Market Access (DMA) Systems:**
- Retail and institutional order routing platforms
- Real-time order book visualization for traders
- Pre-trade analytics and market impact estimation
- Integration with existing FIX-based OMS/EMS systems

**Firms with Existing FIX Infrastructure:**
- Organizations already using FIX for other markets
- Ability to reuse parsing libraries and frameworks
- Reduced development time and testing burden
- Standardized operational procedures across venues

**Cost-Sensitive Deployments:**
- Firms not requiring ultra-low latency
- Strategies where EMDI latency is sufficient
- Lower total cost of ownership than EOBI
- Reduced complexity and maintenance burden

**Multi-Asset Class Strategies:**
- Cross-market arbitrage with millisecond horizons
- Portfolio rebalancing and risk management
- Statistical arbitrage with longer holding periods

## Implementation Considerations

Implementing EMDI connectivity requires attention to several technical areas:

**Parser Development:**
- Use commercial FAST libraries (e.g., CoralFAST, QuickFAST) or open-source alternatives
- Load Deutsche Boerse-provided FAST templates (1.1 or 1.2)
- Validate message parsing against FIXML schema files
- Implement robust error handling for malformed messages

**Snapshot Synchronization Logic:**
- Maintain separate buffers for snapshot and incremental channels
- Implement sequence number tracking and gap detection
- Buffer incrementals during snapshot recovery
- Apply incrementals only when sequence numbers align

**Multicast Management:**
- Subscribe to both Side A and Side B for redundancy
- Implement duplicate detection based on MsgSeqNum
- Monitor message rates and latencies from both sides
- Detect and alert on side-specific failures or degradation

**Order Book Reconstruction:**
- Maintain in-memory order book state per instrument
- Apply incremental updates to current state
- Handle price level additions, updates, and deletions
- Implement book integrity checks and validation

**Performance Optimization:**
- Pre-allocate memory for order book structures
- Use efficient data structures (e.g., skip lists, sorted arrays)
- Minimize parsing overhead in critical path
- Consider multi-threading for parsing and book maintenance

**Testing and Validation:**
- Use Deutsche Boerse test environments
- Validate against reference implementations
- Test snapshot recovery under various scenarios
- Stress test with production-like message rates

---

[Back to Chapter 5 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [EOBI Deep Dive](eobi.md) | [MDI Deep Dive](mdi.md)
