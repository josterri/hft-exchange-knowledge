---
layout: default
title: "6. Order Types & Matching"
nav_order: 6
parent: Chapters
---

# Chapter 6: Order Types & Matching Engine

The Deutsche Boerse T7 trading platform supports a sophisticated order management framework with over 15 distinct order types, multiple matching algorithms, and comprehensive risk protections at the order level. Understanding these mechanisms is critical for HFT developers building trading strategies on Eurex derivatives and Xetra equities markets.

This chapter examines the order types available across Eurex and Xetra, the matching algorithms that execute these orders, and the various protections and controls that operate at the order level to maintain fair and orderly markets.

## Introduction to T7 Order Management

The T7 system processes orders from submission through execution or cancellation using a multi-layered approach:

1. **Order Type Validation**: Ensures the order conforms to allowed types and parameters for the specific instrument
2. **Risk Controls**: Applies pre-trade risk checks including maximum order value, quantity limits, and price reasonability
3. **Matching Algorithm Selection**: Routes the order to the appropriate matching logic based on product configuration
4. **Book Management**: Maintains order priority according to algorithm-specific rules
5. **Execution Reporting**: Delivers fill confirmations with full execution details

The T7 platform handles orders for multiple asset classes across Eurex (futures and options on equity indices, interest rates, commodities, dividends, volatility, and FX) and Xetra (German and international equities, ETFs, ETCs, bonds). Each product category may utilize different order types, matching algorithms, and trading phases.

## Basic Order Types

T7 supports three fundamental order types that form the foundation for all trading activity:

| Order Type | Description | Key Behavior | Restrictions |
|-----------|-------------|--------------|--------------|
| Market | Execute immediately at best available price with no price limit | Not visible in order book, prioritized over limit orders | Not allowed for complex instruments (strategies) |
| Limit | Execute at specified price or better | Visible in order book until executed or cancelled | Available for all product types with all time-in-force options |
| Stop | Inactive order that becomes active when trigger price reached | Converts to active order (market or limit) when stop condition met | Reference price configurable (last traded, best bid/ask) |

### Market Orders

Market orders provide certainty of execution but uncertainty of price. Key characteristics include:

- **Immediate Execution**: Matched against the best available opposite-side limit orders
- **No Book Visibility**: Not displayed in order book depth since they execute immediately
- **Priority**: Executed before limit orders at the same price level
- **Fill Behavior**: May be partially filled if insufficient liquidity at best price, remainder executes at next price level
- **Pro-Rata Products**: Automatically flagged as Immediate-or-Cancel (IOC) for products using pro-rata matching

Market orders are particularly useful for strategies prioritizing execution certainty over price control, such as unwinding positions quickly or capturing immediate market opportunities.

### Limit Orders

Limit orders represent the majority of order book activity and provide price certainty with execution uncertainty:

- **Price Protection**: Never executes worse than specified limit price
- **Book Visibility**: Displayed in order book with full or partial quantity (iceberg orders)
- **Time-in-Force Flexibility**: Supports all TIF options including persistent orders that survive system restarts
- **Modification Rules**: Price changes create new order, quantity decreases maintain time priority
- **Universal Support**: Available across all T7 products including complex instruments

Limit orders form the foundation of liquidity provision and enable market makers to post two-sided quotes efficiently.

### Stop Orders

Stop orders enable conditional trading strategies by remaining inactive until market conditions trigger them:

- **Trigger Mechanism**: Becomes active when reference price reaches or crosses stop price
- **Reference Price Options**: Last traded price, best bid (for buy stops), best ask (for sell stops)
- **Conversion Behavior**: Transforms into market or limit order (stop-limit) upon activation
- **Use Cases**: Stop-loss protection, breakout strategies, trailing stops

The T7 system evaluates stop conditions continuously during trading phases and immediately converts triggered stops into active orders subject to normal matching rules.

## Time-in-Force Options

Time-in-Force (TIF) instructions control order lifecycle and persistence:

| TIF | Code | Behavior | Persistence | Key Use Cases |
|-----|------|----------|-------------|---------------|
| Good-for-Day | GFD | Expires at end of trading day | Non-persistent (deleted at market close) | Intraday strategies, daily reset positions |
| Good-Till-Cancelled | GTC | Active until executed or cancelled | Persistent (survives Market Reset, auto-deleted after 1 year) | Long-term limit orders, standing quotes |
| Good-Till-Date | GTD | Active until specified date | Persistent (survives Market Reset) | Event-driven strategies, calendar spreads |
| Immediate-or-Cancel | IOC | Execute immediately, cancel unfilled portion | Non-persistent | Liquidity taking, minimizing market impact |
| Fill-or-Kill | FOK | Fully executable or deleted entirely | Non-persistent (cash markets only) | All-or-nothing execution requirement |

### Persistence Behavior

Order persistence determines whether orders survive system maintenance events and session boundaries:

**Persistent Orders (GTC, GTD)**:
- Written to persistent storage (database)
- Survive T7 Market Reset events
- Restored automatically when trading resumes
- Higher latency due to database write operations
- Visible across all sessions
- Automatically deleted after 1 year (GTC) or specified date (GTD)

**Non-Persistent Orders (GFD, IOC, FOK)**:
- Stored in memory only
- Deleted during Market Reset
- Lower submission latency
- Must be re-entered after system restart
- Visible across all sessions

**Lean Orders**:
- Fastest submission path (memory-only, no replication)
- Visible only to submitting session
- Not survived across Market Reset
- Optimal for HFT strategies with continuous order management
- Available for both persistent and non-persistent TIF types

| Type | Persistent | Visible to Other Sessions | Survives Market Reset | Latency | HFT Suitability |
|------|-----------|--------------------------|----------------------|---------|-----------------|
| Standard Persistent | Yes (GTC/GTD) | Yes | Yes | Higher (DB write) | Medium |
| Standard Non-Persistent | No | Yes | No | Lower | High |
| Lean | No | No (submitting session only) | No | Lowest | Highest |

## Execution Restrictions

T7 provides several execution restrictions that modify how orders interact with the order book:

### Book-or-Cancel (BOC)

Book-or-Cancel orders ensure passive liquidity provision by preventing immediate execution:

- **Behavior**: Order rejected if immediately executable upon entry
- **Use Case**: Market makers ensuring they only add liquidity, never take it
- **Availability**: Options and futures products with closing auction support
- **Rejection**: Generates specific error code when executable condition detected

BOC orders guarantee that submitted orders will rest in the book and not cross the spread, making them ideal for liquidity provision strategies that require rebate capture or regulatory liquidity requirements.

### Market-to-Limit

Market-to-Limit orders provide hybrid behavior combining market order urgency with limit order price protection:

- **Initial Execution**: Behaves like market order, executing against available liquidity
- **Conversion**: After partial fill, converts remainder to limit order at last execution price
- **Price Protection**: Prevents adverse selection on remainder after initial liquidity exhausted
- **Use Case**: Large orders requiring immediate partial fill with price protection on remainder

This order type bridges the gap between full market orders (execution certainty but no price protection) and pure limit orders (price certainty but execution uncertainty).

## Eurex Special Order Types

Eurex markets support specialized order types for derivatives trading:

### One-Cancels-the-Other (OCO)

OCO orders combine limit and stop orders into a single logical order:

- **Structure**: Limit order component + stop order component
- **Single Order ID**: One Exchange Order ID for both components
- **Cancellation Logic**: Execution of either component automatically cancels the other
- **Use Case**: Bracket orders for profit-taking and stop-loss simultaneously
- **Priority**: Both components maintain independent time priority in respective queues

OCO orders streamline order management by reducing message traffic and ensuring atomic cancellation when one side executes.

### Trailing Stop

Trailing stops provide dynamic stop-loss protection that automatically adjusts to favorable price movements:

- **Variable Stop Limit**: Stop price continuously adjusted based on reference price movement
- **Favorable Adjustment Only**: Stop price moves only when market moves in profitable direction
- **Reference Price**: Configurable (last traded, best bid, best ask)
- **Trailing Distance**: Specified as absolute price offset or percentage
- **Activation**: Becomes active order when final stop price reached

Trailing stops are particularly valuable for momentum strategies and protective stops that lock in profits while allowing positions to run.

### Auction-Only Orders

Auction-only orders restrict execution to specific auction phases:

- **Opening-Auction-Only**: Only executable during opening auction
- **Closing-Auction-Only**: Only executable during closing auction
- **Rejection**: Automatically cancelled if not executed during designated auction
- **Use Case**: Index replication strategies, passive execution at auction prices

