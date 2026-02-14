---
layout: default
title: "ETI Deep-Dive"
nav_order: 1
parent: "4. Trading Interfaces"
grand_parent: Chapters
---

# Enhanced Trading Interface (ETI)

The Enhanced Trading Interface (ETI) represents T7's native, high-performance trading protocol designed specifically for low-latency algorithmic trading. As Deutsche Boerse's proprietary binary protocol, ETI provides the most direct and optimized access path to T7 matching engines, delivering sub-55-microsecond median order-to-response latency for co-located high-frequency sessions. This deep-dive examines ETI's protocol architecture, session management, order lifecycle, specialized trading services, and technical implementation details essential for participants building high-performance connectivity to Eurex derivatives and Xetra cash markets.

## Protocol Architecture

ETI combines the performance advantages of binary serialization with the semantic familiarity of industry-standard FIX messaging. This hybrid design enables both maximum throughput and conceptual accessibility for developers experienced with FIX-based trading systems.

### Binary Encoding with FIX Semantics

ETI employs a proprietary flat binary encoding format while maintaining semantic alignment with FIX 5.0 Service Pack 2 (SP2). Fields, message types, and workflow semantics map directly to FIX equivalents, enabling participants to leverage FIX domain knowledge while implementing a custom binary protocol. For example, ETI's NewOrderSingle request corresponds semantically to FIX MsgType=D (NewOrderSingle), with similar fields for symbol, price, quantity, order type, and time-in-force instructions.

