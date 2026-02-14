---
layout: default
title: "9. Risk Controls"
nav_order: 9
parent: Chapters
---

# Chapter 9: Risk Controls & Pre-Trade Checks

## Introduction

Deutsche Boerse operates a multi-layered risk management framework spanning pre-trade validation, intra-day monitoring, emergency controls, and clearing-level protections. This comprehensive system ensures market integrity, prevents erroneous trades, and protects participants from excessive losses. The framework integrates exchange-level controls (implemented in T7) with clearing-level risk management (PRISMA methodology at Eurex Clearing), regulatory requirements (MiFID II, German HFT Act), and participant-configurable protections.

This chapter documents all risk control mechanisms available on Deutsche Boerse's trading platforms, their configuration parameters, triggering conditions, and operational procedures. Understanding these controls is essential for high-frequency trading operations, as they directly impact order acceptance, execution behavior, and potential penalties.

## 1. Pre-Trade Risk Limits (PTRL)

Pre-Trade Risk Limits provide real-time validation of every order before acceptance into the order book. These checks occur within microseconds and reject orders that violate configured thresholds.

### Minimum Order Quantity (MOQ)

MOQ defines the smallest permissible order size for each product. Orders below MOQ are rejected immediately. MOQ is configured per product group and aims to prevent excessive micro-orders that consume system resources without meaningful liquidity contribution.

**Configuration**: Set by exchange per product, typically ranges from 1 contract (equity derivatives) to higher values for less liquid instruments.

### Minimum Order Value (MOV)

MOV establishes a minimum notional value threshold for orders. This control prevents submission of economically insignificant orders that increase message traffic disproportionately to their trading value.

**Calculation**: Order quantity × reference price (last traded price or theoretical value)

**Typical thresholds**: Vary by product group, commonly EUR 500-5000 notional

### Price Range Validation

Every order undergoes validation against dynamic price corridors before acceptance. These corridors adjust based on recent market activity and volatility conditions.

**Static Price Range**: Configured per product as percentage deviation from reference price (typically ±20-30%)

**Dynamic Price Range**: Adjusted based on recent volatility, calculated using short-term price movements

**Reference Price**: Latest traded price, or theoretical price if no recent trades

**Rejection**: Orders outside valid range receive immediate rejection message

### Price Reasonability Checks

Beyond simple range validation, the system performs multi-dimensional reasonability assessment:

1. **Spread Check**: Validates bid-ask spread against historical norms
2. **Volume-Weighted Validation**: Cross-references price against recent volume distribution
3. **Cross-Product Validation**: Compares related instruments (e.g., futures vs options on same underlying)
4. **Time-of-Day Adjustments**: Applies different thresholds during open, continuous trading, and closing

Orders failing reasonability checks are rejected with specific error codes indicating the violated constraint.

## 2. Transaction Size Limits (TSL)

Transaction Size Limits control the maximum order size and open position exposure per member, implementing a critical defense against runaway algorithms and operational errors.

### Configuration Hierarchy

TSL operates at multiple levels with cascading validation:

1. **Clearing Member Level**: Aggregate exposure across all trading members
2. **Trading Member Level**: Individual participant limits
3. **Product Group Level**: Limits per instrument family (e.g., all ODAX maturities)
4. **Individual Product Level**: Specific contract limits

### Limit Components

**Maximum Order Quantity**: Largest single order size permitted
- Validated on order entry
- Separate limits for buy and sell sides
- Product-specific configuration

**Maximum Open Position**: Net exposure ceiling
- Continuously monitored against filled orders
- Includes pending orders (gross exposure)
- Can trigger automatic order cancellation when approached

**Daily Volume Limit**: Cumulative traded volume per trading day
- Resets at start of trading day (00:00 CET)
- Tracks both order volume and executed volume

### Multipliers and Scaling

TSL supports configurable multipliers allowing temporary limit increases:

**Standard Multiplier**: 1.0× (baseline limits)
**Extended Multiplier**: 1.5-3.0× (increased capacity for market makers or special situations)
**Emergency Multiplier**: 0.1-0.5× (reduced exposure during stress events)

Multipliers apply uniformly across product groups or can be product-specific.

### Clearing Member vs Trading Member Control

