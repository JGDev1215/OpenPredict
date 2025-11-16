# ICT Quantitative Prediction Model
## Setup Scoring System

---

**Document Version**: 2.0 Prediction Model Focus
**Created**: November 2025
**Purpose**: Automated ICT Setup Scoring & Prediction
**Framework**: ICT Methodology + Quantitative Validation

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [Scoring Components (Detailed)](#scoring-components)
4. [Two Agent System](#two-agent-system)
5. [Technical Implementation](#technical-implementation)
6. [Quick Reference Cards](#quick-reference)

---

## System Overview

### The Purpose
**Objective**: Real-time quantitative scoring of bullish and bearish trading setups based on ICT methodology

### The Problem
**Analysis Paralysis**: Subjective evaluation of ICT concepts leads to:
- Inconsistent setup identification
- Delayed decision-making
- Emotional bias in trade selection
- Difficulty comparing setup quality

### The Solution
**Quantitative ICT Prediction Model**:
- Converts ICT qualitative concepts → 0-100 numerical score
- Generates bullish AND bearish scores simultaneously
- Updates automatically every 3 minutes OR on-demand via UI trigger
- Two-agent architecture: Data collection + Score calculation
- Real-time scoring with historical data validation

---

## System Philosophy

### Core Principles

#### 1. Maintain ICT Methodology Integrity
**ICT concepts preserved**:
- PD Arrays (Fibonacci Pivot Points S1-3, PP, R1-3 (Weekly and Daily), Premium Discount Levels)
- Liquidity concepts (raids, sweeps, institutional flow)
- Kill Zone timing (London, NY sessions)
- Market structure analysis
- HTF bias alignment

**Enhancement through quantification** - Convert subjective analysis into objective scores

#### 2. Dual-Direction Scoring

**Simultaneous bullish AND bearish evaluation**:
```
Every 3 minutes (or on-demand):
├─ Bullish Setup Score: 0-100
└─ Bearish Setup Score: 0-100

User sees both scores side-by-side:
- Bullish: 45/100 ⭐⭐
- Bearish: 92/100 ⭐⭐⭐⭐⭐

Clear directional bias indicated by score differential
```

#### 3. Data-Driven Scoring

**Real-time market data processed**:
- Current price vs reference levels (opens, pivots, highs/lows)
- Session timing and position within kill zone
- Recent liquidity events (raids, sweeps)
- Market structure breaks and displacement
- Multi-timeframe alignment

**Historical context integrated**:
- Score-to-outcome correlation tracking
- Component effectiveness validation
- Session-based performance patterns

---

## System Architecture

### Visual System Design

```
┌────────────────────────────────────────────────────┐
│       ICT QUANTITATIVE PREDICTION MODEL            │
│                                                    │
│  ┌──────────────────┐      ┌──────────────────┐  │
│  │   AGENT 1        │─────►│   SUPABASE DB    │  │
│  │   Data Collector │      │                  │  │
│  │                  │      │ • OHLC Data      │  │
│  │ • yfinance API   │      │ • Reference      │  │
│  │ • 1-min bars     │      │   Levels         │  │
│  │ • Auto-refresh   │      │ • Liquidity      │  │
│  │   (every 60s)    │      │   Events         │  │
│  └──────────────────┘      └────────┬─────────┘  │
│                                     │            │
│                                     ▼            │
│  ┌──────────────────┐      ┌──────────────────┐  │
│  │   UI TRIGGER     │─────►│   AGENT 2        │  │
│  │   (Manual)       │      │   Score Engine   │  │
│  └──────────────────┘      │                  │  │
│                            │ Calculates:      │  │
│  ┌──────────────────┐      │ • Bullish 0-100  │  │
│  │   AUTO TIMER     │─────►│ • Bearish 0-100  │  │
│  │   (Every 3 min)  │      │                  │  │
│  └──────────────────┘      │ Components:      │  │
│                            │ • HTF Bias  30%  │  │
│                            │ • Kill Zone 20%  │  │
│                            │ • PD Array  25%  │  │
│                            │ • Liquidity 15%  │  │
│                            │ • Structure 10%  │  │
│                            │ • Equilib   ±5%  │  │
│                            └────────┬─────────┘  │
│                                     ▼            │
│                            ┌──────────────────┐  │
│                            │  DUAL SCORE      │  │
│                            │  OUTPUT          │  │
│                            │                  │  │
│                            │ Bullish: XX/100  │  │
│                            │ Bearish: XX/100  │  │
│                            └──────────────────┘  │
└────────────────────────────────────────────────────┘
```

### Data Flow

**Agent 1 (Data Collector) → Supabase**:
- Fetches OHLC data from yfinance every 60 seconds
- Calculates and stores reference levels (opens, pivots, highs/lows)
- Detects and logs liquidity events (raids, sweeps)
- Maintains historical data for scoring context

**Agent 2 (Score Engine) ← Supabase**:
- Triggered every 3 minutes (automatic) OR via UI button (manual)
- Reads latest market data from Supabase
- Calculates 6 scoring components for BOTH directions
- Outputs dual scores with component breakdowns

---

## Scoring Components

### Component 1: HTF Bias Alignment (30% Weight)

**Purpose**: Ensure trade direction aligns with higher timeframe institutional flow

#### Reference Levels (Priority Order)

| Level | Weight | Update | Purpose |
|-------|--------|--------|---------|
| Weekly Open | 3.0 | Monday 00:00 UTC | Primary institutional bias |
| Daily Open (00:00 UTC) | 3.0 | Every UTC midnight | Daily direction anchor |
| NY Open (08:30 ET) | 2.5 | Daily 08:30 ET | US market structure shift |
| Prev Day High | 2.5 | Daily close | Key resistance level |
| Prev Day Low | 2.5 | Daily close | Key support level |
| 4H Open | 1.5 | Every 4 hours | Medium-term intraday trend |
| 1H Open | 1.0 | Hourly | Short-term reference |
| Monthly Open | 1.0 | 1st of month | Macro context (seasonal) |

**Weighting Logic**: Higher timeframe opens receive greater weight (institutional significance)

#### Scoring Logic

```
For BEARISH setup:
  IF current_price < reference_level:
    signal = +1 (aligned)
  ELSE:
    signal = -1 (conflict)

For BULLISH setup:
  IF current_price > reference_level:
    signal = +1 (aligned)
  ELSE:
    signal = -1 (conflict)

Weighted Score = Σ(signal × weight) / Σ(weights)
HTF Score = Weighted Score × 30%
```

#### Example

```
BEARISH Setup at 21,440:

Weekly Open (21,450): Below ✓ → +1 × 3.0 = +3.0
Daily Open (21,425): Above ✗ → -1 × 3.0 = -3.0
Prev Day High (21,480): Below ✓ → +1 × 2.5 = +2.5
Prev Day Low (21,350): Above ✗ → -1 × 2.5 = -2.5
Monthly Open (21,200): Above ✗ → -1 × 1.0 = -1.0

Sum: 3.0 - 3.0 + 2.5 - 2.5 - 1.0 = -1.0
Total Weight: 12.0
Ratio: -1.0 / 12.0 = -0.083

HTF Score = -0.083 × 30 = -2.5%
```

**Result**: Weak bearish alignment (Daily Open conflict)

---

### Component 2: Kill Zone Timing (20% Weight)

**Purpose**: Trade during high-probability institutional activity windows

#### Kill Zone Definitions

| Session | Time (CEST) | Weight | ICT Principle |
|---------|-------------|--------|---------------|
| London KZ | 07:00-11:00 | 3.0 | Daily high/low formation |
| NY AM KZ | 13:30-16:00 | 3.0 | Continuation/reversal |
| NY PM KZ | 17:30-20:00 | 2.0 | Final push |
| London Close | 16:00-18:00 | 1.5 | Banking zone |
| Asian Session | 01:00-05:00 | 1.0 | Range formation |
| Outside | Other times | 0.5 | Low probability |

#### Time Decay Within Session

```
Session Position     Decay Factor
═════════════════   ══════════════
First 25%           1.00 (fresh setups)
Middle 50%          0.95 (optimal)
Final 25%           0.70 (late entry risk)
```

#### Day of Week Multiplier

```
Day         Multiplier   Historical Context
════        ══════════   ════════════════════════════════════════
Monday      1.00         Baseline (often lower volume, choppy)
Tuesday     1.15         Strong institutional activity begins
Wednesday   1.15         Peak continuation probability
Thursday    0.85         Reversal risk / profit-taking begins
Friday      0.70         Range-bound, targets often achieved early

Note: Multipliers reflect volume/volatility patterns that favor directional movement
```

#### Scoring Formula

```
Base Weight = Kill Zone Weight (0.5 to 3.0)
Time Decay = Position factor (0.70 to 1.00)
Day Mult = Day multiplier (0.70 to 1.15)

Adjusted = Base × Time Decay × Day Mult
(Capped at 3.0 maximum)

Kill Zone Score = (Adjusted / 3.0) × 20%
```

#### Example

```
Time: Tuesday 08:15 CEST
Session: London Kill Zone (07:00-11:00)

Calculation:
- Base Weight: 3.0 (London)
- Elapsed: 75 min / 240 min = 31% (middle 50%)
- Time Decay: 0.95
- Day Multiplier: 1.15 (Tuesday)

Adjusted = 3.0 × 0.95 × 1.15 = 3.28 (cap at 3.0)

Kill Zone Score = 3.0/3.0 × 20% = 20%
```

**Result**: Perfect kill zone timing

---

### Component 3: PD Array Confluence (25% Weight)

**Purpose**: Validate entry at institutional reference points

#### PD Array Types

| Type | Weight | ICT Definition |
|------|--------|----------------|
| Fibonacci Pivot Points | 3.0 | S3/S2/S1, PP, R1/R2/R3 (Weekly & Daily levels) |
| Previous Day High/Low | 2.5 | Daily range extremes (institutional reference) |
| Fair Value Gap (FVG) | 2.0 | Intraday imbalance (15-min timeframe; smaller FVG less reliable) |
| Price Discount/Premium Zone | 2.0 | 50% level between high/low of prior 2-hour period |
| Week High/Low | 2.0 | Weekly range extremes |
| Previous Week High/Low | 1.5 | Prior week range extremes | 

**Discount vs Premium Definition**:
- Bullish Trend: Price < 50% midpoint = Discount (buy opportunity)
- Bearish Trend: Price > 50% midpoint = Premium (sell opportunity)

#### Confluence Multiplier

**Principle**: Multiple institutional reference points aligned = higher probability

```
Arrays Present    Multiplier   Justification
══════════════   ══════════   ═════════════════════════════════
Single array     1.00×        One confirmation (baseline)
Two arrays       1.30×        Independent confluence (+30% boost)
Three+ arrays    1.50×        Strong institutional alignment (+50% boost)

Example progression:
- Fibonacci Pivot alone: +1.0
- Fibonacci + Premium Discount: +1.3
- Fibonacci + Premium Discount + FVG: +1.5 (maximum confidence boost)
```

#### Scoring Formula

```
Base = (Array Weight / 3.0) × Distance Factor
Enhanced = Base × Confluence Multiplier
PD Score = Enhanced × 25% (capped at 25%)
```

#### Example

```
Setup: BEARISH at 21,442

Arrays Present:
1. Fibonacci Pivot S1: 21,440 (distance: 2 pips)
2. FVG: 21,438-21,448 (price within zone)

Distance:
Price 21,442 at S1 level (21,440) → Factor 1.00 (within 5 pips)

Calculation:
Base = (3.0/3.0) × 1.00 = 1.00
Enhanced = 1.00 × 1.30 (two arrays) = 1.30
PD Score = 1.30 × 25% = 32.5%

Capped at 25% maximum
```

**Result**: Perfect PD confluence

---

### Component 4: Liquidity Raid (15% Weight)

**Purpose**: Confirm institutional stop-hunt before reversal

#### Raid Types

| Type | Weight | Typical Magnitude |
|------|--------|-------------------|
| Asia Range Raid | 3.0 | 10-30 pips |
| Prev Day High/Low | 2.5 | 15-50 pips |
| Equal Highs/Lows | 2.0 | 5-20 pips |
| Session High/Low | 1.5 | 5-15 pips |

#### Raid Quality

```
Quality Type       Factor   Definition
═══════════════   ═══════  ════════════════════════
Clean Sweep       1.00     Exceeded by 5+ pips
Wick Sweep        0.80     Wick touched, body didn't
Near Miss         0.40     Within 1-5 pips
Failed            0.00     >5 pips away
```

#### Hold Confirmation Bonus

```
Post-Raid Behavior              Bonus
═══════════════════════════════ ═════
Holds opposite side >15 min     +0.20
Immediate rejection (5-10 min)  +0.10
Slow drift (10-15 min)          +0.05
No hold/continues through       +0.00
```

#### Scoring Formula

```
Base = (Raid Weight / 3.0) × Quality Factor
Enhanced = Base + Hold Bonus
Liquidity Score = Enhanced × 15% (capped at 15%)
```

#### Example

```
Event: Asia Low raid (Weight 3.0)
Level: 21,380
Actual Low: 21,372 (-8 pips = clean sweep)
Quality: 1.00
Hold: 18 minutes above → Bonus +0.20

Calculation:
Base = (3.0/3.0) × 1.00 = 1.00
Enhanced = 1.00 + 0.20 = 1.20
Liquidity Score = 1.20 × 15% = 18%

Capped at 15% maximum
```

**Result**: Perfect liquidity raid

---

### Component 5: Market Structure (10% Weight)

**Purpose**: Validate directional bias through structure break

#### Structure Types

| Break Type | Weight | ICT Definition |
|------------|--------|----------------|
| Major Swing | 3.0 | Higher high/lower low on HTF |
| Intermediate | 2.0 | Swing break on execution TF |
| Minor Swing | 1.0 | Small internal structure |
| No Break | 0.0 | Structure intact |

#### Displacement Quality

```
Speed               Quality Factor
═════════════════  ══════════════
Strong (>20 pips in <15 min)  1.00
Moderate (10-20 pips)         0.70
Weak (<10 pips)               0.40
No displacement               0.00
```

#### Scoring Formula

```
Base = (Break Weight / 3.0) × Displacement Quality
Structure Score = Base × 10%
```

#### Example

```
Break: Intermediate swing (Weight 2.0)
Displacement: 25 pips in 12 min (strong)
Quality: 1.00

Calculation:
Base = (2.0/3.0) × 1.00 = 0.667
Structure Score = 0.667 × 10% = 6.67%
```

**Result**: Good structure confirmation

---

### Component 6: Equilibrium Context (±5% Bonus/Penalty)

**Purpose**: Multi-timeframe reference price alignment check

#### Reference Opens

| Reference | Weight | Purpose |
|-----------|--------|---------|
| Daily Open (00:00) | 3.0 | Primary equilibrium |
| NY Open (08:30) | 3.0 | Structure anchor |
| 4H Open | 2.5 | Intraday structure |
| 1H Open | 2.0 | Short-term reference |
| Prev 1H Open | 1.5 | Momentum context |

#### Agreement Calculation

```
For each reference:
  IF setup direction matches (price vs reference):
    contribution = +weight
  ELSE:
    contribution = -weight

Equilibrium Score = Σ(contributions) / Σ(weights)
```

#### Bonus/Penalty Assignment

```
Score Range    Adjustment
═══════════   ══════════
>70%          +5.0% (strong alignment)
60-70%        +2.5%
40-59%        0.0% (neutral)
30-39%        -2.5%
<30%          -5.0% (fighting TFs)
```

#### Example

```
BEARISH Setup at 21,440:

Daily Open (21,450): Below ✓ → +3.0
NY Open (21,430): Above ✗ → -3.0
4H Open (21,445): Below ✓ → +2.5
1H Open (21,442): Below ✓ → +2.0

Sum: 3.0 - 3.0 + 2.5 + 2.0 = +4.5
Total Weight: 10.5
Score: 4.5 / 10.5 = 0.429 (42.9%)

Result: 0% adjustment (neutral zone)
```

---

### Final Score Aggregation

```
TOTAL SCORE = HTF Bias (0-30%)
            + Kill Zone (0-20%)
            + PD Array (0-25%)
            + Liquidity (0-15%)
            + Structure (0-10%)
            + Equilibrium (±5%)

Range: -5% to 105% (practical: 0-100%)
```

#### Execution Thresholds

```
Score      Rating              Action
═════════  ═════════════════  ════════════════════════
85-100%    ⭐⭐⭐⭐⭐ ELITE     Execute immediately
70-84%     ⭐⭐⭐⭐ HIGH       Execute with confidence
55-69%     ⭐⭐⭐ ACCEPTABLE  Caution (skip if possible)
40-54%     ⭐⭐ MARGINAL     Skip
0-39%      ⭐ POOR           DO NOT TRADE
```

---

## Two Agent System

### Agent 1: yfinance Data Collector → Supabase

**Trigger**: Automatic every 60 seconds (continuous background process)

**Data Source**: yfinance API
- Instrument: User-configurable (NQ=F, ES=F, GC, CL, etc.)
- Timeframe: 1-minute OHLC bars
- Historical: Rolling 7-day window for context

**Data Collection Process**:
1. **Fetch Real-Time OHLC** (every 60 seconds)
   - Open, High, Low, Close, Volume
   - Timestamp (UTC)

2. **Calculate Reference Levels**:
   - Weekly Open (Monday 00:00 UTC)
   - Daily Open (00:00 UTC)
   - NY Open (13:30 UTC / 08:30 ET)
   - Previous Day High/Low
   - 4H Open, 1H Open
   - Monthly Open (1st of month)

3. **Compute Fibonacci Pivot Points**:
   **Formula**:
   ```
   Pivot Point (PP) = (High + Low + Close) / 3

   Resistance Levels (Fibonacci ratios):
   R1 = PP + (0.382 × (High - Low))
   R2 = PP + (0.618 × (High - Low))
   R3 = PP + (1.000 × (High - Low))

   Support Levels (Fibonacci ratios):
   S1 = PP - (0.382 × (High - Low))
   S2 = PP - (0.618 × (High - Low))
   S3 = PP - (1.000 × (High - Low))
   ```

   **Timeframes**:
   - Weekly pivots: Calculated using previous week's High, Low, Close
   - Daily pivots: Calculated using previous day's High, Low, Close

4. **Detect Liquidity Events**:
   - Asia session range (high/low)
   - Liquidity raids (price exceeds key level + returns)
   - Equal highs/lows sweeps
   - Session highs/lows

5. **Identify Market Structure**:
   - Higher highs / Lower lows (15min, 1H, 4H)
   - Structure breaks and displacement speed
   - Fair Value Gaps (FVG) - imbalance detection

6. **Block Segmentation Analysis** (Hourly Division):
   **Concept**: Divide each hour into 7 equal blocks for intra-hour bias analysis

   **Block Structure** (60 minutes ÷ 7 ≈ 8.57 min per block):
   ```
   Block 1 (00:00-08:34): Early formation
   Block 2 (08:34-17:08): Bias establishment
   Block 3 (17:08-25:42): Early counter detection
   Block 4 (25:42-34:16): Mid-hour pivot
   Block 5 (34:16-42:50): Sustained counter
   Block 6 (42:50-51:24): Late hour positioning
   Block 7 (51:24-60:00): Hour close targeting
   ```

   **Analysis Components**:

   a) **EarlyBiasAnalyzer** (Blocks 1-2):
      - Calculates initial directional bias from first two blocks
      - Measures price deviation from hour open
      - Determines dominant block (highest range)

   b) **SustainedCounterAnalyzer** (Blocks 3-5):
      - Detects reversal patterns in middle blocks
      - Identifies sustained counter-trend movement
      - Validates with volume and volatility confirmation

   c) **BlockPredictionEngine** (3 Decision Trees):

      **Tree 1: Early Bias Validation**
      ```
      IF (Block 1-2 avg deviation > +0.15%)
         AND (Block 2 higher high)
         AND (volatility increasing):
         → BULLISH continuation likely

      ELIF (Block 1-2 avg deviation < -0.15%)
         AND (Block 2 lower low)
         AND (volatility increasing):
         → BEARISH continuation likely

      ELSE:
         → NEUTRAL (consolidation)
      ```

      **Tree 2: Counter-Trend Detection**
      ```
      IF (Blocks 3-5 opposite direction to 1-2)
         AND (sustained crosses >= 2 blocks)
         AND (volume supports reversal):
         → REVERSAL signal

      ELIF (Mixed signals):
         → CHOP (range-bound)
      ```

      **Tree 3: Hour Close Prediction** (After Block 5)
      ```
      Components:
      - Early bias weight: 40%
      - Counter-trend weight: 35%
      - Volatility trend: 15%
      - Volume confirmation: 10%

      IF weighted_score > 60%:
         Direction = Dominant bias
         Confidence = weighted_score
      ELSE:
         Direction = NEUTRAL
      ```

   d) **Enhanced Volatility Calculation**:
      - Per-block range tracking
      - Block-to-block volatility comparison
      - Expansion/contraction pattern detection
      - ATR normalization for multi-instrument comparison

   **Storage**:
   - Each hourly block analysis saved to Supabase
   - Enables historical pattern recognition
   - Validates prediction accuracy over time