These order types enable strategies targeting auction prices specifically, such as closing price tracking or minimizing market impact through auction-only execution.

### Strategy Orders (Multi-Leg)

Eurex supports complex strategy orders spanning multiple legs:

| Strategy Type | Description | Max Legs | Use Case |
|--------------|-------------|----------|----------|
| Futures Combinations | Calendar spreads, butterfly spreads | Multiple | Term structure trading |
| Standard Options | Vertical spreads, straddles, strangles | Multiple | Volatility strategies |
| Non-Standard Options | Custom multi-leg combinations | Up to 5 | Complex options strategies |
| Option Volatility | Volatility surface trading | Multiple | Vol arbitrage |

Strategy orders execute atomically - all legs fill together or none fill, ensuring ratio integrity and preventing adverse selection on partial fills.

## Xetra Special Order Types

Xetra cash markets introduced several specialized order types in December 2024:

### Xetra Midpoint Orders

Midpoint orders enable hidden liquidity matching at the midpoint of the visible order book:

| Order Type | Description | Execution | Transparency |
|-----------|-------------|-----------|--------------|
| Limit Midpoint | Limit order executed at midpoint if available | Midpoint only | No pre-trade transparency |
| Market Midpoint | Market order executed at midpoint if available | Midpoint only | No pre-trade transparency |
| Limit Sweep | Try midpoint first, forward to CLOB if no match | Midpoint then CLOB | CLOB portion visible |
| Market Sweep | Try midpoint first, forward to CLOB if no match | Midpoint then CLOB | CLOB portion visible |

**Midpoint Execution Details**:
- Execution price = (best_bid + best_ask) / 2
- Requires tight spread (within configured maximum)
- No pre-trade transparency (orders not visible in book)
- Matching occurs before CLOB for sweep orders
- Sub-tick price improvement for traders
- Reduced market impact for large orders

Midpoint orders provide an alternative liquidity pool with price improvement for both buyers and sellers while maintaining market quality through spread requirements.

### Iceberg Orders

Iceberg orders enable large order placement while limiting market impact:

- **Hidden Quantity**: Only small portion (peak) visible in order book
- **Minimum Peak**: At least 5% of total quantity must be visible (factor of 20 maximum)
- **Refresh Behavior**: Hidden quantity automatically replenishes peak when executed
- **Time Priority**: New peak receives new timestamp upon refresh (loses priority)
- **Use Case**: Large institutional orders, minimizing information leakage

Example: 10,000-share iceberg with 500-share peak appears as 500 shares in book. After 500-share execution, next 500 shares appear with new timestamp.

### Pegged Orders

Pegged orders automatically adjust their limit price relative to a reference price:

- **Reference Prices**: Best bid, best ask, midpoint, last traded
- **Offset**: Configurable price offset (positive or negative) from reference
- **Automatic Adjustment**: Price updates continuously as reference moves
- **Priority**: Maintains time priority unless price change required
- **Use Case**: Algorithmic trading, relative value strategies

Pegged orders enable dynamic pricing strategies that track market movement without continuous manual repricing.

### Minimum Acceptable Quantity (MAQ)

MAQ provides fill-size protection for orders:

- **Behavior**: Order only executable if minimum quantity available
- **Partial Fill Control**: Prevents numerous small fills
- **Combination**: Works with other order types (limit, midpoint, etc.)
- **Use Case**: Large orders avoiding death by a thousand cuts
- **Rejection**: Order not matched if available quantity below MAQ

MAQ helps institutional traders control execution quality by ensuring meaningful fill sizes.

## Matching Algorithms

T7 employs three primary matching algorithms, each optimized for different product characteristics:

### Price-Time Priority (PTP)

Price-Time Priority is the primary matching algorithm for most T7 products:

**Algorithm Steps**:
1. **Price Priority**: Orders at best price (lowest for sell, highest for buy) matched first
2. **Time Priority**: At same price level, earliest order timestamp matched first (FIFO)
3. **Pro-Rata Within Time**: If multiple orders share identical timestamp, pro-rata allocation

**Key Characteristics**:
- Incentivizes early order placement for priority
- Rewards liquidity providers willing to improve price
- Simple and transparent priority rules
- Modification behavior affects priority

**Modification Rules**:

| Modification Type | Time Priority Impact | Rationale |
|------------------|---------------------|-----------|
| Quantity Increase | **Lost** (new timestamp) | Prevents gaming by adding quantity for priority |
| Quantity Decrease | **Maintained** (original timestamp) | Allows partial cancellation without penalty |
| Price Change | **Lost** (treated as new order) | Price change represents new trading decision |
| Other Attributes | **Maintained** (original timestamp) | Non-price/quantity changes don't affect queue |

**Product Coverage**:
- All Xetra equities and ETFs
- Most Eurex futures (equity index, interest rate, commodity)
- Eurex options excluding equity options
- Complex instruments (strategies)

Price-Time matching provides predictable execution priority and encourages tight spreads through price competition.

### Pro-Rata (PTR) Matching

Pro-Rata matching allocates incoming order quantity proportionally among resting orders at the best price:

**Algorithm Steps**:
1. **Price Priority**: Best price matched first (same as PTP)
2. **Pro-Rata Allocation**: At same price, quantity allocated proportionally to displayed size
3. **Size Priority**: Larger orders receive proportionally more allocation
4. **Time Priority**: After pro-rata rounding, residual quantity allocated by time

**Allocation Formula**:
```
allocated_qty = min(order_open_qty, floor((order_qty / total_best_price_qty) * incoming_qty))
```

**Example**:
```
Order Book (Best Price Level):
Order A: 100 shares (earliest)
Order B: 300 shares
Order C: 600 shares
Total: 1,000 shares

Incoming: 500-share market order

Allocation:
Order A: floor(100/1000 * 500) = 50 shares
Order B: floor(300/1000 * 500) = 150 shares
Order C: floor(600/1000 * 500) = 300 shares
Total: 500 shares (no residual)

If incoming = 501 shares:
Residual 1 share allocated to Order A (time priority)
```

**Key Characteristics**:
- Incentivizes larger order size for better fill rates
- Reduces incentive to race for time priority
- Encourages displayed liquidity over hidden orders
- Market orders automatically flagged IOC for pro-rata products

**Product Coverage**:
- All Eurex equity options
- Selected Eurex products configured for pro-rata

Pro-rata matching is particularly suitable for markets where displayed liquidity is valued and racing for time priority is less desirable.

### Pro-Rata with Top-of-Book Priority

This hybrid algorithm combines time priority for the top of book with pro-rata allocation for the rest:

**Algorithm Steps**:
1. **Price Priority**: Best price matched first
2. **Top-of-Book Priority**: First order at best price receives allocation until fully filled
3. **Pro-Rata for Rest**: Remaining orders at same price allocated pro-rata
4. **Time Priority for Residual**: After pro-rata, residual by time

**Example**:
```
Order Book:
Order A: 200 shares (earliest)
Order B: 300 shares
Order C: 500 shares
Total: 1,000 shares

Incoming: 500-share market order

Allocation:
Order A: 200 shares (filled completely - top of book priority)
Remaining: 300 shares for pro-rata

Order B: floor(300/800 * 300) = 112 shares
Order C: floor(500/800 * 300) = 187 shares
Residual: 300 - (112 + 187) = 1 share → Order B (time priority)

Final:
Order A: 200 shares
Order B: 113 shares
Order C: 187 shares
```

This hybrid approach balances time priority incentives for aggressive quoting with pro-rata benefits for displayed liquidity.

### Auction Matching

Auctions employ specialized matching logic optimized for single-price execution:

**Auction Types**:
- Opening Auction: Determines opening price and initial execution
- Closing Auction: Determines closing price (widely used as reference price)
- Intraday Auction: Scheduled or event-driven auctions during trading day
- Volatility Auction: Triggered by price movements outside dynamic corridors

**Price Determination Objectives**:
1. **Maximize Tradeable Volume**: Select price executing most shares
2. **Price Continuity**: Prefer price closest to reference price (last traded, prior auction)
3. **Market Pressure**: If tie, prefer price favoring market buy/sell pressure

**Auction Process**:
1. **Call Phase**: Orders entered, modified, cancelled (order book accumulation)
2. **Price Determination**: Calculate auction price based on objectives
3. **Order Book Freeze**: Brief freeze period (product-specific)
4. **Execution**: All matched orders execute at single auction price
5. **Publication**: Auction result published, continuous trading resumes

**Key Characteristics**:
- Single-price execution for all participants
- Uncrossing ensures no two executable orders remain
- Supports order entry, modification, cancellation during call phase
- Indicative auction price may be published during call phase
- Surplus orders remain in book after auction