This approach contrasts with text-based FIX protocols (FIX 4.2, 4.4, FIXT 1.1 with FIX 5.0 semantics) where messages are human-readable tag=value pairs delimited by SOH (Start of Header) characters. Binary encoding eliminates parsing overhead associated with text tokenization, string-to-integer conversion, and delimiter scanning. Messages are transmitted as compact byte sequences with fixed-length fields or explicit length prefixes for variable-length strings, enabling deterministic parsing performance. (Source: [ETI Manual R13.1](https://www.eurex.com/resource/blob/4305946/dcadfeef8842b1a84b0e9afa439802e1/data/T7_R.13.1_Enhanced_Trading_Interface_-_Manual_Version_1.pdf))

### Little-Endian Byte Ordering

ETI messages use little-endian byte ordering throughout, meaning the least significant byte appears first in multi-byte integers. This design aligns with x86 and x64 processor architectures, which are predominant in algorithmic trading infrastructure. Little-endian alignment eliminates byte-swapping overhead during message serialization and deserialization, reducing CPU cycles and contributing to lower latency. Participants implementing ETI parsers on x86/x64 systems can directly cast byte sequences to native integer types without transformation.

For example, a 32-bit integer with value 0x12345678 is transmitted as byte sequence `78 56 34 12` in little-endian format. On an x86 processor, this byte sequence can be directly read as a 32-bit integer without reordering. (Source: [ETI Technical Specification](https://www.eurex.com))

### TemplateID-Based Message Identification

Each ETI message type is uniquely identified by a TemplateID field (field number 28500) in the message header. TemplateID serves as the message type discriminator, enabling efficient message routing and validation. The standard ETI message structure includes:

1. **Message Header**: Contains TemplateID, message body length, and protocol metadata
2. **Message Body**: Contains message-specific fields defined by the TemplateID

Participants use TemplateID to route incoming messages to appropriate handler functions and to construct outgoing messages with the correct field layout. ETI defines separate TemplateIDs for requests, responses, notifications, and broadcast messages. For example:
- TemplateID 10100: NewOrderSingle request
- TemplateID 10101: NewOrderSingle response
- TemplateID 10025: Execution Report (unsolicited notification)

The TemplateID approach provides type safety and explicit versioning, as each protocol update can introduce new TemplateIDs while maintaining backward compatibility for existing TemplateIDs. (Source: [ETI Message Reference](https://www.eurex.com))

### Transport Layer and Asynchronous Operation

ETI operates over TCP/IP connections with mandatory TLS 1.3 encryption (discussed in Encryption and Security section). The protocol is fully asynchronous, meaning participants can submit multiple requests without waiting for responses. The matching engine processes orders in FIFO (first-in-first-out) sequence based on arrival time, and responses return asynchronously via the same TCP connection.

This asynchronous design contrasts with request-response protocols where each request must complete before submitting the next. Asynchronous operation maximizes throughput by enabling order pipelining: while the matching engine processes an earlier order, subsequent orders can already be in-flight on the network and in gateway queues. This design is essential for achieving maximum transactions-per-second (TPS) rates in high-frequency sessions.

ETI participants must maintain internal order state tracking based on received ExecutionReport messages rather than relying on synchronous confirmation. This stateful client design is standard for high-performance trading systems. (Source: [ETI Manual R13.0](https://www.eurex.com/resource/blob/4118924/92d2265da7b15bb8e18f7a90a37e95a6/data/T7_R.13.0_Enhanced_Trading_Interface_-_Manual_Version_3.pdf))

### Protocol Evolution and Versioning

ETI has evolved through multiple major versions aligned with T7 platform releases. Historical versions include 8.0, 9.1, 10.0, 11.0, 11.1, 12.0, 12.1, and 13.0. Current production versions are Release 13.1 and Release 14.0, with Release 14.1 scheduled for deployment in May 2026 (simulation environment March 23, 2026; production May 18, 2026).

Each release introduces new features, message types, and protocol enhancements while typically maintaining backward compatibility for existing message flows. Participants must track release notes and migration guides to adapt their ETI implementations to new protocol versions. Major changes, such as the decommissioning of legacy order entry messages in Release 14.1, require explicit code updates and testing. (Source: [Release 14.1 Circular](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-14.1-Mandatory-Implementation-of-New-ETI-Order-Entry-Requests-and-Decommissioning-of-Support-for-TLS-1.2-4913448))

## Session Types

ETI supports multiple session types differentiated by maximum throughput (measured in transactions per second, TPS), partition access model, co-location requirements, and monthly pricing. Session type selection represents a fundamental architectural decision that directly impacts latency performance, infrastructure requirements, and operational costs.

| Session Type | Max TPS | Pricing (EUR/mo) | Access | Key Characteristics |
|-------------|---------|-------------------|--------|---------------------|
| HF Light | 50 | 125 (1-4 sessions) / 250 (5+ sessions) Eurex; 250 Xetra | PS Gateway | Partition-specific, co-location required |
| HF Full | 150 | 250 (1-4 sessions) / 500 (5+ sessions) Eurex; 500 Xetra | PS Gateway | Full HF capabilities, co-location required |
| HF Ultra | 250 | See Price List | PS Gateway | Highest throughput, since June 2023 |
| LF | Lower | Varies | LF Gateway | Multi-partition, +12 µs latency |
| Back-Office | Lower | 100-104 | LF Gateway | Trade confirmations, drop copy, risk events only |

### High-Frequency Light (HF Light)

HF Light sessions provide entry-level high-frequency access with 50 TPS throughput. These sessions connect directly to Partition-Specific (PS) gateways co-located with matching engines, delivering the same low-latency network path as higher-tier HF sessions but with reduced throughput capacity.

**Use Cases:**
- Entry-level HF trading for participants testing high-frequency infrastructure
- Strategies with moderate message rates that do not require maximum throughput
- Market making in less liquid instruments where quote updates are infrequent
- Cost-optimized HF access for participants not requiring full 150 or 250 TPS capacity

**Pricing:** EUR 125 per month for the first 1-4 sessions, increasing to EUR 250 per month for the 5th session and beyond on Eurex; EUR 250 per month on Xetra. This tiered pricing incentivizes consolidation of order flow into fewer sessions. (Source: [Eurex Pricing](https://www.eurex.com))

### High-Frequency Full (HF Full)

HF Full sessions represent the standard high-frequency tier, supporting 150 TPS throughput. This throughput capacity accommodates active market making strategies, algorithmic trading systems with substantial order flow, and multi-instrument trading strategies requiring frequent order updates.

**Use Cases:**
- Active market making across multiple instruments within a single partition
- Algorithmic strategies generating 50-150 orders per second
- High-frequency statistical arbitrage or momentum strategies
- Participants requiring low latency but not absolute maximum throughput

**Pricing:** EUR 250 per month for the first 1-4 sessions, increasing to EUR 500 per month for the 5th session and beyond on Eurex; EUR 500 per month on Xetra. (Source: [Eurex Pricing](https://www.eurex.com))

### High-Frequency Ultra (HF Ultra)

HF Ultra sessions, introduced in June 2023, provide the highest throughput tier at 250 TPS. This session type targets ultra-high-frequency market makers and quote-driven strategies generating maximum message rates.

**Use Cases:**
- Ultra-high-frequency market making with aggressive quote updates
- Multi-leg option strategies requiring frequent re-pricing
- Participants operating at the upper limits of T7 throughput capacity
- Strategies where 150 TPS throughput creates a performance bottleneck

**Pricing:** Contact Deutsche Boerse for HF Ultra pricing, which varies based on usage patterns and volume commitments. HF Ultra represents the premium session tier with corresponding premium pricing. (Source: [HF Ultra Circular](https://www.eurex.com/ex-en/find/circulars/circular-3498396))

### Low-Frequency (LF)

LF sessions provide multi-partition access via Low-Frequency gateways, which route messages to appropriate PS gateways based on target partition. LF sessions introduce approximately 12 microseconds of additional latency compared to direct PS gateway connections for same-side requests. Cross-partition operations add approximately 1 microsecond.

**Use Cases:**
- Buy-side participants and algorithmic trading strategies with moderate message rates
- Multi-partition trading strategies spanning multiple product groups
- Participants requiring simplified session management (single LF session vs. multiple partition-specific HF sessions)
- Cost-optimized access when sub-100-microsecond latency is not required

**Pricing:** LF sessions typically cost less than multiple HF sessions for multi-partition access. Exact pricing varies based on service configuration and features enabled. (Source: [Eurex Pricing](https://www.eurex.com))

### Back-Office

Back-Office sessions provide a subset of LF functionality focused on post-trade operations rather than active order entry. These sessions receive trade confirmations, drop copy messages (copies of execution reports for audit and reconciliation), and risk event notifications.

**Use Cases:**
- Post-trade reconciliation and trade capture systems
- Drop copy feeds for compliance and audit
- Risk management systems receiving risk event notifications
- Back-office operations not requiring direct order entry

**Pricing:** EUR 100-104 per month depending on market segment. Back-Office sessions are priced lower than full LF sessions due to reduced functionality scope. (Source: [Eurex Pricing](https://www.eurex.com))

### Session Limit Per Participant

As of June 2024, T7 supports a maximum of 600 ETI trading sessions per participant, increased from the previous limit of 400 sessions. This capacity expansion accommodates large trading organizations operating multiple strategies, desks, algorithmic systems, or administrative processes requiring dedicated sessions.

Participants managing complex multi-strategy operations may allocate sessions across:
- Partition-specific HF sessions for latency-sensitive strategies
- LF sessions for multi-partition strategies and back-office systems
- Backup and disaster recovery sessions
- Simulation environment sessions for testing

Participants approaching the 600-session limit should coordinate with Deutsche Boerse to evaluate infrastructure capacity and discuss potential accommodations. (Source: [Session Limit Increase Circular](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-ETI-trading-sessions-Limit-increase-per-Participant-3965220))

### Co-Location Requirements

All HF session types (HF Light, HF Full, HF Ultra) are restricted to co-location at Equinix FR2 in Frankfurt in production environments. This requirement ensures that HF throughput guarantees remain achievable given the predictable low-latency network path between co-located participant servers and PS gateways.

LF and Back-Office sessions can be accessed remotely via wide-area network connections, though remote access introduces significant additional latency (typically milliseconds rather than microseconds) due to network propagation delays and intermediate routing infrastructure.

Participants can access HF sessions from remote locations in simulation and testing environments to facilitate development and pre-production validation before migrating to co-location. (Source: [ETI Manual](https://www.eurex.com))

### Disaster Recovery Throttle

In disaster recovery scenarios where T7 operates at the backup data center with reduced infrastructure capacity, all ETI sessions are throttled to 30 TPS regardless of normal session type limits. This throttle ensures fair access to limited resources and prevents any single participant from monopolizing available capacity during degraded operations.

Participants must design their trading systems to detect and adapt to DR throttle conditions, typically by reducing order submission rates, prioritizing critical order flow, or activating alternative liquidity sources. (Source: [ETI Manual](https://www.eurex.com))

## Session Management

ETI session lifecycle encompasses connection establishment, authentication, heartbeat maintenance, sequence number tracking, and session recovery procedures. Understanding these mechanics is essential for building robust trading systems that maintain connectivity under normal operations and recover gracefully from network disruptions or gateway failovers.

### Connection Establishment

The ETI connection establishment sequence follows these steps:

1. **TCP Connection**: Participant initiates TCP connection to assigned ETI gateway IP address and port
2. **TLS Handshake**: Participant and gateway negotiate TLS 1.3 encrypted session (mandatory)
3. **Logon Request**: Participant sends ETI Logon Request message containing:
   - Session ID: Unique identifier assigned by Deutsche Boerse during onboarding
   - Credentials: Username and password (encrypted using public key cryptography)
   - Application details: Application name, version, protocol version
4. **Logon Response**: Gateway validates credentials and returns Logon Response with:
   - Session parameters: Heartbeat intervals, timeout thresholds
   - Throttle limits: TPS limit for this session type
   - Sequence numbers: Last inbound/outbound sequence numbers (for session recovery)
   - System status: Trading status (pre-open, continuous trading, closing auction, etc.)

Successful logon establishes an active ETI session ready to accept order requests. Failed logon results in TCP connection closure and requires retry with correct credentials. (Source: [ETI Manual Section 6](https://www.eurex.com))

### Heartbeat Mechanism

ETI uses bidirectional heartbeat messages to detect stalled or failed TCP connections. Both participant and gateway must send periodic heartbeat messages at configurable intervals (typically 10-30 seconds). If either side fails to receive a heartbeat within the configured timeout window, the connection is considered stalled and may be disconnected.

**Stalled Connection Scenario:**
A stalled TCP connection occurs when TCP keepalive probes are not exchanged (e.g., due to network issues or gateway process hang) but the TCP session remains nominally open. In this state, ETI heartbeats cease but the participant's TCP stack does not detect connection failure. Deutsche Boerse's infrastructure actively monitors heartbeat flow and forcibly closes stalled connections, triggering participant-side reconnection logic.

Participants should implement:
- Periodic heartbeat transmission on schedule
- Heartbeat timeout detection and automatic reconnection
- Logging of stalled connection events for operational monitoring

(Source: [ETI Manual Section 6.5](https://www.eurex.com))

### Sequence Number Management

ETI tracks message sequence numbers separately for inbound (participant-to-gateway) and outbound (gateway-to-participant) message flows. Sequence numbers enable detection of message loss and support session recovery with message retransmission.

**Inbound Sequence Numbers**: Each order request, cancel, or modification sent by the participant includes an incrementing sequence number. The gateway validates sequence continuity and rejects messages with unexpected sequence numbers.

**Outbound Sequence Numbers**: Each execution report, notification, or response sent by the gateway includes a sequence number. Participants must validate sequence continuity to detect missing messages during session interruptions.

During session logon, the gateway returns the last processed inbound and outbound sequence numbers, enabling participants to identify any gap in message flow that occurred during disconnection. Participants can then request retransmission of missed messages. (Source: [ETI Manual Section 6.6](https://www.eurex.com))

### Session Recovery

Session recovery procedures differ between HF and LF sessions due to their distinct gateway architectures.

**HF Session Recovery:**
1. Attempt reconnection to the same PS gateway and partition last connected
2. If same PS gateway unavailable (e.g., due to server failure), connect to backup PS gateway for the same partition
3. Session login is immediately possible once standby PS gateway is available (no grace period)
4. Query order status and position using Mass Order Status Request or Mass Quote Request
5. Reconcile local order state with exchange-reported state
6. Resume normal trading operations

HF sessions are partition-specific, so recovery must reconnect to a PS gateway serving the same partition. T7's architecture ensures that standby PS gateways maintain synchronized order state and can immediately accept logon requests after primary gateway failure. (Source: [Gateway Consolidation Circular](https://www.eurex.com/ex-en/find/circulars/circular-2404602))

**LF Session Recovery:**
1. Reconnect to any available LF gateway (LF gateways are not partition-specific)
2. Request retransmission of missed messages using sequence number gap detection
3. Recover order data across all partitions using Mass Order Status Request
4. Reconcile local state with execution notifications received
5. Resume normal operations

LF sessions benefit from multi-partition access and simplified recovery since any LF gateway can serve the session. Message retransmission ensures that execution reports generated during disconnection are delivered upon reconnection. (Source: [ETI Manual Section 7](https://www.eurex.com))

### Throttle Management

Each session type enforces maximum TPS limits. The gateway tracks request rates on a rolling time window basis (exact window size is implementation-dependent but typically 1 second). When a participant exceeds the TPS limit:

1. **Back-Pressure**: Gateway may apply back-pressure by delaying acknowledgment of additional requests
2. **Reject**: Requests exceeding throttle limits are rejected with specific error code indicating throttle violation
3. **Session Continuity**: Session remains active; throttle violation does not trigger disconnection

Participants must implement rate-limiting logic to avoid throttle violations. Common strategies include:
- Token bucket rate limiting on client side to cap submission rate below session limit
- Monitoring reject codes for throttle violations and dynamically reducing submission rate
- Prioritizing critical order flow (e.g., hedge orders, risk-reducing orders) over discretionary flow when approaching throttle limits

During disaster recovery scenarios, the 30 TPS throttle applies regardless of normal session limits, requiring participants to drastically reduce submission rates or activate failover to alternative trading venues. (Source: [ETI Manual Section 6.8](https://www.eurex.com))

## Order Management

ETI provides comprehensive order lifecycle management covering order entry, modification, deletion, and execution reporting. These workflows form the core of ETI-based trading system functionality.

### Order Entry

Participants submit new orders using order entry request messages. As of Release 12.0 (June 2022), Deutsche Boerse introduced five new unified order management requests with aligned layouts across all T7 exchanges (Eurex, Xetra, 360T). These new requests combined previously separate simple and complex order entry messages, optimized field arrangements for reduced parsing latency, and provided a foundation for future protocol enhancements.

**Unified Order Entry Requests (Release 12.0+):**
- NewOrderSingle: Submit single-leg order
- NewOrderMultiLeg: Submit multi-leg order (e.g., options strategies)
- ModifyOrder: Modify existing order
- DeleteOrder: Delete single order
- MassDeleteOrder: Delete multiple orders by criteria

**Legacy Requests (Deprecated, Decommissioned Release 14.1):**
Previous ETI versions provided separate "Single" and "MultiLeg" request variants with different message layouts. These legacy requests are deprecated and will be decommissioned in Release 14.1 (May 2026), requiring all participants to migrate to unified requests. (Source: [Release 14.1 Circular](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-14.1-Mandatory-Implementation-of-New-ETI-Order-Entry-Requests-and-Decommissioning-of-Support-for-TLS-1.2-4913448))

**NewOrderSingle Message Fields:**
- SecurityID: Instrument identifier (assigned by exchange)
- Side: Buy (1) or Sell (2)
- OrderQty: Order quantity
- Price: Limit price (for limit orders; omitted for market orders)
- OrdType: Order type (Market, Limit, Stop, etc.)
- TimeInForce: DAY, IOC, GTC, GTD, FOK
- ClOrdID: Client order identifier for tracking
- Additional fields: ExecInst, ExpireDate, account codes, free-text fields

Upon submission, the order enters T7 matching logic and triggers execution reporting (discussed below). (Source: [ETI Message Reference](https://www.eurex.com))

### Order Modification

ModifyOrder requests enable participants to change order price, quantity, or other attributes without canceling and replacing the order. Modification behavior depends on exchange rules and order parameters:

**Quantity Decrease or Price Improvement:** Order typically maintains time priority if the modification makes the order less aggressive (e.g., reducing quantity, improving price for a buy order). Exact rules vary by market segment and order type.

**Quantity Increase or Price Deterioration:** Order typically loses time priority and moves to the back of the queue at the new price level, as increasing quantity or worsening price represents a new commitment of liquidity.

ModifyOrder requests must include:
- OrderID: Exchange-assigned order identifier (from original NewOrderSingle response)
- New price, quantity, or other fields to modify
- ClOrdID: New client order identifier for this modification event

Successful modification generates an ExecutionReport with ExecType=Replaced (5), conveying the new order state. Rejected modifications generate Business Message Reject with error code explaining rejection reason. (Source: [ETI Manual Section 8](https://www.eurex.com))

### Order Deletion

Participants can cancel orders individually or in bulk using deletion requests.

**DeleteOrder (Single Order Deletion):**
Cancels a specific order identified by OrderID or ClOrdID. Generates ExecutionReport with ExecType=Canceled (4) upon success.

**CancelOrderSingleOrMultiLeg (Unified Deletion):**
Release 12.0 introduced a unified cancellation request supporting both single-leg and multi-leg orders with a single message type. This simplifies client code by eliminating the need to track whether an order is simple or complex when issuing cancellations.

**MassDeleteOrder (Bulk Cancellation):**
Cancels multiple orders based on criteria:
- All orders for a specific ProductComplex (e.g., all Euro-BUXL futures)
- All orders on a specific partition
- All orders for a specific session
- All orders for a specific instrument (SecurityID)

Mass deletion is useful for emergency de-risking scenarios, end-of-day cleanup, or strategy shutdown. Each deleted order generates an individual ExecutionReport with ExecType=Canceled, which may result in burst of execution reports if many orders are cancelled simultaneously.

Participants must handle cancellation reject scenarios where orders have already been filled or are in the process of execution at the time the cancel request arrives. In such cases, the cancel is rejected and the order execution proceeds. (Source: [ETI Manual Section 8.3](https://www.eurex.com))

### Execution Reports

ExecutionReport messages (TemplateID 10025, corresponding to FIX MsgType=8) communicate all order lifecycle events from the matching engine to participants. ETI mandates that exactly one response message is sent per request, ensuring deterministic response handling.

**ExecType Field (Field 150):** Specifies the type of execution event:
- 0 (New): Order accepted and entered into order book
- 1 (PartialFill): Order partially executed
- 2 (Fill): Order fully executed
- 4 (Canceled): Order canceled
- 5 (Replaced): Order modified
- 8 (Rejected): Order rejected
- Additional ExecTypes for triggered stop orders, expired orders, etc.

**OrdStatus Field (Field 39):** Conveys current order state:
- 0 (New): Order active in order book
- 1 (PartiallyFilled): Order partially executed with remaining quantity active
- 2 (Filled): Order fully executed, no remaining quantity
- 4 (Canceled): Order canceled
- 8 (Rejected): Order rejected and never entered order book

**Key Timestamp Fields:**
- RequestTime (5979): Timestamp when participant submitted request (from participant's clock)
- TrdRegTSTimePriority: Matching engine timestamp when order received time priority
- TrdRegTSPrevTimePriority: Previous time priority timestamp (for modifications)

These timestamps enable precise latency measurement and sequence reconstruction for post-trade analysis.

**Order State Maintenance:**
Participants must maintain local order state based on ExecutionReport messages. ETI is not a synchronous request-response protocol where order state is returned in a reply to each request. Instead, participants build order state incrementally from execution reports and must reconcile local state with exchange state if discrepancies arise (e.g., after session recovery).

Example state transition for a limit order:
1. Submit NewOrderSingle → Receive ExecutionReport ExecType=New, OrdStatus=New (order active)
2. Partial fill occurs → Receive ExecutionReport ExecType=PartialFill, OrdStatus=PartiallyFilled
3. Submit ModifyOrder → Receive ExecutionReport ExecType=Replaced, OrdStatus=PartiallyFilled (order modified)
4. Remaining quantity fills → Receive ExecutionReport ExecType=Fill, OrdStatus=Filled (order complete)

(Source: [ETI Manual Section 8.5](https://www.eurex.com))

### Reject Messages

ETI provides Business Message Reject messages for application-level rejections that occur during request processing. Reject messages include:
- Reject reason code: Numeric code indicating specific rejection reason
- Reject reason text: Human-readable description
- Rejected field: Identifies which field caused rejection (if applicable)

Common reject scenarios:
- Invalid SecurityID (instrument does not exist or is not tradable)
- Price outside allowable range (violates price collar or tick size rules)
- Insufficient credit or risk capacity (pre-trade risk limit exceeded)
- Invalid order attributes (e.g., IOC with GTD expiration date)
- Order does not exist (for modify/delete requests)

Participants must handle rejects programmatically by mapping reject codes to appropriate business logic. For example, "insufficient credit" rejects may trigger risk reduction workflows or halt trading for specific accounts, while "invalid tick size" rejects indicate a pricing logic error requiring correction.

Reject codes are documented in the ETI Message Reference and represent critical integration points for error handling. (Source: [ETI Manual Section 9](https://www.eurex.com))

## Quote Management (Market Making)

ETI provides optimized message types for market makers who need to submit, update, and cancel quotes across multiple instruments with minimal latency and message overhead.

### MassQuote for Bulk Quote Submission

The MassQuote request enables market makers to submit or update quotes for multiple instruments in a single message. This bulk operation reduces message count, network round-trips, and gateway processing overhead compared to individual quote messages per instrument.

**MassQuote Message Structure:**
- QuoteID: Identifier for this quote set (assigned by market maker)
- List of QuoteEntry elements, each containing:
  - SecurityID: Instrument identifier
  - BidPx, BidSize: Bid price and quantity
  - OfferPx, OfferSize: Offer price and quantity
  - QuoteEntryStatus: Active, Inactive (for selective enable/disable)

MassQuote supports up to a specified maximum number of instruments per message (exact limit depends on message size constraints). Market makers operating across hundreds of instruments typically batch quotes into multiple MassQuote messages.

### Quote Lifecycle Operations

**Quote Entry:** Submit new two-sided quote (bid and offer) for an instrument
**Quote Modification:** Update price or quantity for existing quote
**Quote Deletion:** Remove quote from order book
**Quote Activation/Deactivation:** Dynamically enable or disable quotes without deleting them

Quote activation/deactivation is particularly useful for market makers managing quotes across multiple instruments. During high-volatility periods or operational issues, market makers can quickly deactivate all quotes (removing liquidity) and reactivate when conditions normalize, without losing quote state or re-submitting full quote details.

**Release 12.0 Enhancement:** Quote Activation requests are no longer delayed by the matching engine, improving responsiveness for market makers needing to rapidly adjust liquidity provision. (Source: [ETI Manual Section 10](https://www.eurex.com))

### Quote Mass Cancellation

Similar to order mass deletion, market makers can cancel all quotes for:
- All instruments in a specific ProductComplex
- All instruments on a specific partition
- All quotes for the session

Mass cancellation supports rapid liquidity withdrawal during market disruptions, end-of-day closeout, or system maintenance.

### Enhanced Mass Quote Facility

T7 provides an Enhanced Mass Quote Facility for high-frequency market makers requiring maximum quote throughput and minimal update latency. This facility is available via ETI and optimized for quote-driven strategies with frequent price updates.

Enhanced Mass Quote functionality includes:
- Optimized message processing for quote updates
- Reduced matching engine overhead for quote re-pricing
- Prioritized gateway handling for quote messages

Participants must explicitly enable Enhanced Mass Quote during onboarding and configure their sessions appropriately. (Source: [Eurex Market Making](https://www.eurex.com))

## Trade Entry Services (TES)

Trade Entry Services enable participants to report off-exchange negotiated trades for clearing through Eurex Clearing. TES supports various bilateral and multilateral trading workflows that complement central order book trading.

### Block Trades

Block trades are large-size transactions negotiated bilaterally between two parties and reported to the exchange for clearing. Block trades execute without execution risk (the counterparties agree on price and quantity before submission) and must meet minimum contract size requirements defined by the exchange.

**ETI Block Trade Workflow:**
1. Two counterparties negotiate trade details (instrument, price, quantity) off-platform
2. One party submits TES Trade Request via ETI with trade details and counterparty identifier
3. Counterparty confirms or rejects trade via ETI
4. If confirmed, trade is registered and submitted to clearing
5. Both parties receive TES execution confirmations via ETI

Block trades are subject to post-trade publication requirements under MiFID II, with publication delayed by a specified time interval to minimize market impact.

### Exchange-for-Physical (EFP)

EFP transactions enable participants to simultaneously exchange a derivatives position for a related physical position or over-the-counter instrument. EFP-F Service specifically targets fixed income off-book trading, allowing participants to exchange bond futures positions for physical bonds or swaps.

**EFP Use Cases:**
- Hedging bond portfolios using futures
- Basis trading between futures and physical bonds
- Unwinding futures positions into deliverable bonds

EFP transactions are reported via TES messaging in ETI, with specific message types for EFP trade entry and confirmation.

### Bilateral Services

Bilateral TES enables two-party price and quantity agreement for instruments where negotiated execution is preferred over order book trading. This service is commonly used for:
- Less liquid instruments where order book depth is insufficient
- Large orders requiring price discovery negotiation
- Client facilitation trades where dealer negotiates price with client

Both parties submit matching TES Trade Requests, and the exchange registers the trade if details match.

### Multilateral Trade Registration

Multilateral TES supports multi-counterparty off-book trading where more than two parties participate in a single transaction. This functionality accommodates complex trading workflows involving multiple dealers, clients, or crossing networks.

### Additional TES Services

**Delta TAM (Total Asset Margin):** Trade registration service for portfolio margining strategies
**Vola Trades:** Volatility strategy trades negotiated off-exchange
**Trade at Index Close:** Execution at closing index price for equity derivatives
**Exchange for Swaps:** Exchange futures positions for related swap positions

Each TES service type uses dedicated ETI message types with service-specific fields. Participants intending to use TES must configure appropriate entitlements during onboarding and implement TES message handling in their trading systems. (Source: [Eurex TES](https://www.eurex.com/ex-en/trade/eurex-t7-entry-services))

### TES Notifications

TES execution notifications are delivered to ETI sessions subscribed to trade reporting. Participants can configure Back-Office sessions to receive TES notifications for reconciliation and post-trade processing without requiring full trading session access.

## SRQS / EnLight

Selective Request for Quote Service (SRQS) provides a structured request-for-quote (RFQ) workflow integrated into ETI. This service enables participants to solicit competitive quotes from designated liquidity providers for specific instruments, improving execution quality for less liquid instruments or large orders.

### EnLight Service Variants

**Eurex EnLight:** SRQS implementation for Eurex derivatives markets, covering fixed income futures, equity index derivatives, and commodity futures. Market makers subscribe to instrument categories and respond to RFQ messages via ETI.

**Xetra EnLight:** SRQS implementation for Xetra cash equities, targeting less liquid stocks and large block trades. Liquidity providers quote competitively in response to client RFQs.

### SRQS Workflow via ETI

1. **RFQ Submission:** Participant submits Request for Quote message via ETI specifying:
   - Instrument (SecurityID)
   - Side (Buy or Sell)
   - Quantity
   - Optional price guidance
2. **Quote Solicitation:** Exchange routes RFQ to registered liquidity providers for that instrument
3. **Quote Responses:** Liquidity providers submit quote responses via ETI with bid/offer prices
4. **Quote Selection:** Requesting participant reviews quotes and selects best execution
5. **Trade Execution:** Selected quote executes as a negotiated trade, submitted to clearing

SRQS reduces negotiation friction compared to bilateral phone or chat-based negotiation while maintaining competitive quote dynamics. For market makers, SRQS provides an additional liquidity provision channel beyond continuous order book quoting.

SRQS messages integrate into standard ETI message flow, enabling participants to combine order book trading, SRQS execution, and TES workflows within a unified trading session. (Source: [Eurex SRQS](https://www.eurex.com))

## CLIP (Client Liquidity Improvement Process)

CLIP, branded as "Eurex Improve," is a derivatives-only workflow that enables participants to improve client order execution by matching client orders against internal liquidity before accessing the central order book.

### CLIP Workflow

1. Participant receives client order (e.g., large option order)
2. Participant submits CLIP request via ETI indicating intent to improve execution
3. T7 matching engine allocates a time window for the participant to provide improvement (e.g., better price than current order book)
4. Participant can fill the order partially or fully from proprietary inventory at improved price
5. Unfilled quantity executes against central order book at market prices

CLIP is subject to:
- Minimum size thresholds (order must be sufficiently large to qualify)
- Price improvement requirements (CLIP execution must offer better price than prevailing market)
- Regulatory transparency and best execution obligations

CLIP is not available for cash equities on Xetra and is restricted to Eurex derivatives markets. Implementation requires specific CLIP message types in ETI and operational procedures for managing CLIP time windows and execution obligations. (Source: [Eurex CLIP](https://www.eurex.com))

## Strategy Creation

T7 supports multi-leg instrument creation for derivatives markets, enabling participants to define custom option strategies (spreads, straddles, combinations) as single tradable instruments with unified order books.

### Strategy Types

ETI supports four categories of multi-leg strategies:

**1. Futures Combinations:**
- Time spreads (calendar spreads): Long one expiry, short another expiry
- Packs and bundles: Predefined combinations of quarterly futures
- Strips: Combinations of consecutive expiries
- Inter-product spreads: Spreads between related products (e.g., DAX vs. EURO STOXX futures)

**2. Standard Options Strategies (Eurex Templates):**
Predefined option strategy templates covering common structures:
- Vertical spreads (bull/bear call/put spreads)
- Straddles and strangles
- Butterfly and condor spreads
- Ratio spreads

These templates simplify strategy creation by providing standardized leg ratios and strike relationships.

**3. Non-Standard Options Strategies (Freely Configurable):**
Custom multi-leg options strategies with up to 5 option legs. Participants specify:
- Strike prices for each leg
- Leg ratios (e.g., 1x2 call spread)
- Expiration dates
- Buy/sell side for each leg

Non-standard strategies provide maximum flexibility for complex hedging or trading strategies not covered by standard templates.

**4. Option Volatility Strategies:**
Strategies combining options with underlying futures, commonly used for volatility trading and delta-hedging. Example: Long straddle combined with short underlying futures to isolate volatility exposure.

### CreateStrategy Message

Participants submit CreateStrategy requests via ETI with:
- MarketSegmentID: Target market segment
- ProductComplex: Product family (e.g., equity options)
- Leg definitions: Array of leg specifications (SecurityID, side, ratio)
- Strategy parameters: Price conventions, allocation rules

**CreateStrategyResponse:** Returns:
- SecurityID: Exchange-assigned identifier for the newly created strategy
- Strategy signature: Encoded representation of leg structure

Participants use the returned SecurityID to submit orders for the strategy instrument, and the matching engine handles leg allocation and execution across component instruments.

### Strategy Lifecycle

**User-Created Strategies are Temporary:** All participant-created strategies are canceled at end-of-day. Strategies must be re-created for each trading session. This policy prevents accumulation of inactive or stale strategies and ensures order book clarity.

**Predefined Exchange Strategies:** T7 also provides exchange-defined standard strategies (e.g., Euro-BUXL calendar spreads) that exist permanently and do not require participant creation.

Strategy trading is a powerful tool for derivatives market participants managing complex multi-leg positions, and ETI provides the protocol infrastructure to create, trade, and manage these instruments programmatically. (Source: [Eurex Strategy Trading](https://www.eurex.com/ex-en/trade/order-book-trading/trading-in-complex-instruments))

## Risk Management via ETI

T7 integrates pre-trade risk controls and risk limit management directly into ETI, enabling participants to query and modify risk parameters in real-time without accessing separate administrative interfaces.

### Pre-Trade Risk Limits (PTRL)

Pre-Trade Risk Limits enforce maximum order size, position limits, and notional exposure limits before orders reach the matching engine. If an order would violate a configured PTRL, it is rejected immediately.

**PTRL Inquiry via ETI (Release 12.0+):** HF sessions can query current PTRL settings via ETI messages, enabling algorithmic systems to validate order sizes against current limits before submission. This capability reduces reject rates and improves operational efficiency.

**PTRL Definition via ETI:** Clearing members can define and update Pre-Trade Risk Position Limits for their clients via ETI, supporting dynamic credit management and intraday limit adjustments based on market conditions or client activity.

### Advanced Risk Protection (ARP)

Advanced Risk Protection provides comprehensive pre-trade risk controls including:
- Order size limits (maximum quantity per order)
- Total position limits (net position cannot exceed specified threshold)
- Notional exposure limits (total market value of positions)
- Order rate limits (maximum orders per time interval)
- Duplicate order protection (reject orders matching recent submissions)

ARP parameters are typically configured via the C7 ARP GUI (administrative web interface) but can also be adjusted via ETI for latency-sensitive updates.

### Intraday Limit Maintenance

Participants can modify risk limits intraday via ETI Limit Maintenance messages. Use cases include:
- Increasing limits after client provides additional collateral
- Reducing limits in response to increased market volatility or client drawdown
- Temporarily disabling limits for specific instruments during market events

Intraday limit changes propagate to matching engines within microseconds for HF sessions, ensuring risk controls remain synchronized with current market conditions.

### Risk Events

Risk events (e.g., limit breaches, margin call warnings, position limit violations) are delivered to both trading sessions and Back-Office sessions via ETI notifications. Participants should implement risk event handlers to:
- Alert trading desks or risk managers
- Automatically reduce positions or cancel orders
- Log events for regulatory reporting and compliance audit

Risk management via ETI enables fully automated risk control workflows, essential for high-frequency and algorithmic trading operations where manual intervention is impractical. (Source: [Eurex Risk Management](https://www.eurex.com))

## Technical Details

### Message Format

ETI messages follow a standardized binary format with header and body components:

**Message Header:**
- TemplateID (28500): 4-byte integer identifying message type
- BodyLen: 4-byte integer specifying message body length in bytes
- Additional header fields: protocol version, sequence number, timestamps

**Message Body:**
Binary-encoded fields specific to the TemplateID. Field encoding rules:
- **Integers:** Little-endian byte order, typically 1, 2, 4, or 8 bytes
- **Decimals:** Fixed-point representation (e.g., price fields with implicit decimal places)
- **Strings:** Fixed-length or variable-length with length prefix, ASCII or UTF-8 encoding
- **Enumerations:** Integer codes (e.g., Side field: 1=Buy, 2=Sell)
- **Timestamps:** Nanosecond-precision Unix timestamps (8-byte integer)

Maximum message sizes vary by message type. Order entry messages are typically small (hundreds of bytes), while MassQuote messages can be larger (several kilobytes for bulk quote updates).

Minimal parsing overhead is a key ETI design goal. Participants can implement zero-copy parsing strategies where binary fields are accessed directly from network buffers without intermediate data structure allocation. (Source: [ETI Message Reference](https://www.eurex.com))

### Gateway Architecture

T7 gateway architecture directly impacts ETI session performance and failover behavior.

**Partition-Specific (PS) Gateways:**
- Co-located with matching engines on the same physical server (since H1 2021 consolidation)
- Handle HF sessions exclusively
- Dedicated to a specific partition (e.g., equity index derivatives partition)
- Active/standby configuration: One PS gateway per partition is active; standby activates only during failover

This architecture eliminates network latency between gateway and matching engine, contributing to sub-55-microsecond end-to-end latency for HF sessions. (Source: [Gateway Consolidation Circular](https://www.eurex.com/ex-en/find/circulars/circular-2404602))

**Low-Frequency (LF) Gateways:**
- Route messages to appropriate PS gateways based on target partition
- Support LF and Back-Office sessions
- Multi-partition access via single LF session
- Software optimizations prevent LF requests from overtaking PS requests during high system load, ensuring FIFO fairness

LF gateways introduced in T7 architecture enable simplified session management for multi-partition strategies at the cost of approximately 12 microseconds additional latency. (Source: [ETI Manual Section 5](https://www.eurex.com))

**Standby PS Gateway Behavior:**
Standby PS gateways are started only during actual failover events, not pre-started in hot standby mode. This design reduces infrastructure resource consumption while ensuring that standby capacity is available when needed. Failover to standby PS gateway typically completes within seconds, and session reconnection is immediately possible. (Source: [Gateway Architecture](https://www.eurex.com))

### Encryption

TLS 1.3 is mandatory for all ETI connections, providing transport-layer encryption with minimal latency overhead.

**TLS 1.3 Performance Characteristics:**
- Single round-trip handshake (vs. two round-trips for TLS 1.2)
- Optimized cipher suites (e.g., AES-GCM, ChaCha20-Poly1305)
- Session resumption with pre-shared keys (PSK) for zero round-trip reconnection
- Latency impact: Single-digit microseconds per round-trip for encryption/decryption on modern processors with AES-NI hardware acceleration

**TLS 1.2 Decommissioning:**
T7 Release 14.1 (May 18, 2026 production deployment; March 23, 2026 simulation deployment) will decommission TLS 1.2 support. All ETI sessions must use TLS 1.3 after this date. Participants must:
1. Verify TLS 1.3 support in trading system TLS library (OpenSSL 1.1.1+, GnuTLS 3.6.5+, etc.)
2. Test TLS 1.3 connectivity in simulation environment before production cutover
3. Update any hardcoded TLS version configurations to require TLS 1.3

(Source: [Release 14.1 Circular](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-14.1-Mandatory-Implementation-of-New-ETI-Order-Entry-Requests-and-Decommissioning-of-Support-for-TLS-1.2-4913448))

**Password Encryption:**
In addition to TLS transport encryption, ETI Logon Request messages include password fields encrypted using public key cryptography (RSA). Deutsche Boerse publishes a public key certificate during onboarding, and participants encrypt their passwords with this public key before transmission. This defense-in-depth approach ensures passwords are never transmitted in plaintext even before TLS handshake completes or in scenarios where TLS is inadvertently disabled. (Source: [ETI Security](https://www.eurex.com))

## Release 14.1 Changes (May 2026)

T7 Release 14.1 introduces mandatory protocol changes and performance enhancements impacting all ETI participants.

### Deployment Schedule

**Simulation Environment:** March 23, 2026 (system available for participant testing)
**Production Environment:** May 18, 2026 (mandatory cutover)

Participants must complete testing in simulation and deploy updated software to production before May 18, 2026.

### Mandatory New ETI Order Entry Requests

The five new unified order management requests introduced in Release 12.0 become mandatory in Release 14.1. Legacy "Single" and "MultiLeg" request variants are decommissioned and will be rejected.

**Migration Requirements:**
- Update ETI client code to use NewOrderSingle, NewOrderMultiLeg, ModifyOrder, DeleteOrder, CancelOrderSingleOrMultiLeg
- Remove all references to deprecated legacy requests
- Test new requests in simulation environment to validate message layouts and field mappings
- Validate that execution reports and responses are parsed correctly with new message formats

Participants still using legacy requests after May 18, 2026 will experience order rejections and trading disruptions.

### TLS 1.2 Decommissioning

TLS 1.2 support is decommissioned in Release 14.1. Only TLS 1.3 connections will be accepted.

**Migration Requirements:**
- Verify TLS library version supports TLS 1.3 (minimum OpenSSL 1.1.1, GnuTLS 3.6.5, etc.)
- Update TLS configuration to negotiate TLS 1.3
- Test TLS 1.3 handshake and connectivity in simulation
- Monitor TLS version negotiation logs during production cutover

### Synthetic Matching for Packs and Bundles

Release 14.1 introduces synthetic matching for packs and bundles in Short-Term Interest Rate (STIR) futures. This enhancement improves liquidity and price discovery for STIR strategy instruments by synthesizing pack/bundle order book prices from constituent quarterly futures.

Participants trading STIR packs and bundles should review matching logic changes and adjust pricing algorithms if necessary.

### Optimized Field Layouts

New ETI requests in Release 14.1 feature optimized field layouts designed to reduce parsing latency. Fields are reordered for better cache locality and alignment, and rarely-used optional fields are grouped at the end of messages.

Participants implementing custom ETI parsers should regenerate message parsing code from updated ETI message specifications to leverage optimized layouts. (Source: [Release 14.1 Circular](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-14.1-Mandatory-Implementation-of-New-ETI-Order-Entry-Requests-and-Decommissioning-of-Support-for-TLS-1.2-4913448))

## Key Sources

The following authoritative sources provide comprehensive ETI protocol documentation and operational guidance:

- **ETI Manual R13.1:** [T7 Release 13.1 Enhanced Trading Interface Manual](https://www.eurex.com/resource/blob/4305946/dcadfeef8842b1a84b0e9afa439802e1/data/T7_R.13.1_Enhanced_Trading_Interface_-_Manual_Version_1.pdf)
- **ETI Manual R13.0:** [T7 Release 13.0 Enhanced Trading Interface Manual](https://www.eurex.com/resource/blob/4118924/92d2265da7b15bb8e18f7a90a37e95a6/data/T7_R.13.0_Enhanced_Trading_Interface_-_Manual_Version_3.pdf)
- **HF Ultra Circular:** [High-Frequency Ultra Session Type Announcement](https://www.eurex.com/ex-en/find/circulars/circular-3498396)
- **Release 14.1 Circular:** [Release 14.1 Mandatory ETI Changes and TLS 1.2 Decommissioning](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-T7-Release-14.1-Mandatory-Implementation-of-New-ETI-Order-Entry-Requests-and-Decommissioning-of-Support-for-TLS-1.2-4913448)
- **Session Limit Increase:** [ETI Trading Sessions Limit Increase to 600 Per Participant](https://www.eurex.com/ex-en/find/circulars/Eurex-Readiness-Newsflash-ETI-trading-sessions-Limit-increase-per-Participant-3965220)
- **Gateway/ME Consolidation:** [PS Gateway and Matching Engine Consolidation Architecture](https://www.eurex.com/ex-en/find/circulars/circular-2404602)
- **TES Services:** [Eurex Trade Entry Services Overview](https://www.eurex.com/ex-en/trade/eurex-t7-entry-services)
- **Strategy Trading:** [Trading in Complex Instruments (Strategies)](https://www.eurex.com/ex-en/trade/order-book-trading/trading-in-complex-instruments)

---

[Back to Chapter 4 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [FIX Gateway Deep Dive](fix-gateway.md)
