# Enhanced Order Book Interface (EOBI)

The Enhanced Order Book Interface (EOBI) is Deutsche Boerse's ultra-low latency market data feed, designed specifically for high-frequency trading and market-making applications. As the fastest market data feed available on the T7 trading platform, EOBI provides complete order book depth with individual order-level granularity and delivers trade information approximately 4 microseconds faster than any other feed on the platform.

## Protocol Architecture

EOBI employs a native binary protocol that follows FIX 5.0 SP2 semantics but uses a highly optimized custom binary encoding. This is a critical distinction: despite following FIX semantics, EOBI is **not** a text-based FIX protocol and does not use the FIX Adapted for Streaming (FAST) encoding employed by EMDI and MDI. Instead, EOBI messages are transmitted as fixed-length binary structures designed to be as compact as possible, minimizing bandwidth requirements and parsing overhead.

The protocol is integrated directly into the matching engine process itself, eliminating inter-process communication latency that would be introduced by a separate market data gateway. This architectural decision is fundamental to EOBI's latency advantage. Market data is published via UDP multicast, providing efficient one-to-many distribution to all subscribed participants simultaneously.

EOBI is available for both Eurex derivatives markets and Xetra cash equities, making it the universal ultra-low latency feed across Deutsche Boerse's electronic trading venues.

## Data Content and Message Types

EOBI provides complete transparency into the order book with no depth restrictions. Every individual order and quote change is published in real-time, enabling participants to maintain a perfect replica of the exchange's order book state. This granularity far exceeds aggregate feeds that only publish best bid/offer or limited depth levels.

Key message types include:

- **Order Add**: New orders entering the book with full details including price, quantity, side, and order ID
- **Order Modify**: Changes to existing order quantity or price that result in loss of time priority
- **Order Modify Same Priority**: Quantity reductions that maintain the order's time priority position
- **Order Delete**: Explicit order cancellations
- **Execution Messages**: Trade executions with matched quantity, price, and aggressive side indicator
- **Trade Reports**: Consolidated trade information including trade statistics
- **Product State Changes**: Trading phase transitions and halt notifications

Additionally, EOBI provides dedicated snapshot channels that publish complete order book snapshots at regular intervals. These snapshots are essential for recovery scenarios when gap detection indicates missed packets.

## Latency Characteristics

EOBI's latency characteristics represent the theoretical minimum achievable on the T7 platform. Trades are received on EOBI approximately **4 microseconds faster** than on other market data feeds. Perhaps even more significant for certain trading strategies, EOBI publishes trade information roughly **1.5 microseconds before** ETI execution reports are sent to the participants involved in the trade. This "public data first" principle means that the market learns about trades before the counterparties receive their private execution confirmations.

This latency advantage stems from EOBI's integration directly within the matching engine process. When a trade occurs, the matching engine can immediately serialize the EOBI message and transmit it via multicast without any inter-process communication overhead. Other feeds and execution reports require additional hops through separate gateway processes.

Since T7 Release 12.0, EMDI has also been consolidated into the matching engine process, significantly narrowing the latency gap between EMDI and EOBI. However, EOBI retains its position as the absolute fastest feed due to its more streamlined binary protocol and direct integration point.

## Redundancy and Reliability

EOBI implements a live-live redundancy configuration designated as Side A and Side B. Both sides transmit identical market data simultaneously on separate multicast groups with different IP addresses. This redundancy operates at the protocol level rather than the network level—both sides are generated from the same matching engine process but transmitted on independent network paths.

Participants should subscribe to both Side A and Side B multicast groups to maximize reliability. UDP multicast is inherently unreliable—packets can be lost due to network congestion, switch buffer overflows, or receiver processing delays. By receiving from both sides, participants can tolerate packet loss on either individual feed without experiencing gaps in their order book state.

Each EOBI channel includes sequence numbers that increment with every message. These sequence numbers enable gap detection: if a participant receives message sequence 1000 followed by message 1002, it knows that message 1001 was lost and recovery action is required.

## Recovery Mechanisms

When gap detection indicates missing messages, participants must recover the missing market data to maintain accurate order book state. EOBI provides two primary recovery mechanisms:

**Snapshot Channel**: A dedicated multicast channel publishes complete order book snapshots at regular intervals (typically every few seconds). When a gap is detected, participants can resynchronize their order book state using the most recent snapshot plus any incremental messages received after the snapshot's sequence number. This approach trades perfect accuracy for rapid recovery—the snapshot represents book state at a point in time, and some historical order events may be skipped.

**Replay Service**: For participants requiring complete historical message recovery or recovering from longer outages, Deutsche Boerse provides a replay service. This service allows on-demand retrieval of historical EOBI messages for any time window, enabling perfect reconstruction of order book history. The replay service is typically accessed via a separate TCP-based protocol rather than multicast.

The choice between snapshot-based recovery and full replay depends on the application's requirements. Market makers focused on current order book state typically use snapshots for fast recovery, while compliance and surveillance systems may require full replay to reconstruct exact historical state.

## Network Requirements and Deployment

EOBI is available exclusively via **10 Gbit/s Co-Location 2.0** connections at Equinix FR2 in Frankfurt. Co-location is mandatory—EOBI is not available to remote participants under any circumstances. This restriction reflects both technical requirements (the extremely low latency requires proximity to eliminate propagation delay) and commercial considerations (premium pricing for premium service).

Market data flows over a dedicated market data network that is physically and logically separate from the transaction network used for order entry via ETI. This network separation prevents order flow from impacting market data delivery and vice versa. The market data network uses IGMPv2 for multicast group management, requiring participants to configure their network stacks appropriately.

The 10 Gbit/s bandwidth requirement reflects the aggregate message volume across all subscribed products. During peak trading periods, particularly around major market events or futures expiries, message rates can exceed millions of messages per second across all products. Participants must provision sufficient network and processing capacity to handle these peak loads without packet loss.