Auctions concentrate liquidity at specific times and provide transparent price discovery, making them ideal for index replication, large orders, and benchmark pricing.

## Self-Match Prevention (SMP)

Self-Match Prevention prevents a trading firm's own orders from matching each other, avoiding wash trades and potential regulatory issues:

**Purpose**:
- Prevent business unit orders from matching internally
- Avoid wash trades (artificially inflating volume)
- Mandatory for proprietary algorithmic orders under MiFID II (effective April 1, 2021)

**Implementation**:
- SMP Type A on T7 platform
- Identification via Tag 28744 (MatchInstCrossID) in ETI protocol
- Active during continuous trading phase only (not auctions)
- Configurable cancellation behavior

### SMP Cancellation Options

As of Release 14.0 (December 1, 2025), T7 provides three cancellation options when self-match detected:

| Option | Code | Behavior | Default Since | Use Case |
|--------|------|----------|--------------|----------|
| Cancel Passive | CP | Resting order cancelled, incoming order matched | Dec 1, 2025 | Prioritize new order intent |
| Cancel Aggressive & Passive | CAP | Both orders cancelled | Pre-Dec 2025 | Maximum wash trade prevention |
| Cancel Aggressive | CA | Incoming order cancelled, resting order remains | Optional | Prioritize existing quotes |

**Default Change**:
Prior to December 1, 2025, the default was Cancel Aggressive & Passive (CAP). The new default of Cancel Passive (CP) reflects market participant feedback preferring to prioritize incoming order intent while maintaining wash trade prevention.

**Configuration**:
- Set at Business Unit level
- Applied consistently across all orders from that unit
- Configurable via ETI session parameters

**Example Scenario**:
```
Situation:
- Order A: Sell 100 @ 50.00 (resting in book, Business Unit X)
- Order B: Buy 100 @ 50.00 (incoming, Business Unit X)
- Both orders have same MatchInstCrossID

Outcome by SMP Setting:
- CP (Cancel Passive): Order A cancelled, Order B matches with other liquidity
- CAP: Both Order A and Order B cancelled
- CA (Cancel Aggressive): Order B cancelled, Order A remains in book
```

Self-Match Prevention is essential for algorithmic trading firms running multiple strategies that may generate opposing orders inadvertently.

## Passive Liquidity Protection (PLP)

Passive Liquidity Protection addresses latency arbitrage and stale quote sniping by deferring aggressive order execution:

**Purpose**:
- Protect market makers from latency-based arbitrage
- Prevent stale quote sniping when market makers updating quotes
- Level playing field for liquidity providers
- Encourage tighter spreads and deeper order books

**Mechanism**:
- Aggressive orders (taking liquidity) delayed by product-specific deferral time before matching
- Passive orders (posting liquidity) impact order book immediately without delay
- Deferral applied at matching engine before order matching logic

### PLP Deferral Times by Product

| Product Category | Deferral Time | Implementation Date |
|-----------------|--------------|---------------------|
| EURO STOXX 50 Index Options (OESX) | 1 ms | August 2019 (pilot) |
| DAX Index Options (ODAX) | 1 ms | August 2020 |
| STOXX 600 Index Options (OMSX) | 1 ms | Subsequent rollout |
| Equity Options (single stocks) | 1 ms | Ongoing expansion |
| Fixed Income Options | 1 ms | Ongoing expansion |
| Money Market Index Options | 1 ms | Ongoing expansion |
| FTSE 100 Options (OTUK) | 3 ms | October 2022 |
| FX Futures & Options | Varies by product | Product-specific |

**Order Type Behavior**:

| Order Type | Classification | PLP Applied |
|-----------|---------------|-------------|
| Market Order | Aggressive | Yes (deferred) |
| IOC Limit Order | Aggressive | Yes (deferred) |
| FOK Order | Aggressive | Yes (deferred) |
| Resting Limit Order (new) | Passive | No (immediate) |
| Resting Limit Order (existing) | Passive | No (immediate) |

**Matching Timeline Example (1 ms PLP)**:
```
T+0.00 ms: Aggressive market order arrives at matching engine
T+0.00 ms: PLP deferral timer starts
T+1.00 ms: Order released to matching algorithm
T+1.00 ms: Order matches against order book
T+1.05 ms: Fill confirmation sent to participant

During 0-1 ms window:
- Market makers can update/cancel stale quotes
- Other passive orders can be submitted
- Order book can adjust before aggressive order matches
```