**Supabase Storage**:
```sql
-- Tables updated by Agent 1:
ohlc_data (timestamp, open, high, low, close, volume, instrument)
reference_levels (level_type, value, timestamp_created)
fibonacci_pivots (timeframe, s3, s2, s1, pp, r1, r2, r3, valid_from)
liquidity_events (event_type, level, timestamp, quality_factor)
market_structure (timeframe, structure_type, timestamp, displacement_pips)
fvg_zones (start_price, end_price, timeframe, timestamp_created)
hourly_blocks (hour_start, block_number, bias_direction, volatility, prediction_confidence)
```

**Error Handling**:
- Retry logic: 3 attempts with exponential backoff
- Data validation: Reject invalid/missing candles
- Logging: All errors written to Supabase error_log table

---

### Agent 2: Setup Score Calculator (Dual Direction)

**Trigger Options**:
1. **Automatic Timer**: Every 3 minutes (00, 03, 06, 09, 12, 15, etc.)
2. **Manual UI Button**: User clicks "Generate Score" in dashboard

**Data Source**: Supabase (populated by Agent 1)

**Processing Time**: <5 seconds

**Calculation Process**:

For **BOTH** bullish and bearish directions simultaneously:

1. **HTF Bias Component (30%)**:
   - Query reference levels from Supabase
   - Compare current price vs 8 reference opens
   - Calculate weighted alignment score for bullish direction
   - Calculate weighted alignment score for bearish direction

