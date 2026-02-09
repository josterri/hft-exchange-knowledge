# Glossary

## A

### Advanced Risk Protection (ARP)
Risk management feature in T7 that monitors trading activity in real-time to prevent breach of risk limits. Automatically blocks orders that would exceed predefined thresholds.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### Auction
Trading phase where orders are collected without immediate execution, then matched at a single equilibrium price. Deutsche Boerse exchanges use auctions for opening, closing, and volatility interruptions.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

## B

### BaFin
Bundesanstalt für Finanzdienstleistungsaufsicht - German Federal Financial Supervisory Authority. Regulates financial markets and institutions in Germany, including Deutsche Boerse.

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

### CoLo 2.0
Deutsche Boerse's latest generation colocation facility offering ultra-low latency connectivity to T7, Xetra, and market data services with sub-microsecond precision.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## D

### D7
Market data distribution system providing consolidated real-time and historical data from Deutsche Boerse Group exchanges.

### DAX
Deutsche Boerse's flagship equity index comprising the 40 largest and most liquid German companies trading on Xetra. Futures and options on DAX are among the most traded derivatives globally.

### Deutsche Boerse AG
Germany's leading exchange organization operating Xetra (cash equities), Eurex (derivatives), and providing clearing, settlement, and market data services.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

### Designated Sponsor
Market participant committed to providing continuous bid and ask quotes in specific securities to enhance liquidity and reduce spreads, particularly in less liquid instruments.

## E

### EMDI
Enhanced Market Data Interface - high-performance market data feed delivering real-time order book snapshots and incremental updates with microsecond timestamps.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### EOBI
Enhanced Order Book Interface - ultra-low latency market data feed providing direct access to T7 order book changes with minimum processing overhead.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### ETF
Exchange-Traded Fund - investment fund traded on exchanges like regular stocks. Xetra is Europe's leading ETF trading venue.

### ETI
Enhanced Trading Interface - Deutsche Boerse's native binary protocol for high-frequency order entry and management on T7 with microsecond-level performance.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### EEX
European Energy Exchange - part of Deutsche Boerse Group, operating energy and commodity derivatives markets.

### Eurex
Europe's largest derivatives exchange operated by Deutsche Boerse, offering futures and options on equity indices, interest rates, and dividends.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

### Eurex Clearing
Central counterparty (CCP) within Deutsche Boerse Group providing clearing services for Eurex derivatives and other markets, managing risk through margin requirements and default procedures.

## F

### Fill-or-Kill (FOK)
Order type that must be executed immediately in its entirety or cancelled completely. No partial fills allowed.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### FIX
Financial Information eXchange protocol - industry-standard messaging protocol for electronic trading. Deutsche Boerse supports FIX alongside native ETI protocol.

### FWB
Frankfurter Wertpapierbörse (Frankfurt Stock Exchange) - Germany's traditional floor-based exchange, now operating primarily through the Xetra electronic platform.

## G

### Good-Till-Cancelled (GTC)
Order time-in-force instruction where the order remains active until executed or explicitly cancelled by the trader.

### Good-Till-Date (GTD)
Order time-in-force instruction where the order remains active until a specified date or until executed/cancelled.

## H

### High-Frequency Session (HF Session)
T7 trading session optimized for algorithmic and high-frequency trading with enhanced performance characteristics and partition-specific access.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## I

### IBIS
Integriertes Börsenhandels- und Informationssystem - predecessor electronic trading system to Xetra, launched in 1991.

### Immediate-or-Cancel (IOC)
Order type that must be executed immediately for any available quantity, with unfilled portions automatically cancelled. Permits partial fills.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## L

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

## N

### N7
Deutsche Boerse's news distribution service delivering corporate actions, market announcements, and regulatory notifications to market participants.

## O

### Open Market (Freiverkehr)
German unregulated trading segment where securities not admitted to regulated markets can be traded with less stringent listing requirements.

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

### Pro-Rata (PTR)
Alternative matching method allocating fills proportionally among same-priced orders based on displayed quantity, used in some derivative products.

## R

### RDI
Reference Data Interface - Deutsche Boerse data feed providing instrument static data, trading calendars, and product specifications.

### Regulated Market
Trading venue meeting EU regulatory requirements under MiFID II, including transparency, reporting, and admission standards. Xetra and Eurex operate regulated markets.

## S

### Self-Match Prevention (SMP)
Risk control feature preventing trader's orders from matching against their own opposite-side orders, avoiding unintended wash trades and position churn.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### ServiceAvailabilityBroadcast
T7 system message notifying participants of trading service status changes, partition availability, and upcoming maintenance windows.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## T

### T7
Trade Entry Services Version 7 - Deutsche Boerse's flagship trading platform serving Eurex derivatives and certain cash market segments with microsecond-level latency.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### TES
Trade Entry Services - T7 functionality enabling off-book trade reporting for block trades, exchange-for-physicals (EFPs), and other negotiated transactions.

### TPS
Transactions Per Second - performance metric measuring T7 system capacity to process order messages and generate executions.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

## V

### Volatility Interruption
Automatic trading halt triggered when prices move beyond predefined thresholds, followed by auction phase to re-establish orderly price discovery.
*See: [Chapter 2 - T7 Architecture](../02-t7-architecture/README.md)*

### VSTOXX
EURO STOXX 50 Volatility Index - measure of European equity market volatility, with futures and options traded on Eurex.

## X

### Xetra
Exchange Electronic Trading - Deutsche Boerse's electronic trading platform for cash equities and ETFs, serving as Germany's primary stock market and Europe's leading ETF venue.
*See: [Chapter 1 - Exchange Overview](../01-exchange-overview/README.md)*

---
[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
