# Market Data Interface (MDI)

The Market Data Interface (MDI) is Deutsche Boerse's aggregated, bandwidth-efficient market data feed designed for participants who require top-of-book quotes and trade data without the overhead of full order book reconstruction. MDI prioritizes low bandwidth consumption and broad accessibility over granular depth and ultra-low latency, making it the optimal choice for retail distribution, market surveillance, and monitoring applications.

## Protocol and Transport Architecture

MDI leverages industry-standard protocols with flexible connectivity options to accommodate diverse deployment scenarios:

**Protocol Stack:**
- FIX 5.0 Service Pack 2 (FIX 5.0 SP2)
- FAST 1.1 and 1.2 (FIX Adapted for Streaming) encoding
- XML FAST template files provided by Deutsche Boerse
- FIXML schema files for message structure validation

**Transport Options:**
- UDP multicast for efficient distribution (primary delivery mechanism)
- TCP connectivity available for remote participants requiring reliable delivery
- Lower bandwidth requirements than EMDI or EOBI
- Suitable for participants with constrained network capacity

The dual transport model distinguishes MDI from the multicast-only EMDI and EOBI feeds. UDP multicast provides efficient distribution for co-located or well-connected participants, while TCP offers an alternative for firms requiring guaranteed delivery or operating over leased lines with limited bandwidth. The FAST encoding ensures efficient wire representation, minimizing network utilization even when delivering continuous market updates.

## Data Content and Market Data Scope

MDI delivers netted, consolidated market data focused on top-of-book quotes and executed trades:

**Pre-Trade Data:**
- Best bid and best ask prices (top-of-book only)
- Total visible quantity at best bid and ask
- Aggregated across all orders at the best price
- No visibility into deeper price levels or individual orders

**Trade Data:**
- Last traded price and quantity
- Trade timestamp and trade conditions
- Cumulative trade statistics
- Daily high, low, and opening prices

**Market Statistics:**
- Total daily traded volume
- Volume-weighted average price (VWAP)
- Number of trades executed
- Turnover figures
- Best execution metrics

**Instrument Status:**
- Trading phase indicators (pre-opening, continuous trading, auction, closed)
- Market state transitions
- Circuit breaker status
- Reference prices and auction results

The aggregated nature of MDI means participants receive consolidated market snapshots rather than incremental order-by-order updates. This model eliminates the need for complex order book reconstruction logic while still providing sufficient information for price discovery, execution quality assessment, and retail order routing decisions.

## MDI vs EMDI vs EOBI Comparison

Understanding the positioning of MDI relative to Deutsche Boerse's other market data feeds clarifies appropriate use cases:

| Aspect | EOBI | EMDI | MDI |
|--------|------|------|-----|
| **Depth** | Full unlimited | 10-15 levels | Top-of-book only |
| **Granularity** | Individual orders | Price-level aggregated | Netted consolidated |
| **Latency** | Lowest (~tens of µs) | Medium (~hundreds of µs) | Higher (~milliseconds) |
| **Bandwidth** | High | Medium | Low |
| **Protocol** | Proprietary binary | FIX/FAST | FIX/FAST |
| **Transport** | UDP multicast only | UDP multicast only | UDP multicast or TCP |
| **Cost** | Highest (EUR 7,200/mo) | Medium (EUR 5,200-6,000/mo) | Lowest |
| **Connectivity** | CoLo 10 GbE required | High bandwidth required | Low bandwidth, remote OK |
| **Best for** | HFT, market making | Algorithmic trading | Monitoring, retail distribution |

**Key Differentiators:**

- **MDI vs EMDI**: MDI provides only top-of-book, whereas EMDI offers 10-15 levels of depth. EMDI is appropriate for algorithmic strategies requiring deeper market context; MDI is sufficient for simple execution and monitoring.

- **MDI vs EOBI**: EOBI provides full order book depth with individual order visibility and ultra-low latency. MDI aggregates all data to best bid/ask and trades, sacrificing granularity for bandwidth efficiency.

The choice between these feeds depends on strategy requirements, infrastructure capabilities, and budget constraints. Many firms subscribe to multiple feeds: EOBI or EMDI for real-time trading, MDI for backup monitoring or retail client distribution.

## Use Cases and Target Applications

MDI serves specific market participant profiles where full order book depth and ultra-low latency are unnecessary:

**Retail Distribution Platforms:**
- Client-facing trading platforms requiring best bid/offer display
- Retail broker order routing systems
- Mobile trading applications with bandwidth constraints
- Charting and technical analysis tools

**Market Surveillance and Compliance:**
- Real-time monitoring of executed trades and best prices
- Compliance systems tracking market activity
- Surveillance dashboards for regulatory oversight
- Audit trail and market abuse detection systems

**Risk Management Systems:**
- Portfolio valuation based on current market prices
- Mark-to-market calculations for positions
- Real-time P&L monitoring
- Margin and exposure calculations

**Back-Office and Middle-Office Operations:**
- Trade reconciliation systems
- Settlement price validation
- Corporate actions and reference price monitoring
- End-of-day valuation processes

**Information Vendors and Data Redistributors:**
- Financial portals and news websites
- Market data aggregators combining multiple venues
- Delayed data publishing (15-minute delayed feed)
- Content delivery networks distributing market information

**Cost-Sensitive Deployments:**
- Firms not requiring full order book depth
- Organizations with limited bandwidth or remote connectivity
- Systems where latency is not critical to performance
- Monitoring and backup systems complementing primary feeds

