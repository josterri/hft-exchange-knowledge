# Chapter 11: Simulation & Testing Environments

## Introduction

Deutsche Börse provides a comprehensive multi-tier testing infrastructure designed to ensure participants can thoroughly validate their trading systems before deploying to production. This infrastructure encompasses both dedicated on-demand testing capabilities and shared release simulation environments that mirror production configurations. The testing framework supports the full spectrum of preparation activities, from initial development and connectivity testing to mandatory release readiness validation and disaster recovery procedures. Understanding the architecture, capabilities, and requirements of these simulation environments is essential for maintaining operational readiness and compliance with exchange participation standards.

## T7 Cloud Simulation

T7 Cloud Simulation represents Deutsche Börse's on-demand testing solution, launched on August 1, 2025. This service provides participants with dedicated 24/7 simulation instances accessible via the internet through SSL/IPSEC connectivity. The cloud simulation environment is specifically designed for development and testing activities, operating on a per-hour billing model with automatic termination capabilities to optimize cost efficiency.

Participants access Cloud Simulation through a dedicated login portal at cloudsim.deutsche-boerse.com. The environment provides isolated testing infrastructure where development teams can validate functionality, perform integration testing, and conduct preliminary system checks without impacting other participants or requiring coordination with exchange simulation schedules.

Importantly, T7 Cloud Simulation does not include post-trade environment integration or graphical user interfaces. This streamlined configuration focuses exclusively on the core trading system interfaces, making it ideal for automated testing, development validation, and continuous integration workflows. The absence of post-trade systems allows for simplified setup and reduced complexity during early-stage development and component testing phases.

## T7 Release Simulation

The T7 Release Simulation environment serves as the primary shared testing platform for validating new T7 releases before production deployment. Unlike the dedicated Cloud Simulation, Release Simulation operates as a shared environment that precisely mirrors the production architecture, configuration, and behavior. This environment provides the definitive validation platform where participants must verify their systems' compatibility with upcoming releases.

Participation in Release Simulation is mandatory for all trading participants prior to each major T7 release. The simulation calendar, published on eurex.com, establishes the testing schedule, coordination windows, and milestone dates for each release cycle. This calendar ensures all participants can plan their testing activities and allocate resources appropriately.

A critical advantage of Release Simulation is its persistence beyond the production go-live date. After a new release enters production, the Release Simulation environment remains available configured with that version, enabling ongoing testing, system validation, and troubleshooting activities without requiring production connectivity. This continued availability supports development of new features, investigation of production issues in a controlled environment, and training activities.

## Simulation Architecture

The T7 simulation environments replicate the production partition structure to ensure testing accurately reflects the operational environment. The architecture has evolved from the original 5-partition design to the current 6-partition configuration, distributing products across specialized trading partitions aligned with asset classes and market segments.

### Partition Structure

The current partition allocation mirrors production topology:

**Partition 1**: Xetra German equities and related products
**Partition 2**: Eurex equity derivatives and certain fixed income derivatives
**Partition 3**: Eurex equity derivatives and certain fixed income derivatives
**Partition 4**: Eurex interest rate derivatives and fixed income products
**Partition 5**: Reserved for specialized products and expansion
**Partition 55**: Xetra non-German equities (added February 16, 2024)
**Partition 6**: Eurex FX products (FCUR/OCUR contracts)

This partition distribution ensures that simulation testing accurately reflects the production system's load distribution, routing logic, and partition-specific behavior. Products are allocated to partitions based on their asset class, with equity derivatives, fixed income derivatives, and FX products each mapped to their respective specialized partitions.

### Differences from Production

While simulation environments closely mirror production, several important differences exist. Simulation systems are explicitly not designed for performance testing at production scale. The infrastructure capacity, latency characteristics, and throughput capabilities differ from production systems. Participants planning large-volume testing or performance validation must contact their Technical Key Account Manager (TKAM) to arrange appropriate testing conditions or access to specialized performance testing facilities.