2. **Kill Zone Component (20%)**:
   - Determine current session (London/NY AM/NY PM/Asia/Other)
   - Calculate position within session (time decay factor)
   - Apply day-of-week multiplier
   - Same scoring applied to both directions

3. **PD Array Component (25%)**:
   - Query active Fibonacci pivots
   - Identify proximity to FVG zones
   - Check Previous Day/Week Highs/Lows
   - Calculate confluence multiplier (1.0x, 1.3x, 1.5x)
   - Evaluate distance factor
   - Bullish: Score higher near discount zones (S1, S2, S3)
   - Bearish: Score higher near premium zones (R1, R2, R3)

4. **Liquidity Component (15%)**:
   - Query recent liquidity events (last 4 hours)
   - Evaluate raid quality (clean sweep, wick, near miss)
   - Check hold confirmation (time above/below raid level)
   - Apply liquidity weight (3.0 for Asia raid, 2.5 for prev day H/L)

5. **Structure Component (10%)**:
   - Query market structure breaks (15min, 1H, 4H)
   - Measure displacement quality (pips moved / time)
   - Bullish: Higher weight for bullish structure breaks
   - Bearish: Higher weight for bearish structure breaks

6. **Equilibrium Component (±5%)**:
   - Query reference opens (Daily, NY, 4H, 1H)
   - Calculate multi-timeframe alignment
   - Award +5% bonus for strong alignment
   - Apply -5% penalty for conflicting timeframes