**Market Impact**:
- Tighter spreads observed post-implementation (DAX options: spread reduction 10-15%)
- Increased order book depth (more displayed liquidity)
- Reduced adverse selection for market makers
- Minimal impact on overall market quality or execution speed

**Rollout History**:
- August 2019: Pilot for EURO STOXX 50 options (OESX)
- August 2020: DAX options (ODAX) after successful pilot
- October 2022: FTSE 100 options (OTUK) with 3 ms deferral
- Ongoing: Expansion to additional equity options and other asset classes

PLP represents a significant market structure innovation addressing the latency arms race while maintaining market quality and fairness.

## Risk Controls at Order Level

T7 implements several order-level risk controls to prevent erroneous orders and protect market integrity:

### Maximum Order Value (MOV)

Maximum Order Value provides fat finger protection by rejecting excessively large orders:

**Implementation**:
- Calculated as: Transaction Size Limit × Contract Size × Tick Value
- Applied at order entry before order reaches matching engine
- Effective limit = min(user-configured limit, exchange-defined limit)
- Rejection generates specific error code for immediate feedback

**Limit Determination**:
- Exchange sets per-product maximum based on typical trading volumes
- Annual review and adjustment by Deutsche Boerse risk committee
- Participants can set lower limits via risk management parameters
- Different limits for different product categories

**Example Calculation**:
```
Product: ODAX (DAX Options)
Contract Size: EUR 5
Tick Value: EUR 0.10
Transaction Size Limit: 10,000 contracts

Maximum Order Value: 10,000 × 5 × 0.10 = EUR 5,000
Maximum Notional: Depends on strike price and option value
```

MOV prevents single erroneous orders from causing extreme market dislocations while allowing legitimate large orders within reasonable boundaries.

### Maximum Order Quantity

Product-specific quantity limits prevent unreasonably large orders:

**Implementation**:
- Hard limit per product category
- Rejection at order entry with specific error code
- Published in product specifications
- Can be more restrictive than MOV for certain products

**Example Limits**:
```
Product Type          | Max Quantity
----------------------|-------------
Equity Index Options  | 50,000 contracts
Fixed Income Futures  | 10,000 contracts
Single Stock Options  | 25,000 contracts
Commodity Futures     | 5,000 contracts
```

Quantity limits complement MOV by preventing extreme position concentrations regardless of notional value.

### Price Reasonability Checks

Price collars prevent orders with clearly erroneous prices from entering the order book:

**Implementation**:
- Entry Interval: Acceptable price range around reference price
- Reference Price: Last traded, last auction, theoretical price (product-dependent)
- Rejection: Orders outside interval rejected immediately
- No Trading Halt: Unlike volatility interruptions, price collar violations do NOT trigger trading halts

**Price Collar Characteristics**:

| Check Type | Trigger | Action | Market Impact |
|-----------|---------|--------|---------------|
| Price Collar | Order price outside entry interval | Reject order | None (no halt) |
| Volatility Interruption | Potential execution outside dynamic corridor | Halt trading, auction | Temporary halt |

**Application Scope**:
- EnLight (OTC clearing): Prevents unreasonable clearing prices
- TES (Trade Entry Service): Validates manually entered trades
- Regular Order Entry: Applied to standard limit orders

Price reasonability checks provide an early filter for erroneous prices without disrupting continuous trading.

## Volatility Interruptions

Volatility Interruptions pause continuous trading and transition to auction mode when price movements exceed configured thresholds:

### Dynamic Price Corridors

Dynamic corridors establish acceptable price ranges based on recent market activity:

**Trigger Conditions**:
- Incoming order would execute outside dynamic corridor range
- Reference price: last traded price or theoretical price
- Corridor width: configurable percentage based on product volatility
- Fast Market Adjustment: Corridors auto-widen during "fast market" declaration

**Corridor Parameters**:
```
Corridor Width = Reference Price × Volatility Factor
Upper Limit = Reference Price × (1 + Volatility Factor)
Lower Limit = Reference Price × (1 - Volatility Factor)

Example (5% corridor, Reference = 100.00):
Upper Limit = 100.00 × 1.05 = 105.00
Lower Limit = 100.00 × 0.95 = 95.00
```

