# Chapter 12: Developer Onboarding & Resources

## Introduction

Successfully integrating with Deutsche Börse's T7 trading platform requires careful planning, technical expertise, and navigation through a comprehensive onboarding process. This chapter provides a practical roadmap for developers and technical teams getting started with Deutsche Börse's electronic trading infrastructure, covering everything from initial contact through production go-live and beyond.

Whether you're building a proprietary trading system, developing third-party trading software, or integrating existing platforms with Eurex or Xetra markets, understanding the onboarding journey and available resources is critical to a smooth and efficient deployment. The process involves regulatory compliance, technical setup, simulation testing, and coordination with multiple support teams across Deutsche Börse.

This guide synthesizes information from participant manuals, network access documentation, ISV program materials, and technical specifications to provide a comprehensive developer-focused view of the onboarding landscape.

## Getting Started: Step-by-Step

The onboarding process for Deutsche Börse trading platforms follows a structured five-phase approach:

### Phase 1: Initial Contact and Admission Requirements

The journey begins with reaching out to Deutsche Börse's Client Services team at **client.services@eurex.com**. Before technical integration can begin, participants must meet regulatory and business requirements:

**Admission Requirements:**
- **Minimum Equity Capital**: EUR 50,000 unless the entity is a bank or regulated under MiFID II
- **Trader Registration**: All individuals executing trades must be registered
- **Back Office Staff**: Adequate operational support infrastructure
- **Clearing Membership**: Either direct clearing membership or relationship with a clearing member

The electronic registration system **eXAS (Eurex Xetra Application Services)** facilitates the formal admission process. This web-based portal handles applications, documentation submission, and status tracking throughout the admission workflow.

### Phase 2: Compliance and Documentation

Once initial contact is established, participants must complete regulatory and contractual requirements:

- **Exchange Rules**: Review and acknowledgment of Eurex Exchange Rules and Xetra Trading Rules
- **Terms and Conditions**: Execution of participant agreements
- **Fee Regulations**: Understanding of applicable trading, market data, and connectivity fees
- **Due Diligence**: KYC (Know Your Customer) and AML (Anti-Money Laundering) procedures

This phase typically runs in parallel with technical preparation activities. The legal and compliance teams work independently from technical onboarding but both must complete before production access is granted.

### Phase 3: Simulation Phase

Technical teams gain access to simulation environments to develop and test trading systems:

**Simulation Tools Available:**
- **T7 GUI**: Web-based graphical interface for manual testing and familiarization
- **ETI (Enhanced Trading Interface)**: Primary high-performance trading protocol in simulation
- **FIX LF (FIX Lightweight)**: Alternative trading protocol for FIX-based systems
- **Cloud Simulation**: Remote access to simulation environment without dedicated network infrastructure

The simulation environment mirrors production functionality but uses synthetic market data and operates on a separate network infrastructure. This allows developers to build, test, and refine implementations without risk to production systems or capital.

### Phase 4: Technical Setup

Parallel to simulation testing, production technical infrastructure must be prepared:

**Certificate Management:**
- Obtain certificates from Deutsche Börse Certificate Authority (mandatory)
- Separate certificates required for each market, environment, and access type
- TLS 1.3 mandatory for all new connections (TLS 1.2 decommissioning May 2026)

**Network Connectivity:**
- Choose between leased line or internet connectivity with SSL/IPSEC tunneling
- Configure IP addresses (separate allocations for production and simulation)
- Implement firewall rules per Network Access Guide specifications
- Set up monitoring for network health and latency

**Interface Selection:**
- Trading: ETI (binary, low-latency) vs. FIX LF (text-based, FIX compatibility)
- Market Data: EOBI (binary, multicast) vs. EMDI (text-based, request/response)
- Reference Data: RDI (Reference Data Interface) for product specifications and trading calendars

### Phase 5: Production Go-Live

The final phase involves coordination with Technical Key Account Management (TKAM):

- **Pre-Production Testing**: Final validation in production-like environment
- **TKAM Coordination**: Schedule go-live, review technical readiness
- **Capacity Planning**: Confirm order rate limits and system capacity
- **Production Credentials**: Receive production certificates and access credentials
- **Cutover Execution**: Controlled transition from simulation to production
- **Post-Launch Monitoring**: Enhanced monitoring during initial production period

The TKAM team (reachable at **onboarding-team@deutsche-boerse.com**) acts as the primary technical coordinator, ensuring all prerequisites are met and facilitating a smooth transition to live trading.

## Essential Documentation

Deutsche Börse provides extensive technical documentation. For new developers, the following prioritized reading order optimizes learning efficiency:

### Priority 1 (Week 1): Foundation Documents

**Network Access Guide**
- Connectivity options: leased lines vs. internet access
- Certificate requirements and management
- Firewall configuration and IP addressing
- Network architecture diagrams

**Participant Maintenance Manual**
- User account management
- Authentication and authorization
- System access procedures
- Security policies

**Incident Handling Guide**
- Emergency contact procedures
- Incident severity classifications
- Escalation paths
- Business continuity protocols

These documents establish the foundational understanding of how to connect to and maintain access to Deutsche Börse systems.

### Priority 2 (Week 2): Trading Protocols

**ETI Manual** (or **FIX LF Manual** if using FIX)
- Protocol architecture and message flow
- Session management and heartbeating
- Order entry and modification
- Trade capture and execution reporting
- Error handling and recovery procedures

**Message Reference**
- Complete message specifications
- Field definitions and data types
- Enumeration values
- Message sequencing rules

**Participant Simulation Guide**
- Simulation environment access
- Testing procedures and scenarios
- Data characteristics in simulation
- Limitations vs. production environment

Week 2 focus enables developers to begin implementing trading connectivity and understanding protocol-level interactions.

### Priority 3 (Week 3): Market Data

**EMDI/MDI/RDI Manual**
- Market Data Interface architecture
- Subscription management
- Snapshot and incremental updates
- Reference data structures

**EOBI Manual**
- Order Book Interface protocol
- Multicast group management
- Packet structure and sequencing
- Gap detection and recovery

Market data integration typically follows trading connectivity, as reliable data feeds are essential for order management and risk systems.

### Priority 4 (Week 4): Operations and Maintenance

**Emergency Playbook**
- System outage procedures
- Failover and redundancy protocols
- Contact trees for emergency situations
- Recovery time objectives

**Release Notes**
- Recent system changes
- Upcoming releases and migration timelines
- Compatibility impacts
- Deprecated features

**Known Limitations**
- Current system constraints
- Workarounds for known issues
- Feature availability across environments
- Performance characteristics under various conditions

These operational documents ensure teams are prepared for production operations and ongoing system evolution.

## Developer Portal

Deutsche Börse operates a comprehensive developer portal ecosystem:

**Main Developer Portal**: **developer.deutsche-boerse.com**
- Central access point for technical resources
- Registration and account management
- News and announcements
- Community information

**Documentation Portal**: **docs.developer.deutsche-boerse.com**
- Searchable technical documentation
- API specifications and schemas
- Code examples and integration guides
- Version-controlled documentation sets

**API Catalogue**: **console.developer.deutsche-boerse.com/apis**
- Browse available APIs across Deutsche Börse Group
- Interactive API exploration
- Sandbox environments for testing
- Authentication and credential management

**Eurex Reference Data API**
- RESTful API for product specifications
- Trading calendars and holiday schedules
- Contract specifications and lifecycle events
- JSON and XML response formats

The developer portal provides self-service access to many resources, though production credentials and market access still require formal onboarding through Client Services.

## Connectivity Setup

Establishing connectivity to Deutsche Börse trading platforms involves seven critical steps:

### Step 1: Network Access Configuration

**Leased Line Connectivity:**
- Direct fiber connections to Deutsche Börse data centers
- Lowest latency option for high-frequency trading
- Requires physical installation and coordination
- Higher cost but dedicated bandwidth

**Internet Connectivity:**
- SSL/IPSEC tunneling over public internet
- Lower cost alternative for moderate-frequency trading
- Subject to internet routing variability
- Requires VPN configuration per Network Access Guide

### Step 2: Certificate Management

**Deutsche Börse Certificate Authority:**
- All connections MUST use certificates issued by Deutsche Börse CA
- Third-party certificates (e.g., commercial CAs) are NOT accepted
- Certificate request process managed through Member Section

**TLS 1.3 Requirements:**
- TLS 1.3 mandatory for all new connections
- TLS 1.2 supported until May 2026 (Release 14.1 decommissioning)
- Older TLS versions no longer supported

**Approved Cipher Suites (NIST-compliant):**
- secp384r1 (NIST P-384)
- secp521r1 (NIST P-521)
- Ed25519 (Edwards-curve Digital Signature Algorithm)
- Ed448 (Edwards-curve, 448-bit)

**Certificate Granularity:**
- Separate certificates required for each market (Eurex, Xetra, etc.)
- Separate certificates for production vs. simulation
- Separate certificates for different access types (trading, market data, etc.)

This granular certificate model enhances security but requires careful certificate lifecycle management.

### Step 3: Firewall Rules