## Multicast Configuration

EOBI uses IP multicast for efficient one-to-many data distribution. Each product partition is assigned unique multicast group addresses for both Side A and Side B. Participants subscribe to specific multicast groups based on the products they wish to receive.

To optimize network utilization, Deutsche Boerse may assign multiple product partitions to the same multicast address. In such cases, messages from different partitions are distinguished by the SenderCompID field in the message header. Participants must parse this field to route messages to the appropriate order book instance.

The complete mapping of products to multicast group addresses is published via the Reference Data Interface (RDI). This reference data must be retrieved before EOBI connectivity can be configured. The multicast configuration can change with system releases or product additions, so participants must implement mechanisms to update their multicast subscriptions based on current RDI data.

## Pricing Structure

EOBI pricing reflects its positioning as a premium ultra-low latency product:

- **Xetra EOBI**: EUR 7,200 per month (requires CoLo 2.0 10 Gbit/s connection)
- **Eurex EOBI Futures**: EUR 7,200 per month (requires CoLo 2.0 10 Gbit/s connection)
- **Combined EMDI + EOBI**: EUR 7,280/month (Xetra), EUR 8,400+/month (Eurex)
- **Dual Connection Rebate**: EUR 750 per connection for Eurex participants using redundant connections

The relatively small incremental cost of adding EOBI to an existing EMDI subscription (EUR 80 for Xetra, EUR 1,200+ for Eurex) reflects Deutsche Boerse's recognition that many sophisticated participants will consume both feeds—EMDI for its richer field set and simpler integration, EOBI for its latency advantage.

Pricing is per connection, not per subscriber. A single firm co-located at FR2 requires one subscription regardless of how many internal systems consume the feed. However, disaster recovery sites or geographically separated trading venues would each require separate subscriptions.

## Use Cases

EOBI's characteristics make it essential for specific high-frequency trading applications:

**Ultra-Low Latency Market Making**: Market makers competing on speed require EOBI to maintain competitive quotes. The 4-microsecond advantage over other feeds translates directly to better adverse selection avoidance—knowing about trades earlier enables faster quote adjustments.

**High-Frequency Arbitrage**: Statistical arbitrage and cross-market strategies benefit from EOBI's speed advantage when detecting price dislocations across correlated instruments.

**Full Order Book Reconstruction**: Research and analytics applications requiring complete order book history use EOBI's individual order-level detail to study market microstructure and order flow dynamics.

**Trade-Through Detection**: Regulatory compliance and execution quality monitoring systems use EOBI's complete depth to detect potential trade-through violations or sub-optimal execution.

**Real-Time Risk Monitoring**: Risk systems monitoring large positions benefit from EOBI's complete book visibility to assess available liquidity and potential market impact of position liquidation.

## Implementation Considerations

Implementing EOBI connectivity presents significant technical challenges compared to simpler market data feeds:

**Custom Protocol Parsing**: The binary protocol requires custom parser implementation. Unlike EMDI, which can leverage existing FIX/FAST libraries, EOBI's proprietary binary format necessitates building parsers from scratch or licensing third-party middleware.

**High Message Rates**: During peak trading, EOBI can deliver millions of messages per second across all subscribed products. Conventional socket programming and user-space networking stacks may introduce unacceptable latency or packet loss. Kernel bypass technologies like DPDK (Data Plane Development Kit) or vendor-specific solutions like Solarflare's Onload are commonly employed for optimal performance.

**Multicast Reception Efficiency**: Efficiently receiving and demultiplexing multiple multicast groups requires careful network programming. Participants must avoid blocking operations and minimize system calls in the receive path.

**Memory-Efficient Data Structures**: Maintaining full order books for hundreds or thousands of products requires carefully designed data structures. Naive implementations using standard containers may exhibit poor cache locality and excessive memory allocation overhead.

**Gap Detection and Recovery**: Robust gap detection logic must continuously monitor sequence numbers across all channels. Recovery workflows must execute quickly enough to minimize periods of stale or incomplete order book state.

**Testing and Validation**: Without access to production EOBI until deployment, participants must rely on simulation environments and historical replay data for testing. Validating correct order book reconstruction requires extensive regression testing against known reference states.

## Historical Evolution

EOBI was introduced with T7 Release 7.0 in September 2018, initially covering selected benchmark futures contracts and KOSPI products on Eurex. This limited initial rollout reflected both technical complexity and commercial strategy—targeting the most liquid, latency-sensitive products first.

Subsequent T7 releases expanded EOBI coverage to encompass all Eurex products, making it universally available across the derivatives markets. The introduction of Xetra EOBI brought the same ultra-low latency capabilities to cash equities, unifying Deutsche Boerse's market data offerings across asset classes.

The consolidation of EMDI into the matching engine process in Release 12.0 represented a significant architectural evolution, narrowing the latency gap between EOBI and EMDI while maintaining EOBI's position as the absolute fastest feed.

## Conclusion

EOBI represents the pinnacle of market data performance on Deutsche Boerse's trading platforms. Its direct integration into the matching engine process, binary protocol optimization, and complete order book transparency make it indispensable for high-frequency trading applications where microseconds matter. However, this performance comes at the cost of implementation complexity, mandatory co-location, and premium pricing. Firms must carefully evaluate whether EOBI's latency advantage justifies these costs relative to their specific trading strategies and operational requirements.

For many participants, a hybrid approach proves optimal: consuming EOBI for latency-critical trading signals while using EMDI for less time-sensitive applications, analytics, and operational systems. This strategy balances performance with implementation complexity and cost efficiency.

---

[Back to Chapter 5 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [EMDI Deep Dive](emdi.md)