**Clearing Member Responsibilities**:
- Set aggregate limits for all sponsored trading members
- Monitor total exposure across all participants
- Can override individual trading member limits
- Receives real-time alerts when thresholds approached

**Trading Member Autonomy**:
- Configure limits within clearing member allocation
- Self-imposed risk constraints below clearing member caps
- Direct control over participant-level TSL

### Enforcement and Notifications

When TSL threshold reached:
1. New orders in direction increasing exposure are rejected
2. Existing orders may be automatically canceled (configurable)
3. Real-time alert sent to trading member and clearing member
4. Event logged in audit trail with timestamp and limit details
5. Recovery requires manual intervention or automatic reset (time-based or position reduction)

## 3. Advanced Risk Protection (ARP)

Advanced Risk Protection integrates margin-based monitoring with automatic protective actions, bridging exchange-level order management with clearing-level risk assessment.

### Margin-Based Monitoring

ARP continuously evaluates member positions against margin requirements calculated by Eurex Clearing's PRISMA system:

**Initial Margin Utilization**: Real-time comparison of open positions value against posted collateral
**Variation Margin Exposure**: Intraday P&L tracking relative to available resources
**Stress Scenario Assessment**: Positions evaluated under extreme market moves

### C7 Integration

ARP integrates with Eurex Clearing's C7 clearing system, receiving real-time margin data and limit updates:

**Margin Call Prevention**: Predictive alerts when positions approach margin call territory
**Automatic Position Reduction**: Can trigger forced liquidation of positions before formal margin call
**Clearing Member Coordination**: Synchronizes risk actions between trading platform and clearing house

### Automatic Actions

When ARP thresholds breached:

1. **Level 1 (Warning - 70% utilization)**: Alert notification to member, no automatic action
2. **Level 2 (Risk - 85% utilization)**: Prevent new orders increasing exposure, maintain existing positions
3. **Level 3 (Critical - 95% utilization)**: Cancel all resting orders, prevent new submissions
4. **Level 4 (Emergency - 100% utilization)**: Automatic position liquidation via market orders

All actions logged with microsecond timestamps and communicated via dedicated risk channels.

### Recovery Procedures

ARP restrictions automatically lift when:
- Additional margin posted to clearing account
- Positions reduced below threshold through trading
- Market movements reduce margin requirements
- Clearing member manually acknowledges and approves continuation

## 4. Self-Match Prevention (SMP)

Self-Match Prevention prevents a trading participant's buy and sell orders from executing against each other, a mandatory requirement under MiFID II for market integrity.

### SMP Types

**CA (Cancel Aggressor)**: Cancels the incoming aggressive order that would cause self-match
- Preserves existing passive order in book
- Most common setting for market makers
- Minimizes market impact

**CP (Cancel Passive)**: Cancels the resting passive order
- Allows aggressive order to continue seeking fills
- Preferred by some aggressive strategies
- Can reveal liquidity removal

**CAP (Cancel Aggressor and Passive)**: Cancels both orders
- Maximum protection against self-execution
- Used for strict compliance environments
- May reduce fill rates

### Configuration

SMP settings configured per:
- Trading member level (applies to all users)
- User ID level (individual trader control)
- Product group level (instrument-specific behavior)

**Scope Definition**: SMP group identifier determines which orders checked against each other
- Same legal entity
- Same fund/account structure
- Configurable grouping logic

### MiFID II Compliance

MiFID II Article 48(6) mandates prevention of self-matching for continuous trading. Deutsche Boerse implements:

1. **Mandatory SMP**: All members must configure SMP setting (no default bypass)
2. **Audit Trail**: All prevented self-matches logged for regulatory reporting
3. **Periodic Review**: Clearing members must review SMP configurations quarterly
4. **Exception Reporting**: Any self-matches occurring despite SMP trigger investigation

### Default Setting Change (December 1, 2025)

Since December 1, 2025, the default SMP mode changed from CA to CP:

**Rationale**: Better alignment with typical HFT workflows where aggressive orders represent intentional liquidity-taking decisions

**Migration**: Existing members retained CA settings; new members default to CP

**Override**: Members can explicitly configure any SMP type regardless of default

## 5. Passive Liquidity Protection (PLP)

Passive Liquidity Protection introduces a deferral mechanism preventing immediate execution of aggressive orders against the participant's own passive quotes, providing a brief window for quote updates.

### Mechanism