Configure firewalls according to specifications in the Network Access Guide:
- Allow outbound connections to Deutsche Börse IP ranges
- Permit inbound responses for established sessions
- Configure rules for multicast market data (EOBI/RDI)
- Implement rate limiting and DDoS protection

### Step 4: IP Address Allocation

**Production IP Addresses:**
- Assigned by Deutsche Börse network team
- Static allocation tied to participant ID
- Separate ranges for trading and market data

**Simulation IP Addresses:**
- Distinct from production addresses
- Used exclusively for simulation environment access
- May be shared across multiple test instances

### Step 5: Interface Selection

**Trading Interfaces:**
- **ETI**: Binary protocol, lowest latency, complexity moderate
- **FIX LF**: Text-based FIX protocol, broader ecosystem compatibility

**Market Data Interfaces:**
- **EOBI**: Binary multicast, full order book depth, lowest latency
- **EMDI**: Text-based request/response, simpler integration

**Reference Data:**
- **RDI**: Required for subscribing to multicast market data
- Provides product specifications and trading calendar

Choose interfaces based on latency requirements, existing technology stack, and development resources.

### Step 6: Simulation Testing

Comprehensive testing in the simulation environment should cover:
- Session establishment and teardown
- Order entry across all supported order types
- Modification and cancellation workflows
- Execution and fill handling
- Market data subscription and processing
- Failover and reconnection scenarios
- Error condition handling
- Compliance with exchange rules (e.g., order-to-trade ratios)

**Important**: The simulation environment is NOT designed for performance testing. Contact TKAM for performance and capacity testing arrangements.

### Step 7: TKAM Coordination

Final production readiness review with Technical Key Account Management:
- Review simulation test results
- Confirm technical infrastructure readiness
- Schedule production cutover window
- Receive production credentials
- Establish ongoing support relationship

## SDK and Reference Implementations

Unlike some exchanges, **Deutsche Börse does NOT provide comprehensive SDKs or client libraries**. Developers must implement trading and market data protocols from specifications. However, several reference tools and schemas are available:

**STEP (Sample Tool for ETI Password Encryption):**
- Python script demonstrating ETI password encryption algorithm
- Available from Deutsche Börse support
- Reference implementation for session authentication

**XML FAST Templates:**
- Version 1.1 and 1.2 templates for FAST-encoded market data
- Used with EOBI market data feeds
- Define message structure and compression dictionaries

**FIXML Schemas:**
- XML Schema Definitions for FIX-based messages
- Supports FIX LF protocol integration
- Enables XML-based message validation

**XSD for ETI Messages:**
- XML Schema for ETI message structures
- Used for documentation and validation
- Can drive code generation tools

**Implementation Responsibility:**
- Participants must develop custom implementations based on protocol specifications
- Third-party vendors offer commercial ETI/EOBI client libraries
- Open-source implementations may exist but are not officially endorsed

This approach gives developers maximum flexibility but requires significant technical investment compared to SDK-based integration models.

## ISV Program

Deutsche Börse operates an Independent Software Vendor (ISV) program to support third-party developers building trading software:

**Registration:**
- Email **vendors@deutsche-boerse.com** to initiate registration
- Must be a registered Eurex participant or sponsored by one
- Complete ISV application form and agreement

**Program Benefits:**
- **Simulation Access**: ISVs receive simulation environment credentials for development and testing
- **Technical Support**: Access to CTS (Central Technical Services) support channels
- **Eurex Webpage Listing**: ISVs listed on Eurex vendor directory, increasing visibility
- **Documentation Distribution**: Direct access to technical documentation updates and release notes
- **Focused Testing Days**: Participation in exchange-organized testing events for new releases

**Important Limitation:**
**Eurex does NOT perform conformance testing or certification of third-party software.** ISVs are responsible for ensuring their implementations comply with protocol specifications and exchange rules. The ISV program provides access and support but does not include formal validation or endorsement of software quality.

**Focused Testing Days:**
- Exchange-organized events prior to major releases
- Opportunity to test against new platform versions
- Collaborative troubleshooting with exchange technical staff
- Networking with other ISVs and participants

The ISV program lowers barriers for software vendors while maintaining responsibility for implementation quality with the vendors themselves.

## Training & Education

Deutsche Börse offers several educational resources for market participants and developers:

### Capital Markets Academy

**Website**: **academy.deutsche-boerse.com**

- Comprehensive training on capital markets products and operations
- Courses on derivatives trading, market structure, and risk management
- Combines e-learning modules with instructor-led sessions
- Certifications available for completing course sequences

### Eurex Online System Training

