# Reference Data Interface (RDI)

The Reference Data Interface (RDI) is Deutsche Boerse's essential foundation for all trading and market data operations, providing static instrument definitions, product configurations, and system parameters required to interpret market data feeds and validate trading activity. Unlike the real-time feeds EOBI, EMDI, and MDI, RDI delivers reference information published before market open and updated intraday when instrument parameters change. All trading participants, regardless of their chosen market data feed, must consume RDI to maintain accurate instrument mappings, understand trading rules, and configure connectivity.

## Protocol and Transport Architecture

RDI employs the same protocol family as EMDI and MDI, ensuring consistency across Deutsche Boerse's market data ecosystem:

**Protocol Stack:**
- FIX 5.0 Service Pack 2 (FIX 5.0 SP2)
- FAST 1.1 and 1.2 (FIX Adapted for Streaming) encoding
- XML FAST template files provided by Deutsche Boerse for message parsing
- FIXML schema files for message structure validation

**Transport Mechanism:**
- UDP multicast delivery for efficient distribution to all subscribers
- High bandwidth network required (alternative RDF available for low-bandwidth participants)
- Side A and Side B redundancy channels for resilience
- IGMPv2 protocol for multicast group management

**Cost Model:**
- Free of charge for registered exchange participants and members
- Registration required but no subscription fees
- Available to all firms with exchange membership or sponsored access

The UDP multicast delivery ensures all participants receive reference data updates simultaneously, maintaining consistent instrument definitions across the trading community. The free-of-charge model reflects the foundational nature of this data—accurate reference information is a prerequisite for market integrity and operational safety.

## Data Content and Scope

RDI publishes comprehensive static data across several categories, each essential for different aspects of trading operations:

### Instrument Master Data

Core instrument identifiers and attributes:

- **Security Identifiers**: SecurityID (internal exchange identifier), ISIN (international standard), Bloomberg symbol, Reuters RIC
- **Instrument Descriptions**: Full instrument name, short name, classification codes
- **Instrument Types**: Equity, derivative, ETF, fund, bond classifications
- **Contract Specifications**: For derivatives, includes underlying asset, contract size, expiration dates, settlement type (cash or physical)
- **Tick Size Tables**: Minimum price increment by price range (e.g., different tick sizes for prices below EUR 1 vs. above EUR 10)
- **Lot Sizes**: Minimum tradeable quantity and quantity increments
- **Price Precision**: Number of decimal places for price representation
- **Currency**: Denomination and settlement currency

This information enables systems to validate order prices against tick size rules, ensure order quantities meet minimum size requirements, and correctly format price and quantity fields in order entry messages.

### Product-to-Partition Assignments

Mapping of tradeable products to T7 system partitions:

- **Partition Identifiers**: Which partition (1-10) handles which instruments
- **Product Assignments**: Complete list of instruments assigned to each partition
- **Partition-Specific Rules**: Trading parameters that vary by partition
- **Instrument Groups**: Logical grouping of related instruments

Understanding partition assignments is critical for connectivity configuration. Trading gateways must connect to the specific partition responsible for the instrument being traded, and market data subscriptions must target the correct partition to receive updates.

### Trading Calendar and Schedule

Temporal information governing market availability:

- **Trading Hours**: Standard trading hours for each market segment
- **Trading Phases**: Opening auction, continuous trading, closing auction, intraday auctions
- **Auction Schedules**: Precise timing of auction calls and uncrossing events
- **Holiday Calendars**: Exchange holidays and non-trading days for each market
- **Settlement Dates**: T+2, T+1, or same-day settlement specifications
- **Expiration Dates**: Derivative expiration schedules and last trading days

This information enables automated systems to anticipate market state transitions, schedule pre-market preparations, and avoid submitting orders during non-trading periods.

### Technical Configuration Parameters

Market data subscription and connectivity details:

- **Multicast Addresses**: IP addresses and port numbers for EOBI, EMDI, MDI feeds
- **Partition-to-Feed Mappings**: Which multicast groups carry data for which partitions
- **SenderCompID Assignments**: FIX SenderCompID values used by each partition
- **Network Topology**: Routing information for market data subscription
- **Feed-Specific Parameters**: FAST template versions, sequence number ranges, channel assignments