The simulation environment uses modified market data identifiers, separate multicast groups, and isolated network segments to prevent any possibility of simulation data appearing in production systems or vice versa. Certificate requirements, while following the same security standards, use separate certificate authorities and validation chains for simulation versus production access.

## Available Interfaces

The simulation environments provide access to the complete suite of T7 trading and market data interfaces, ensuring comprehensive testing coverage:

### Trading Interfaces

**ETI (Enhanced Trading Interface)**: The primary asynchronous TCP/IP-based trading protocol supporting order entry, modification, deletion, and mass operations. ETI in simulation provides full functional parity with production, including all message types, business validation rules, and error handling behavior.

**FIX Gateway**: Supporting both FIX 4.2 and FIX 4.4 protocols, the FIX Gateway provides standards-based connectivity for participants preferring FIX over the native ETI protocol. As of March 10, 2023, TLS encryption became mandatory for all FIX Gateway connections in simulation environments, establishing the security baseline before the production requirement took effect.

### Market Data Interfaces

**EOBI (Eurex Order Book Interface)**: Provides real-time Level 2 market data via multicast with A/B channel redundancy. EOBI delivers complete order book depth, trade notifications, and market state changes with microsecond-precision timestamps.

**EMDI (Eurex Market Data Interface)**: Delivers formatted market data optimized for display and analysis applications. EMDI provides both A and B multicast channels, ensuring redundant data delivery for high-availability market data consumption.

**MDI (Market Data Interface)**: Supports Xetra market data distribution with multicast A/B redundancy, providing order book updates, trade data, and market statistics for equity markets.

**RDI (Reference Data Interface)**: Distributes product specifications, instrument definitions, trading calendar information, and configuration parameters required for accurate order validation and market data interpretation.

All multicast interfaces provide redundant A and B channels, enabling participants to validate their failover logic and redundant data consumption architectures during simulation testing.

## Testing Capabilities

The simulation environments provide sophisticated capabilities beyond simple connectivity and message exchange, enabling comprehensive functional and scenario-based testing:

### Market Control Features

Participants with appropriate permissions can create and manage custom orderbooks, allowing testing of specific product configurations, contract specifications, or market structure scenarios. Trading phase control enables manual advancement through trading phases (pre-trading, opening auction, continuous trading, closing auction, post-trading), facilitating validation of phase-specific behavior and phase transition logic.

Product state management allows authorized users to modify instrument states, enabling testing of suspended products, halted instruments, and resumption scenarios. These capabilities ensure participants can validate their systems' responses to all possible market conditions and state transitions.

### Liquidity and Matching Tools

The **Liquidity Generator** provides automated order flow generation, creating synthetic market activity to simulate realistic trading conditions. This tool enables testing under various liquidity scenarios, from thin markets with wide spreads to deep, liquid markets with tight bid-ask spreads.

The **Auto Matcher** automatically executes matching logic, enabling rapid progression through trading scenarios without requiring manual order entry. This capability dramatically accelerates testing cycles for complex multi-leg strategies, aggressive order scenarios, and high-frequency order sequences.

**Trade Reversal** capabilities allow authorized users to unwind executed trades, resetting the market state for iterative testing scenarios. This functionality proves essential for testing error recovery procedures, trade bust handling, and state reconciliation logic.

### Failover and Stress Testing

Simulation supports comprehensive failover testing, enabling participants to validate their disaster recovery procedures and redundant connectivity configurations. Participants can test switching between primary and backup connections, multicast channel failover (A to B), and partition failover scenarios.

**Focus Day** provides scheduled stressed market conditions for capacity and resilience testing. During Focus Day sessions, three designated products experience intensive order flow and trading activity for 10 minutes, followed by a 1-hour period where exceptional market circumstances apply across the entire market. These controlled stress scenarios enable validation of system behavior under peak load conditions.

## Release Simulation Schedule

Each T7 release follows a structured simulation timeline coordinating testing activities across all participants. The schedule typically spans several weeks, providing multiple testing opportunities and escalating validation milestones.

