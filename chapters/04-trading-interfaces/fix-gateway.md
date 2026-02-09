# FIX Gateway

## Introduction

The Financial Information eXchange (FIX) protocol is the industry-standard electronic trading protocol used globally across financial markets. Deutsche Boerse provides a FIX Gateway for market participants who prefer standard FIX messaging rather than developing custom integrations for the proprietary ETI (Enhanced Trading Interface) binary protocol.

The FIX Gateway acts as a translation layer, converting standard FIX messages to and from the ETI binary protocol used by the T7 trading system. This architecture allows firms with existing FIX infrastructure to access Eurex and Xetra markets without the development overhead of implementing a proprietary binary protocol. The gateway is particularly suitable for institutional buy-side firms, traditional brokers, and any participant prioritizing rapid deployment over absolute minimum latency.

While the FIX Gateway provides convenient access to Deutsche Boerse's markets, it introduces additional latency compared to direct ETI connections due to the protocol translation and routing through the Low Frequency (LF) Gateway infrastructure. This trade-off makes FIX appropriate for moderate-frequency institutional trading but less suitable for ultra-low latency high-frequency trading strategies.

## FIX Protocol Support

### Supported Versions

Deutsche Boerse's FIX Gateway supports two widely-adopted versions of the FIX protocol:

- **FIX 4.2**: The most widely deployed FIX version globally, ensuring maximum compatibility with legacy systems
- **FIX 4.4**: A more modern version with enhanced functionality and additional message types

Both versions are supported through the FIX LF (Low Frequency) interface designation. The current implementation is documented in the T7 Release 14.0 FIX LF Manual Version 1, which provides comprehensive specifications for message formats, session management, and exchange-specific extensions.

### Supported Message Types

The FIX Gateway supports a comprehensive set of message types covering session management, order routing, and execution reporting:

| Message Type | FIX Tag | Direction | Description |
|-------------|---------|-----------|-------------|
| Logon | A | Both | Session establishment and authentication |
| Logout | 5 | Both | Graceful session termination |
| Heartbeat | 0 | Both | Connection keep-alive mechanism |
| ResendRequest | 2 | Both | Request retransmission for gap recovery |
| SequenceReset | 4 | Both | Sequence number management and gap fill |
| NewOrderSingle | D | Inbound | Submit new order to market |
| OrderCancelRequest | F | Inbound | Cancel existing order |
| OrderCancelReplaceRequest | G | Inbound | Modify price/quantity of existing order |
| ExecutionReport | 8 | Outbound | Order acknowledgment, fill, rejection |
| BusinessMessageReject | j | Outbound | Application-level rejection with reason |

These message types cover the core functionality required for electronic trading, from session lifecycle management through order execution and status reporting.

### Custom and Proprietary Tags

While the FIX Gateway adheres to standard FIX specifications, Deutsche Boerse utilizes several custom and proprietary tags to support exchange-specific functionality:

**PartyIDSource (447)**: Identifies the source of party identification
- Value "D" = Proprietary custom code
- Value "P" = Short code identifier

**TradingCapacity (1815)**: Indicates the capacity in which the participant is trading
- Value 3 = Proprietary (market participant trading own account)

Additionally, Eurex employs various custom tags to enable functionality specific to the T7 trading system that extends beyond standard FIX capabilities. These proprietary extensions are documented in the FIX LF Interface Message Reference documentation.

## Gateway Architecture

### Message Flow

The FIX Gateway implements a multi-layer architecture that bridges standard FIX messaging with the T7 trading system's native ETI protocol:

1. **FIX Message Reception**: Participant sends a standard FIX message to the FIX Gateway over a TCP/IP connection
2. **Protocol Validation**: FIX Gateway validates the message format, sequence numbers, and session state
3. **FIX to ETI Translation**: Gateway translates the FIX message into the corresponding ETI binary format
4. **LF Gateway Routing**: Translated message is routed to the Low Frequency (LF) Gateway infrastructure
5. **PS Gateway Routing**: LF Gateway forwards the message to the corresponding Partition-Specific (PS) Gateway
6. **Matching Engine Processing**: PS Gateway forwards the message to the appropriate matching engine partition
7. **Response Flow**: Responses follow the reverse path with ETI to FIX translation occurring at the FIX Gateway

