---
layout: default
title: "3. Network Infrastructure"
nav_order: 3
parent: Chapters
---

# Chapter 3: Network Infrastructure and Co-Location

[<< Previous: Chapter 2 - T7 Architecture](../02-t7-architecture/README.md) | [Next: Chapter 4 - Trading Interfaces >>](../04-trading-interfaces/README.md)

## Introduction

In high-frequency trading, network latency represents the critical differentiator between profitable and unprofitable strategies. A few microseconds of advantage can determine whether a market-making algorithm captures spread or loses to faster competitors. Deutsche Börse's network infrastructure, centered on its co-location facility at Equinix FR2 in Frankfurt, provides institutional participants with direct, deterministic, and ultra-low latency connectivity to the T7 matching engines powering Eurex and Xetra markets.

This chapter examines the network architecture, co-location services, connectivity options, time synchronization infrastructure, and disaster recovery mechanisms that enable high-frequency trading operations at Deutsche Börse. Understanding these infrastructure components is essential for participants designing trading systems that must achieve sub-microsecond precision and maintain resilience across failover scenarios.

## Co-Location Facility

### Equinix FR2 Frankfurt

Deutsche Börse's primary hosting location for T7 matching engines resides at the Equinix FR2 data center in Frankfurt am Main, Germany. The facility's address is Rebstöcker Straße 33, 60326 Frankfurt. This location serves as the nerve center of European derivatives and cash equities trading, housing the production matching engines, gateways, and market data distribution infrastructure for Eurex and Xetra. *(Source: [Deutsche Börse Connectivity Services](https://www.deutsche-boerse.com))*

### Strategic Partnership with Equinix

Since 2010, Deutsche Börse has maintained a strategic partnership with Equinix (Germany) GmbH to operate co-location services for market participants. This long-standing relationship has enabled continuous infrastructure improvements, capacity expansion, and technological evolution to meet the demands of algorithmic and high-frequency trading firms. *(Source: [Eurex Co-Location Services](https://www.eurex.com))*

The Equinix FR2 facility provides carrier-neutral connectivity, enabling participants to select their preferred network service providers for connections to their remote sites, trading desks, or disaster recovery locations. The carrier-neutral model ensures competitive pricing for network services and flexibility in connectivity architecture design.

### Purpose and Benefits

The primary purpose of co-location is to minimize network latency for algorithmic trading participants. By placing trading servers in the same physical data center as the T7 matching engines, participants eliminate wide-area network latency and reduce round-trip order submission times to tens of microseconds. This proximity advantage is essential for:

- **Market making strategies**: Capturing bid-ask spreads requires rapid response to market data updates and minimal order-to-execution latency.
- **Statistical arbitrage**: Identifying and exploiting pricing inefficiencies across correlated instruments demands synchronized market data consumption and simultaneous order submission.
- **Liquidity provision**: Providing competitive quotes requires the ability to update prices rapidly in response to market movements, which is feasible only with co-located infrastructure.

Co-location also provides bandwidth advantages. While remote connections typically operate over standard leased lines with limited capacity, co-located participants connect via 10 Gigabit Ethernet (10GbE) links, providing ample bandwidth for high message rate trading strategies and market data consumption.

## Network Architecture

### Separation of Transaction and Market Data Networks

Deutsche Börse's network architecture implements strict separation between transaction networks (used for order submission and execution) and market data networks (used for distributing EOBI, EMDI, MDI, and RDI feeds). This separation ensures that:

1. **Performance Isolation**: High-volume market data multicast traffic does not compete for bandwidth with latency-sensitive order traffic.
2. **Security Segmentation**: Transaction networks enforce stricter access controls and encryption requirements, while market data networks prioritize throughput and distribution efficiency.
3. **Fault Isolation**: Network issues on the market data distribution layer do not affect order submission paths, maintaining trading continuity even if market data delivery experiences degradation.

This architectural principle extends throughout Deutsche Börse's infrastructure, with physically separate network switches, routers, and network interface cards dedicated to each network type. *(Source: [Deutsche Börse Network Architecture](https://www.deutsche-boerse.com))*

### No Single Point of Failure Design

The network architecture implements comprehensive redundancy at multiple layers:

- **Dual physical network paths**: Eurex and Xetra environments are accessible via distinct physical network pathways, ensuring that a fiber cut or switch failure affecting one path does not render the exchange inaccessible.
- **Side A and Side B infrastructure**: Both transaction and market data networks operate with Side A and Side B redundancy, providing independent paths from participant equipment to matching engines.
- **Geographic redundancy**: Room A and Room B separation (discussed in Chapter 2) extends to network infrastructure, with dedicated network equipment in each room.

This multi-layered redundancy approach ensures that participants can maintain connectivity even during infrastructure failures, planned maintenance, or disaster recovery scenarios. *(Source: [Deutsche Börse High Availability Architecture](https://www.deutsche-boerse.com))*

### 10 Gigabit Latency-Optimized Network

Co-location participants connect to T7 environments via 10 Gigabit Ethernet (10GbE) links. These connections are latency-optimized, utilizing low-latency switches and minimal hop counts between participant equipment and matching engines. The 10GbE bandwidth provides capacity for:

- **Order submission**: Participants generating thousands of orders per second experience no bandwidth constraints.
- **Market data consumption**: EOBI and EMDI feeds can deliver hundreds of thousands of market data messages per second, requiring substantial bandwidth during high-volatility trading periods.
- **Multicast subscriptions**: Participants can subscribe to multiple multicast groups across Side A and Side B without bandwidth limitations.

The latency-optimized network configuration minimizes queuing delays and jitter, ensuring deterministic network behavior. This determinism is critical for high-frequency strategies that depend on consistent, predictable latency profiles. *(Source: [Deutsche Börse Co-Location Connectivity](https://www.deutsche-boerse.com))*

### Distinct Physical Pathways for Eurex and Xetra

Eurex derivatives markets and Xetra cash equities markets are accessible via distinct physical network pathways. This separation ensures that participants trading both asset classes can implement independent connectivity strategies and that network issues affecting one market do not impact the other. For participants trading only Eurex or only Xetra, this design provides assurance that cross-market failures will not disrupt their trading operations. *(Source: [Deutsche Börse Multi-Market Connectivity](https://www.deutsche-boerse.com))*

## CoLo 2.0 Connection Pricing

As of January 2023, Deutsche Börse's Co-Location 2.0 (CoLo 2.0) infrastructure offers 10 Gigabit Ethernet connectivity with the following monthly pricing structure. These fees cover network connectivity for specific data feeds or transaction channels.

### Xetra Market Data Feeds

**Xetra EMDI (Enhanced Market Data Interface)**
- Monthly fee: EUR 6,000
- Description: Real-time order book data for Xetra cash equities, including full order book depth, trade notifications, and instrument status updates. EMDI provides the lowest-latency market data feed for Xetra.
- Use case: High-frequency trading, algorithmic trading, market making on Xetra equities. *(Source: [Deutsche Börse Pricing](https://www.deutsche-boerse.com))*

**Xetra EOBI (Enhanced Order Book Interface)**
- Monthly fee: EUR 7,200
- Description: Standardized market data feed for Xetra using the same protocol as Eurex EOBI, providing order book snapshots, incremental updates, and trade messages.
- Use case: Participants requiring cross-asset market data infrastructure (using EOBI for both Eurex and Xetra), lower-latency market data than standard MDI. *(Source: [Deutsche Börse Pricing](https://www.deutsche-boerse.com))*

**Combined Xetra EMDI & EOBI**
- Monthly fee: EUR 8,400
- Description: Bundled connectivity for both EMDI and EOBI feeds, providing cost savings compared to subscribing to each feed separately (EUR 6,000 + EUR 7,200 = EUR 13,200 individually).
- Use case: Participants requiring redundant market data sources or those consuming both feeds for latency arbitrage or data quality verification. *(Source: [Deutsche Börse Pricing](https://www.deutsche-boerse.com))*

### Xetra Transaction Connectivity

**Xetra Transactions ETI (Enhanced Trading Interface)**
- Monthly fee: EUR 6,000
- Description: Connectivity for order submission, modification, cancellation, and execution reporting on Xetra via the ETI protocol.
- Use case: All active trading participants on Xetra requiring transaction connectivity. *(Source: [Deutsche Börse Pricing](https://www.deutsche-boerse.com))*

These pricing figures reflect the cost of 10GbE network connectivity and do not include rack space, power, cross-connects, or other co-location services, which are priced separately (see Rack Space Pricing section below).

## Network Segments

Deutsche Börse's network architecture is divided into multiple segments, each serving distinct functions and participant types.

### Trading Network (ETI)

The Trading Network provides connectivity for order submission and execution reporting via the Enhanced Trading Interface (ETI) protocol. This network operates using TCP/IP for session-oriented, reliable message delivery. ETI sessions connect to either Partition-Specific (PS) gateways for lowest-latency access or Low-Frequency (LF) gateways for multi-partition access (as discussed in Chapter 2).

**Security**: All ETI connections support TLS 1.3 encryption, ensuring confidentiality and integrity of order data transmitted between participants and the exchange. TLS 1.3 provides forward secrecy, protection against downgrade attacks, and improved performance compared to earlier TLS versions. *(Source: [Deutsche Börse ETI Security](https://www.deutsche-boerse.com))*

**Gateway Types**:
- **PS Gateways (Partition-Specific)**: Ultra-low latency, partition-dedicated gateways for high-frequency participants.
- **LF Gateways (Low-Frequency)**: Multi-partition gateways for participants trading across multiple partitions or those with lower latency requirements.

The Trading Network implements stringent access controls, requiring authentication via session credentials and supporting risk management integration (Advanced Risk Protection, Post-Trade Risk limits) at the network edge.

### Market Data Networks

Market data distribution occurs via dedicated network segments using UDP multicast for efficient one-to-many distribution. Deutsche Börse operates multiple market data feeds, each optimized for different participant needs.

**EOBI (Enhanced Order Book Interface)**:
- Standardized, low-latency market data feed available for both Eurex and Xetra.
- Protocol: Native binary format without FIX or FAST encoding, optimized for minimal processing overhead.
- Delivery: UDP multicast with live-live A/B concept (described below).
- Use case: High-frequency trading, market making, algorithmic trading requiring lowest-latency market data. *(Source: [Eurex EOBI](https://www.eurex.com))*

**EMDI (Enhanced Market Data Interface)**:
- Xetra-specific market data feed providing full order book depth and trade details.
- Protocol: FIX 5.0 SP2 with FAST (FIX Adapted for Streaming) encoding for bandwidth efficiency.
- Delivery: UDP multicast with live-live A/B concept.
- Use case: Xetra-focused participants requiring comprehensive order book visibility. *(Source: [Deutsche Börse EMDI](https://www.deutsche-boerse.com))*

**MDI (Market Data Interface)**:
- Standard market data feed for both Eurex and Xetra, providing top-of-book, trade data, and instrument status.
- Protocol: FIX 5.0 SP2 with FAST encoding.
- Delivery: UDP multicast.
- Use case: Participants requiring reliable market data with broader latency tolerance (typically non-high-frequency firms). *(Source: [Deutsche Börse MDI](https://www.deutsche-boerse.com))*

**RDI (Reference Data Interface)**:
- Provides instrument reference data, including contract specifications, trading calendar information, and configuration parameters.
- Protocol: FIX 5.0 SP2 with FAST encoding.
- Delivery: UDP multicast.
- Use case: All participants requiring instrument metadata for order validation, symbol mapping, and configuration management. *(Source: [Deutsche Börse RDI](https://www.deutsche-boerse.com))*

**Live-Live A/B Concept**: Market data feeds are distributed via two independent multicast streams (Side A and Side B), transmitted over separate physical network paths. Both streams carry identical data simultaneously, allowing participants to subscribe to both for redundancy. In the event of network issues affecting one side, the other side continues delivering market data without interruption. Each side uses different multicast addresses, enabling participants to distinguish between sources and implement failover logic. *(Source: [Deutsche Börse Market Data Architecture](https://www.deutsche-boerse.com))*

### GUI Network

The GUI Network provides connectivity for graphical user interface applications, including:

- **Eurex Trader GUI**: Web-based trading interface for Eurex derivatives, supporting manual trading, order management, and portfolio monitoring.
- **T7 Web Apps**: Administrative and operational web applications for session management, risk configuration, and reporting.

GUI Network access is typically provided via standard HTTPS connections and does not require the ultra-low latency infrastructure used for algorithmic trading. *(Source: [Eurex Trader GUI](https://www.eurex.com))*

### Back-Office Network

The Back-Office Network supports administrative and operational functions, including:

- **Account management**: Clearing member and participant administration.
- **Trade reporting**: Access to executed trade data, transaction logs, and audit trails.
- **Drop copy services**: Real-time copies of order and execution messages for back-office systems, risk management platforms, and compliance monitoring.
- **Risk configuration**: Management of Advanced Risk Protection (ARP) settings, position limits, and credit controls.

Back-Office connectivity is separate from production trading networks, ensuring that administrative activities do not impact latency-sensitive trading operations. *(Source: [Deutsche Börse Back-Office Connectivity](https://www.deutsche-boerse.com))*

## Connection Types

Deutsche Börse offers multiple connectivity options to accommodate diverse participant profiles, latency requirements, and operational models.

### Co-Location (10GbE)

Co-location connectivity provides the lowest latency access to T7 matching engines. Participants deploy their trading servers, market data handlers, and network equipment within the Equinix FR2 data center, connecting to Deutsche Börse's network via 10 Gigabit Ethernet links.

**Advantages**:
- Sub-microsecond network latency to matching engines.
- 10GbE bandwidth supporting high message rates and market data throughput.
- Direct physical proximity to exchange infrastructure.
- Deterministic network behavior due to minimized hop counts.

**Requirements**:
- Rack space rental at Equinix FR2 (see Rack Space Pricing below).
- 10GbE network interface cards in participant servers.
- Cross-connect fees for connections between participant racks and Deutsche Börse network equipment.

Co-location is the standard connectivity model for high-frequency trading firms, market makers, and proprietary trading firms requiring competitive latency performance. *(Source: [Deutsche Börse Co-Location Services](https://www.deutsche-boerse.com))*

### Leased Lines

Leased lines provide dedicated, point-to-point network connectivity between participant sites (typically in London, Zurich, Paris, or other European financial centers) and the Equinix FR2 data center. Deutsche Börse orders leased lines on behalf of participants, ensuring compatibility and operational support.

**Standard Leased Lines (7 Mbit/s)**:
- Bandwidth: 7 Mbit/s (sufficient for low-to-moderate message rate trading).
- Use case: Buy-side participants, smaller trading firms, back-office connectivity.
- Ordering: Deutsche Börse coordinates with network service providers to provision leased lines.

**Enhanced Leased Lines (80 Mbit/s and 200 Mbit/s)**:
- Bandwidth: 80 Mbit/s or 200 Mbit/s (supporting higher message rates and market data throughput).
- Use case: Active algorithmic trading firms not requiring co-location, multi-strategy funds, larger broker-dealers.
- Ordering: Deutsche Börse coordinates provisioning.

**Dual Lines for High Availability**: Participants seeking maximum availability can order dual leased lines from different network service providers. This configuration ensures that if one provider experiences a network outage or service degradation, the participant can failover to the second leased line, maintaining connectivity to T7. Deutsche Börse supports dual-line configurations and provides guidance on failover configuration. *(Source: [Deutsche Börse Leased Line Connectivity](https://www.deutsche-boerse.com))*

Leased lines introduce higher latency compared to co-location (typically several milliseconds for intra-European connections), making them unsuitable for high-frequency strategies but acceptable for medium-frequency algorithmic trading, portfolio trading, and buy-side execution.

### iAccess (VPN via IPSec)

iAccess provides an Internet-based connectivity alternative using IPSec (Internet Protocol Security) VPN tunnels. This option enables participants to connect to T7 without requiring dedicated leased lines or co-location infrastructure.

**Advantages**:
- Lower cost compared to leased lines.
- Rapid provisioning (can be activated within days rather than weeks).
- Suitable for testing, simulation environment access, and non-production use cases.

**Disadvantages**:
- Higher and more variable latency due to Internet routing.
- Bandwidth and throughput depend on Internet connectivity quality.
- Not suitable for latency-sensitive or high-frequency trading.

**Use Cases**:
- Access to simulation environments (SIM and SES) for development and testing.
- Back-office and administrative connectivity.
- Disaster recovery scenarios where primary leased line connectivity is unavailable.
- New participants conducting initial certification testing before ordering leased lines or co-location.

iAccess connections utilize standard IPSec protocols, enabling participants to deploy commercial VPN gateways or software VPN clients. Deutsche Börse provides IPSec configuration parameters and supports common IPSec implementations. *(Source: [Deutsche Börse iAccess Connectivity](https://www.deutsche-boerse.com))*

## PTP Time Synchronization

Accurate and precise time synchronization is essential for high-frequency trading, regulatory timestamping requirements, and market data sequence reconstruction. Deutsche Börse offers Precision Time Protocol (PTP) services to co-located participants, providing sub-microsecond and sub-nanosecond time accuracy.

### Standard PTP

Standard PTP, defined by IEEE 1588-2008, delivers sub-microsecond time accuracy with best-case synchronization precision of approximately ±50 nanoseconds.

**Infrastructure**:
- Dedicated 1 Gbps Single-Mode Fiber (SMF) cross-connects between participant equipment and Deutsche Börse PTP grandmaster clocks.
- Participants install PTP-capable network interface cards (NICs) or dedicated PTP appliances in their servers.

**Pricing**:
- Monthly fee: EUR 400 per PTP cross-connect.

**Use Cases**:
- Regulatory timestamping: MiFID II and MiFIR regulations require nanosecond-precision timestamps for certain order and execution events.
- Market data timestamp alignment: Synchronizing market data processing across multiple servers or strategies.
- Latency measurement: Accurate timestamping enables participants to measure order-to-execution latency, network delays, and strategy performance.

Standard PTP is suitable for most algorithmic trading participants requiring high-precision time synchronization. *(Source: [Deutsche Börse PTP Services](https://www.deutsche-boerse.com))*

### White Rabbit Protocol

White Rabbit Protocol, developed at CERN (European Organization for Nuclear Research), extends standard PTP to achieve sub-nanosecond accuracy (typically <1 nanosecond) with picosecond precision. White Rabbit accomplishes this through:

- **Fully deterministic Ethernet network**: Eliminates variable queuing delays by implementing time-division multiplexing at the physical layer.
- **BiDi SFPs (Bidirectional Small Form-Factor Pluggables)**: Single-fiber bidirectional transceivers that eliminate asymmetry in transmit/receive paths, a major source of timing error in standard Ethernet.
- **Enhanced phase-locked loop algorithms**: Provide superior frequency stability and synchronization convergence compared to standard PTP.

**Performance**:
- Time accuracy: <1 nanosecond (sub-nanosecond).
- Time precision: Picosecond-level stability.
- Use case: Ultra-high-frequency trading strategies requiring the absolute lowest timing uncertainty, research applications, participants with strict regulatory timestamp requirements.

White Rabbit Protocol is offered as a premium time synchronization service for participants who require timing accuracy beyond standard PTP capabilities. *(Source: [Deutsche Börse White Rabbit Time Synchronization](https://www.deutsche-boerse.com))*

### GPS Antenna Roof Space

For participants requiring GPS-based time synchronization (as a complement to or alternative to PTP), Deutsche Börse offers GPS antenna roof space at Equinix FR2.

**Pricing**:
- Monthly fee: EUR 850 per GPS antenna location.

**Description**:
- Roof-mounted GPS antenna locations with cabling to participant racks.
- Participants supply their own GPS receivers and antennas.
- GPS provides independent time source, enabling participants to validate PTP synchronization or implement GPS-only time distribution.

**Use Cases**:
- Redundant time source for critical trading systems.
- Validation of PTP synchronization accuracy.
- Participants with existing GPS-based time distribution infrastructure.

GPS time synchronization typically achieves accuracy in the range of 10-100 nanoseconds, making it less precise than standard PTP or White Rabbit but sufficient for many regulatory and operational requirements. *(Source: [Deutsche Börse GPS Antenna Services](https://www.deutsche-boerse.com))*

## High Precision Timestamps (HPT)

High Precision Timestamps (HPT) provide nanosecond-precise timestamps for order and execution events, captured at the network boundary between participant connections and T7 infrastructure. HPT services enable participants to measure latency, analyze execution quality, and meet regulatory timestamping obligations without deploying their own nanosecond-precision timestamping infrastructure.

### Capture Point and Precision

HPT timestamps are captured at the network boundary as messages enter Deutsche Börse's infrastructure. This capture point represents the earliest moment the exchange observes a participant's message, providing an authoritative timestamp that is independent of participant clock accuracy. Timestamps are generated using hardware-synchronized clocks with nanosecond precision, ensuring consistency across all captured events. *(Source: [Deutsche Börse HPT Services](https://www.deutsche-boerse.com))*

### HPT Executions

HPT Executions provides nanosecond timestamps exclusively for executed orders. This service captures:

- Order submission timestamp (when the order entered Deutsche Börse's network).
- Execution timestamp (when the order matched against a counter-order).
- Execution latency (time difference between submission and execution).

**Use Cases**:
- Execution quality analysis: Measuring how quickly orders execute after submission.
- Regulatory reporting: Providing nanosecond-precise timestamps for executed trades to satisfy MiFID II/MiFIR requirements.
- Strategy performance measurement: Analyzing fill rates and execution speeds for different order types and market conditions.

HPT Executions is suitable for participants primarily interested in execution performance rather than comprehensive order lifecycle tracking. *(Source: [Deutsche Börse HPT Executions](https://www.deutsche-boerse.com))*

### HPT All

HPT All extends timestamp capture to all order lifecycle events, including:

- Order additions (new order submissions).
- Order modifications (price changes, quantity changes).
- Order deletions (cancellations).
- Order executions (full or partial fills).

**Use Cases**:
- Comprehensive latency analysis: Understanding processing delays for order modifications and cancellations in addition to submissions and executions.
- Algorithmic strategy debugging: Identifying bottlenecks in order management logic by comparing intended order actions to actual execution.
- Regulatory compliance: Providing complete audit trail with nanosecond timestamps for all order events.

HPT All generates significantly more data than HPT Executions, as it captures every order state change. Participants must ensure adequate storage and processing capacity for HPT All data consumption. *(Source: [Deutsche Börse HPT All](https://www.deutsche-boerse.com))*

### Delivery Format and Schedule

HPT data is delivered in CSV (Comma-Separated Values) format, providing straightforward parsing and integration with standard data analysis tools. Files are delivered on a T+1 basis, meaning that data for trading day T is available on the following business day (T+1). This delivery schedule supports post-trade analysis, compliance reporting, and strategy backtesting but is not suitable for real-time monitoring (participants requiring real-time latency monitoring must implement their own timestamping infrastructure). *(Source: [Deutsche Börse HPT Delivery](https://www.deutsche-boerse.com))*

### Availability

HPT services are available for:

- **Eurex**: All Eurex derivatives products.
- **Xetra**: All Xetra cash equities.
- **EEX**: European Energy Exchange commodity and energy products.

This broad availability ensures that participants trading across multiple asset classes can maintain consistent timestamping and latency measurement methodologies. *(Source: [Deutsche Börse HPT Availability](https://www.deutsche-boerse.com))*

## Rack Space Pricing (Equinix FR2)

Rack space at Equinix FR2 is priced based on power allocation, measured in kilowatts (kW) or kilovolt-amperes (kVA). As of January 2023, the following monthly pricing applies:

### Rack Space and Power Tiers

**3 kVA Rack**
- Monthly fee: EUR 2,330
- Description: Suitable for small deployments with limited power requirements (e.g., single trading server, network equipment, market data appliance).
- Use case: Smaller trading firms, testing infrastructure, low-frequency algorithmic trading.

**4 kVA Rack**
- Monthly fee: EUR 2,870
- Description: Standard deployment size for moderate trading operations (e.g., dual trading servers for redundancy, market data processing servers, network switches).
- Use case: Medium-sized trading firms, single-strategy high-frequency operations.

**5 kVA Rack**
- Monthly fee: EUR 3,390
- Description: Larger deployment supporting multiple trading servers, extensive market data infrastructure, or GPU-based computation.
- Use case: Multi-strategy trading firms, market makers, larger proprietary trading operations.

**6 kVA Rack**
- Monthly fee: EUR 3,910
- Description: High-power deployment for compute-intensive strategies or participants deploying multiple trading systems within a single rack.
- Use case: High-frequency trading firms with complex multi-asset strategies, machine learning-based trading, extensive backtesting infrastructure.

These fees include:
- Physical rack space in Equinix FR2.
- Power distribution (up to the specified kVA allocation).
- Cooling for allocated power consumption.
- Physical security and access control.
- 24/7 facility monitoring and support.

Fees do not include network connectivity (see CoLo 2.0 Connection Pricing), cross-connects, or additional services. *(Source: [Deutsche Börse Rack Space Pricing](https://www.deutsche-boerse.com))*

### Cross-Connect Pricing

Cross-connects are physical fiber or copper cables connecting participant equipment to Deutsche Börse network infrastructure or to other participants within the data center.

**Standard Cross-Connect**
- Monthly fee: EUR 150 per cross-connect.
- Description: Single fiber or copper connection between participant rack and Deutsche Börse network equipment (e.g., ETI trading network, market data network).
- Use case: Every co-located participant requires at least one cross-connect for trading connectivity and typically additional cross-connects for market data feeds and redundancy.

Participants deploying redundant connectivity (Side A and Side B) require multiple cross-connects, as each network side uses independent physical cabling. For example, a participant connecting to ETI Side A, ETI Side B, EMDI Side A, EMDI Side B, and PTP time synchronization would require five cross-connects, totaling EUR 750 per month. *(Source: [Deutsche Börse Cross-Connect Pricing](https://www.deutsche-boerse.com))*

## Disaster Recovery

Deutsche Börse operates comprehensive disaster recovery (DR) and business continuity infrastructure to ensure market availability during extraordinary events.

### Regular DR Tests

Deutsche Börse conducts regular disaster recovery tests to validate failover procedures, backup system readiness, and operational recovery processes. Recent notable DR tests include:

- **March 2025**: Scheduled disaster recovery test for Eurex production environment.
- **June 2023**: Eurex disaster recovery test, simulating failover to backup infrastructure.

During DR tests, the production matching engines at Equinix FR2 (Room A) are rendered inaccessible, simulating a catastrophic failure of the primary data center room. Matching engines fail over to Room B (or in full-scale DR scenarios, to a geographically separate disaster recovery site). *(Source: [Deutsche Börse Disaster Recovery](https://www.deutsche-boerse.com))*

### Co-Location Accessibility During DR Tests

Importantly, co-located participant infrastructure remains accessible during disaster recovery tests. While the back-end matching engines may fail over to Room B or an alternate site, co-located participants retain access to their equipment, enabling them to monitor failover behavior, adjust connectivity configurations, and validate their own disaster recovery procedures.

This design ensures that participants can maintain operational control and visibility even during simulated or actual disaster scenarios. Participants should implement their own DR testing aligned with Deutsche Börse's DR schedule to validate end-to-end failover readiness. *(Source: [Deutsche Börse DR Testing](https://www.deutsche-boerse.com))*

### Network Operations Team

Deutsche Börse's Network Operations Team monitors network infrastructure 24 hours per day, 7 days per week, 365 days per year. This continuous monitoring provides:

- **Proactive issue detection**: Identifying network performance degradation, hardware failures, or connectivity issues before they impact participants.
- **Automatic corrective actions**: Deploying automated failover mechanisms, rerouting traffic, or activating backup infrastructure in response to detected issues.
- **Participant communication**: Notifying participants of network events, planned maintenance, or service disruptions via email, web portal announcements, and emergency contact procedures.

The Network Operations Team coordinates with Equinix facility management, network service providers, and Deutsche Börse's technical operations teams to maintain high availability and rapid incident resolution. *(Source: [Deutsche Börse Network Operations](https://www.deutsche-boerse.com))*

## Contact Information

Participants requiring connectivity services, technical support, or co-location assistance can contact the following resources:

### Equinix FR2 Data Center

**Contact**: Elke Ay
**Email**: elke.ay@eu.equinix.com
**Phone**: +49 151 61352692
**Role**: Equinix account management for Deutsche Börse co-location services

Elke Ay provides support for:
- Rack space provisioning and availability inquiries.
- Physical access coordination and security escort requests.
- Facility-specific questions (power, cooling, physical infrastructure).
- Cross-connect ordering and installation coordination.

### Deutsche Börse Connectivity Services

**Email**: accessproducts@deutsche-boerse.com
**Phone**: +49 69 21111690
**Description**: Central contact for all Deutsche Börse connectivity services, including:
- Co-location 2.0 connectivity orders (10GbE connections for ETI, market data feeds).
- Leased line provisioning and configuration.
- iAccess VPN setup and support.
- PTP time synchronization services.
- HPT (High Precision Timestamps) services.
- Network troubleshooting and technical support.

Participants planning connectivity deployments, migrations, or expansions should contact accessproducts@deutsche-boerse.com as the primary point of contact. *(Source: [Deutsche Börse Contact Information](https://www.deutsche-boerse.com))*

## Conclusion

Deutsche Börse's network infrastructure, centered on the Equinix FR2 co-location facility in Frankfurt, provides high-frequency trading participants with deterministic, ultra-low latency connectivity to Eurex and Xetra markets. The architecture's separation of transaction and market data networks, comprehensive redundancy through Side A/Side B and Room A/Room B configurations, and diverse connectivity options (co-location, leased lines, iAccess) accommodate participants across the spectrum from high-frequency market makers to buy-side algorithmic traders.

Time synchronization services, ranging from standard PTP (sub-microsecond) to White Rabbit Protocol (sub-nanosecond), enable participants to meet regulatory timestamping requirements and measure latency with exceptional precision. High Precision Timestamps (HPT) services provide nanosecond-accurate order and execution timestamps for post-trade analysis and compliance reporting.

Understanding the network infrastructure options, pricing, and operational characteristics enables participants to design connectivity strategies aligned with their latency requirements, redundancy needs, and budget constraints. The following chapters will build on this infrastructure foundation, exploring the trading interfaces (ETI, FIX) and market data protocols (EOBI, EMDI, MDI, RDI) that operate over these network connections.

---

[<< Previous: Chapter 2 - T7 Architecture](../02-t7-architecture/README.md) | [Next: Chapter 4 - Trading Interfaces >>](../04-trading-interfaces/README.md)