When an aggressive order would match a participant's passive order:
1. Matching engine identifies potential self-match
2. Instead of immediate execution, system defers aggressive order
3. Deferral period (product-specific) allows quote management to update passive side
4. After deferral, if passive order still present, trade executes
5. If passive order canceled/modified during deferral, aggressive order continues to next level

### Product-Specific Timings

PLP deferral durations calibrated per product based on typical quote update latencies:

| Product Group | PLP Deferral Time |
|---------------|-------------------|
| ODAX (DAX Futures) | 1 millisecond |
| OESX (EURO STOXX 50 Futures) | 1 millisecond |
| OSTK FR (French Stock Options) | 3 milliseconds |
| OTUK (UK Stock Options) | 3 milliseconds |
| Fixed Income Options | 1 millisecond |

**Rationale for Variation**: Stock options markets have longer typical quote-to-cancel latencies due to wider product sets and lower per-instrument message rates.

### Interaction with SMP

PLP executes before SMP check:
1. PLP deferral occurs first
2. If passive order survives deferral window, SMP logic applies
3. SMP then determines whether execution proceeds or orders canceled

This sequencing allows quote managers to react to aggressive flow before enforcement of hard SMP rules.

### Performance Considerations

PLP deferral times are included in order latency measurements:
- Adds 1-3ms to matching latency for affected orders
- Does not affect orders not triggering PLP
- Transparent in order book depth (passive orders remain visible during deferral)
- Logged in execution reports with PLP flag indicator

## 6. Volatility Interruptions

Volatility Interruptions pause continuous trading and initiate auctions when price movements exceed predefined thresholds, preventing disorderly markets and allowing participants to reassess fair value.

### Dynamic Corridors

Dynamic corridors adjust continuously based on recent volatility:

**Calculation**: Reference price ± (volatility factor × recent price range)
**Update Frequency**: Recalculated every 5 seconds during continuous trading
**Volatility Factor**: Derived from 5-minute rolling window of price changes
**Trigger**: Trade or order crossing dynamic corridor boundary initiates interruption

### Static Corridors (Activated July 8, 2024)

Static corridors provide absolute percentage-based protection independent of recent volatility:

**Configuration**: Fixed percentage bands around reference price (typically ±5-15% depending on product)
**Activation Date**: July 8, 2024 (introduced to address flash crash scenarios where dynamic corridors widen excessively)
**Priority**: Static corridor acts as outer boundary; dynamic corridor operates within static bands
**Reference**: Opening price or last auction price

### Auction Call Extension (ACE)

ACE prevents interruption from ending during period of continued price discovery stress:

**Trigger Condition**: During volatility interruption auction, if auction clearing price would still violate corridor
**Action**: Auction extended by additional time period (typically 30-60 seconds)
**Maximum Extensions**: Usually 2-3 extensions before forced clearing at best available price
**Notification**: Broadcast message indicates ACE activation and new auction end time

### Auction Behavior During Interruptions

Volatility interruption auctions follow modified rules:

1. **Order Entry**: Participants can enter, modify, cancel orders freely during auction
2. **Price Determination**: Auction algorithm calculates clearing price maximizing executable volume
3. **Corridor Re-validation**: Calculated auction price checked against original trigger corridor
4. **Expansion Logic**: If still outside corridor, corridor temporarily widened (±1% increments) up to static limit
5. **Uncrossing**: When price within acceptable range, auction concludes with batch execution

### Random End

Auction termination uses random end mechanism to prevent gaming:

**Base Duration**: Announced auction minimum period (e.g., 120 seconds)
**Random Extension**: Additional 0-30 seconds random window
**Communication**: Participants know base time but not exact end moment
**Purpose**: Prevents front-running auction uncrossing or manipulative final-second order entry

## 7. Market Maker Protection (MMP)

Market Maker Protection allows designated market makers to configure automatic order cancellation when trading activity or market conditions exceed specified thresholds, protecting against adverse selection and runaway fills.

### Volume-Based MMP

**Metric**: Cumulative executed volume over rolling time window
**Configuration**: Maximum contracts executed per minute/5-minute/15-minute period
**Action**: When threshold breached, all resting orders automatically canceled
**Granularity**: Configurable per product group or aggregated across portfolio

### Delta-Based MMP