- Web-based training for Eurex trading systems
- Interactive modules on T7 GUI functionality
- Self-paced learning with scenario-based exercises
- Accessible from simulation environment

### Eurex Trader Examination Preparation

- Q&A sets covering exchange rules and trading procedures
- Exam simulation environment
- Preparation for mandatory trader registration examinations
- Updated regularly to reflect rule changes

### Developer-Specific Training

**Important Note**: Deutsche Börse does **NOT** offer a developer-specific bootcamp or technical training program focused on API integration or protocol implementation. Developer education relies on:
- Self-study of technical documentation
- Simulation environment experimentation
- CTS support for specific technical questions
- ISV program resources (for registered vendors)

Organizations often supplement official resources with:
- Internal training programs
- Third-party consulting and training services
- Knowledge transfer from experienced exchange developers

## Key Contact Points

Understanding the correct contact point for different needs accelerates issue resolution:

| Team | Phone | Email | Availability | Purpose |
|------|-------|-------|--------------|---------|
| **CTS (Central Technical Services)** | +49-69-211-10888 | cts@deutsche-boerse.com | Mon 00:00 - Fri 22:00 CET | Technical issues, connectivity problems, API support |
| **Client Services** | - | client.services@eurex.com | Mon-Fri 09:00-18:00 CET | Onboarding, admission, account management |
| **Member Section Support** | +49-69-211-17888 | member.section@deutsche-boerse.com | Mon-Fri 09:00-18:00 CET | Certificates, credentials, access administration |
| **TMR (Trading Member Representative)** | - | onboarding-team@deutsche-boerse.com | Mon-Fri 09:00-18:00 CET | Onboarding coordination, go-live planning |
| **ISV Program** | - | vendors@deutsche-boerse.com | Mon-Fri 09:00-18:00 CET | ISV registration, vendor program inquiries |

**Emergency Escalation:**
For critical production incidents outside CTS hours, emergency escalation procedures are documented in the Incident Handling Guide and Emergency Playbook.

## Staying Informed

Proactive monitoring of system changes, incidents, and planned maintenance is essential for operational stability:

### Circulars & Newsflashes Subscription

Subscribe to Deutsche Börse notifications with focus on:
- **Releases & Technology**: Technical system changes, release announcements, migration timelines
- **Regulatory**: Rule changes affecting trading behavior or compliance requirements

Subscription management available through Member Section portal.

### Production Newsboard

**Real-time status updates** on production systems:
- Current system status and availability
- Active incidents and their impact
- Scheduled maintenance windows
- Post-incident summaries

Accessible via Member Section and integrated into some third-party monitoring tools.

### Readiness Newsflashes

Advance notification of upcoming changes:
- New feature announcements
- Deprecation warnings
- Migration deadlines
- Testing opportunities

Critical for planning development roadmaps and avoiding surprises.

### Implementation News

Detailed technical information about specific features:
- Implementation guides for new functionality
- Configuration examples
- Migration strategies
- Best practices

Supplements formal documentation with practical implementation guidance.

### Release Initiative Pages

Dedicated web pages for major releases containing:
- Release overview and objectives
- Detailed change inventory
- Migration guides and timelines
- Testing resources
- FAQ and known issues

Examples include pages for major T7 releases (e.g., Release 14.0, 14.1).

### Known Limitations Documents

Published documentation of current system constraints:
- Performance limitations under specific scenarios
- Feature gaps vs. intended functionality
- Workarounds for known issues
- Expected resolution timelines

Essential reading before filing support tickets to avoid reporting known issues.

## Critical Upcoming Changes

Developers should be aware of significant upcoming platform changes:

### TLS 1.2 Decommissioning (May 2026, Release 14.1)

**Action Required:**
- All connections must migrate to TLS 1.3
- TLS 1.2 will no longer be supported after Release 14.1
- Testing in simulation environment required before production cutover
- Certificate renewals may be required

**Timeline:**
- Now: TLS 1.3 available and recommended
- May 2026: TLS 1.2 support removed

### New ETI Order Entry Requests (Mandatory May 2026)

**Changes:**
- New order entry message structures
- Enhanced validation and risk controls
- Modified response message formats

**Action Required:**
- Review Release 14.1 specifications
- Update ETI implementations
- Test in simulation during 2025/early 2026
- Mandatory adoption by May 2026

### ETI Password Encryption Changes (May 2025)

**Changes:**
- Updated encryption algorithm for session passwords
- New STEP reference implementation
- Backward compatibility period

**Action Required:**
- Update password encryption logic
- Test with new STEP tool
- Deploy before May 2025 deadline