**Fast Market Behavior**:
- Exchange declares fast market based on heightened volatility
- Corridor width automatically increases (e.g., 5% → 10%)
- Prevents excessive interruptions during high-volatility periods
- Automatic reversion to normal corridors when conditions normalize

### Static Price Corridors (Release 12.1+)

Static corridors complement dynamic corridors by preventing full-day price dislocations:

**Implementation**:
- Reference prices: Last auction price, last traded price, theoretical price
- Corridor width: Wider than dynamic corridors (typically 10-20%)
- Objective: Prevent circuit breaker triggers from extreme single-day moves
- Complementary: Both dynamic and static corridors evaluated

**Static vs. Dynamic Comparison**:

| Aspect | Dynamic Corridor | Static Corridor |
|--------|------------------|-----------------|
| Reference Price | Recent traded price (updates frequently) | Auction price, daily open (updates less) |
| Width | Narrow (2-5%) | Wide (10-20%) |
| Purpose | Prevent rapid short-term moves | Prevent extreme single-day moves |
| Update Frequency | Continuous | Per auction or session |
| Priority | Primary protection | Secondary protection |

### Automated Corridor Expansion (ACE) - Xetra

Xetra's Automated Corridor Expansion widens corridors progressively when auctions fail to produce valid prices:

**ACE Process**:
1. Volatility Interruption triggered
2. Volatility Auction begins
3. If no valid price: Wait minimum interval (120 seconds single-level, 120-300 multi-level)
4. Automatically widen corridor to next level
5. Repeat until valid price found or Extended Volatility Interruption

**Expansion Levels**:
```
Level 1: Standard corridor (e.g., 5%)
Level 2: First expansion (e.g., 8%)
Level 3: Second expansion (e.g., 12%)
Level 4: Final expansion (e.g., 20%)

If no valid price at Level 4: Extended Volatility Interruption (manual intervention)
```

**Interval Requirements**:
- Single-Level Products: Minimum 120 seconds per level
- Multi-Level Products: 120-300 seconds depending on product configuration
- Ensures sufficient time for participants to reassess and adjust orders

### Volatility Interruption Process

Full VI workflow from trigger to resolution:

**Trigger Event**:
```
Scenario: Eurex ODAX product
Current best bid: 18,500
Current best ask: 18,510
Dynamic corridor: ±3% (555 points)

Incoming order: Buy at 19,100
Potential execution: 19,100 (outside upper limit 19,055)
Action: Volatility Interruption triggered
```

**VI Workflow**:
1. **Immediate Halt**: Continuous trading suspended instantly
2. **Instrument Status**: Changed to "Volatility Interruption" (broadcast via market data)
3. **Transition to Auction**: Volatility Auction call phase begins
4. **Order Management**: Participants can enter, modify, cancel orders during call phase
5. **Indicative Price**: T7 publishes indicative auction price (if calculable)
6. **Price Determination**: Auction matching algorithm calculates final price
7. **Validation**: Check if auction price within valid corridors
8. **Resolution Scenarios**:
   - **Valid Price**: Auction executes, continuous trading resumes
   - **No Valid Price (Xetra)**: ACE widens corridor, repeat auction
   - **No Valid Price (Final)**: Extended Volatility Interruption (manual intervention required)
9. **Resumption**: If successful, return to continuous trading mode

**Frequency Limits**:
- No minimum interval between consecutive VIs (removed in recent releases)
- Allows rapid successive interruptions during extreme volatility
- Each interruption treated independently

**Market Data**:
- VI trigger broadcast immediately
- Instrument status updates via EOBI and EMDI
- Indicative auction price published during call phase
- Final auction result published before continuous trading resumes

Volatility interruptions balance market safety (preventing disorderly trading) with efficiency (minimizing trading halt duration).

## Order Book Management

### Order Priority After Modification

Understanding priority rules is critical for optimizing order placement and modification strategies:

| Modification Type | Time Priority | Price Level | Rationale |
|------------------|---------------|-------------|-----------|
| Quantity Increase | **Lost** (new timestamp) | Same | Prevents gaming via quantity addition for priority |
| Quantity Decrease | **Maintained** (original timestamp) | Same | Allows partial cancellation without penalty |
| Price Improvement | **Lost** (new timestamp) | New (better) | New price = new order entry |
| Price Worsening | **Lost** (new timestamp) | New (worse) | New price = new order entry |
| TIF Change | **Maintained** (original timestamp) | Same | Non-execution attribute change |
| Other Attributes | **Maintained** (original timestamp) | Same | Display quantity, identifiers, etc. |