**Output Format**:
```json
{
  "timestamp": "2025-11-16T08:15:00Z",
  "instrument": "NQ=F",
  "current_price": 21440,
  "bullish_score": {
    "total": 45,
    "rating": "⭐⭐",
    "components": {
      "htf_bias": 8.5,
      "kill_zone": 20.0,
      "pd_array": 5.2,
      "liquidity": 3.0,
      "structure": 2.8,
      "equilibrium": 5.5
    }
  },
  "bearish_score": {
    "total": 92,
    "rating": "⭐⭐⭐⭐⭐",
    "components": {
      "htf_bias": 28.0,
      "kill_zone": 20.0,
      "pd_array": 24.5,
      "liquidity": 15.0,
      "structure": 7.0,
      "equilibrium": -2.5
    }
  },
  "directional_bias": "BEARISH",
  "bias_strength": 47
}
```

**UI Display** (rendered in dashboard):
```
═══════════════════════════════════════════════════════════
📊 SETUP SCORES - NQ=F @ 21,440
Updated: 08:15:00 CEST | Auto-refresh in 2:45
═══════════════════════════════════════════════════════════

🟢 BULLISH SCORE: 45/100 ⭐⭐ MARGINAL
├─ HTF Bias:     8.5/30  ⚠️  (Conflict - price above weekly open)
├─ Kill Zone:   20.0/20  ✓   (London KZ optimal)
├─ PD Array:     5.2/25  ⚠️  (Far from discount zone)
├─ Liquidity:    3.0/15  ⚠️  (No recent bullish raid)
├─ Structure:    2.8/10  ⚠️  (Bearish structure intact)
└─ Equilibrium: +5.5/5   ✓   (Some TF alignment)

🔴 BEARISH SCORE: 92/100 ⭐⭐⭐⭐⭐ ELITE
├─ HTF Bias:    28.0/30  ✓   (Strong alignment below opens)
├─ Kill Zone:   20.0/20  ✓   (London KZ optimal)
├─ PD Array:    24.5/25  ✓   (S1 pivot + FVG confluence)
├─ Liquidity:   15.0/15  ✓   (Asia low raided, held 18min)
├─ Structure:    7.0/10  ✓   (Bearish structure break)
└─ Equilibrium: -2.5/5   ⚠️  (Minor TF conflict)

🎯 DIRECTIONAL BIAS: BEARISH (Δ 47 points)
═══════════════════════════════════════════════════════════
[🔄 Generate New Score]  [📊 View History]  [⚙️ Settings]
═══════════════════════════════════════════════════════════
```