### System Availability Targets

**Long-term Performance:**
- **Eurex**: 99.97% availability over 20 years
- **FWB (Xetra)**: 99.98% availability over 20 years

These targets demonstrate platform reliability but developers should still implement robust reconnection and failover logic for the remaining downtime window.

## Common Pitfalls

Learning from common mistakes accelerates successful integration:

### Wrong Certificates

**Problem:** Using incorrect certificates for market, environment, or access type

**Solution:**
- Maintain certificate inventory tracking market, environment, and access type
- Implement automated certificate expiration monitoring
- Test certificate changes in simulation before production
- Separate certificate storage for production vs. simulation

### Deprecated FIX Gateway 4.4

**Problem:** Attempting to use legacy FIX Gateway 4.4

**Solution:**
- Migrate to FIX LF (FIX Lightweight) for FIX-based connectivity
- FIX Gateway 4.4 is deprecated and no longer supported
- FIX LF provides modern FIX protocol support with lower latency

### ETI Password Encryption

**Problem:** Using outdated password encryption from pre-May 2025

**Solution:**
- Implement encryption logic from current STEP reference implementation
- Test password encryption in simulation before production
- Monitor Release Notes for encryption algorithm updates

### RDI Required for Multicast

**Problem:** Attempting to subscribe to EOBI multicast without RDI connectivity

**Solution:**
- RDI (Reference Data Interface) is **mandatory** for receiving multicast addresses
- Implement RDI connectivity before attempting EOBI subscription
- Use RDI to discover multicast groups and product mappings

### Simulation for Performance Testing

**Problem:** Using simulation environment to benchmark latency or throughput

**Solution:**
- Simulation is NOT designed for performance testing
- Simulation uses different infrastructure with different characteristics
- Contact TKAM for performance and capacity testing arrangements
- Production-like performance testing requires special coordination

## Events & Community

Deutsche Börse fosters developer engagement through events and information sharing:

### Open Day

**Annual technology event** showcasing Deutsche Börse technology:
- **Exchange Lab Tours**: Behind-the-scenes look at trading infrastructure
- **Technical Presentations**: Deep dives into platform architecture and new features
- **Networking**: Meet exchange technologists and other participants
- **Product Demonstrations**: Hands-on exposure to new tools and services

Open Day provides rare insight into the exchange's technical roadmap and architecture philosophy.

### Eurex Derivatives Forum

Annual conference focusing on derivatives markets:
- Market structure discussions
- Product innovation announcements
- Regulatory updates
- Networking with market participants

While less developer-focused than Open Day, the Derivatives Forum provides business context for technical decisions.

### Focused Testing Days

Exchange-organized testing events for major releases:
- Coordinated testing of new features
- Direct access to exchange technical staff
- Collaborative troubleshooting
- Validation of migration readiness

Participation highly recommended for ISVs and participants with custom integrations.

### Developer Community

**Important Note**: Deutsche Börse does **NOT** operate a public developer forum or community platform. Developer support operates through official channels:
- CTS support for technical issues
- Client Services for onboarding and account management
- ISV program for registered vendors

**Informal Community:**
Some informal community interaction occurs through:
- LinkedIn groups focused on exchange technology
- Industry conferences and events
- Third-party vendor user groups
- Consulting networks

### T7 Ecosystem

**T7 Platform Adoption:**
The T7 trading platform is used across **9+ European exchanges**, creating a broader ecosystem:
- Eurex (derivatives)
- Xetra (equities)
- Bulgarian Stock Exchange
- Vienna Stock Exchange
- Malta Stock Exchange
- Ljubljana Stock Exchange
- Zagreb Stock Exchange
- Others

Knowledge and implementations developed for Deutsche Börse systems may have applicability across this broader T7 ecosystem, though specific configurations and rules vary by exchange.

---

## Conclusion

Successfully onboarding to Deutsche Börse's T7 trading platform requires navigating regulatory requirements, technical complexity, and extensive documentation. The process spans weeks to months depending on organizational readiness and technical sophistication.

Key success factors include:
- Early engagement with Client Services and TKAM
- Systematic progression through simulation testing
- Proactive monitoring of release notes and upcoming changes
- Investment in robust error handling and operational procedures
- Ongoing education on platform evolution

While Deutsche Börse does not provide comprehensive SDKs or developer bootcamps, the combination of detailed technical documentation, simulation environments, responsive technical support, and the ISV program provides a solid foundation for successful integration.

Developers should view onboarding not as a one-time project but as the beginning of an ongoing relationship with a platform that continues to evolve with market needs and technology advancements.

[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