**Metric**: Net delta exposure accumulated from executions
**Application**: Particularly relevant for options market making
**Configuration**: Maximum net delta (positive or negative) per time period
**Calculation**: Sum of (executed quantity × option delta) for all fills
**Reset**: Time-based (e.g., every 5 minutes) or manual

### Vega-Based MMP

**Metric**: Cumulative vega exposure from options executions
**Purpose**: Protects against excessive volatility risk accumulation
**Configuration**: Maximum vega threshold per rolling window
**Calculation**: Sum of (executed quantity × option vega)
**Use Case**: Critical during high volatility events when vega risk expensive to hedge

### Percent-Based MMP

**Metric**: Percentage of typical daily volume executed in short period
**Configuration**: E.g., "cancel all if 10% of normal daily volume traded in 5 minutes"
**Adaptive**: Compares current activity to historical norms (20-day average)
**Anomaly Detection**: Triggers on unusual fill rates relative to baseline

### Auto-Deactivation

MMP can be configured with automatic resumption:

**Time-Based**: MMP restriction lifts after configurable cooldown period (e.g., 30 seconds)
**Manual Override Required**: Member must explicitly acknowledge and re-enable quoting
**Partial Reactivation**: Can resume with reduced order sizes or wider spreads
**Alert Integration**: MMP events trigger notifications to risk management systems

### Futures MMP

Futures MMP operates similarly but with adaptations for futures contract characteristics:

**Directional Limits**: Separate thresholds for long vs short exposure accumulation
**Rollover Handling**: Special logic during contract expiry/rollover periods
**Inter-Contract**: Can aggregate exposure across contract months
**Spread Trading**: Option to exclude spread trades from MMP calculations

## 8. Order-to-Trade Ratio (OTR)

Order-to-Trade Ratio monitoring identifies potentially abusive or inefficient trading behavior by measuring the proportion of orders submitted relative to trades executed.

### Volume-Based Formula

**Calculation**: (Total Ordered Volume / Total Traded Volume) - 1

**Example**:
- Ordered volume: 10,000 contracts
- Traded volume: 100 contracts
- OTR = (10,000 / 100) - 1 = 99

**Interpretation**: An OTR of 99 means 99 times more volume ordered than traded

**Threshold**: Typical concern thresholds range from 50-100 depending on product and market conditions

### Transaction-Based Formula

**Calculation**: (Number of Orders / Number of Trades) - 1

**Example**:
- Orders submitted: 5,000
- Trades executed: 50
- OTR = (5,000 / 50) - 1 = 99

**Purpose**: Captures messaging burden independent of order size
**Complementary**: Used alongside volume-based to detect different abuse patterns

### Volatility Factor (Since December 2023)

Deutsche Boerse introduced dynamic volatility adjustments to OTR thresholds in December 2023:

**Factor Levels**:
- **Factor 1.0**: Normal market conditions (baseline OTR thresholds apply)
- **Factor 1.5**: Moderate volatility (OTR thresholds increased 50%)
- **Factor 2.0**: High volatility (OTR thresholds doubled)
- **Factor 4.0**: Extreme volatility (OTR thresholds quadrupled)

**Determination**: Exchange sets volatility factor per product based on:
- Recent price volatility (standard deviation of returns)
- Order book depth changes
- Unusual market events (e.g., central bank announcements)

**Communication**: Volatility factor changes broadcast via market status messages

**Example**: If baseline OTR threshold is 50, during extreme volatility (factor 4.0), acceptable OTR becomes 200 before triggering warnings

### TR100 Reports

Deutsche Boerse generates TR100 reports containing detailed OTR statistics:

**Frequency**: Daily, covering previous trading day
**Content**:
- Member-level OTR metrics (volume-based and transaction-based)
- Per-product OTR breakdowns
- Hourly OTR distribution
- Comparison to peer averages
- Threshold breach notifications

**Distribution**: Sent to clearing members via secure portal (Clearing Gateway)

**Regulatory Use**: TR100 data shared with BaFin for German HFT Act compliance monitoring

**Thresholds in TR100**:
- **Green**: OTR below 50 (normal activity)
- **Yellow**: OTR 50-100 (monitoring)
- **Red**: OTR above 100 (explanation may be requested)

## 9. Excessive System Usage (ESU) Fees

Excessive System Usage fees charge participants for message traffic exceeding reasonable thresholds, incentivizing efficient order management and discouraging wasteful practices.

