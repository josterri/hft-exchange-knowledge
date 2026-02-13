# Glossary

## A

### ACE (Automated Corridor Expansion)
Mechanism that automatically widens volatility interruption price corridors in specified time intervals.
*See: [Chapter 9 - Risk Management](../09-risk-management/README.md)*

### Advanced Risk Protection (ARP)
Risk management feature in T7 that monitors trading activity in real-time to prevent breach of risk limits. Automatically blocks orders that would exceed predefined thresholds.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Algo ID
Unique identifier assigned to algorithmic trading strategies for regulatory flagging under MiFID II.

### Auction
Trading phase where orders are collected without immediate execution, then matched at a single equilibrium price. Deutsche Boerse exchanges use auctions for opening, closing, and volatility interruptions.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

## B

### BaFin
Bundesanstalt für Finanzdienstleistungsaufsicht - German Federal Financial Supervisory Authority. Regulates financial markets and institutions in Germany, including Deutsche Boerse.

### Binary Protocol
Wire-level encoding used by ETI and EOBI for minimal serialization overhead and lowest latency.

### Book-or-Cancel (BOC)
Order type that must be fully added to the order book or be cancelled entirely. Cannot match against existing liquidity immediately upon entry.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## C

### C7
Deutsche Boerse's clearing system for cash market transactions, processing trades from Xetra and Frankfurter Wertpapierbörse.

### Central Counterparty (CCP)
Entity that interposes itself between counterparties to trades, becoming the buyer to every seller and seller to every buyer. Eurex Clearing serves as CCP for Deutsche Boerse derivatives.

### Clearstream
Deutsche Boerse's post-trade services division providing settlement, custody, and asset servicing for domestic and international securities.

### CLIP (Central Limit Order Book Improvement Process)
Eurex Improve mechanism providing 150ms price improvement window for options. Also known as Eurex Improve.

### Cloud Simulation
T7 on-demand testing environment providing 24/7 dedicated instance access via SSL/IPSEC internet connection. Launched August 2025.

### CoLo 2.0
Deutsche Boerse's latest generation colocation facility offering ultra-low latency connectivity to T7, Xetra, and market data services with sub-microsecond precision.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Cross-Connect
Physical fiber connection (EUR 150/month) linking participant equipment to Deutsche Boerse network infrastructure in co-location facility.

## D

### D7
Market data distribution system providing consolidated real-time and historical data from Deutsche Boerse Group exchanges.

### DAX
Deutsche Boerse's flagship equity index comprising the 40 largest and most liquid German companies trading on Xetra. Futures and options on DAX are among the most traded derivatives globally.

### DEA (Direct Electronic Access)
Arrangement where trading member allows clients to use its trading identity. Requires flagging under MiFID II.

### Designated Sponsor
Market participant committed to providing continuous bid and ask quotes in specific securities to enhance liquidity and reduce spreads, particularly in less liquid instruments.

### Deutsche Boerse AG
Germany's leading exchange organization operating Xetra (cash equities), Eurex (derivatives), and providing clearing, settlement, and market data services.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

### Drop Copy
ETI service providing real-time copy of order and trade activity to separate monitoring session for risk management.

## E

### EEX
European Energy Exchange - part of Deutsche Boerse Group, operating energy and commodity derivatives markets.

### EMDI
Enhanced Market Data Interface - high-performance market data feed delivering real-time order book snapshots and incremental updates with microsecond timestamps.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### EnLight (SRQS)
Eurex's Selective Request for Quote Service - integrated RFQ platform allowing participants to request quotes from multiple counterparties simultaneously.

### EOBI
Enhanced Order Book Interface - ultra-low latency market data feed providing direct access to T7 order book changes with minimum processing overhead.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Equinix FR2
Primary co-location data center in Frankfurt (Rebstöcker Straße 33, 60326) hosting Deutsche Boerse T7 matching engines and participant infrastructure.

### ESU (Excessive System Usage)
Fee regime penalizing participants whose message rates exceed defined thresholds. Formula: (Transaction count - Transaction limit) x Fee.

### ETF
Exchange-Traded Fund - investment fund traded on exchanges like regular stocks. Xetra is Europe's leading ETF trading venue.

### ETI
Enhanced Trading Interface - Deutsche Boerse's native binary protocol for high-frequency order entry and management on T7 with microsecond-level performance.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Eurex
Europe's largest derivatives exchange operated by Deutsche Boerse, offering futures and options on equity indices, interest rates, and dividends.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