**Storage**:
- Each score calculation saved to Supabase `score_history` table
- Includes all component breakdowns for analysis
- Enables historical tracking and validation

---

## Technical Implementation

### System Architecture

**Tech Stack**:
- **Backend**: Python 3.11+
  - `yfinance` library for market data
  - `supabase-py` client for database operations
  - `pandas` for data manipulation
  - `schedule` or `APScheduler` for automated triggers

- **Database**: Supabase (PostgreSQL)
  - Real-time subscriptions for UI updates
  - Row-level security for data protection
  - TimescaleDB extension for time-series optimization

- **Frontend**: React + TypeScript (or Next.js)
  - Real-time score updates via Supabase subscriptions
  - Manual trigger button for score generation
  - Chart.js or TradingView widget for price visualization

### Supabase Database Schema

```sql
-- OHLC Data (populated by Agent 1)
CREATE TABLE ohlc_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    UNIQUE(timestamp, instrument)
);

-- Reference Levels (populated by Agent 1)
CREATE TABLE reference_levels (
    id BIGSERIAL PRIMARY KEY,
    level_type VARCHAR(50) NOT NULL,  -- 'weekly_open', 'daily_open', 'ny_open', etc.
    value DECIMAL(10,2) NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    timestamp_created TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ
);

-- Fibonacci Pivot Points (populated by Agent 1)
CREATE TABLE fibonacci_pivots (
    id BIGSERIAL PRIMARY KEY,
    timeframe VARCHAR(20) NOT NULL,  -- 'weekly', 'daily'
    instrument VARCHAR(20) NOT NULL,
    s3 DECIMAL(10,2),
    s2 DECIMAL(10,2),
    s1 DECIMAL(10,2),
    pp DECIMAL(10,2),
    r1 DECIMAL(10,2),
    r2 DECIMAL(10,2),
    r3 DECIMAL(10,2),
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ
);

-- Liquidity Events (populated by Agent 1)
CREATE TABLE liquidity_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,  -- 'asia_raid', 'prev_day_high_sweep', etc.
    level DECIMAL(10,2) NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    quality_factor DECIMAL(3,2),  -- 0.00 to 1.00
    hold_duration_minutes INTEGER
);

-- Market Structure (populated by Agent 1)
CREATE TABLE market_structure (
    id BIGSERIAL PRIMARY KEY,
    timeframe VARCHAR(20) NOT NULL,  -- '15min', '1H', '4H'
    structure_type VARCHAR(50) NOT NULL,  -- 'higher_high', 'lower_low', 'break_of_structure'
    instrument VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    displacement_pips DECIMAL(10,2)
);

-- Fair Value Gaps (populated by Agent 1)
CREATE TABLE fvg_zones (
    id BIGSERIAL PRIMARY KEY,
    start_price DECIMAL(10,2) NOT NULL,
    end_price DECIMAL(10,2) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    timestamp_created TIMESTAMPTZ NOT NULL,
    filled BOOLEAN DEFAULT FALSE
);

-- Hourly Block Segmentation (populated by Agent 1)
CREATE TABLE hourly_blocks (
    id BIGSERIAL PRIMARY KEY,
    hour_start TIMESTAMPTZ NOT NULL,
    block_number INTEGER NOT NULL,  -- 1 to 7
    instrument VARCHAR(20) NOT NULL,

    -- Block OHLC data
    block_open DECIMAL(10,2) NOT NULL,
    block_high DECIMAL(10,2) NOT NULL,
    block_low DECIMAL(10,2) NOT NULL,
    block_close DECIMAL(10,2) NOT NULL,
    block_volume BIGINT,

    -- Analysis metrics
    deviation_from_hour_open DECIMAL(5,2),  -- Percentage
    bias_direction VARCHAR(10),  -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    range_pips DECIMAL(10,2),
    volatility_score DECIMAL(5,2),

    -- Prediction fields (populated after block 5)
    hour_close_prediction VARCHAR(10),  -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    prediction_confidence DECIMAL(5,2),  -- 0-100%
    early_bias_weight DECIMAL(5,2),
    counter_trend_weight DECIMAL(5,2),

    -- Actual outcome (for validation)
    actual_hour_close DECIMAL(10,2),
    prediction_correct BOOLEAN,

    UNIQUE(hour_start, block_number, instrument)
);

-- Score History (populated by Agent 2)
CREATE TABLE score_history (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,

    bullish_total DECIMAL(5,2),
    bullish_htf_bias DECIMAL(5,2),
    bullish_kill_zone DECIMAL(5,2),
    bullish_pd_array DECIMAL(5,2),
    bullish_liquidity DECIMAL(5,2),
    bullish_structure DECIMAL(5,2),
    bullish_equilibrium DECIMAL(5,2),
    bullish_rating VARCHAR(20),

    bearish_total DECIMAL(5,2),
    bearish_htf_bias DECIMAL(5,2),
    bearish_kill_zone DECIMAL(5,2),
    bearish_pd_array DECIMAL(5,2),
    bearish_liquidity DECIMAL(5,2),
    bearish_structure DECIMAL(5,2),
    bearish_equilibrium DECIMAL(5,2),
    bearish_rating VARCHAR(20),

    directional_bias VARCHAR(10),
    bias_strength DECIMAL(5,2),

    trigger_source VARCHAR(20)  -- 'auto_timer' or 'manual_button'
);

-- Agent Error Logs
CREATE TABLE error_log (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    error_type VARCHAR(100),
    error_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

### Agent 1 Implementation (Python)

```python
# agent1_data_collector.py
import yfinance as yf
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import time