### Timeline Example: T7 14.1 Release

A representative timeline demonstrates the typical progression:

**January 2, 2026**: T7 14.0 enters production
**March 23, 2026**: T7 14.1 Release Simulation begins
**Weeks 1-2**: Initial connectivity testing and basic functional validation
**Weeks 3-4**: Comprehensive functional testing, interface integration validation
**Week 5**: Focus Day stressed market testing
**Week 6**: Weekend simulation sessions for extended validation
**Week 7**: Dress rehearsal simulating production go-live procedures
**Support Windows**: Dedicated connectivity testing windows with TKAM assistance

The simulation calendar published on eurex.com provides precise dates, session times, and specific testing focus areas for each simulation period. Weekend simulation sessions typically provide extended hours and reduced competition for simulation resources, enabling more thorough testing for complex scenarios.

Dress rehearsals simulate the complete production go-live sequence, including the cutover procedures, system initialization, and market opening processes. These rehearsals serve as the final validation checkpoint before production release approval.

## Mandatory Testing Requirements

Deutsche Börse enforces strict mandatory testing requirements to ensure all participants achieve adequate readiness before production release deployment:

### Consultation and Preparation

Participants must complete a **consulting call with Technical Market Readiness (TMR)** staff prior to beginning Release Simulation testing. This consultation reviews the release changes, identifies potential impacts on the participant's systems, and establishes a customized testing plan addressing the participant's specific architecture and trading workflows.

### Testing Milestones

The **end-to-end test** validates complete transaction flows from order submission through execution, clearing confirmation, and settlement integration where applicable. This comprehensive test ensures all system components correctly process the new release's functionality and message formats.

The **connection test** verifies basic connectivity, authentication, session management, and heartbeat handling across all interfaces the participant intends to use in production. This test establishes the foundation for subsequent functional testing activities.

### Readiness Statement

Upon completion of testing, participants must submit a **Readiness Statement** through an online questionnaire accessed via the Member Section portal using their Eurex PIN credentials. This formal declaration confirms the participant has completed all required testing, validated their systems against the new release, and confirmed readiness for production deployment.

The Readiness Statement serves as both a compliance checkpoint and a risk management control, ensuring participants consciously acknowledge their responsibility for validating system compatibility before the production release. Functional preparation activities are mandatory before production system access becomes available for new releases.

## Certificate Requirements

All simulation and production access to T7 systems requires X.509v3 digital certificates issued by the Deutsche Börse Certificate Authority (CA). The certificate infrastructure provides strong authentication and encrypted communication channels for all trading and market data connections.

### Certificate Specifications

Certificates must conform to X.509v3 standards using sha256RSA signature algorithms. The Deutsche Börse CA is the exclusive issuing authority; certificates from external CAs are not accepted for T7 system access.

### Certificate Scope and Segmentation

Separate certificates are required for each combination of market (Eurex, Xetra, EEX), environment (production, simulation, cloud simulation), and access type (trading, market data, GUI). This segmentation provides granular access control and supports the security principle of least privilege.

For example, a participant trading both Eurex derivatives and Xetra equities across production and simulation environments might require:

- Eurex production ETI trading certificate
- Eurex simulation ETI trading certificate
- Xetra production ETI trading certificate
- Xetra simulation ETI trading certificate
- Eurex production market data certificate
- Eurex simulation market data certificate
- Xetra production market data certificate
- Xetra simulation market data certificate

There is no limit on the number of certificates that can be issued per participant account, enabling flexibility for complex architectures with multiple trading systems, backup systems, and development environments.

### Certificate Validation

Wrong or invalid certificates result in immediate access denial. The authentication system performs strict validation of certificate validity periods, signature chains, and revocation status. Participants must monitor certificate expiration dates and initiate renewal processes with sufficient lead time to avoid connectivity disruptions.