### Formula

**ESU Fee = (Transaction Count - Limit) × Per-Transaction Fee**

Where:
- **Transaction Count**: Total messages sent during measurement period (1 trading day)
- **Limit**: Free threshold before fees apply
- **Per-Transaction Fee**: Progressive rate increasing with excess volume

### Components

**Floor Component**: Minimum free transaction allowance
- Typical baseline: 500,000 messages per day per member
- Adjusted for market maker status (higher allowances)

**Volume Component**: Additional allowance based on traded volume
- Formula: Executed Volume (contracts) × Multiplier
- Multiplier varies by product liquidity (0.5-5.0)
- Rewards actual trading activity vs empty message traffic

**Total Limit = Floor + Volume Component**

### December 2025 Update: Passive/Aggressive Split

Starting December 2025, ESU fees differentiate message types:

**Passive Order Messages** (Order entry, modification, cancellation in book):
- Lower ESU weight (0.5×)
- Recognizes liquidity provision value
- Encourages market making

**Aggressive Order Messages** (Immediate execution attempts, IOC orders):
- Standard ESU weight (1.0×)
- Standard treatment

**Calculation Example**:
- Passive messages: 1,000,000 (weighted as 500,000)
- Aggressive messages: 200,000 (weighted as 200,000)
- Total weighted: 700,000 messages
- If limit is 500,000, ESU applies to 200,000 messages

### Volatility Factor

ESU limits adjust with volatility factor (same levels as OTR):

**Factor 1.0**: Standard ESU limits
**Factor 1.5**: ESU limits increased 50%
**Factor 2.0**: ESU limits doubled
**Factor 4.0**: ESU limits quadrupled

**Purpose**: Prevent penalties during legitimate high-activity periods driven by market conditions rather than participant behavior

### TR102 Reports

TR102 reports provide ESU fee transparency:

**Frequency**: Daily
**Content**:
- Total message count by member
- Passive/aggressive split
- Volume-based limit calculation
- Actual fees charged
- Weekly and monthly cumulative totals

**Dispute Process**: Members can challenge TR102 fees within 5 business days with supporting documentation

**Fee Collection**: Deducted from clearing account monthly

## 10. Kill Switch / Stop Button

The Kill Switch provides emergency capability to immediately halt all trading activity for a member, protecting against runaway algorithms or operational failures.

### 4-Eyes Principle

Kill Switch activation requires dual authorization:

**First Authorization**: Trading desk operator initiates kill switch request
**Second Authorization**: Risk manager or compliance officer confirms action
**Time Window**: Second authorization must occur within 60 seconds of first, otherwise request expires

**Purpose**: Prevents accidental activation while ensuring rapid response to genuine emergencies

### Emergency Trading Stop Role

**Configuration**: Clearing members designate specific personnel with Emergency Trading Stop role
**Privileges**: Ability to initiate and confirm kill switch
**Requirements**: Minimum 2 individuals per clearing member required
**Training**: Annual certification mandatory for role holders

### Clearing Member vs Participant Controls

**Clearing Member Kill Switch**:
- Immediately cancels all orders for all trading members under clearing member
- Blocks new order submission across all sponsored participants
- Cannot be overridden by trading members
- Requires clearing member action to restore trading

**Participant Kill Switch**:
- Cancels only that participant's orders
- Other participants under same clearing member unaffected
- Participant can self-restore after root cause resolved (with clearing member approval)

### Recovery Procedures

Restoration after kill switch activation:

1. **Root Cause Analysis**: Document reason for kill switch activation
2. **System Verification**: Confirm trading systems operating normally
3. **Risk Assessment**: Verify positions, margins, exposures acceptable
4. **Controlled Restart**: Gradual re-enablement (e.g., limit order entry only, then full functionality)
5. **Monitoring**: Enhanced surveillance for 24 hours post-restoration

**Regulatory Reporting**: Kill switch activations reported to BaFin within 24 hours with incident details

### Emergency GUI

Deutsche Boerse provides web-based emergency access:

**URL**: t7gui.emergency.eurex.com

**Functionality**:
- View current orders and positions
- Cancel individual orders or all orders
- Activate kill switch
- Access without T7 gateway connection
- Available 24/7

**Authentication**: Multi-factor authentication using hardware tokens