This architecture ensures that FIX clients receive the familiar FIX messaging experience while benefiting from access to Deutsche Boerse's high-performance T7 trading system.

### Routing Architecture

The FIX Gateway is integrated into Deutsche Boerse's broader gateway infrastructure:

- **Redundant Infrastructure**: The FIX LF interface gateway infrastructure is built redundantly to ensure high availability
- **Dual-Side Configuration**: One set of gateways is primarily attached to each line connection (Side A and Side B)
- **Multi-Tier Routing**: All FIX requests route through the LF Gateway before forwarding to the corresponding PS Gateway
- **Request Ordering**: Software changes implemented in November 2019 prevent LF requests from overtaking PS requests during high-load conditions, ensuring fair ordering
- **Network Optimization**: Infrastructure changes minimize latency impact on LF sessions, though latency remains higher than direct PS Gateway access

### Redundancy and Failover

The FIX Gateway infrastructure implements comprehensive redundancy mechanisms:

- **Side A and Side B Gateways**: Redundant gateway instances provide failover capability
- **Redundancy Link**: A dedicated link between gateway sides enables automatic network failover
- **Single-Line Fallback**: All gateways remain reachable via a single line in case of connection failure
- **Dual Leased-Line Support**: Participants can implement redundant two-leased-line installations for maximum resilience

This redundancy architecture ensures continuous trading access even during network or hardware failures, though the redundancy link introduces additional latency (>50 µs) when active.

## Performance Characteristics

### Latency

The FIX Gateway introduces measurable latency overhead compared to direct ETI connections due to several factors:

**Protocol Translation Overhead**: FIX messages are text-based and require parsing, validation, and conversion to ETI binary format. This translation adds computational overhead compared to native binary protocol handling.

**LF Gateway Routing**: The requirement to route through the LF Gateway infrastructure adds approximately 12 microseconds compared to direct PS Gateway access for high-frequency sessions.

**TLS Encryption**: When TLS encryption is enabled (recommended for secure connections), it adds single-digit microseconds of latency per roundtrip due to encryption/decryption operations.

**Redundancy Link Latency**: When the redundancy link is active during failover scenarios, it introduces over 50 microseconds of additional latency.

**Latency Profile Summary**: The cumulative latency overhead makes the FIX Gateway unsuitable for ultra-low latency high-frequency trading strategies that require sub-millisecond response times. However, for institutional trading strategies operating on millisecond or longer timeframes, the latency overhead is typically acceptable given the implementation advantages.

### Throughput

The FIX Gateway operates under Low Frequency session throughput constraints:

- **LF Session Limits**: Maximum throughput is constrained by LF session limits, which are lower than High Frequency (HF) session limits
- **Institutional Trading Suitability**: The throughput is suitable for moderate-frequency institutional trading activities
- **Multiple Session Support**: Participants can establish multiple concurrent FIX sessions to increase aggregate throughput capacity
- **No HF Session Access**: FIX Gateway does not provide access to High Frequency session types (HF Light, HF Full, HF Ultra)

For participants requiring higher throughput for market making or high-frequency strategies, direct ETI connections with HF sessions are the appropriate choice.

## Session Management

### Logon and Logout

FIX Gateway sessions follow standard FIX session management protocols:

**Logon Process**:
- Participant sends standard FIX Logon message (MsgType=A)
- Credentials include username and password
- Password encryption supported using public key encryption
- Exchange assigns unique Session ID upon successful authentication
- Gateway responds with Logon acknowledgment

**Logout Process**:
- Graceful termination via Logout message (MsgType=5)
- Outstanding orders can be configured to remain active or be automatically canceled
- Sequence numbers preserved for potential session recovery
- Clean session state maintained for next logon