Clients use this information to construct market data subscription configurations, configure multicast group joins, and map incoming messages to the correct partition and instrument context.

### Trading Parameters and Risk Limits

Dynamic and static risk controls:

- **Static Price Range Limits**: Maximum permitted deviation from reference prices
- **Dynamic Price Ranges**: Intraday volatility interruption thresholds
- **Quantity Limits**: Maximum order size and maximum executable quantity per order
- **Instrument-Specific Risk Parameters**: Margin requirements, position limits
- **Order Type Restrictions**: Which order types permitted for which instruments
- **Self-Match Prevention Settings**: Instrument-level configuration for self-trade prevention

These parameters enable pre-trade risk checks in client systems, preventing rejected orders due to parameter violations and reducing operational risk.

## Publication Schedule and Update Frequency

RDI follows a predictable publication schedule with intraday updates as needed:

**Pre-Market Publication:**
- Primary RDI distribution occurs before the trading session begins each day
- Typically published during the pre-market preparation window
- Contains the complete instrument universe for the trading day
- Clients must process RDI before connecting to trading interfaces or subscribing to market data

**Intraday Updates:**
- New instrument listings (e.g., newly created options series)
- Parameter changes (e.g., tick size modifications, trading hour adjustments)
- Instrument halts and resumptions
- Corporate actions affecting instrument definitions

**End-of-Day Publication:**
- Reference data for the following trading day
- Instrument expirations and delistings
- Next-day holiday and trading hour changes

**User-Created Instruments (Derivatives):**
- Complex instruments (spreads, strategies) created by participants during the day
- Published immediately after creation for use by all market participants
- Cancelled and removed at end-of-day unless marked for persistence

Understanding this schedule is critical for system initialization. Trading systems must load RDI before market open to ensure accurate instrument data throughout the session. Intraday updates require event-driven processing to incorporate parameter changes without system restart.

## RDI vs RDF: Delivery Mechanism Trade-offs

Deutsche Boerse provides two delivery mechanisms for identical reference data content:

**RDI (Reference Data Interface):**
- Real-time UDP multicast delivery
- Event-driven updates as changes occur
- High bandwidth requirement
- Requires multicast network infrastructure
- Suitable for colocation or high-bandwidth remote connectivity
- Immediate visibility into parameter changes

**RDF (Reference Data File):**
- File-based batch delivery (CSV or XML format)
- Available via SFTP or HTTP download
- Low bandwidth requirement
- Suitable for participants without multicast infrastructure
- Updated daily or on-demand
- Requires polling or scheduled retrieval

**Selection Criteria:**

Choose RDI when:
- Real-time awareness of parameter changes is critical
- Multicast network infrastructure is available
- System architecture supports event-driven updates
- Colocation or high-bandwidth remote connectivity deployed

Choose RDF when:
- Batch daily reference data update is sufficient
- No multicast network available
- Simple file-based processing preferred
- Bandwidth or infrastructure constraints exist

Both mechanisms provide equivalent data content. The choice depends on operational requirements, infrastructure capabilities, and system architecture. Many participants use RDF for overnight batch loads and RDI for intraday update awareness.

## GraphQL Reference Data API

Deutsche Boerse offers a publicly accessible GraphQL API for programmatic reference data access:

**Availability:**
- Hosted on Deutsche Boerse Developer Portal
- Free anonymous access without authentication
- REST and GraphQL interface options
- Web-based query console available

**Data Coverage:**
- Instrument master data and classifications
- Product configurations and trading schedules
- Contract specifications and tick sizes
- Historical reference data queries

**Use Cases:**
- Development and testing without production RDI subscription
- Ad-hoc reference data queries for analysis
- Integration into non-trading applications
- Educational and research purposes

**Access:**
- URL: https://console.developer.deutsche-boerse.com/apis
- Interactive GraphQL query builder
- Example queries and documentation provided
- Rate limiting applies for fair usage