MDI's lower cost, reduced bandwidth requirements, and remote accessibility make it ideal for applications where comprehensive market context is unnecessary but current pricing information is essential.

## Network Requirements and Infrastructure

MDI's design prioritizes accessibility and efficiency over minimal latency:

**Bandwidth Characteristics:**
- Significantly lower data volume than EMDI or EOBI
- Reduced message frequency due to aggregation
- Suitable for standard corporate network connections
- Does not require dedicated 10 GbE colocation infrastructure

**Connectivity Options:**
- **UDP Multicast**: Primary delivery method for co-located or well-connected participants
- **TCP**: Available for remote participants requiring guaranteed delivery
- **Leased Lines**: Accessible via leased line connectivity, not restricted to colocation
- **Redundancy**: Side A and Side B available for both UDP and TCP

**Geographic Flexibility:**
- Not restricted to Frankfurt or Chicago colocation facilities
- Remote participants can access via leased lines or managed network services
- Lower cost barriers to entry compared to EMDI/EOBI
- Suitable for distributed organizational deployments

The ability to consume MDI via TCP over leased lines enables cost-effective market data distribution to remote offices, backup data centers, and regional trading desks without requiring dedicated colocation presence.

## Pricing and Commercial Terms

MDI's pricing reflects its positioning as an accessible, cost-effective market data solution:

**Cost Structure:**
- Lower monthly subscription fees than EMDI or EOBI
- No colocation requirement reduces infrastructure costs
- Suitable for budget-conscious deployments
- Volume discounts available for enterprise-wide distribution

**Comparison to Premium Feeds:**
- EOBI: EUR 7,200 per month, requires 10 GbE colocation
- EMDI: EUR 5,200-6,000 per month, high bandwidth required
- MDI: Lower cost, accessible via leased lines or standard connectivity

**Cost-Benefit Analysis:**
- Appropriate for firms where latency is not strategy-critical
- Eliminates colocation expenses for non-latency-sensitive applications
- Enables cost-effective distribution to retail clients and monitoring systems
- Lowers total cost of ownership for multi-location deployments

The lower pricing makes MDI accessible to a broader range of market participants, including retail brokers, information vendors, and firms with limited trading technology budgets.

## Redundancy and Reliability

MDI provides standard redundancy mechanisms consistent with Deutsche Boerse's market data architecture:

**Side A and Side B Channels:**
- Two independent multicast streams (for UDP delivery)
- Identical data transmitted simultaneously on both sides
- Separate multicast IP addresses and port numbers
- IGMPv2 protocol for multicast group management

**TCP Redundancy:**
- Dual TCP connections available for guaranteed delivery
- Client-managed failover for TCP connections
- No automatic failover; client responsible for connection management

**Recovery Mechanisms:**
- Snapshot-based delivery simplifies state recovery
- Lower update frequency reduces packet loss impact
- TCP option eliminates packet loss for reliability-critical deployments
- Standard sequence numbering enables gap detection

**Client Implementation Pattern:**

For UDP multicast deployment:
1. Subscribe to both Side A and Side B multicast groups
2. Process first message received for each sequence number
3. Discard duplicate when received from second side
4. Monitor both sides for health and asymmetries

For TCP deployment:
1. Establish connections to both Side A and Side B servers
2. Implement application-level failover logic
3. Monitor connection health and latency
4. Switch to backup connection upon primary failure

The live-live redundancy model ensures continuous market data availability even during network failures or infrastructure maintenance.

## Implementation Considerations

Implementing MDI connectivity requires less complexity than EOBI or EMDI due to reduced data volume and simpler data model:

**Parser Development:**
- Use commercial FAST libraries (e.g., CoralFAST, QuickFAST) or open-source alternatives
- Load Deutsche Boerse-provided FAST templates (1.1 or 1.2)
- Validate message parsing against FIXML schema files
- Lower parsing throughput requirements than EOBI/EMDI

**Data Handling:**
- No order book reconstruction required
- Simple state management for top-of-book quotes
- Trade data processing and aggregation
- Minimal memory footprint compared to full order book feeds

**Transport Selection:**
- **UDP Multicast**: Choose for lowest latency and bandwidth efficiency
- **TCP**: Choose for guaranteed delivery and simplified firewall traversal
- Consider network topology and reliability requirements
- Evaluate bandwidth availability and quality of service

**Multicast Management (if UDP selected):**
- Subscribe to both Side A and Side B for redundancy
- Implement sequence number tracking for gap detection
- Handle multicast join/leave operations
- Configure IGMP settings appropriately

**TCP Management (if TCP selected):**
- Implement connection establishment and keepalive logic
- Handle reconnection and failover scenarios
- Monitor connection latency and throughput
- Implement appropriate timeout and retry policies

**Testing and Validation:**
- Use Deutsche Boerse test environments for integration testing
- Validate message parsing and data accuracy
- Test failover scenarios for both UDP and TCP
- Verify handling of trading phase transitions and edge cases

The reduced complexity of MDI compared to EMDI and EOBI lowers development effort, testing burden, and operational risk, making it accessible to firms with limited market data engineering resources.

## Key Sources

- **EMDI/MDI/RDI Manual R13.1**: https://www.eurex.com/resource/blob/4332344/43e75aa168ed97fff40f8607002d560f/data/T7_R.13.1_%20EMDI_MDI_RDI_Manual_Version_2.pdf

---

[Back to Chapter 5 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [EMDI Deep Dive](emdi.md) | [RDI Deep Dive](rdi.md)
