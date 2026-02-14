---
layout: default
title: "Quick Reference"
nav_order: 2
parent: Appendices
---

# Quick Reference

**Deutsche Börse HFT Exchange Knowledge Base**

This appendix provides a compact, at-a-glance reference card for key metrics, parameters, and contacts related to high-frequency trading on Deutsche Börse's T7 trading platform.

---

## 1. Key Metrics at a Glance

| Metric | Value |
|--------|-------|
| Minimum reaction time | 2,787 ns |
| Median order latency (PS Gateway) | < 55 μs |
| LF Gateway additional latency | ~12 μs |
| EOBI publication lead over ETI | ~1.5 μs |
| Peak throughput | 201,000 msg/sec |
| Daily request volume (April 2025) | 1.25 billion |
| System availability (20-year avg) | 99.97-99.98% |

---

## 2. Session Types & Throttle Limits

| Type | Max TPS | Monthly Fee (Sessions 1-4) |
|------|---------|---------------------------|
| HF Light | 50 | EUR 125 (Eurex) / EUR 250 (Xetra) |
| HF Full | 150 | EUR 250 (Eurex) / EUR 500 (Xetra) |
| HF Ultra | 250 | See Price List |
| **Max sessions per participant** | **600** | - |

**Key Points:**
- TPS = Transactions Per Second (inbound requests)
- Throttle fees apply from session 5 onwards
- Sessions are participant-specific, not user-specific
- Throttle limits enforced per session with configurable action (reject, log, reject & log)

---

## 3. Market Data Feeds Comparison

| Feed | Protocol | Depth | Latency | CoLo Fee/mo |
|------|----------|-------|---------|-------------|
| EOBI | Binary | Full order book | 20-30 μs | EUR 6,240-7,200 |
| EMDI | FIX/FAST | 10-15 levels | 30-40 μs | EUR 5,200-6,000 |
| MDI | FIX/FAST | Top-of-book | 100-200 μs | Included |
| RDI | FIX/FAST | Static reference | Pre-market | Included |

**Key Points:**
- EOBI (Enhanced Order Book Interface): Lowest latency, full depth, binary protocol
- EMDI (Enhanced Market Data Interface): FIX/FAST, partial depth, slightly higher latency
- MDI (Market Data Interface): Standard feed, suitable for non-HFT applications
- RDI (Reference Data Interface): Static instrument data, corporate actions, calendar information

---

## 4. Gateway Types

| Type | Latency | Access | Use Case |
|------|---------|--------|----------|
| PS Gateway (Partition-Specific) | Lowest | Single partition | HFT, market making, latency-sensitive |
| LF Gateway (Logical Flow) | +12 μs | Multi-partition | Cross-product strategies, lower frequency |

**Key Points:**
- PS Gateway: Direct connection to one product partition (e.g., DAX futures)
- LF Gateway: Consolidated access across multiple partitions via single session
- Additional ~12 μs latency on LF Gateway due to message routing layer
- Choose PS Gateway for single-product, ultra-low latency strategies
- Choose LF Gateway for multi-product access with acceptable latency overhead

---

## 5. Co-Location Costs (Monthly)

| Service | Xetra | Eurex |
|---------|-------|-------|
| CoLo 2.0 EOBI | EUR 6,240 | EUR 7,200 |
| CoLo 2.0 EMDI | EUR 5,200 | EUR 6,000 |
| CoLo 2.0 ETI | EUR 6,000 | EUR 6,000 |
| Cross-connect (per cable) | EUR 150 | EUR 150 |
| PTP time sync | EUR 400 | EUR 400 |
| Rack space (5 kVA) | EUR 3,390 | EUR 3,390 |

**Key Points:**
- CoLo fees are per data center (Frankfurt FRA1 or Eschborn ESC1)
- ETI access fee covers order entry/execution gateway
- Cross-connect fee applies per physical cable connection
- Rack space includes power, cooling, and physical security
- Additional services: GPS antenna (EUR 850/mo), White Rabbit (<1 ns, contact DB)

---

## 6. Time Synchronization Options

| Service | Accuracy | Monthly Fee |
|---------|----------|-------------|
| Standard PTP (IEEE 1588) | ±50 ns (4-5 ns RMS typical) | EUR 400 |
| GPS Antenna | 10-100 ns | EUR 850 |
| White Rabbit | < 1 ns | Contact DB |

**Key Points:**
- PTP (Precision Time Protocol): Industry standard, sufficient for most HFT applications
- GPS Antenna: Independent reference source, useful for regulatory compliance
- White Rabbit: Ultra-precise synchronization for latency arbitrage and cross-venue strategies
- RMS accuracy typically 4-5 ns for PTP under normal conditions
- All timestamps in T7 are UTC with nanosecond precision

---

## 7. Risk Control Parameters

### Pre-Trade Controls
| Parameter | Value/Options |
|-----------|---------------|
| PLP (Price Limit Protection) deferral | 1-3 ms by product |
| OTR (Order-to-Trade Ratio) volatility factors | 1, 1.5, 2, 4 |
| OTR penalty (maximum) | EUR 1,000,000 |
| SMP (Self-Match Prevention) default | Cancel Passive (CP) since Dec 1, 2025 |

### Post-Trade Controls
| Parameter | Value |
|-----------|-------|
| PRISMA confidence level (listed) | 99% |
| PRISMA confidence level (OTC) | 99.5% |
| Default Fund SITG | EUR 143M |
| Default Fund SSITG | EUR 57M |
| **Total Default Fund** | **EUR 200M** |