class DataCollector:
    def __init__(self, supabase_url, supabase_key, instrument='NQ=F'):
        self.supabase = create_client(supabase_url, supabase_key)
        self.instrument = instrument

    def run(self):
        """Main loop - runs every 60 seconds"""
        while True:
            try:
                self.fetch_and_store_ohlc()
                self.update_reference_levels()
                self.update_fibonacci_pivots()
                self.detect_liquidity_events()
                self.detect_market_structure()
                self.detect_fvg_zones()
                self.process_hourly_blocks()  # Block segmentation analysis

                time.sleep(60)  # Wait 60 seconds before next cycle

            except Exception as e:
                self.log_error('DataCollector', str(e))
                time.sleep(60)

    def fetch_and_store_ohlc(self):
        """Fetch 1-min OHLC from yfinance"""
        ticker = yf.Ticker(self.instrument)
        data = ticker.history(period='1d', interval='1m')

        for index, row in data.iterrows():
            self.supabase.table('ohlc_data').upsert({
                'timestamp': index.isoformat(),
                'instrument': self.instrument,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }).execute()

    def process_hourly_blocks(self):
        """Divide current hour into 7 blocks and analyze"""
        now = datetime.utcnow()
        hour_start = now.replace(minute=0, second=0, microsecond=0)

        # Calculate block number (1-7)
        minutes_elapsed = (now - hour_start).total_seconds() / 60
        block_number = min(int(minutes_elapsed / 8.571428) + 1, 7)

        # Fetch 1-min data for current block
        block_start_min = int((block_number - 1) * 8.571428)
        block_end_min = min(int(block_number * 8.571428), 60)

        # Query OHLC data for this block
        # Calculate block metrics (open, high, low, close, volume)
        # Compute deviation from hour open
        # Determine bias direction

        # If block >= 5, run prediction engine
        if block_number >= 5:
            self.predict_hour_close(hour_start, block_number)

        # Store block data to Supabase
        self.supabase.table('hourly_blocks').upsert({
            'hour_start': hour_start.isoformat(),
            'block_number': block_number,
            'instrument': self.instrument,
            # ... block OHLC and analysis data
        }).execute()

    # Additional methods for reference levels, pivots, liquidity, structure, FVG...
