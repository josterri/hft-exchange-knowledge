# T7 Architecture Overview

The following diagram illustrates the T7 trading system architecture, showing the participant layer, gateway layer, core processing components, market data distribution, and persistence infrastructure.

```mermaid
flowchart TB
    subgraph Participants["Participant Layer"]
        HFS["High Frequency Session<br/>(Partition-Specific)<br/>Max 150 TPS"]
        LFS["Low Frequency Session<br/>(Multi-Partition)<br/>Single Connection"]
        FIXS["FIX Session<br/>(Industry Standard)<br/>Protocol Translation"]
        GUI["T7 GUI<br/>(Manual Trading)<br/>Web Interface"]
    end

    subgraph Gateways["Gateway Layer"]
        PSG1["PS Gateway 1<br/>(Partition 1)<br/>Co-located with ME"]
        PSG2["PS Gateway 2<br/>(Partition 2)<br/>Co-located with ME"]
        PSG3["PS Gateway N<br/>(Partition 11)<br/>Co-located with ME"]
        LFG["LF Gateways<br/>(All Partitions)<br/>+12us latency"]
        FIXG["FIX Gateways<br/>(Route via PS)<br/>Direct to partition"]
    end

    subgraph Core["Core Processing Layer"]
        subgraph Part1["Partition 1"]
            ME1["Matching Engine<br/>In-Memory State<br/>FIFO Processing"]
            RISK1["Risk Engine<br/>Pre-Trade Checks<br/>ARP / PTR Limits"]
        end
        subgraph Part2["Partition 2"]
            ME2["Matching Engine<br/>In-Memory State<br/>FIFO Processing"]
            RISK2["Risk Engine<br/>Pre-Trade Checks<br/>ARP / PTR Limits"]
        end
        subgraph PartN["Partition 11"]
            MEN["Matching Engine<br/>In-Memory State<br/>FIFO Processing"]
            RISKN["Risk Engine<br/>Pre-Trade Checks<br/>ARP / PTR Limits"]
        end
    end

    subgraph MarketData["Market Data Layer"]
        EOBI["EOBI<br/>Enhanced Order Book<br/>Full depth, all updates"]
        EMDI["EMDI<br/>Integrated in ME<br/>Lowest latency"]
        MDI["MDI<br/>Market Data Interface<br/>Aggregated data"]
        RDI["RDI<br/>Reference Data<br/>Static instrument data"]
    end

    subgraph Persistence["Persistence Layer"]
        PERS["Persistent Storage<br/>GTC/GTD Orders<br/>Survives failover"]
    end

    subgraph Redundancy["Redundancy Infrastructure"]
        RoomA["Room A<br/>Active System<br/>Primary Site"]
        RoomB["Room B<br/>Backup System<br/>Geographic Separation"]
        RedLink["Redundancy Link<br/>State Synchronization<br/>Emergency Backup"]
    end

    HFS --> PSG1
    HFS -.-> PSG2
    HFS -.-> PSG3
    LFS --> LFG
    FIXS --> FIXG
    GUI --> LFG

    PSG1 --> ME1
    PSG2 --> ME2
    PSG3 --> MEN
    LFG --> ME1
    LFG --> ME2
    LFG --> MEN
    FIXG --> PSG1
    FIXG -.-> PSG2
    FIXG -.-> PSG3

    ME1 --> RISK1
    ME2 --> RISK2
    MEN --> RISKN

    ME1 --> EOBI
    ME1 --> EMDI
    ME1 --> MDI
    ME2 --> EOBI
    ME2 --> EMDI
    ME2 --> MDI
    MEN --> EOBI
    MEN --> EMDI
    MEN --> MDI

    ME1 -.-> PERS
    ME2 -.-> PERS
    MEN -.-> PERS

    RDI -.-> Participants

    Part1 -.-> RoomA
    Part2 -.-> RoomA
    PartN -.-> RoomA
    RoomA <-.-> RedLink
    RedLink <-.-> RoomB

    classDef participantStyle fill:#e1f5ff,stroke:#0066b3,stroke-width:2px,color:#000
    classDef gatewayStyle fill:#cce7ff,stroke:#0052a3,stroke-width:2px,color:#000
    classDef coreStyle fill:#b3d9ff,stroke:#003d7a,stroke-width:2px,color:#000
    classDef dataStyle fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#000
    classDef persistStyle fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#000
    classDef redundancyStyle fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#000

    class HFS,LFS,FIXS,GUI participantStyle
    class PSG1,PSG2,PSG3,LFG,FIXG gatewayStyle
    class ME1,ME2,MEN,RISK1,RISK2,RISKN coreStyle
    class EOBI,EMDI,MDI,RDI dataStyle
    class PERS persistStyle
    class RoomA,RoomB,RedLink redundancyStyle
```

## Architecture Layers

### Participant Layer
- **High Frequency Sessions**: Partition-specific, ultra-low latency access via PS gateways. Maximum 150 TPS (Full) or 50 TPS (Light).
- **Low Frequency Sessions**: Single session accessing all partitions, approximately 12 microseconds additional latency.
- **FIX Sessions**: Industry-standard FIX protocol, routed directly to partitions via PS gateways.
- **T7 GUI**: Web-based interface for manual trading and monitoring.

### Gateway Layer
- **PS Gateways (Partition-Specific)**: One-to-one mapping with matching engines, co-located on same physical server (since H1 2021). Lowest latency path.
- **LF Gateways (Low Frequency)**: Cross-partition routing, access all products via single connection.
- **FIX Gateways**: Protocol translation from FIX to ETI, routes to appropriate PS gateway.

### Core Processing Layer
- **Matching Engines**: In-memory order book, FIFO processing, deterministic execution. One per partition.
- **Risk Engine**: Pre-trade risk checks (ARP), post-trade risk limits (PTR), maximum order value enforcement.

### Market Data Layer
- **EOBI**: Enhanced Order Book Interface - full depth, all order book updates.
- **EMDI**: Enhanced Market Data Interface - integrated in matching engine process, lowest latency.
- **MDI**: Market Data Interface - aggregated market data for broader distribution.
- **RDI**: Reference Data Interface - static instrument data, product definitions, trading calendars.

### Persistence Layer
Stores GTC (Good-Till-Cancelled) and GTD (Good-Till-Date) orders. Persistent orders survive Market Reset and failover events.

### Redundancy Infrastructure
- **Room A / Room B**: Geographic redundancy with active-backup configuration.
- **Redundancy Link**: State synchronization between rooms, emergency backup path.
- **Side A / Side B**: Dual-sided infrastructure within each room for additional fault tolerance.

## Key Architectural Characteristics

1. **Partition Isolation**: Each partition is an independent failure domain. Failover on one partition does not impact others.

2. **Public Data First**: Market data published before execution reports sent to order originators, ensuring informational equality.

3. **Deterministic Processing**: Same input sequence produces same output sequence, critical for testing and strategy development.

4. **CoLo 2.0 Fairness**: Equal network access for all co-located participants, one low-latency entry point per partition.

5. **No Batching**: Orders processed individually in FIFO sequence without artificial delays.

6. **Sub-55 Microsecond Latency**: Median order request to response time under 55 microseconds via PS gateways.

---

[Back to Chapter 2: T7 Architecture](../chapters/02-t7-architecture/README.md)