The GraphQL API is ideal for prototyping, testing, and applications where real-time reference data delivery is unnecessary. It complements production RDI subscriptions by providing a development-friendly interface for exploratory queries and integration testing.

## Use Cases and Applications

RDI serves foundational roles across all trading system components:

**System Initialization and Configuration:**
- Load complete instrument universe before market open
- Configure partition-specific gateway connections
- Populate local instrument databases and caches
- Initialize tick size tables and validation rules

**Order Entry Validation:**
- Verify tick size compliance before order submission
- Validate minimum lot size and quantity increments
- Check instrument tradability and trading phase eligibility
- Enforce order type restrictions

**Market Data Subscription Management:**
- Determine correct multicast groups for desired instruments
- Map SecurityIDs to human-readable instrument names
- Configure partition-specific market data handlers
- Subscribe to appropriate Side A and Side B channels

**Partition Mapping and Connectivity:**
- Identify which partition handles which instruments
- Configure gateway connections to correct partitions
- Route orders to appropriate partition based on instrument
- Optimize connectivity by co-locating related instruments

**Regulatory Reporting and Compliance:**
- Maintain accurate ISIN and instrument classification mappings
- Track instrument lifecycle events (listings, delistings, expirations)
- Report instrument-level trade activity with correct identifiers
- Comply with MiFID II and other transparency requirements

**Strategy and Risk Management:**
- Understand contract specifications for derivative strategies
- Validate position limits and margin requirements
- Track expiration schedules for roll management
- Monitor parameter changes affecting strategy behavior

Every production trading system, regardless of sophistication or strategy, depends on accurate reference data. RDI ensures all participants operate with consistent instrument definitions, reducing operational errors and enhancing market integrity.

## Implementation and Integration

Integrating RDI into trading infrastructure requires careful architecture to handle both batch initialization and intraday updates:

**Parser Development:**
- Use commercial or open-source FAST libraries for message decoding
- Load Deutsche Boerse-provided FAST templates (version 1.1 or 1.2)
- Validate parsed messages against FIXML schema files
- Handle both snapshot and incremental update message types

**Data Storage Strategy:**
- **In-Memory Cache**: Fast access for order validation and market data lookups
- **Persistent Database**: Long-term storage for regulatory and audit purposes
- **Hybrid Approach**: Memory cache backed by database for resilience

**Update Handling:**
- Subscribe to RDI multicast groups before connecting to trading interfaces
- Process complete RDI snapshot during system initialization
- Implement event-driven handlers for intraday updates
- Maintain sequence number tracking for gap detection and recovery

**Partition Mapping:**
- Parse product-to-partition assignments from RDI
- Construct lookup table mapping SecurityID to partition number
- Configure trading gateway connections per partition
- Update routing logic when partition assignments change

**Synchronization with Other Systems:**
- Propagate reference data updates to risk management systems
- Notify order management systems of parameter changes
- Update market data handlers with new instrument definitions
- Coordinate reference data versions across distributed components

**Testing and Validation:**
- Verify RDI parsing against known instrument definitions
- Test intraday update handling without full system restart
- Validate tick size and lot size enforcement
- Confirm partition mapping accuracy

**Monitoring and Alerting:**
- Alert on missing RDI updates before market open
- Monitor intraday update latency and processing delays
- Detect discrepancies between RDI and actual market behavior
- Track reference data version consistency across systems

Robust RDI integration ensures trading systems operate with accurate, current instrument data, reducing the risk of rejected orders, incorrect pricing, and regulatory violations.

## Key Sources

- **EMDI/MDI/RDI Manual R13.1**: https://www.eurex.com/resource/blob/4332344/43e75aa168ed97fff40f8607002d560f/data/T7_R.13.1_%20EMDI_MDI_RDI_Manual_Version_2.pdf
- **Reference Data API**: https://console.developer.deutsche-boerse.com/apis
- **RDI Release Notes (T7 13.1)**: https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-13.1-Important-change-in-the-publication-of-complex-instruments-via-RDF-RDI-and-initial-start-of-day-behavior-in-T7-Release-13.1-Production-4416582

---

[Back to Chapter 5 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [MDI Deep Dive](mdi.md)