Certificate generation and management capabilities are provided through the Member Section portal, where participants can request new certificates, download certificate files, and monitor certificate status and expiration dates.

## T7 GUI Testing

Deutsche Börse provides web-based graphical user interfaces for manual trading, market monitoring, and system administration in the simulation environment:

### Trading and Monitoring GUIs

**Eurex Trader GUI**: Accessible at t7gui.simulation.eurex.com/xeur/index.html, this web-based interface provides full trading functionality for Eurex products including order entry, modification, deletion, position monitoring, and market data display. The Eurex Trader GUI enables manual trading scenarios, visual validation of system behavior, and training activities.

**EEX Simulation GUI**: Available at t7gui.simulation.eurex.com/xeee/index.html, supporting EEX power and commodity products with equivalent functionality to the Eurex Trader interface.

### Administrative GUIs

**T7 Admin GUI**: Provides administrative functions for user management, permission configuration, and account settings. This interface enables configuration of trading parameters, risk limits, and user authorizations in the simulation environment.

**T7 Controller GUI**: Offers market control capabilities for authorized users, including trading phase management, product state control, and market supervision functions available during simulation sessions.

### GUI Launcher

The **T7 GUI Launcher** utilizes getdown technology to provide automatic updates and version management for the GUI applications. This launcher ensures participants always access the correct simulation GUI version without requiring manual downloads or version verification.

The web-based architecture requires only a modern browser with TLS support; no local installation or specialized software is necessary. This accessibility simplifies training, testing, and manual validation activities across distributed teams.

## Market Data in Simulation

Simulation environments provide complete market data distribution via the same protocols and multicast infrastructure used in production:

### Multicast Market Data

EMDI, MDI, and EOBI all operate in simulation with A/B multicast channel redundancy, identical message formats, and equivalent latency characteristics to production. The simulation multicast groups use different IP address ranges to ensure complete isolation from production market data flows.

Participants can validate their market data consumption logic, A/B failover handling, gap detection and recovery, and sequencing algorithms using live simulation market data generated by actual trading activity and supplemented by automated tools like the Liquidity Generator.

### Market Data Failure Testing

The simulation environment supports controlled market data failure scenarios, including simulated partition crashes, multicast channel interruptions, and sequencing anomalies. These scenarios enable participants to validate their error handling, recovery procedures, and redundancy mechanisms.

Market data failure testing typically occurs during dedicated testing windows announced in the simulation calendar, ensuring participants can plan their testing activities and allocate engineering resources appropriately.

### Reference Data

RDI distributes complete reference data in simulation, including product specifications, instrument definitions, trading calendars, and configuration parameters. The reference data reflects the planned production configuration for the upcoming release, enabling participants to validate their product databases, instrument loaders, and configuration management systems against the actual production reference data that will become active on release day.

## Performance and Stress Testing

While simulation environments support comprehensive functional testing, important limitations exist regarding performance and capacity testing:

### Performance Testing Limitations

T7 Cloud Simulation and standard Release Simulation environments are explicitly not designed for production-scale performance testing. The infrastructure capacity, network latency, and throughput characteristics differ from production systems. Latency measurements, throughput benchmarks, and capacity assessments conducted in standard simulation environments do not represent production performance.

### TKAM Coordination Required

Participants requiring performance testing, large-volume scenario validation, or capacity benchmarking must contact their Technical Key Account Manager (TKAM). The TKAM can arrange access to specialized performance testing facilities, coordinate dedicated testing windows, or provide guidance on appropriate testing approaches for capacity validation.

### Focus Day Stress Testing

The scheduled Focus Day sessions provide the primary stress testing capability within the standard simulation environment. During Focus Day, three designated products experience intensive automated order flow for 10 minutes, followed by a 1-hour period of exceptional market circumstances applied across the entire market.

These controlled stress scenarios enable validation of:

- Order processing during high message rates
- Risk check performance under load
- Queue management and flow control handling
- Graceful degradation and backpressure mechanisms
- Error recovery during stressed conditions