### Sequence Number Management

The FIX Gateway implements strict sequence number tracking as required by the FIX protocol:

- **MsgSeqNum (tag 34)**: Every message includes a sequence number
- **Bidirectional Tracking**: Both inbound (client to gateway) and outbound (gateway to client) sequence numbers are maintained independently
- **Gap Detection**: The gateway automatically detects sequence number gaps indicating missing messages
- **Continuous Sequence**: Sequence numbers increment continuously across session disconnects and reconnects

Proper sequence number management is critical for ensuring message reliability and detecting communication failures.

### Gap Fill and Recovery

When message gaps are detected, the FIX Gateway supports standard FIX recovery mechanisms:

**ResendRequest Message**:
- Client or gateway can request retransmission of specific message ranges
- BeginSeqNo and EndSeqNo tags specify the range to resend
- Gateway retrieves and retransmits requested messages

**SequenceReset Message**:
- **Gap Fill Mode** (GapFillFlag=Y): Used to skip over administrative messages that don't require retransmission
- **Reset Mode**: Used to reset sequence numbers to a new starting value
- NewSeqNo (36) tag specifies the next expected sequence number

**Duplicate Detection**:
- PossDupFlag (43) = "Y" marks potentially duplicate messages during recovery
- Clients must be prepared to handle duplicate ExecutionReports idempotently

**Gap Testing**:
- Participants can intentionally create gaps for testing recovery procedures
- Submit orders via another interface (direct ETI or GUI) to trigger gap detection on the FIX session
- Verify that gap recovery procedures operate correctly before production use

### Connection Recovery

The FIX Gateway supports robust connection recovery procedures:

1. **Reconnection**: Client reconnects using the same Session ID
2. **State Reconciliation**: Gateway maintains session state during disconnection period
3. **Message Recovery**: All potentially missing application messages are available for resend
4. **Order State Synchronization**: Gateway provides current state of all active orders via ExecutionReports
5. **Sequence Number Continuity**: Sequence numbers continue from pre-disconnect values

Proper connection recovery implementation is essential for maintaining reliable trading operations during network disruptions.

## FIX Message Mapping to ETI

### Order Management Message Mapping

The FIX Gateway provides direct mapping between FIX order management messages and their ETI equivalents:

| FIX Message | ETI Equivalent | Notes |
|------------|----------------|-------|
| NewOrderSingle (D) | NewOrderSingle / NewOrderSingleMultiLeg | Order submission for single or multi-leg instruments |
| OrderCancelRequest (F) | DeleteOrder | Order cancellation by ClOrdID or OrderID |
| OrderCancelReplaceRequest (G) | ModifyOrder | Price/quantity modification of existing order |
| ExecutionReport (8) | ExecutionReport | Order acknowledgment, fill, rejection responses |
| BusinessMessageReject (j) | Business Message Reject | Application-level rejection with reason code |

This mapping enables standard FIX clients to perform essential trading operations without understanding ETI-specific message structures.

### Key Field Mapping

Critical fields are mapped consistently between FIX and ETI protocols:

**ExecType (150)**: Maps directly between FIX and ETI execution types
- New (0), Partial Fill (1), Fill (2), Canceled (4), Replaced (5), Rejected (8)

**OrdStatus (39)**: Order status codes map directly
- New (0), Partially Filled (1), Filled (2), Canceled (4), Rejected (8)

**RequestTime**: Available in both protocols for order entry timestamps

**PartyID Fields**: Mapped with appropriate source and role identifiers
- PartyIDSource and PartyRole tags provide context for party identification

**Price and Quantity**: Direct numeric mapping with appropriate decimal precision

### Feature Differences and Limitations

Several advanced T7 features are NOT available through the FIX Gateway:

**Strategy Creation**: Multi-leg instrument definition and strategy creation are not supported via FIX. Strategies must be pre-defined by the exchange or submitted via ETI.