**Key Points:**
- PLP: Configurable per session, rejects orders outside dynamic price range
- OTR: Monitored monthly, penalties applied for excessive message-to-execution ratios
- SMP: Four modes available (CancelNew, CancelPassive, CancelBoth, NoSMP)
- PRISMA: Real-time clearing risk monitoring with intraday margin calls
- Default Fund: CCP protection layer beyond participant margin

---

## 8. Key Regulatory Dates

| Date | Event |
|------|-------|
| May 15, 2013 | German HFT Act (HFT-MeldV) effective |
| Jan 3, 2018 | MiFID II/MiFIR effective |
| Apr 1, 2020 | SMP mandatory for algo proprietary trading |
| Dec 1, 2025 | SMP default changed to Cancel Passive (CP) |
| Nov 10, 2025 | T7 Release 14.0 production |
| May 18, 2026 | T7 Release 14.1 (TLS 1.3 only) |

**Upcoming Regulatory Milestones:**
- **MiFID III/MiFIR II**: Expected Q4 2026, pending European Commission adoption
- **DLT Pilot Regime**: Ongoing (June 2023 - March 2026), monitoring impact on exchange infrastructure
- **EMIR 3.0**: Expected Q2 2026, enhancing clearing and settlement oversight

---

## 9. Key Contact Points

| Team | Email | Phone |
|------|-------|-------|
| CTS (Customer Technology Services) | cts@deutsche-boerse.com | +49-69-211-10888 |
| Client Services (Eurex) | client.services@eurex.com | - |
| Member Section | member.section@deutsche-boerse.com | +49-69-211-17888 |
| ISV Registration | vendors@deutsche-boerse.com | - |
| Clearing Support | clearing.support@eurex.com | - |
| Production Newsboard | - | - |

**Key Points:**
- CTS: Primary contact for technical integration, connectivity, and co-location
- Client Services: Market access, membership, and commercial questions
- Member Section: Secure portal access, certificates, and user management
- ISV Registration: Required for third-party software vendors providing T7 connectivity
- Production Newsboard: Real-time notifications of system events (subscriptions via web portal)

---

## 10. Essential URLs

### Technical Resources
- **T7 Cloud Simulation**: [cloudsim.deutsche-boerse.com](https://cloudsim.deutsche-boerse.com)
- **Developer Portal**: [developer.deutsche-boerse.com](https://developer.deutsche-boerse.com)
- **GitHub Repositories**: [github.com/Deutsche-Boerse](https://github.com/Deutsche-Boerse)
- **API Documentation**: [deutsche-boerse.com/resource/API](https://www.deutsche-boerse.com/resource/API)

### Operational Resources
- **Production Newsboard**: [eurex.com/ex-en/trade/production-newsboard](https://www.eurex.com/ex-en/trade/production-newsboard)
- **Circulars**: [eurex.com/ex-en/find/circulars](https://www.eurex.com/ex-en/find/circulars)
- **Member Section**: [membersection.deutsche-boerse.com](https://membersection.deutsche-boerse.com)
- **System Status**: [status.deutsche-boerse.com](https://status.deutsche-boerse.com)

### Regulatory & Compliance
- **MiFID II/MiFIR Resources**: [deutsche-boerse.com/mifid-ii](https://www.deutsche-boerse.com/mifid-ii)
- **Clearing Rules & Procedures**: [eurex.com/ex-en/rules-regs/clearing](https://www.eurex.com/ex-en/rules-regs/clearing)
- **Market Data Policies**: [deutsche-boerse.com/market-data-policies](https://www.deutsche-boerse.com/market-data-policies)

### Training & Certification
- **T7 Trading Certification**: [eurex.com/ex-en/support/education](https://www.eurex.com/ex-en/support/education)
- **Webinar Archive**: [deutsche-boerse.com/webinars](https://www.deutsche-boerse.com/webinars)

---

## Quick Decision Trees

### Choosing a Session Type
```
Need > 150 TPS? → HF Ultra
Need 51-150 TPS? → HF Full
Need ≤ 50 TPS? → HF Light
```

### Choosing a Gateway Type
```
Single-product strategy + latency critical? → PS Gateway
Multi-product access OR latency tolerance +12 μs? → LF Gateway
```

### Choosing a Market Data Feed
```
HFT / market making? → EOBI
Partial depth + FIX/FAST preferred? → EMDI
Standard trading application? → MDI
Pre-market / static data only? → RDI
```

### Choosing Time Synchronization
```
Latency arbitrage / sub-microsecond precision? → White Rabbit
Standard HFT application? → PTP (±50 ns)
Independent reference / compliance? → GPS Antenna
```

---

## Abbreviations Reference

| Abbr. | Full Term |
|-------|-----------|
| CoLo | Co-Location |
| CP | Cancel Passive (SMP mode) |
| EMDI | Enhanced Market Data Interface |
| EOBI | Enhanced Order Book Interface |
| ETI | Enhanced Trading Interface |
| HFT | High-Frequency Trading |
| LF | Logical Flow |
| MDI | Market Data Interface |
| OTR | Order-to-Trade Ratio |
| PLP | Price Limit Protection |
| PS | Partition-Specific |
| PTP | Precision Time Protocol (IEEE 1588) |
| RDI | Reference Data Interface |
| RMS | Root Mean Square |
| SMP | Self-Match Prevention |
| SSITG | Supplemental Skin-in-the-Game |
| SITG | Skin-in-the-Game |
| TPS | Transactions Per Second |

---

[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