```

### Agent 2 Implementation (Python)

```python
# agent2_score_calculator.py
from supabase import create_client
from datetime import datetime
import schedule

class ScoreCalculator:
    def __init__(self, supabase_url, supabase_key, instrument='NQ=F'):
        self.supabase = create_client(supabase_url, supabase_key)
        self.instrument = instrument

    def run_auto_timer(self):
        """Auto-trigger every 3 minutes"""
        schedule.every(3).minutes.do(self.calculate_scores, trigger='auto_timer')

        while True:
            schedule.run_pending()
            time.sleep(1)

    def calculate_scores(self, trigger='manual_button'):
        """Main scoring logic"""
        current_price = self.get_current_price()

        # Calculate components for BOTH directions
        bullish_scores = self.calculate_bullish_components(current_price)
        bearish_scores = self.calculate_bearish_components(current_price)

        # Determine directional bias
        bias = 'BULLISH' if bullish_scores['total'] > bearish_scores['total'] else 'BEARISH'
        bias_strength = abs(bullish_scores['total'] - bearish_scores['total'])

        # Store to Supabase
        self.supabase.table('score_history').insert({
            'timestamp': datetime.utcnow().isoformat(),
            'instrument': self.instrument,
            'current_price': current_price,
            'bullish_total': bullish_scores['total'],
            # ... all component scores ...
            'directional_bias': bias,
            'bias_strength': bias_strength,
            'trigger_source': trigger
        }).execute()

        return {
            'bullish': bullish_scores,
            'bearish': bearish_scores,
            'bias': bias
        }

    # Component calculation methods...
```

---

## Quick Reference Cards

### Scoring Interpretation

```
SCORE      RATING              INTERPRETATION
═══════   ═════════════════   ═══════════════════════════════
85-100    ⭐⭐⭐⭐⭐ ELITE     Strong directional setup
70-84     ⭐⭐⭐⭐ HIGH       Favorable conditions
55-69     ⭐⭐⭐ ACCEPTABLE  Moderate setup quality
40-54     ⭐⭐ MARGINAL     Weak setup - caution advised
0-39      ⭐ POOR           Avoid - conditions unfavorable
```

### Component Weights

```
COMPONENT         WEIGHT    KEY FACTOR
════════════════ ═══════   ══════════════════════════════════
HTF Bias         30%       Price vs reference opens
Kill Zone        20%       Session timing + day multiplier
PD Array         25%       Pivot/FVG confluence + distance
Liquidity        15%       Raid quality + hold confirmation
Structure        10%       Break type + displacement speed
Equilibrium      ±5%       Multi-timeframe alignment bonus
```

### Directional Bias Interpretation

```
Bias Strength (Δ)    Interpretation
═══════════════════ ═══════════════════════════════════════
Δ > 40 points        Strong directional conviction
Δ 20-40 points       Moderate directional lean
Δ 10-19 points       Weak bias - mixed signals
Δ < 10 points        Neutral - no clear direction
```

---

## System Summary

This ICT quantitative prediction model successfully integrates:

1. **ICT Framework** - Proven institutional concepts (PD Arrays, Liquidity, Kill Zones, Structure, HTF Bias)
2. **Quantitative Scoring** - 0-100 objective validation for both bullish AND bearish setups
3. **Two-Agent Architecture** - Automated data collection + dual-direction score calculation
4. **Real-Time Updates** - Auto-refresh every 3 minutes + manual on-demand generation
5. **Historical Tracking** - All scores stored in Supabase for pattern analysis

### Key Capabilities

**Dual-Direction Scoring**:
- Simultaneous bullish and bearish evaluation
- Clear directional bias with strength indication
- Component-level breakdown for transparency

**Automated Data Pipeline**:
- Agent 1 fetches yfinance data every 60 seconds
- Calculates reference levels, pivots, liquidity events
- Detects market structure and Fair Value Gaps
- Stores everything in Supabase for Agent 2

**Flexible Triggering**:
- Auto-timer: Every 3 minutes during market hours
- Manual button: User-initiated score generation on demand
- Real-time UI updates via Supabase subscriptions

### Use Cases

1. **Pre-Entry Analysis**: Check current market bias before placing trades
2. **Confirmation Tool**: Validate trade ideas against quantified ICT concepts
3. **Pattern Recognition**: Identify which components drive high-probability setups
4. **Historical Validation**: Review past scores vs actual price movements
5. **Educational Tool**: Understand ICT methodology through numerical feedback

---

## Getting Started

### Setup Requirements

**1. Environment Setup**:
```bash
# Install Python dependencies
pip install yfinance supabase pandas schedule APScheduler