### Eurex Clearing
Central counterparty (CCP) within Deutsche Boerse Group providing clearing services for Eurex derivatives and other markets, managing risk through margin requirements and default procedures.

### ExecutionReport
ETI response message confirming order acceptance, modification, fill, or cancellation. T7 sends exactly one response per request.

## F

### FAST (FIX Adapted for Streaming)
Data compression protocol used with FIX for efficient market data distribution on EMDI and MDI feeds.

### Fill-or-Kill (FOK)
Order type that must be executed immediately in its entirety or cancelled completely. No partial fills allowed.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### FIX
Financial Information eXchange protocol - industry-standard messaging protocol for electronic trading. Deutsche Boerse supports FIX alongside native ETI protocol.

### FIX LF
FIX Low-Frequency interface replacing the legacy FIX Gateway. Introduced in T7 Release 9.0. Supports FIX 4.2 and 4.4.

### FWB
Frankfurter Wertpapierbörse (Frankfurt Stock Exchange) - Germany's traditional floor-based exchange, now operating primarily through the Xetra electronic platform.

## G

### Good-Till-Cancelled (GTC)
Order time-in-force instruction where the order remains active until executed or explicitly cancelled by the trader.

### Good-Till-Date (GTD)
Order time-in-force instruction where the order remains active until a specified date or until executed/cancelled.

### GPS Antenna
Roof-mounted GPS receiver providing 10-100 ns time synchronization accuracy at EUR 850/month in co-location facility.

## H

### Heartbeat
Periodic keep-alive message exchanged between trading application and T7 gateway to maintain session liveness.

### High-Frequency Session (HF Session)
T7 trading session optimized for algorithmic and high-frequency trading with enhanced performance characteristics and partition-specific access.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### HPT (High Precision Timestamps)
Deutsche Boerse product providing nanosecond-precision timestamps for latency analysis of trading and market data.

## I

### IBIS
Integriertes Börsenhandels- und Informationssystem - predecessor electronic trading system to Xetra, launched in 1991.

### Immediate-or-Cancel (IOC)
Order type that must be executed immediately for any available quantity, with unfilled portions automatically cancelled. Permits partial fills.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## K

### Kill Switch
Emergency mechanism to halt all trading activity for a participant or business unit. Requires 4-eyes principle (two authorized users).

## L

### LEI (Legal Entity Identifier)
ISO 17442 standard identifier used for short code registration of legal persons under MiFID II transaction reporting.

### Low-Frequency Gateway (LF Gateway)
T7 access gateway designed for traditional institutional traders with lower message rate requirements, providing access to all partitions through a single connection.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Low-Frequency Session (LF Session)
Standard T7 trading session for traditional order flow with relaxed rate limits compared to high-frequency sessions.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## M

### Market Data Interface (MDI)
Generic term for Deutsche Boerse's market data distribution systems including EOBI, EMDI, and RDI providing various latency-cost trade-offs.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Market Maker
Professional trading firm committed to providing continuous two-sided quotes (bid and ask) in assigned instruments, enhancing market liquidity and efficiency.

### Market Reset
Emergency procedure where T7 system temporarily halts trading to address technical issues or imbalances, followed by controlled restart with order book reconstruction.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Matching Engine
Core component of T7 that executes order matching logic using price-time priority, determining trade execution and maintaining order book integrity.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### MiFID II
Markets in Financial Instruments Directive II - EU regulation governing financial markets, imposing transparency, reporting, and best execution requirements on Deutsche Boerse participants.

### MMP (Market Maker Protection)
Automated protection mechanism monitoring volume, delta, vega, and percentage statistics to prevent excessive market maker exposure.

### MOQ (Maximum Order Quantity)
Pre-trade risk limit setting maximum quantity per order, configurable by exchange and clearing member.

### MOV (Maximum Order Value)
Pre-trade risk limit setting maximum notional value per order, validated before order acceptance.

### Multicast
UDP network distribution method used by EOBI, EMDI, MDI, and RDI to simultaneously deliver market data to all subscribers on a network segment.

## N

### N7
Deutsche Boerse's news distribution service delivering corporate actions, market announcements, and regulatory notifications to market participants.

## O

### Open Market (Freiverkehr)
German unregulated trading segment where securities not admitted to regulated markets can be traded with less stringent listing requirements.

