---
layout: default
title: "Pricing Summary"
nav_order: 4
parent: Appendices
---

# Pricing Summary

## Disclaimer

All prices listed in this appendix are approximate and sourced from publicly available Deutsche Boerse Group documentation as of early 2026. Actual fees are subject to change and may differ based on individual agreements, volume discounts, and negotiated terms. Participants should consult the official Eurex and Xetra Price Lists and contact Deutsche Boerse directly for current, binding pricing information.

For the most current pricing information, please refer to:
- Eurex: [Connection Agreement Price List](https://www.eurex.com)
- Xetra: [Bandwidths and Connection Fees](https://www.cashmarket.deutsche-boerse.com)
- Market Data: [MDDA Price List](https://www.mds.deutsche-boerse.com)

## Overview

Accessing Deutsche Boerse's trading infrastructure involves multiple cost components spanning connectivity, co-location, market data subscriptions, and session fees. This appendix provides a comprehensive breakdown of pricing for high-frequency trading participants connecting to Eurex and Xetra platforms. Understanding these costs is essential for budgeting and cost-benefit analysis when evaluating Deutsche Boerse connectivity options.

The major cost categories include:

1. **Co-Location 2.0 Connectivity**: High-bandwidth network connections to trading engines and market data feeds
2. **Session/Gateway Fees**: Access to order entry and management sessions
3. **Rack Space**: Physical infrastructure housing from Equinix
4. **Cross-Connects and Infrastructure**: Physical and logical connectivity between participant equipment and exchange systems
5. **Time Synchronization**: Precision timing services for regulatory compliance and latency optimization
6. **Remote Connectivity**: Leased line options for participants not co-located
7. **Multi-Member Service Provider (MMSP)**: Services for firms providing access to multiple trading members
8. **GUI Connectivity**: Browser-based trading interfaces

## Co-Location 2.0 Connectivity

Deutsche Boerse's Co-Location 2.0 infrastructure provides ultra-low latency connectivity to trading engines and market data systems. These fees are charged monthly per connection and represent the primary connectivity cost for high-frequency trading participants.

### Xetra Co-Location 2.0 (10 Gbit/s Connections)

All Xetra connectivity operates at 10 Gbit/s bandwidth, providing high-capacity links for market data and order entry.

| Service | Monthly Fee (EUR) | Description |
|---------|-------------------|-------------|
| CoLo 2.0 EMDI | 5,200 | Enhanced Market Data Interface - order book snapshots and updates |
| CoLo 2.0 EOBI | 6,240 | Enhanced Order Book Interface - ultra-low latency market data |
| CoLo 2.0 EMDI + EOBI | 7,280 | Combined EMDI and EOBI market data access |
| CoLo 2.0 ETI (Transaction) | 6,000 | Enhanced Trading Interface - order entry and management |

*Source: [Xetra Bandwidths and Connection Fees](https://www.cashmarket.deutsche-boerse.com/resource/blob/2954524/adc1ef0e9fbf67ade042dcd205a70917/data/20220223_Bandwidths-and-Connection-Fees.pdf)*

### Eurex Co-Location 2.0 (10 Gbit/s Connections)

Eurex Co-Location 2.0 pricing was updated effective January 1, 2026, reflecting approximately 15% fee increases partially offset by connection rebates for dual connectivity.

| Service | Monthly Fee (EUR) | Description |
|---------|-------------------|-------------|
| CoLo 2.0 EMDI | 6,000 | Enhanced Market Data Interface for Eurex derivatives |
| CoLo 2.0 EOBI Futures | 7,200 | Enhanced Order Book Interface for futures products |
| Connection Rebate (dual connections) | -750 per connection | Discount applied when maintaining redundant connectivity |

**Important Notes:**
- Eurex fees increased by approximately 15% on January 1, 2026
- Dual connection rebate of EUR 750 per connection partially offsets the increase
- Participants maintaining redundant connections (recommended for production trading) receive EUR 1,500 total monthly rebate

*Source: [Eurex Circular 104/25](https://www.eurex.com/resource/blob/4803696/43359c9b6a32316ac0fd11501f6a88d7/data/Eurex_Circular_104_25_en_Attach1.pdf)*

### 1 Gbit/s Prime Order Entry

Deutsche Boerse introduced a 1 Gbit/s Prime Order Entry option in November 2025, providing a lower-cost alternative for firms with moderate trading volumes.

| Service | Monthly Fee (EUR) | Description |
|---------|-------------------|-------------|
| 1 Gbit/s Prime Order Entry | 5,600 | Reduced bandwidth order entry connection |

**Restrictions:**
- Available exclusively to participants co-located in Equinix FR2 facility
- Maximum of 6 connections per access point
- Suitable for medium-frequency trading strategies with lower throughput requirements

*Source: Deutsche Boerse Connection Agreement Price Lists*

## Session and Gateway Pricing

In addition to connectivity fees, participants pay monthly session fees based on the type of trading access and expected message rates.

### Eurex ETI Sessions

Eurex offers tiered session types optimized for different trading profiles, with pricing scaled by message throughput capacity.

| Session Type | Max TPS | Sessions 1-4 (EUR/month) | Session 5+ (EUR/month) | Description |
|--------------|---------|--------------------------|------------------------|-------------|
| HF Light | 50 | 125 | 250 | Entry-level high-frequency access |
| HF Full | 150 | 250 | 500 | Standard high-frequency access |
| HF Ultra | 250 | See Price List | See Price List | Premium high-frequency access (available since June 2023) |

**Volume Discounting:**
- Sessions 1-4: Lower rate encourages initial connectivity
- Session 5 onwards: Higher incremental rate
- HF Ultra pricing available in current Eurex Price List

*TPS = Transactions Per Second (maximum sustained message rate)*

### Xetra ETI Sessions

Xetra provides simplified two-tier session pricing without volume-based discounting.

| Session Type | Monthly Fee (EUR) | Description |
|--------------|-------------------|-------------|
| ETI HF Light | 250 | Standard high-frequency session |
| ETI HF Full | 500 | Enhanced high-frequency session |

### Back-Office Sessions

For non-trading functions such as drop-copy, clearing connectivity, and reporting, Deutsche Boerse offers back-office session access at reduced rates.

| Session Type | Monthly Fee (EUR) | Description |
|--------------|-------------------|-------------|
| ETI Back Office | 100-104 | Order and trade reporting access |
| FIX LF Back Office | 100 | FIX protocol back-office connectivity |
| Rebate (per trading member) | Up to -1,000 to -1,040 | Volume-based discount for back-office sessions |

**Note:** Actual back-office rebates depend on trading member activity levels and are subject to specific contract terms.

## Co-Location Housing (Rack Space)

Physical rack space in the Equinix FR2, FR5, and FR6 facilities is contracted directly with Equinix, not with Deutsche Boerse. The following represents approximate pricing based on power allocation tiers.

| Power Rating | Approximate Monthly Fee (EUR) | Description |
|--------------|-------------------------------|-------------|
| 3 kVA | 2,330 | Entry-level rack power allocation |
| 4 kVA | 2,870 | Standard rack configuration |
| 5 kVA | 3,390 | Enhanced power for denser equipment |
| 6 kVA | 3,910 | High-power configuration for compute-intensive setups |

**Important Considerations:**
- Pricing is approximate and subject to Equinix commercial agreements
- Actual costs vary based on contract terms, rack size (full rack, half rack, quarter rack), and facility
- Additional costs may include installation fees, remote hands services, and cross-connect charges
- Contact Equinix directly for binding quotes: [Equinix FR Frankfurt](https://www.equinix.com)

## Cross-Connects and Infrastructure

Physical cross-connects provide direct fiber connections between participant racks and Deutsche Boerse network infrastructure.

| Service | Monthly Fee (EUR) | Description |
|---------|-------------------|-------------|
| Physical Cross-Connect | 150 per connection | Single-mode fiber connection between participant rack and exchange infrastructure |
| White Rabbit Additional SMF | Included | Additional 1 Gbit/s single-mode fiber required for White Rabbit time synchronization |

**Ordering:**
- Cross-connects are ordered through the Deutsche Boerse Member Section portal
- Installation typically requires 5-10 business days lead time
- White Rabbit requires dedicated cross-connect in addition to trading/market data connections

## Time Synchronization

Precise time synchronization is essential for regulatory compliance (MiFID II clock synchronization requirements) and latency-sensitive trading strategies.

| Service | Monthly Fee (EUR) | Accuracy | Description |
|---------|-------------------|----------|-------------|
| Standard PTP (IEEE 1588) | 400 | ±50 ns (4-5 ns RMS after 2024 refresh) | Standard precision time protocol service |
| GPS Antenna (roof space) | 850 | 10-100 ns | Direct GPS receiver with rooftop antenna placement |
| White Rabbit | Contact Deutsche Boerse | <1 ns | Ultra-precise time synchronization using White Rabbit protocol |

**Time Synchronization Notes:**

- **Standard PTP**: Most common choice for regulatory compliance. After the 2024 infrastructure refresh, typical performance is 4-5 ns RMS with ±50 ns maximum deviation.
- **GPS Antenna**: Suitable for participants requiring independent time source. Accuracy varies based on GPS signal quality and atmospheric conditions.
- **White Rabbit**: Sub-nanosecond precision for latency-critical strategies. Requires additional 1 Gbit/s single-mode fiber cross-connect. Pricing available on request.

*Source: Deutsche Boerse Time Synchronization Documentation*

## Remote Connectivity (Leased Lines)

For participants not co-located in Deutsche Boerse proximity hosting facilities, leased line connectivity is available at various bandwidth tiers.

| Bandwidth | Monthly Fee Range (EUR) | Description |
|-----------|-------------------------|-------------|
| 7 Mbit/s | 520+ | Standard remote connectivity |
| 14 Mbit/s | 750+ | Enhanced remote bandwidth |
| 80 Mbit/s | 2,100+ | Premium remote access |
| 200 Mbit/s | 3,800+ | High-bandwidth remote connectivity |
| 260 Mbit/s | 4,600+ | Very high bandwidth option |
| 760 Mbit/s | 6,760+ | Maximum available remote bandwidth |

**Remote Connectivity Considerations:**

- Leased line pricing varies significantly based on geographic distance from Frankfurt data centers
- Latency performance is substantially higher than co-location (typically 2-20 ms vs. <200 microseconds)
- Suitable for medium-frequency trading strategies, risk management systems, and back-office connectivity
- Contract directly with Deutsche Boerse or through approved network service providers

*Source: [Connection Agreement for SPA Price List](https://www.eurex.com/resource/blob/4821986/38ad2da44adee0c1f86b0ae7415e7d23/data/2025_11_11-connection-agreement-for-spa-pricelist_en.pdf)*

## Multi-Member Service Provider (MMSP)

Multi-Member Service Provider status enables firms to provide consolidated connectivity for multiple trading members through a single infrastructure.

| Fee Type | Monthly Fee (EUR) | Description |
|----------|-------------------|-------------|
| MMSP Basic Fee | 4,000 | Base monthly charge for MMSP status |
| Additional Bandwidth Fees | Variable | Based on total bandwidth and session count |
| Per-Member Fees | Variable | Calculated based on registered members |

**MMSP Fee History:**
- Increased from EUR 3,000 to EUR 4,000 effective April 1, 2022
- Additional session and bandwidth charges apply based on aggregate usage
- Suitable for brokers, trading venues, and technology providers serving multiple clients

*Source: Deutsche Boerse MMSP Documentation*

## GUI Connectivity

For participants requiring browser-based trading interfaces, Deutsche Boerse provides GUI access with differentiated pricing based on underlying connectivity.

| Connection Type | Monthly Fee (EUR) | Description |
|----------------|-------------------|-------------|
| T7 GUI via Internet (with MIC, GUI-Channel, 10 GbE, or MMSP) | Free | No additional charge when other connectivity services are active |
| T7 GUI via Internet (otherwise) | 310 | Standalone GUI access without other services |

**GUI Access Notes:**
- Suitable for manual traders, risk managers, and monitoring systems
- Not recommended for latency-sensitive or high-frequency trading
- Typically accessed via browser or thick client application

## Total Cost of Ownership Example

To illustrate the total monthly cost for a typical high-frequency trading setup, consider the following example configuration:

### Example: Dual-Connected Eurex HFT Participant

| Component | Quantity | Unit Cost (EUR) | Total (EUR) |
|-----------|----------|----------------|-------------|
| Eurex CoLo 2.0 EMDI (10 Gbit/s) | 2 | 6,000 | 12,000 |
| Eurex CoLo 2.0 EOBI Futures (10 Gbit/s) | 2 | 7,200 | 14,400 |
| Dual Connection Rebate | 4 | -750 | -3,000 |
| Eurex ETI HF Full Sessions | 8 | 250-500 | 3,000 |
| Physical Cross-Connects | 4 | 150 | 600 |
| Standard PTP Time Sync | 1 | 400 | 400 |
| Equinix Rack Space (5 kVA) | 1 | 3,390 | 3,390 |
| **Total Monthly Costs** | | | **30,790** |

**Annual Cost:** EUR 369,480

This example demonstrates that a production-grade dual-connected setup with redundant market data and order entry connectivity requires approximately EUR 30,000-35,000 in monthly infrastructure costs before considering data center power, hardware depreciation, and personnel expenses.

## Cost Optimization Strategies

High-frequency trading participants can optimize infrastructure costs through several approaches:

### 1. Right-Size Connectivity
- Use 1 Gbit/s Prime Order Entry for moderate-frequency strategies instead of 10 Gbit/s connections
- Evaluate actual throughput requirements before purchasing maximum bandwidth

### 2. Consolidate Sessions
- Leverage multi-partition access through Low-Frequency Gateway for cross-product strategies
- Use session counts 1-4 to benefit from lower per-session pricing

### 3. Selective Market Data Subscriptions
- Subscribe only to required market data feeds (EMDI vs. EOBI based on latency requirements)
- Consider consolidated feeds for less latency-sensitive monitoring systems

### 4. Shared Infrastructure
- Explore MMSP arrangements for firms serving multiple trading entities
- Consider hosted trading solutions from third-party providers

### 5. Remote Connectivity for Non-Critical Systems
- Use leased lines for risk management, back-office, and reporting systems
- Reserve co-location for latency-critical trading components

## Price List References

The following official Deutsche Boerse Group price lists provide complete, current pricing information:

1. **Eurex Connection Agreement Price List** (effective January 1, 2026)
   [https://www.eurex.com/resource/blob/2567152/6c913fe00107e1cf1c2ffe3b506f9dfc/data/2025_01_01_efag_preisv_anv-e_en.pdf](https://www.eurex.com/resource/blob/2567152/6c913fe00107e1cf1c2ffe3b506f9dfc/data/2025_01_01_efag_preisv_anv-e_en.pdf)

2. **Xetra Bandwidths and Connection Fees**
   [https://www.cashmarket.deutsche-boerse.com/resource/blob/2954524/adc1ef0e9fbf67ade042dcd205a70917/data/20220223_Bandwidths-and-Connection-Fees.pdf](https://www.cashmarket.deutsche-boerse.com/resource/blob/2954524/adc1ef0e9fbf67ade042dcd205a70917/data/20220223_Bandwidths-and-Connection-Fees.pdf)

3. **MDDA Market Data Price List**
   [https://www.mds.deutsche-boerse.com/resource/blob/3347708/67fafc73c58441b867d1ce08ce720f3c/data/MDDA_Price_List_12_2.pdf](https://www.mds.deutsche-boerse.com/resource/blob/3347708/67fafc73c58441b867d1ce08ce720f3c/data/MDDA_Price_List_12_2.pdf)

4. **T7 Pricing Factsheet**
   [https://www.deutsche-boerse.com/resource/blob/296832/e251445b0703ede442a2c65c1837fa2b/data/Factsheet_T7-Pricing.pdf](https://www.deutsche-boerse.com/resource/blob/296832/e251445b0703ede442a2c65c1837fa2b/data/Factsheet_T7-Pricing.pdf)

5. **Connection Agreement for SPA Price List** (November 11, 2025)
   [https://www.eurex.com/resource/blob/4821986/38ad2da44adee0c1f86b0ae7415e7d23/data/2025_11_11-connection-agreement-for-spa-pricelist_en.pdf](https://www.eurex.com/resource/blob/4821986/38ad2da44adee0c1f86b0ae7415e7d23/data/2025_11_11-connection-agreement-for-spa-pricelist_en.pdf)

6. **Eurex Circular 104/25** (January 1, 2026 Pricing Updates)
   [https://www.eurex.com/resource/blob/4803696/43359c9b6a32316ac0fd11501f6a88d7/data/Eurex_Circular_104_25_en_Attach1.pdf](https://www.eurex.com/resource/blob/4803696/43359c9b6a32316ac0fd11501f6a88d7/data/Eurex_Circular_104_25_en_Attach1.pdf)

## Conclusion

Understanding the cost structure of Deutsche Boerse connectivity is essential for evaluating the business case for direct market access and high-frequency trading strategies. Total infrastructure costs typically range from EUR 15,000 to EUR 50,000 per month depending on redundancy requirements, bandwidth needs, and session counts.

When budgeting for Deutsche Boerse connectivity, participants should account for:
- Initial setup costs (cross-connect installation, equipment procurement)
- Ongoing monthly infrastructure fees (connectivity, sessions, rack space)
- Data center power and cooling costs
- Hardware refresh cycles and maintenance
- Personnel costs for system administration and support

For participants evaluating Deutsche Boerse market access, the pricing information in this appendix provides a foundation for total cost of ownership analysis. However, given the complexity of pricing structures and the availability of volume discounts and negotiated rates, prospective participants should engage directly with Deutsche Boerse sales representatives for binding quotations tailored to specific requirements.

---
[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