# Set environment variables
export SUPABASE_URL="your_supabase_project_url"
export SUPABASE_KEY="your_supabase_anon_key"
```

**2. Supabase Database**:
- Create new Supabase project
- Run database schema from "Technical Implementation" section
- Enable Row Level Security policies as needed
- Configure real-time subscriptions for score_history table

**3. Agent Deployment**:
```bash
# Run Agent 1 (background process)
python agent1_data_collector.py &

# Run Agent 2 (with auto-timer)
python agent2_score_calculator.py &
```

**4. Frontend Integration**:
- Connect React app to Supabase client
- Subscribe to `score_history` table for real-time updates
- Implement "Generate Score" button to trigger Agent 2 manually
- Display dual scores with component breakdowns

### Validation Checklist

```
DATA COLLECTION (Agent 1):
☐ yfinance API successfully fetches 1-min OHLC data
☐ Reference levels calculated correctly (Weekly/Daily/NY opens)
☐ Fibonacci pivots computed using correct formula (0.382, 0.618, 1.000 ratios)
☐ Weekly and daily pivots calculated from previous period H/L/C
☐ Liquidity events detected and stored with quality factors
☐ Market structure breaks identified on 15min/1H/4H timeframes
☐ Fair Value Gaps detected and tracked
☐ Hourly block segmentation divides hours into 7 blocks correctly
☐ EarlyBiasAnalyzer processes blocks 1-2 for initial bias
☐ SustainedCounterAnalyzer detects reversals in blocks 3-5
☐ BlockPredictionEngine generates hour close prediction after block 5
☐ Volatility calculations track per-block ranges and trends

SCORE CALCULATION (Agent 2):
☐ Auto-timer triggers every 3 minutes
☐ Manual button trigger works from UI
☐ Bullish score calculated with all 6 components
☐ Bearish score calculated with all 6 components
☐ Directional bias determined correctly
☐ Scores stored in Supabase with full breakdown

UI DISPLAY:
☐ Real-time score updates appear within 3 minutes
☐ Manual refresh button functional
☐ Component scores displayed with visual indicators
☐ Directional bias and strength shown prominently
☐ Historical scores accessible via "View History"
```

---

## Document Version History

**Version 2.0 - Prediction Model Focus** - November 16, 2025

**Major Changes**:
- **Complete system redesign**: Removed all profit targets, prop firm goals, trading execution sections
- **Two-agent architecture**: Redefined Agent 1 (yfinance → Supabase) and Agent 2 (dual-direction scoring)
- **Removed Agents 3, 4, 5**: Eliminated Trade Logger, Time Block Predictor, Weekly Analyzer
- **Removed sections**: Position Sizing, Performance Tracking, Daily Workflow, Trade execution guidance
- **Added**: Comprehensive Supabase schema, Python implementation outlines, dual-direction scoring logic
- **Focus shift**: Pure prediction model for setup scoring, NOT trading system

**Version 1.0 Improvements** (retained in V2.0):
- Fixed malformed PD Array table with proper weights and ICT definitions
- Removed Order Block (OB) concept - replaced with Fibonacci Pivots and FVG focus
- Reorganized PD Array types by weight priority (Fib Pivots highest at 3.0)
- Corrected Day of Week multiplier range (0.70 to 1.15)
- Fixed Tuesday multiplier in Kill Zone example (1.15, not 1.10)
- Updated PD Array example to use Fibonacci S1 pivot + FVG instead of OB

**Core Methodology** (unchanged):
- ICT Framework integrity maintained
- Scoring component weights (30/20/25/15/10/±5%) unchanged
- Reference level priorities unchanged
- Kill Zone definitions unchanged
- Fibonacci pivot calculations unchanged

---

## Disclaimer

**Purpose**: This system is a **prediction model** that quantifies ICT setup quality. It does NOT provide trading signals, entry/exit recommendations, or investment advice.

**System Limitations**:
- Scores are probabilistic evaluations, not guarantees of price direction
- Historical score accuracy varies based on market conditions
- Trending markets typically produce clearer directional bias than range-bound markets
- Gap opens, major news events, and low liquidity periods can invalidate scoring logic
- yfinance data may have delays or gaps during market hours

**User Responsibility**:
- This tool is for educational and analytical purposes only
- Users must perform their own analysis before making trading decisions
- No warranty or guarantee of accuracy, profitability, or fitness for any purpose
- Developers assume no responsibility for trading losses incurred using this system