### OTR (Order-to-Trade Ratio)
Regulatory metric measuring ratio of orders to trades. Volume-based: (ordered volume / traded volume) - 1. Transaction-based: (number of orders / number of trades) - 1.

## P

### Partition
Logical subdivision of T7 matching engine processing subset of instruments independently. Enables horizontal scaling and optimized latency for specific product groups.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Partition-Specific Gateway (PS Gateway)
Direct T7 access gateway connecting to single partition for ultra-low latency trading, minimizing network hops and processing overhead for high-frequency strategies.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Passive Liquidity Protection (PLP)
Risk control mechanism preventing unintended passive order execution during periods of market stress by automatically pulling quotes when triggered.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Price-Time Priority (PTP)
Order matching principle where orders at best price execute first, with same-price orders matched chronologically by entry time.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### PRISMA
Portfolio Risk Integrated Assessment - Eurex Clearing's margin methodology achieving 99%/99.5% confidence levels for listed/OTC instruments.

### Pro-Rata (PTR)
Alternative matching method allocating fills proportionally among same-priced orders based on displayed quantity, used in some derivative products.

## R

### RDI
Reference Data Interface - Deutsche Boerse data feed providing instrument static data, trading calendars, and product specifications.

### Readiness Statement
Mandatory submission by participants confirming technical preparedness before each T7 release production launch.

### Regulated Market
Trading venue meeting EU regulatory requirements under MiFID II, including transparency, reporting, and admission standards. Xetra and Eurex operate regulated markets.

### RTS (Regulatory Technical Standards)
EU technical standards implementing MiFID II. Key standards: RTS 6 (algo requirements), RTS 7 (venue requirements), RTS 11 (tick sizes), RTS 25 (clock sync).

## S

### Self-Match Prevention (SMP)
Risk control feature preventing trader's orders from matching against their own opposite-side orders, avoiding unintended wash trades and position churn.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### ServiceAvailabilityBroadcast
T7 system message notifying participants of trading service status changes, partition availability, and upcoming maintenance windows.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Side A / Side B
Live-live redundancy architecture where market data and matching engine infrastructure operate simultaneously on two independent physical networks.

### SRQS
See EnLight.

### STEP
Sample Tool for ETI Password Encryption - Python reference implementation for ETI session authentication.

## T

### T7
Trade Entry Services Version 7 - Deutsche Boerse's flagship trading platform serving Eurex derivatives and certain cash market segments with microsecond-level latency.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### TES
Trade Entry Services - T7 functionality enabling off-book trade reporting for block trades, exchange-for-physicals (EFPs), and other negotiated transactions.

### TKAM (Technical Key Account Manager)
Dedicated Deutsche Boerse technical contact for participant connectivity, migration planning, and go-live coordination.

### TLS 1.3
Mandatory encryption protocol for all ETI and FIX connections. TLS 1.2 being decommissioned in Release 14.1 (May 2026).

### TMR (Technical Member Readiness)
Deutsche Boerse team coordinating participant testing, consulting calls, and production readiness.

### TPS
Transactions Per Second - performance metric measuring T7 system capacity to process order messages and generate executions.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Trade-at-Close
Xetra trading phase (17:35-17:45 CET) allowing execution at the official closing auction price for fund valuation purposes.

### TSL (Transaction Size Limits)
Risk limits configurable by clearing members for their trading participants, covering on-book, TES, and calendar spread trading.

### TSO (Trading Surveillance Office)
Independent exchange body monitoring trading on Deutsche Boerse exchanges for market abuse and irregularities.

## U

### UDP
User Datagram Protocol - connectionless network protocol used for multicast market data distribution (EOBI, EMDI, MDI, RDI).

## V

### Volatility Interruption
Automatic trading halt triggered when prices move beyond predefined thresholds, followed by auction phase to re-establish orderly price discovery.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### VSTOXX
EURO STOXX 50 Volatility Index - measure of European equity market volatility, with futures and options traded on Eurex.

## W

### White Rabbit
Sub-nanosecond (<1 ns) precision time synchronization protocol developed at CERN, used internally by Deutsche Boerse and available to co-located participants.

## X

### Xetra
Exchange Electronic Trading - Deutsche Boerse's electronic trading platform for cash equities and ETFs, serving as Germany's primary stock market and Europe's leading ETF venue.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

---
[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