**Use Case**: Primary connection failure, allows risk management from any internet-connected device

**Limitations**: Order entry not supported (cancel/view only)

## 11. Clearing-Level Controls

Beyond exchange-level controls, Eurex Clearing implements portfolio-based risk management protecting the central counterparty and market as a whole.

### PRISMA Methodology

Portfolio Risk Management (PRISMA) calculates margin requirements using sophisticated modeling:

**Approach**: Portfolio-based (recognizes offsetting risks across positions)
**Model**: Value-at-Risk (VaR) using historical simulation
**Scenarios**: 5,000+ historical stress scenarios covering major market events since 1987
**Granularity**: Per clearing member, calculated every 5 minutes intraday

### Confidence Levels

PRISMA operates at multiple confidence intervals:

**99% Confidence Level**: Standard initial margin for most products
- Covers 99% of potential 1-day losses
- Typical baseline requirement

**99.5% Confidence Level**: Enhanced margin for higher-risk products
- Stricter protection
- Applied to volatile instruments or concentrated positions

**Risk Horizon**: Time period margin designed to cover:
- **2-day horizon**: Liquid futures and options
- **5-day horizon**: Less liquid instruments or large positions
- **Extended horizon**: Exotic products or stress periods

### Default Fund Waterfall

In the event of clearing member default, losses covered in sequence:

**Step 1: Defaulting Member's Margin**
- Initial margin posted by defaulted member
- First line of defense
- Typically covers 99%+ of default scenarios

**Step 2: Defaulting Member's Default Fund Contribution**
- Member's contribution to mutualized default fund
- Sized based on member's risk profile and trading volume
- Immediate loss absorption before CCP capital engaged

**Step 3: CCP Skin-in-the-Game (SITG) - EUR 143 Million**
- Eurex Clearing's dedicated capital tranche
- Demonstrates CCP alignment with member interests
- Ensures CCP has financial stake in risk management

**Step 4: Non-Defaulted Members' Default Fund Contributions**
- Mutualized losses spread across surviving clearing members
- Capped at each member's default fund contribution
- Incentivizes peer monitoring of risky behavior

**Step 5: Supplementary Skin-in-the-Game (SSITG) - EUR 57 Million**
- Additional CCP capital layer
- Secondary CCP commitment after member default fund exhausted

**Step 6: Assessment Powers**
- Authority to assess additional contributions from surviving members
- Capped amounts per assessment round
- Ultimate backstop

**Total CCP Skin-in-the-Game**: EUR 200 million (SITG EUR 143M + SSITG EUR 57M)

This waterfall structure aligns with EMIR requirements and provides multiple layers before losses reach non-defaulted members.

### Intraday Margin Calls

PRISMA triggers intraday margin calls when:

**Threshold Breach**: Portfolio value declines exceeding 70% of initial margin
**Call Issuance**: Member notified via C7 interface and email/phone
**Settlement Deadline**: Typically 1 hour to post additional collateral
**Escalation**: Failure to meet call triggers automatic position liquidation

**Eligible Collateral**:
- Cash (EUR, USD, GBP)
- Government bonds (haircut applied)
- Gold
- Equities (highly liquid, substantial haircut)

## 12. Regulatory Framework Summary

Deutsche Boerse's risk controls implement multiple regulatory mandates:

### MiFID II Article 48

**Requirements**:
- Pre-trade controls proportionate to member's activity
- Post-trade monitoring of trading behavior
- Automatic order cancellation capabilities
- Self-match prevention mandatory
- Circuit breakers for volatile markets

**Deutsche Boerse Implementation**:
- PTRL, TSL, MMP satisfy pre-trade requirements
- OTR, ESU provide post-trade monitoring
- Kill switch enables rapid intervention
- SMP mandatory for all members
- Volatility interruptions implement circuit breaker obligation

### RTS 6: Organizational Requirements for Trading Venues

**Risk Control Standards**:
- Real-time position monitoring
- Automated pre-trade risk limits
- Clear member vs participant controls
- Audit trail of all risk events

**Deutsche Boerse Compliance**: All risk controls logged with microsecond timestamps, full audit trail maintained for 7 years

### RTS 7: Automated Trading Kill Switch

**Requirement**: Members engaged in algorithmic trading must have capacity to immediately stop trading