Focus Day scenarios, while valuable for resilience testing, still operate within the simulation infrastructure's capacity limits and do not replicate production-scale performance characteristics.

## T7 Market Replay Service

The Market Replay Service provides data recovery capabilities through message retransmission, supporting recovery from data gaps, processing errors, or system interruptions:

### Replay Architecture

Each multicast channel supports at least two replay cycles per trading day. A replay cycle enables participants to request retransmission of historical messages from specific sequence number ranges, recovering data that may have been missed due to packet loss, system downtime, or processing errors.

### Replay Message Format

Replay transmissions are bracketed by **MDReport** messages indicating replay start and completion. These bracket messages enable receiving applications to distinguish replayed historical data from live real-time market data, preventing duplicate processing or state inconsistencies.

The replay request protocol specifies the channel, sequence number range, and delivery parameters. The replay service then retransmits the requested messages in sequence number order, maintaining the original message content and timestamps while adding replay-specific metadata.

### Extended Market Data Service

Market Replay is included as part of the Extended Market Data Service (EMDS) subscription tier. EMDS subscribers receive replay access across all subscribed instruments and channels, providing comprehensive data recovery capabilities without requiring separate subscriptions or additional fees per replay request.

Replay capabilities in simulation mirror production functionality, enabling participants to validate their gap detection algorithms, replay request logic, and duplicate detection mechanisms during simulation testing.

## Disaster Recovery Testing

Deutsche Börse conducts periodic disaster recovery tests using the simulation infrastructure to validate failover procedures and business continuity capabilities:

### DR Test Architecture

Disaster recovery tests simulate complete failover from primary production systems to backup disaster recovery facilities. During DR tests, participants must demonstrate their ability to switch connectivity from primary production interfaces to designated simulation interfaces representing the DR environment.

This interface switching validates that participants' backup connectivity configurations, certificate management for DR systems, and failover automation procedures function correctly under simulated disaster conditions.

### DR Concept Documentation

The comprehensive DR concept document, published annually on the Member Section portal, describes the disaster recovery architecture, failover procedures, participant responsibilities, and testing requirements. This document provides the technical specifications and operational procedures necessary for participants to implement compatible DR capabilities.

### DR Testing Schedule

DR tests follow a published schedule coordinated with the simulation calendar. Participation in DR tests, while not mandatory for all participants, is strongly recommended and required for participants with specific contractual obligations regarding disaster recovery capabilities.

The simulation-based approach to DR testing provides realistic validation without risking production systems or requiring actual disaster scenarios. Participants can validate their DR procedures, measure recovery time objectives (RTO), and verify recovery point objectives (RPO) under controlled conditions.

## Member Section Portal

The Member Section portal serves as the centralized access point for all simulation resources, credential management, and TKAM coordination:

### Portal Capabilities

Through the Member Section, participants can:

- Access the simulation calendar with detailed testing schedules
- Generate and download X.509v3 certificates for all environments
- Manage user credentials and permissions
- Request TKAM consultation sessions
- Submit Readiness Statements and compliance documentation
- Access technical documentation, release notes, and configuration guides
- Monitor system status and maintenance windows

### Credential Management

The Eurex PIN authentication system secures access to all Member Section capabilities. Participants receive PIN credentials during the onboarding process and can manage PIN resets, user additions, and permission assignments through the portal's user management interface.

### Simulation Calendar

The published simulation calendar provides comprehensive visibility into all scheduled testing activities, including:

- Release simulation start and end dates
- Focus Day stress testing sessions
- Weekend simulation availability
- Dress rehearsal schedules
- Connectivity testing support windows
- TKAM availability for consultation

This centralized calendar enables participants to coordinate testing activities with internal development cycles, allocate resources effectively, and ensure adequate preparation time before mandatory testing milestones.

The Member Section portal's integration with certificate generation, TKAM access, and simulation resources creates a unified participant experience, reducing complexity and streamlining the testing preparation process.

---

[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