**CLIP (Client Liquidity Improvement Process)**: This order type for internalizing client flow is not accessible via FIX Gateway.

**Advanced Quote Management**: Some sophisticated quoting functions available in ETI are not exposed through FIX.

**High Frequency Sessions**: FIX Gateway only supports Low Frequency (LF) sessions. HF Light, HF Full, and HF Ultra sessions require direct ETI connections.

**TES Advanced Features**: Certain advanced Trade Entry Service features are not available via FIX.

Participants requiring these advanced features must use direct ETI connections to access the full T7 feature set.

## FIX vs ETI Decision Matrix

Choosing between FIX Gateway and direct ETI connections requires evaluating multiple factors:

| Criterion | FIX Gateway | ETI Direct |
|-----------|-------------|------------|
| Protocol familiarity | Industry standard, widely known | Proprietary, requires specific development |
| Latency | Higher (protocol translation + LF routing) | Lowest possible via PS Gateway |
| Max throughput | LF rates (moderate frequency) | Up to 250 TPS (HF Ultra session) |
| Implementation effort | Lower (existing FIX libraries available) | Higher (custom binary protocol implementation) |
| Feature completeness | Core trading functions only | Full T7 feature set including advanced capabilities |
| Co-location required | No (can connect remotely) | Yes (for HF sessions and optimal latency) |
| Session types available | LF only | HF Light/Full/Ultra, LF, Back-Office |
| Multi-partition access | Yes (via LF routing to all partitions) | Yes (LF) or partition-specific (HF) |
| Typical users | Institutional buy-side, traditional brokers | HFT firms, market makers, proprietary traders |

**Use FIX Gateway when**:
- Rapid deployment is priority
- Existing FIX infrastructure can be leveraged
- Latency requirements are measured in milliseconds, not microseconds
- Trading frequency is moderate (institutional-style)
- Co-location investment is not justified

**Use Direct ETI when**:
- Minimum latency is critical
- High throughput is required (market making, HFT)
- Advanced T7 features are needed
- Co-location infrastructure is available
- Development resources for proprietary protocol are available

## Migration Path: FIX to ETI

Participants can migrate from FIX Gateway to direct ETI connections incrementally:

**Parallel Operation**: Run FIX and ETI sessions simultaneously during the transition period. This allows testing ETI implementation while maintaining production FIX connectivity.

**Superset Functionality**: ETI provides a superset of FIX functionality, ensuring no capability is lost during migration.

**Unified Order Requests**: T7 Release 12.0 and later introduced unified order request messages that simplify ETI implementation by providing consistent message formats across order types.

**Simulation Environment**: Deutsche Boerse provides a simulation environment where participants can test ETI implementations thoroughly before production migration.

**Phased Rollout**: Migrate specific trading desks, strategies, or instrument classes incrementally rather than switching all activity simultaneously.

**Reversibility**: During transition, the ability to maintain both FIX and ETI sessions provides a rollback option if issues arise.

This migration flexibility allows organizations to optimize their connectivity strategy over time as trading requirements evolve.

## Connection Options

Deutsche Boerse offers multiple connectivity options for FIX Gateway access:

**Leased Lines**: Dedicated point-to-point connections provide consistent latency and bandwidth. Suitable for participants requiring reliable connectivity without co-location.

**10 Gbit/s Cross-Connects**: High-bandwidth connections available within co-location facilities for participants with servers in Deutsche Boerse data centers.

**Web Access**: Eurex Trader GUI and Admin GUI provide complementary web-based interfaces for manual trading, monitoring, and administration alongside automated FIX connectivity.

**Standard and Enhanced Bandwidth**: Multiple bandwidth tiers are available to match participant requirements and budget constraints.

**Redundant Connectivity**: Dual leased-line configurations provide network redundancy for mission-critical trading operations.

The choice of connectivity option depends on latency requirements, throughput needs, and infrastructure investment capacity.

---

[Back to Chapter 4 Overview](README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [ETI Deep Dive](eti.md)