**Implementation**: Participant kill switch functionality, 4-eyes principle for activation

### RTS 8: Testing of Algorithms

**Requirement**: Testing and authorization of algorithms before production deployment

**Deutsche Boerse Testing Environment**:
- Simulation environment (T7 simulation)
- Conformance testing suites
- Algorithm registration process
- Annual re-certification

### German HFT Act (May 2013)

The German High-Frequency Trading Act imposes additional requirements:

**Algorithm Registration**: All HFT algorithms must be registered with BaFin
**Testing Documentation**: Evidence of testing required
**Kill Switch**: Mandatory emergency stop functionality
**OTR Monitoring**: Specific obligation to maintain reasonable OTR
**Flagging**: HFT orders must be flagged in regulatory reporting

**Deutsche Boerse Support**:
- TR100/TR102 reports facilitate OTR/ESU compliance
- Algorithm testing environment
- Order flagging fields in T7 protocol
- Audit trail supports regulatory inquiries

### Algorithm Testing Requirements

Formal testing obligations before production:

**Functional Testing**: Verify algorithm behaves as designed under normal conditions
**Stress Testing**: Algorithm behavior during extreme market conditions (volatility, low liquidity)
**Kill Switch Testing**: Verify emergency stop works correctly
**Self-Trade Testing**: Confirm SMP prevents unintended self-execution
**Limit Testing**: Validate algorithm respects PTRL, TSL, MMP

**Documentation**: Test results must be maintained and available for regulator inspection

**Re-Testing**: Required after material algorithm changes

### Order Flagging

MiFID II and German HFT Act require identification of algorithmic trading:

**Algo Flag**: Binary indicator on every order whether generated by algorithm
**HFT Flag**: Additional indicator for high-frequency trading activity
**DEA Flag**: Direct Electronic Access (DEA) identification
**Waiver**: Short-Code Identifier linking orders to specific algorithm

**T7 Implementation**: Flags embedded in order entry messages, validated by gateway, stored in audit trail

## Summary: Risk Controls Matrix

| Control | Type | Controller | Key Parameters | Trigger Condition |
|---------|------|------------|----------------|-------------------|
| **MOQ/MOV** | Pre-Trade | Exchange | Min quantity, min notional value | Order entry |
| **Price Range** | Pre-Trade | Exchange | Static/dynamic corridors | Order entry |
| **TSL** | Pre-Trade | Clearing Member, Trading Member | Max order size, max position, daily volume | Order entry, position update |
| **ARP** | Intra-Day | Exchange + Clearing | Margin utilization thresholds (70/85/95/100%) | Continuous |
| **SMP** | Pre-Trade | Trading Member | CA/CP/CAP mode | Potential self-match |
| **PLP** | Pre-Trade | Exchange | Deferral time (1-3ms by product) | Aggressive order vs own passive |
| **Volatility Interruptions** | Intra-Day | Exchange | Dynamic corridors, static corridors (±5-15%) | Price movement outside corridor |
| **MMP** | Intra-Day | Market Maker | Volume/delta/vega/percent thresholds | Execution activity exceeds limit |
| **OTR** | Post-Trade | Exchange (Regulatory) | Volume-based and transaction-based ratios, volatility factor (1/1.5/2/4) | Daily measurement |
| **ESU** | Post-Trade | Exchange (Fee) | Message limit (floor + volume), volatility factor, passive/aggressive split | Daily measurement |
| **Kill Switch** | Emergency | Clearing Member, Participant | 4-eyes authorization | Manual activation |
| **PRISMA Margins** | Clearing | Eurex Clearing | 99/99.5% confidence, 2-5 day horizon | Continuous (5-min recalc) |
| **Default Fund** | Clearing | Eurex Clearing | Waterfall: Margin → DF → SITG (EUR 143M) → SSITG (EUR 57M) | Member default |

---

This comprehensive risk control framework ensures Deutsche Boerse maintains orderly markets while providing flexibility for diverse trading strategies. Participants must configure and monitor these controls continuously, as improper settings can result in order rejections, trading halts, or regulatory sanctions. The multi-layered approach—from microsecond pre-trade checks through clearing-level portfolio risk management—reflects modern regulatory standards and operational best practices for high-frequency trading environments.

[Back to Table of Contents](../../TABLE_OF_CONTENTS.md)