**Strategic Implications**:
- Quantity reductions safe for maintaining priority (used by market makers adjusting quotes)
- Any price change loses priority - better to cancel and replace if speed critical
- Quantity increases lose priority - submit separate order instead for HFT strategies
- Non-price/quantity modifications preserve queue position

### Iceberg Order Refresh Behavior

Iceberg orders balance large order execution with market impact minimization:

**Initial Entry**:
```
Total Quantity: 10,000 shares
Peak Quantity: 500 shares (5% of total)
Hidden Quantity: 9,500 shares

Order Book Display:
Order ID 12345: 500 shares @ 50.00 (timestamp T1)
```

**After Peak Execution (500 shares)**:
```
Execution: 500 shares @ 50.00
Remaining Total: 9,500 shares
New Peak: 500 shares (next tranche)
Hidden Quantity: 9,000 shares

Order Book Display:
Order ID 12345: 500 shares @ 50.00 (timestamp T2 - NEW)

Priority Lost: New timestamp T2 moves order to back of queue at 50.00
```

**Strategic Considerations**:
- Peak size determines visibility vs. priority tradeoff
- Smaller peaks = lower market impact but more frequent priority loss
- Larger peaks = fewer refreshes but higher information leakage
- Minimum 5% (20:1 ratio) enforced on Xetra

### Market Reset Synchronization

Market Reset events require careful state synchronization:

**Pre-Reset**:
- Participants receive Market Reset notification
- Countdown period before reset execution
- Opportunity to cancel non-persistent orders

**During Reset**:
- T7 system brief downtime (typically <1 minute)
- Persistent orders written to disk
- Non-persistent orders deleted
- Session state cleared

**Post-Reset**:
- System restart and connection re-establishment
- Persistent orders restated via Extended Order Information messages
- Participants process restatement messages to synchronize state
- Lean orders deleted (not restated)
- Trading resumes after synchronization period

**Synchronization Requirements**:
```
Participant State Before Reset:
Order A: GTC, 1000 shares @ 50.00, Order ID 12345
Order B: GFD, 500 shares @ 51.00, Order ID 12346
Order C: Lean GTC, 200 shares @ 49.00, Order ID 12347

Post-Reset Expected State:
Order A: Restated, same parameters, possibly new Order ID
Order B: Deleted (GFD non-persistent)
Order C: Deleted (Lean not restated)

Required Action:
- Match restated Order A by original ClOrdID
- Confirm deletion of Order B and Order C
- Re-enter Order B and Order C if still desired
```

Proper Market Reset handling is essential for avoiding duplicate orders and maintaining accurate position tracking.

## Summary

The T7 order management framework provides a sophisticated toolkit for implementing diverse trading strategies:

**Order Type Selection**:
- Basic types (market, limit, stop) cover fundamental needs
- TIF options control lifecycle and persistence
- Execution restrictions (BOC, market-to-limit) fine-tune behavior
- Specialized types (OCO, trailing stop, midpoint) enable advanced strategies

**Matching Algorithm Understanding**:
- Price-Time for most products incentivizes early placement
- Pro-Rata for equity options rewards size and displayed liquidity
- Auctions concentrate liquidity at specific times for price discovery
- Algorithm choice affects optimal order placement strategies

**Risk Management**:
- Order-level controls (MOV, quantity limits, price collars) prevent errors
- Self-Match Prevention avoids wash trades
- Passive Liquidity Protection addresses latency arbitrage
- Volatility interruptions maintain orderly markets

**Priority Optimization**:
- Modification rules determine queue position preservation
- Iceberg refresh behavior trades visibility for market impact
- Pegged orders enable dynamic pricing without manual updates

For HFT developers, mastering these order management mechanisms is foundational to strategy implementation, risk control, and latency optimization on Deutsche Boerse markets.

---

[Previous: Chapter 5 - Market Data Feeds](../05-market-data/README.md) | [Table of Contents](../../TABLE_OF_CONTENTS.md) | [Next: Chapter 7 - Market Models & Microstructure](../07-market-models/README.md)
