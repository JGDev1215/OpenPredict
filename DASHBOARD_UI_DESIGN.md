# ICT Quantitative Prediction Model - Dashboard UI/UX Design

**Document Version**: 1.0
**Created**: November 16, 2025
**Scope**: Complete dashboard design for real-time dual-direction scoring system
**Target Stack**: React + TypeScript, Bootstrap 5, Chart.js, Supabase subscriptions

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Layout Architecture & Wireframes](#layout-architecture--wireframes)
3. [Visual Hierarchy & Design System](#visual-hierarchy--design-system)
4. [Component Specifications](#component-specifications)
5. [Responsive Breakpoints & Mobile-First Strategy](#responsive-breakpoints--mobile-first-strategy)
6. [Color Palette & Typography](#color-palette--typography)
7. [Real-Time Data Integration](#real-time-data-integration)
8. [Interactive Elements & Filtering](#interactive-elements--filtering)
9. [Chart.js Implementation](#chartjs-implementation)
10. [Auto-Refresh & Timer Mechanism](#auto-refresh--timer-mechanism)
11. [State Management & React Architecture](#state-management--react-architecture)
12. [Loading States & Error Handling](#loading-states--error-handling)
13. [Accessibility Checklist](#accessibility-checklist)
14. [Performance Optimization](#performance-optimization)
15. [Implementation Code Snippets](#implementation-code-snippets)

---

## Executive Overview

### Dashboard Purpose

This dashboard transforms complex ICT quantitative scoring into an intuitive, real-time visualization system. It simultaneously displays:
- **Bullish vs Bearish scores** (0-100 each)
- **6 component breakdowns** per direction
- **Directional bias indicator** with strength visualization
- **Historical trending** with performance validation
- **Market context** (price, session, reference levels, liquidity events)

### Key Design Principles

1. **Dual-Direction Parity**: Both bullish and bearish scores displayed equally
2. **Visual Confidence**: Color intensity and star ratings indicate setup quality
3. **Mobile-First Responsive**: Stacks to single column on mobile, expands to 3-column on desktop
4. **Real-Time Affordance**: Visual countdown timer + auto-refresh feedback
5. **Deep Transparency**: Component tooltips explain every scoring metric
6. **Performance-Conscious**: Lazy loading, memoized components, efficient subscriptions

---

## Layout Architecture & Wireframes

### Desktop Layout (1200px+): 3-Column Grid

```
┌──────────────────────────────────────────────────────────────────────┐
│                      HEADER / TOP NAVIGATION                         │
│ Logo | "ICT Predictor" | Instrument Selector | Settings | Breadcrumb │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────────────────────────────────────┬──────────────────┐
│                 │                                          │                  │
│   LEFT PANEL    │      CENTER CONTENT (Main Feed)          │  RIGHT PANEL     │
│                 │                                          │                  │
│ • Current Price │  ┌──────────────────────────────────┐   │ • Reference      │
│ • Session Info  │  │ DUAL SCORE DISPLAY               │   │   Levels         │
│ • Kill Zone     │  │ ┌────────┐        ┌────────┐     │   │                  │
│   Indicator     │  │ │BULLISH │        │BEARISH │     │   │ • Fibonacci      │
│ • Market        │  │ │  45    │        │  92    │     │   │   Pivots         │
│   Context       │  │ │⭐⭐   │        │⭐⭐⭐⭐⭐│     │   │                  │
│                 │  │ └────────┘        └────────┘     │   │ • Liquidity      │
│ ▼ Collapsible   │  │                                  │   │   Events (4H)    │
│ • Premium/Disc  │  │ DIRECTIONAL BIAS                 │   │                  │
│ • FVG Zones     │  │ BEARISH (Δ 47)                   │   │ ▼ Chart View    │
│ • Recent        │  │ ████████████░░░░ (Progress Bar) │   │ • 1-Hour         │
│   Structure     │  └──────────────────────────────────┘   │ • 4-Hour         │
│                 │                                          │ • Daily          │
│                 │  ┌──────────────────────────────────┐   │                  │
│                 │  │ COMPONENT BREAKDOWN CARDS        │   │                  │
│                 │  │                                  │   │                  │
│                 │  │ BULLISH:                         │   │                  │
│                 │  │ [HTF Bias]  [Kill Zone] [PD]    │   │                  │
│                 │  │ [Liquidity] [Structure] [Equil] │   │                  │
│                 │  │                                  │   │                  │
│                 │  │ BEARISH:                         │   │                  │
│                 │  │ [HTF Bias]  [Kill Zone] [PD]    │   │                  │
│                 │  │ [Liquidity] [Structure] [Equil] │   │                  │
│                 │  └──────────────────────────────────┘   │                  │
│                 │                                          │                  │
│                 │  ┌──────────────────────────────────┐   │                  │
│                 │  │ ACTION BUTTONS                   │   │                  │
│                 │  │ [🔄 Generate New] [📊 History]  │   │                  │
│                 │  │ Auto-refresh in 2:45 ⏱️          │   │                  │
│                 │  └──────────────────────────────────┘   │                  │
│                 │                                          │                  │
└─────────────────┴──────────────────────────────────────────┴──────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ Historical Scores Table / Chart (collapsible, full-width)            │
│ Filters: Date Range | Score Range | Component Filter                │
└──────────────────────────────────────────────────────────────────────┘
```

### Tablet Layout (768px-1199px): 2-Column

```
┌──────────────────────────────────────────────────────┐
│   HEADER / TOP NAVIGATION                           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────┬─────────────────────────────┐
│   LEFT PANEL             │  RIGHT PANEL - MAIN CONTENT │
│ • Current Price          │  ┌──────────────────────┐   │
│ • Kill Zone              │  │ DUAL SCORE DISPLAY   │   │
│ • Context                │  │                      │   │
│                          │  │ BULLISH: 45/100      │   │
│ ▼ Reference Levels       │  │ BEARISH: 92/100      │   │
│ ▼ Liquidity Events       │  │                      │   │
│                          │  │ Bias: BEARISH (47)   │   │
│                          │  └──────────────────────┘   │
│                          │                             │
│                          │  ┌──────────────────────┐   │
│                          │  │ COMPONENTS (Bullish) │   │
│                          │  │ HTF | Kill | PD      │   │
│                          │  │ Liq | Struct | Equil │   │
│                          │  └──────────────────────┘   │
│                          │                             │
│                          │  ┌──────────────────────┐   │
│                          │  │ COMPONENTS (Bearish) │   │
│                          │  │ HTF | Kill | PD      │   │
│                          │  │ Liq | Struct | Equil │   │
│                          │  └──────────────────────┘   │
│                          │                             │
│                          │  [Refresh] [History]        │
│                          │  Auto-refresh: 2:45         │
└──────────────────────────┴─────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ Historical Data (full-width below)                   │
└──────────────────────────────────────────────────────┘
```

### Mobile Layout (< 768px): Single-Column Stacked

```
┌─────────────────────────────┐
│ HEADER (Compact)            │
│ Menu | Instrument | Settings│
└─────────────────────────────┘

┌─────────────────────────────┐
│ MARKET CONTEXT (Sticky Top) │
│ NQ=F @ 21,440              │
│ London KZ | 09:15 CET       │
└─────────────────────────────┘

┌─────────────────────────────┐
│ DUAL SCORE DISPLAY (Large)  │
│                             │
│  🟢 BULLISH                 │
│     45/100                  │
│     ⭐⭐ MARGINAL           │
│                             │
│  🔴 BEARISH                 │
│     92/100                  │
│     ⭐⭐⭐⭐⭐ ELITE        │
│                             │
│  Bias: BEARISH              │
│  Strength: Δ 47             │
└─────────────────────────────┘

┌─────────────────────────────┐
│ BULLISH COMPONENTS (Tabs)   │
│ [HTF] [Kill] [PD] [Liq]     │
│ [Struct] [Equil]            │
│                             │
│ HTF Bias: 8.5/30  ⚠️        │
│ Alignment: Weak (-2.5%)     │
│ > Read More                 │
└─────────────────────────────┘

┌─────────────────────────────┐
│ BEARISH COMPONENTS (Tabs)   │
│ [HTF] [Kill] [PD] [Liq]     │
│ [Struct] [Equil]            │
│                             │
│ HTF Bias: 28.0/30  ✓        │
│ Alignment: Strong (85%)     │
│ > Read More                 │
└─────────────────────────────┘

┌─────────────────────────────┐
│ ACTION BUTTONS (Full Width) │
│ [🔄 Generate New Score]     │
│ [📊 View History]           │
│ [⚙️ Settings]               │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Auto-refresh in: 2:45 ⏱️    │
│ Last update: 2 min ago      │
└─────────────────────────────┘

[Scrollable: Historical data below]
```

---

## Visual Hierarchy & Design System

### Primary Focus Areas (F-Pattern on Desktop)

1. **Top-Left Quadrant**: Dual score numbers (largest visual element)
   - Bullish score (left): Large green number
   - Bearish score (right): Large red number
   - Star ratings directly below

2. **Top-Center**: Directional bias indicator
   - Prominent badge showing "BULLISH", "BEARISH", or "NEUTRAL"
   - Bias strength visualization (progress bar, Δ value)
   - Color-coded background matching direction

3. **Middle**: Component breakdown cards
   - 6 cards per direction arranged in 2 rows x 3 columns
   - Each card shows: component name, score/max, status icon, visual bar
   - Hover reveals tooltip with ICT explanation

4. **Bottom**: Action buttons + timer
   - "Generate New Score" CTA (primary button)
   - "View History" (secondary button)
   - Real-time countdown to next auto-refresh

### Color Intensity Scale

**Score Ranges Drive Visual Intensity**:

```
Score:     0      20      40      50      60      80      100
          |-------|-------|-------|-------|-------|-------|
          POOR    MARGINAL ACCEPTABLE GOOD   HIGH   ELITE
          ████    ████    ████    ████   ████   ████
Bullish:  
Green:   #90EE90  #32CD32  #228B22  #0B8C0B (increasing saturation)
Opacity: 40%      60%     80%     100%

Bearish:
Red:     #FFB6C6  #FF6B6B  #DC143C  #8B0000 (increasing saturation)
Opacity: 40%      60%     80%     100%
```

### Confidence Indicators

- **Star Rating**: 1-5 stars directly below score
  - 1 star: 0-39 (POOR)
  - 2 stars: 40-54 (MARGINAL)
  - 3 stars: 55-69 (ACCEPTABLE)
  - 4 stars: 70-84 (HIGH)
  - 5 stars: 85-100 (ELITE)

- **Status Icons**:
  - ✓ (checkmark): Component > 70% of max
  - ⚠️ (warning): Component 40-70% of max
  - ✗ (x): Component < 40% of max
  - ? (question): Data insufficient

- **Component Bars**: Horizontal progress bars showing current/max
  - Full green bar: Strong component
  - Half-green bar: Moderate component
  - Thin bar: Weak component

---

## Component Specifications

### 1. Score Display Card

**Purpose**: Primary focal point showing bullish/bearish scores

**Desktop (1 per direction)**:
- Width: 280px
- Height: 240px
- Padding: 24px
- Border radius: 12px
- Shadow: 0 4px 16px rgba(0,0,0,0.1)
- Background: Subtle gradient or solid (white/dark mode aware)

**Structure**:
```
┌─────────────────────────────┐
│ 🟢 BULLISH (or 🔴 BEARISH)  │ (16px, semi-bold)
├─────────────────────────────┤
│           45                 │ (72px, bold, green/red)
│         ——————               │
│        100 Points            │ (14px, secondary text)
├─────────────────────────────┤
│    ⭐⭐ MARGINAL             │ (20px stars, rating label)
├─────────────────────────────┤
│ Progress: ████░░░░░░░░ 45%  │ (12px, bar chart)
└─────────────────────────────┘
```

**Mobile (Responsive)**:
- Width: 100% with padding
- Height: Auto
- Score number: 54px instead of 72px
- Horizontal layout: Score left, rating right

### 2. Directional Bias Badge

**Purpose**: Clear indication of setup direction and strength

**Design**:
```
┌─────────────────────────────────┐
│  🎯 BEARISH SETUP               │
│     Strength: Δ 47 points        │
│  ███████████░░░░░░░░ 85%        │
│                                  │
│ Interpretation: Strong bearish   │
│ conviction with minor conflicts  │
└─────────────────────────────────┘
```

**Responsive**:
- Desktop: 320px width, centered below scores
- Tablet: Full width with padding
- Mobile: Full width, stacked prominence

**Color Logic**:
- BULLISH: Green (#228B22) background
- BEARISH: Red (#8B0000) background
- NEUTRAL: Gray (#6C757D) background

### 3. Component Card Grid

**Purpose**: Display 6 component scores for bullish/bearish

**Layout**:
- Desktop: 2 rows x 3 columns per direction (6 cards total)
- Tablet: 3 rows x 2 columns per direction (scrollable if needed)
- Mobile: Single column with tabs or accordion (BTN: show bullish tabs/bearish tabs)

**Individual Card**:
```
┌──────────────────────────┐
│ HTF Bias        ⚠️        │ (Title + Status)
├──────────────────────────┤
│ 8.5 / 30 Points          │ (Score)
├──────────────────────────┤
│ ███░░░░░░░░░░░░░░░░░ 28% │ (Progress bar)
├──────────────────────────┤
│ ⓘ Alignment: Weak        │ (Tooltip trigger)
│   -2.5% below targets    │
└──────────────────────────┘
```

**Card Dimensions**:
- Desktop: 180px x 140px per card
- Tablet: 220px x 160px per card
- Mobile: Full width, ~120px height

**Interaction**:
- Hover: Slight elevation (box-shadow increase)
- Click: Show detailed tooltip (see Tooltips section)
- Touch: Tap to toggle tooltip on mobile

### 4. Reference Levels Panel (Left Sidebar - Desktop/Tablet)

**Purpose**: Display active reference levels for context

**Structure**:
```
┌────────────────────────────┐
│ REFERENCE LEVELS           │
├────────────────────────────┤
│ Weekly Open: 21,450        │
│ Daily Open: 21,425         │
│ NY Open: 21,430            │
│ PDH: 21,480 | PDL: 21,350  │
│ 4H Open: 21,445            │
│ 1H Open: 21,442            │
│ Month Open: 21,200         │
├────────────────────────────┤
│ Current Price: 21,440      │ ⬅️ Distance calc
├────────────────────────────┤
│ ▼ Fibonacci Pivots         │
│   S3: 21,234               │
│   S2: 21,337               │
│   S1: 21,440 ← (At S1!)    │
│   PP: 21,543               │
│   R1: 21,646               │
│   R2: 21,749               │
│   R3: 21,852               │
├────────────────────────────┤
│ ▼ Price Zones              │
│   Discount: 21,350-21,450  │
│   Premium: 21,450-21,550   │
└────────────────────────────┘
```

**Mobile Behavior**:
- Hidden by default
- Accessible via bottom sheet / modal (tap "Context" button)

### 5. Liquidity Events Panel (Right Sidebar - Desktop)

**Purpose**: Show recent (4-hour) liquidity raids and sweeps

**Structure**:
```
┌────────────────────────────┐
│ RECENT LIQUIDITY (4H)      │
├────────────────────────────┤
│ ✓ Asia Low Raid            │
│   Level: 21,372            │
│   Quality: Clean Sweep      │
│   Hold: 18 min ✓           │
│   Time: 06:45 CEST         │
│                             │
│ ⚠️ PDH Sweep               │
│   Level: 21,480            │
│   Quality: Wick Touch      │
│   Hold: 8 min              │
│   Time: 05:30 CEST         │
│                             │
│ ⚠️ Equal High Raid         │
│   Level: 21,442            │
│   Quality: Near Miss       │
│   Hold: Failed             │
│   Time: 04:15 CEST         │
└────────────────────────────┘
```

**Color Coding**:
- ✓: Green for confirmed raids (good hold)
- ⚠️: Orange for weak raids or failed holds
- ✗: Red for failed raids

### 6. Action Button Group

**Primary Button** - "Generate New Score":
- Text: "🔄 Generate New Setup Score"
- Style: Primary color (brand blue), full width on mobile
- State: Disabled during calculation (shows spinner)
- Tooltip: "Trigger manual score calculation (Agent 2)"

**Secondary Button** - "View History":
- Text: "📊 View Historical Scores"
- Style: Secondary color (outline), full width on mobile
- Action: Opens modal with historical scores table/chart

**Tertiary Button** - "Settings":
- Text: "⚙️ Settings"
- Style: Tertiary (text only), top-right corner
- Action: Opens modal for instrument selection, timeframe, etc.

**Desktop Spacing**: Buttons inline, 12px gap
**Mobile Spacing**: Stacked vertically, full width, 8px gap

### 7. Auto-Refresh Timer

**Purpose**: Show countdown to next automatic score generation

**Display**:
```
⏱️ Auto-refresh in 2:45
Last update: 2 minutes ago (as text)
Updated at: 09:15:00 CEST (timestamp)
```

**Behavior**:
- Counts down from 3:00 to 0:00
- Refreshes score at 0:00 (triggers Agent 2)
- Resets to 3:00 after refresh
- Pauses if user manually refreshes (shows "Manual refresh triggered")

**Visual Feedback**:
- Green circle with decreasing arc (countdown animation)
- Text changes color at 30 seconds (yellow)
- Text changes color at 10 seconds (red) with pulse animation

---

## Responsive Breakpoints & Mobile-First Strategy

### Breakpoint Definitions

```
Mobile (Portrait):    0px - 575px
Mobile (Landscape):   576px - 767px
Tablet (Portrait):    768px - 991px
Tablet (Landscape):   992px - 1199px
Desktop:              1200px+
Ultra-Wide:           1920px+
```

### Bootstrap 5 Utilities Applied

**Hide/Show by Breakpoint**:
```html
<!-- Reference levels panel hidden on mobile -->
<aside class="d-none d-lg-block col-lg-2">Reference Levels</aside>

<!-- Dual score cards stack on mobile, inline on desktop -->
<div class="row g-3">
  <div class="col-12 col-md-6 col-lg-auto">Bullish Card</div>
  <div class="col-12 col-md-6 col-lg-auto">Bearish Card</div>
</div>

<!-- Component grid responsive -->
<div class="row g-2 g-md-3">
  <!-- Cards auto-reflow based on container -->
</div>
```

**Typography Scaling**:
- h1 (Score numbers): 72px (desktop) → 48px (mobile)
- h3 (Component titles): 18px → 14px
- body (text): 16px → 14px
- small (labels): 12px → 11px

**Padding/Margin Scaling**:
- Container: 24px (desktop) → 12px (mobile)
- Card gap: 16px (desktop) → 8px (mobile)
- Section spacing: 32px (desktop) → 16px (mobile)

### Mobile-First CSS Pattern

```css
/* Mobile (320px+) - Base styles */
.score-card {
  width: 100%;
  margin-bottom: 12px;
  padding: 16px;
  font-size: 14px;
}

.score-number {
  font-size: 48px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .score-card {
    width: auto;
    margin-bottom: 16px;
    padding: 20px;
    font-size: 16px;
  }
  
  .score-number {
    font-size: 60px;
  }
}

/* Desktop (1200px+) */
@media (min-width: 1200px) {
  .score-card {
    padding: 24px;
    font-size: 16px;
  }
  
  .score-number {
    font-size: 72px;
  }
}
```

### Touch-Friendly Design (Mobile)

- Minimum tap target: 44x44px (all buttons/interactive elements)
- Default: 48x48px for better accuracy on phones
- Spacing between targets: 8px minimum
- Scrollable component cards (horizontal scroll on mobile if needed)
- Bottom sheet modals for secondary content (filters, details)

---

## Color Palette & Typography

### Color System

**Primary Colors** (Bullish):
- Light Green: #90EE90 (40% opacity for backgrounds)
- Medium Green: #32CD32 (60% opacity)
- Standard Green: #228B22 (80% opacity, default)
- Dark Green: #0B8C0B (100% opacity, emphasis)

**Secondary Colors** (Bearish):
- Light Red: #FFB6C6 (40% opacity for backgrounds)
- Medium Red: #FF6B6B (60% opacity)
- Standard Red: #DC143C (80% opacity, default)
- Dark Red: #8B0000 (100% opacity, emphasis)

**Neutral Colors**:
- Gray 100: #F8F9FA (backgrounds)
- Gray 500: #6C757D (secondary text)
- Gray 700: #495057 (primary text)
- Gray 900: #212529 (headings)

**Semantic Colors**:
- Success (Good): #28A745
- Warning (Caution): #FFC107
- Danger (Poor): #DC3545
- Info (Neutral): #17A2B8

**Dark Mode Palette**:
- Background: #1A1A1A
- Surface: #2D2D2D
- Text: #E5E5E5
- Borders: #404040
- Adjust colors above with 30% desaturation in dark mode

### Typography Scale

**Font Family**: "Inter" or "SF Pro Display" (system font fallback)
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 
             'Helvetica Neue', sans-serif;
```

**Heading Hierarchy**:

| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| h1 | 32px | 700 (bold) | 1.2 | -0.5px |
| h2 | 24px | 700 | 1.3 | 0 |
| h3 | 18px | 600 (semibold) | 1.4 | 0 |
| h4 | 16px | 600 | 1.5 | 0 |
| Body | 16px | 400 | 1.6 | 0 |
| Small | 12px | 400 | 1.5 | 0.2px |
| Score Number | 72px | 700 | 1.0 | -1px |

**Mobile Scaling**:
- Reduce all sizes by 10-15%
- Increase line-height by 0.1-0.2 for readability
- Increase letter-spacing by 0.1px for small text

---

## Real-Time Data Integration

### Supabase Subscription Architecture

**Real-Time Score Updates**:
```typescript
// Subscribe to score_history table for new calculations
const subscription = supabase
  .channel('score_updates')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'score_history',
      filter: `instrument=eq.${selectedInstrument}`
    },
    (payload) => {
      // Update component state with new scores
      setCurrentScore(payload.new);
      // Trigger visual feedback animation
      triggerScoreUpdateAnimation();
    }
  )
  .subscribe();
```

**Market Data Real-Time Feed**:
```typescript
// Subscribe to OHLC updates for price ticker
const priceSubscription = supabase
  .channel('price_feed')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'ohlc_data',
      filter: `instrument=eq.${selectedInstrument}`
    },
    (payload) => {
      // Update current price display
      setCurrentPrice(payload.new.close);
      // Update reference level calculations
      updateReferenceLevels(payload.new);
    }
  )
  .subscribe();
```

**Initial Data Load**:
```typescript
useEffect(() => {
  const loadLatestScore = async () => {
    const { data } = await supabase
      .from('score_history')
      .select('*')
      .eq('instrument', selectedInstrument)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single();
    
    setCurrentScore(data);
    setNextRefreshTime(calculateNextRefreshTime());
  };
  
  loadLatestScore();
}, [selectedInstrument]);
```

**Connection Status Indicator**:
```typescript
// Show connection status badge (top-right corner)
<div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
  {isConnected ? '🟢 Live' : '🔴 Offline'}
</div>
```

---

## Interactive Elements & Filtering

### Instrument Selector

**Location**: Header, left-aligned dropdown
**Options**: NQ=F, ES=F, GC, CL, FTSE100 (user-configurable)
**Behavior**:
- Changes subscribe filter for all real-time updates
- Reloads all displayed data
- Persists selection in localStorage

```html
<select id="instrumentSelector" class="form-select form-select-sm">
  <option value="NQ=F">NQ=F (NASDAQ-100 Futures)</option>
  <option value="ES=F">ES=F (S&P 500 Futures)</option>
  <option value="GC=F">GC=F (Gold Futures)</option>
  <option value="CL=F">CL=F (Crude Oil Futures)</option>
  <option value="FTSE" selected>FTSE 100 Index</option>
</select>
```

### Historical Data Filter

**Location**: Below dual score display (collapsible section)
**Filters**:
1. **Date Range Picker**:
   - Preset buttons: "Last 24h" | "Last 7d" | "Last 30d" | "Custom"
   - Custom date range: From/To date inputs
   - Visual calendar picker

2. **Score Range Filter**:
   - Slider: 0-100 (filter scores within range)
   - Quick tags: "ELITE (85+)" | "HIGH (70-84)" | "ACCEPTABLE (55-69)" | "MARGINAL (40-54)" | "POOR (<40)"

3. **Component Filter**:
   - Multi-select checkboxes for each component
   - Show only scores where specific component is strong

4. **Reset Button**:
   - Clear all filters instantly
   - Return to default view

**Mobile Behavior**: Collapsible/expandable section, bottom sheet modal for custom date picker

### Dark Mode Toggle

**Location**: Settings button (top-right)
**Options**:
- System preference (auto-detect)
- Light mode (force light)
- Dark mode (force dark)

**Implementation**:
```typescript
const [darkMode, setDarkMode] = useState(() => {
  const saved = localStorage.getItem('darkMode');
  if (saved) return saved === 'true';
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
});

useEffect(() => {
  document.body.classList.toggle('dark-mode', darkMode);
  localStorage.setItem('darkMode', darkMode);
}, [darkMode]);
```

---

## Chart.js Implementation

### Price Chart (1H, 4H, Daily Timeframe Options)

**Location**: Right sidebar (desktop), collapsible section (mobile)
**Chart Type**: Line chart with candlestick overlay option
**Data Source**: Supabase OHLC data

```typescript
const priceChartConfig = {
  type: 'line',
  data: {
    labels: priceData.map(d => formatTime(d.timestamp)), // 09:00, 09:01, ...
    datasets: [
      {
        label: 'Close Price',
        data: priceData.map(d => d.close),
        borderColor: '#228B22', // Green
        backgroundColor: 'rgba(34, 139, 34, 0.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 6,
        borderWidth: 2
      },
      {
        label: 'Reference Level (Daily Open)',
        data: priceData.map(() => dailyOpen), // Horizontal line
        borderColor: '#6C757D',
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        borderWidth: 1.5
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 3,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: { boxWidth: 15, padding: 15 }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#FFF',
        bodyColor: '#FFF',
        padding: 10,
        displayColors: false,
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => value.toFixed(0)
        }
      },
      x: {
        display: true,
        max: priceData.length - 1
      }
    }
  }
};

const chart = new Chart(ctx, priceChartConfig);
```

### Component Score Gauge Charts (Optional)

**Purpose**: Visual representation of each component's score as gauge/doughnut
**Location**: Component card hover state

```typescript
const componentGaugeConfig = {
  type: 'doughnut',
  data: {
    labels: ['Score', 'Remaining'],
    datasets: [{
      data: [componentScore, 100 - componentScore],
      backgroundColor: ['#228B22', '#E5E5E5'],
      borderColor: ['#FFF', '#FFF'],
      borderWidth: 2
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { display: false }
    }
  }
};
```

### Historical Score Trend Chart

**Location**: "View History" modal
**Chart Type**: Line chart tracking score changes over time

```typescript
const historyChartConfig = {
  type: 'line',
  data: {
    labels: historyData.map(d => formatDateTime(d.timestamp)),
    datasets: [
      {
        label: 'Bullish Score',
        data: historyData.map(d => d.bullish_total),
        borderColor: '#228B22',
        backgroundColor: 'rgba(34, 139, 34, 0.1)',
        fill: true,
        tension: 0.3
      },
      {
        label: 'Bearish Score',
        data: historyData.map(d => d.bearish_total),
        borderColor: '#8B0000',
        backgroundColor: 'rgba(139, 0, 0, 0.1)',
        fill: true,
        tension: 0.3
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true, position: 'top' },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        callbacks: {
          title: (context) => `${context[0].label}`,
          label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(0)}/100`
        }
      }
    },
    scales: {
      y: { min: 0, max: 100, ticks: { callback: (v) => `${v}` } }
    }
  }
};
```

---

## Auto-Refresh & Timer Mechanism

### Timer Implementation

**Frontend Timer Logic**:
```typescript
const [timeUntilRefresh, setTimeUntilRefresh] = useState(180); // 3 minutes in seconds
const [isAutoRefreshing, setIsAutoRefreshing] = useState(false);

useEffect(() => {
  const interval = setInterval(() => {
    setTimeUntilRefresh(prev => {
      if (prev <= 1) {
        // Trigger refresh
        triggerAutoRefresh();
        return 180; // Reset to 3 minutes
      }
      return prev - 1;
    });
  }, 1000);

  return () => clearInterval(interval);
}, []);

const triggerAutoRefresh = async () => {
  setIsAutoRefreshing(true);
  try {
    // Call backend Agent 2 via API endpoint
    const response = await fetch('/api/calculate-scores', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instrument: selectedInstrument })
    });
    
    if (response.ok) {
      // Score updated (real-time subscription will update UI)
      console.log('Score refresh triggered successfully');
    }
  } catch (error) {
    console.error('Auto-refresh failed:', error);
    // Show error notification
    showNotification('Error refreshing score. Retrying...', 'error');
  } finally {
    setIsAutoRefreshing(false);
  }
};

// Format display: "2:45" or "2 minutes 45 seconds"
const formatTimeRemaining = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};
```

**UI Display**:
```jsx
<div className="timer-display">
  <span className="timer-icon">⏱️</span>
  <span className={`timer-text ${timeUntilRefresh <= 10 ? 'urgent' : ''}`}>
    Auto-refresh in {formatTimeRemaining(timeUntilRefresh)}
  </span>
  <span className="last-update">Last update: {formatTimeAgo(lastUpdateTime)}</span>
</div>
```

**CSS for Timer Animation**:
```css
.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #F8F9FA;
  border-radius: 8px;
  border-left: 4px solid #228B22;
}

.timer-text {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  transition: color 0.3s ease;
}

.timer-text.urgent {
  color: #DC3545;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

---

## State Management & React Architecture

### Component Tree Structure

```
App (root)
├── Header
│   ├── InstrumentSelector
│   ├── ConnectionStatus
│   └── SettingsModal
├── MainLayout
│   ├── LeftPanel (desktop-only)
│   │   ├── CurrentPriceCard
│   │   ├── SessionIndicator
│   │   ├── ReferenceLevelsPanel
│   │   └── FibonacciPivotsPanel
│   ├── CenterContent
│   │   ├── DualScoreDisplay
│   │   │   ├── BullishScoreCard
│   │   │   └── BearishScoreCard
│   │   ├── DirectionalBiasBadge
│   │   ├── ComponentBreakdownGrid
│   │   │   ├── ComponentCard[] (bullish)
│   │   │   └── ComponentCard[] (bearish)
│   │   ├── ActionButtons
│   │   │   ├── GenerateScoreButton
│   │   │   └── ViewHistoryButton
│   │   └── AutoRefreshTimer
│   └── RightPanel (desktop-only)
│       ├── PriceChart
│       └── LiquidityEventsPanel
├── HistoryModal
│   ├── FilterControls
│   └── HistoryTable/Chart
└── Footer
```

### Context API for State Management

```typescript
// ScoreContext.ts
type ScoreContextType = {
  currentScore: ScoreData | null;
  loading: boolean;
  error: string | null;
  isConnected: boolean;
  selectedInstrument: string;
  timeUntilRefresh: number;
  
  setSelectedInstrument: (instrument: string) => void;
  manualRefresh: () => Promise<void>;
  dismissError: () => void;
};

export const ScoreContext = createContext<ScoreContextType>(null);

export const useScore = () => {
  const context = useContext(ScoreContext);
  if (!context) {
    throw new Error('useScore must be used within ScoreProvider');
  }
  return context;
};

// Provider component
export const ScoreProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentScore, setCurrentScore] = useState<ScoreData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(true);
  const [selectedInstrument, setSelectedInstrument] = useState('NQ=F');
  const [timeUntilRefresh, setTimeUntilRefresh] = useState(180);

  // Real-time subscription setup
  useEffect(() => {
    const subscription = supabase
      .channel(`score:${selectedInstrument}`)
      .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'score_history' },
        (payload) => setCurrentScore(payload.new as ScoreData)
      )
      .subscribe(status => setIsConnected(status === 'SUBSCRIBED'));

    return () => subscription.unsubscribe();
  }, [selectedInstrument]);

  // Timer countdown
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeUntilRefresh(prev => prev <= 1 ? 180 : prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const manualRefresh = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/calculate-scores', {
        method: 'POST',
        body: JSON.stringify({ instrument: selectedInstrument })
      });
      if (!response.ok) throw new Error('Refresh failed');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScoreContext.Provider value={{
      currentScore, loading, error, isConnected, selectedInstrument,
      timeUntilRefresh, setSelectedInstrument, manualRefresh, dismissError: () => setError(null)
    }}>
      {children}
    </ScoreContext.Provider>
  );
};
```

### Hooks for Data Fetching

```typescript
// useHistoricalScores.ts
export const useHistoricalScores = (instrument: string, filters?: FilterOptions) => {
  const [data, setData] = useState<ScoreData[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    let query = supabase
      .from('score_history')
      .select('*')
      .eq('instrument', instrument)
      .order('timestamp', { ascending: false });

    if (filters?.dateRange) {
      query = query.gte('timestamp', filters.dateRange.from);
      query = query.lte('timestamp', filters.dateRange.to);
    }

    query.limit(100).then(({ data }) => {
      setData(data || []);
      setLoading(false);
    });
  }, [instrument, filters]);

  return { data, loading };
};
```

---

## Loading States & Error Handling

### Loading Skeleton States

**Skeleton for Score Cards**:
```jsx
<div className="skeleton-score-card">
  <div className="skeleton-text skeleton-title"></div>
  <div className="skeleton-number"></div>
  <div className="skeleton-text skeleton-small"></div>
  <div className="skeleton-bar"></div>
</div>
```

**Skeleton CSS**:
```css
.skeleton-text {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-title { height: 16px; width: 100%; margin-bottom: 8px; }
.skeleton-number { height: 48px; width: 100%; margin-bottom: 8px; }
.skeleton-small { height: 12px; width: 80%; margin-bottom: 8px; }
.skeleton-bar { height: 6px; width: 100%; border-radius: 3px; }
```

### Error States

**Error Notification Component**:
```jsx
<div className={`alert alert-${error.severity}`} role="alert">
  <strong>{error.title}</strong>
  <p>{error.message}</p>
  {error.action && (
    <button className="btn btn-sm" onClick={error.onRetry}>
      {error.action}
    </button>
  )}
  <button className="btn-close" onClick={dismissError}></button>
</div>
```

**Error Scenarios**:
1. **Data Fetch Failed**: "Unable to load scores. Showing last known data."
2. **Connection Lost**: "Real-time connection lost. Using polling mode." (with red indicator)
3. **Agent 2 Error**: "Score calculation failed. Please try again." (with retry button)
4. **Invalid Instrument**: "Invalid instrument selected. Defaulting to NQ=F."

---

## Accessibility Checklist

### WCAG 2.1 AA Compliance

- [ ] All interactive elements are keyboard accessible (Tab, Enter, Space, Arrow keys)
- [ ] Focus indicators visible (outline/highlight on all focusable elements)
- [ ] Color not sole indicator (icons + text labels used with color)
- [ ] Contrast ratio >= 4.5:1 for text (normal), >= 3:1 for large text
- [ ] Contrast ratio >= 3:1 for UI components and graphics
- [ ] Images have alt text or aria-label
- [ ] Forms have associated labels (<label> tags)
- [ ] Error messages linked to form fields (aria-describedby)
- [ ] Live regions marked with aria-live="polite" (score updates, timer)
- [ ] Modal dialogs have focus trap and ARIA dialog role
- [ ] Buttons have clear, descriptive labels (avoid "Click here")
- [ ] Tooltips accessible via keyboard (tooltip on focus, not just hover)
- [ ] Page structure uses semantic HTML (h1-h6 hierarchy)
- [ ] No content only accessible via hover (mobile users)
- [ ] Touch targets >= 44x44px minimum
- [ ] Zoom/magnification tested at 200%
- [ ] Screen reader tested (VoiceOver, NVDA, JAWS)

### Semantic HTML Examples

```html
<!-- Score card with semantic structure -->
<article class="score-card" aria-label="Bullish setup score">
  <header>
    <h3>Bullish Score</h3>
  </header>
  <div class="score-value" aria-label="45 out of 100 points">
    <strong>45</strong>
    <span>/100</span>
  </div>
  <div class="stars" aria-label="2 out of 5 stars">
    <span aria-label="Rated 2 stars: Marginal">⭐⭐</span>
  </div>
</article>

<!-- Component with tooltip -->
<div class="component-card">
  <button 
    class="info-button"
    aria-label="What is HTF Bias?"
    aria-describedby="htf-tooltip"
  >
    ⓘ
  </button>
  <div id="htf-tooltip" role="tooltip" class="tooltip">
    HTF Bias aligns your trade direction with higher timeframe institutional flow.
    Higher weight for weekly/daily opens.
  </div>
</div>

<!-- Live region for score updates -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  Score updated: Bullish 45/100, Bearish 92/100. Directional bias: Bearish.
</div>

<!-- Form with error handling -->
<form>
  <label for="instrument">Instrument</label>
  <select id="instrument" aria-describedby="instrument-error">
    <option>NQ=F</option>
  </select>
  <span id="instrument-error" role="alert" class="error-message"></span>
</form>
```

### Screen Reader Announcements

```typescript
// Announce score updates to screen readers
const announceScoreUpdate = (bullish: number, bearish: number, bias: string) => {
  const announcement = `Setup score updated. Bullish score ${bullish} out of 100, 
    Bearish score ${bearish} out of 100. Directional bias ${bias}.`;
  
  const liveRegion = document.querySelector('[aria-live="polite"]');
  liveRegion.textContent = announcement;
  
  // Clear after 5 seconds
  setTimeout(() => {
    liveRegion.textContent = '';
  }, 5000);
};
```

---

## Performance Optimization

### Component Memoization

```typescript
// Memoize expensive components
export const ScoreCard = React.memo(({ score, direction }) => {
  return <div>{/* Component JSX */}</div>;
}, (prev, next) => {
  // Custom comparison: only re-render if score or direction changes
  return prev.score === next.score && prev.direction === next.direction;
});

// Use useMemo for computed values
const biasStrengthPercentage = useMemo(() => {
  return ((Math.abs(bullish - bearish) / 100) * 100).toFixed(0);
}, [bullish, bearish]);

// Use useCallback to prevent unnecessary re-renders of child components
const handleManualRefresh = useCallback(async () => {
  await manualRefresh();
}, [manualRefresh]);
```

### Lazy Loading

```typescript
// Lazy load heavy components (charts, history modal)
const PriceChart = lazy(() => import('./charts/PriceChart'));
const HistoryModal = lazy(() => import('./modals/HistoryModal'));

// Suspense boundary with fallback
<Suspense fallback={<LoadingSpinner />}>
  <PriceChart />
</Suspense>
```

### Subscription Optimization

```typescript
// Unsubscribe when component unmounts to prevent memory leaks
useEffect(() => {
  const subscription = supabase.channel('...').subscribe();
  
  return () => {
    subscription.unsubscribe();
  };
}, []);

// Debounce rapid updates
import { debounce } from 'lodash';

const debouncedScoreUpdate = debounce((newScore) => {
  setCurrentScore(newScore);
}, 300);
```

### Image/Asset Optimization

- Use SVG for icons (scalable, lightweight)
- Optimize PNGs with TinyPNG or similar
- Lazy load non-critical images
- Use WebP with PNG fallback for photography

### Bundle Size

- Tree-shake unused Chart.js modules
- Code split modals/tabs to load on demand
- Use production build for deployment
- Monitor with webpack-bundle-analyzer

---

## Implementation Code Snippets

### 1. Main Dashboard Component

```typescript
// Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { useScore } from '../context/ScoreContext';
import DualScoreDisplay from './DualScoreDisplay';
import ComponentBreakdown from './ComponentBreakdown';
import DirectionalBias from './DirectionalBias';
import AutoRefreshTimer from './AutoRefreshTimer';
import LeftPanel from './panels/LeftPanel';
import RightPanel from './panels/RightPanel';

const Dashboard: React.FC = () => {
  const { currentScore, loading, error, isConnected } = useScore();
  const [showHistory, setShowHistory] = useState(false);

  return (
    <div className="dashboard-container">
      {/* Connection indicator */}
      <div className={`connection-badge ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? '🟢 Live' : '🔴 Offline'}
      </div>

      {/* Error notification */}
      {error && (
        <div className="alert alert-danger alert-dismissible" role="alert">
          {error}
          <button type="button" className="btn-close" onClick={() => dismissError()}></button>
        </div>
      )}

      <div className="row g-3 h-100">
        {/* Left Panel - Desktop Only */}
        <aside className="col-lg-2 d-none d-lg-block">
          {loading ? <LoadingSkeleton /> : <LeftPanel />}
        </aside>

        {/* Center Content */}
        <main className="col-12 col-lg-7">
          {loading ? (
            <LoadingSkeleton type="scores" />
          ) : (
            <>
              {/* Dual Score Cards */}
              <DualScoreDisplay scores={currentScore} />

              {/* Directional Bias */}
              <DirectionalBias 
                bullishScore={currentScore?.bullish_total} 
                bearishScore={currentScore?.bearish_total}
                bias={currentScore?.directional_bias}
              />

              {/* Component Breakdown */}
              <ComponentBreakdown scores={currentScore} />

              {/* Action Buttons */}
              <div className="row g-2 mt-3">
                <div className="col-12 col-sm-6">
                  <button 
                    className="btn btn-primary w-100" 
                    onClick={manualRefresh}
                  >
                    🔄 Generate New Score
                  </button>
                </div>
                <div className="col-12 col-sm-6">
                  <button 
                    className="btn btn-secondary w-100"
                    onClick={() => setShowHistory(true)}
                  >
                    📊 View History
                  </button>
                </div>
              </div>

              {/* Auto-refresh timer */}
              <AutoRefreshTimer />
            </>
          )}
        </main>

        {/* Right Panel - Desktop Only */}
        <aside className="col-lg-3 d-none d-lg-block">
          {loading ? <LoadingSkeleton /> : <RightPanel currentPrice={currentScore?.current_price} />}
        </aside>
      </div>

      {/* History Modal */}
      {showHistory && (
        <HistoryModal 
          isOpen={showHistory}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
```

### 2. DualScoreDisplay Component

```typescript
// DualScoreDisplay.tsx
interface DualScoreDisplayProps {
  scores: ScoreData;
}

const DualScoreDisplay: React.FC<DualScoreDisplayProps> = ({ scores }) => {
  const getColorClass = (direction: 'bullish' | 'bearish') => {
    const score = direction === 'bullish' ? scores.bullish_total : scores.bearish_total;
    if (score >= 85) return 'elite';
    if (score >= 70) return 'high';
    if (score >= 55) return 'acceptable';
    if (score >= 40) return 'marginal';
    return 'poor';
  };

  const renderStars = (score: number) => {
    const stars = Math.round((score / 20)); // 5 stars max
    return '⭐'.repeat(stars) + '☆'.repeat(5 - stars);
  };

  return (
    <div className="row g-3 mb-4">
      {/* Bullish Score Card */}
      <div className="col-12 col-md-6 col-lg-auto">
        <div className={`score-card score-${getColorClass('bullish')}`}>
          <div className="score-header">
            <span className="direction-icon">🟢</span>
            <h3 className="score-direction">Bullish</h3>
          </div>
          <div className="score-value">
            <span className="score-number">{scores.bullish_total.toFixed(0)}</span>
            <span className="score-max">/100</span>
          </div>
          <div className="score-stars">
            {renderStars(scores.bullish_total)}
          </div>
          <div className="score-rating">
            {getScoreRating(scores.bullish_total)}
          </div>
          <div className="score-bar">
            <div 
              className="score-bar-fill" 
              style={{ width: `${scores.bullish_total}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Bearish Score Card */}
      <div className="col-12 col-md-6 col-lg-auto">
        <div className={`score-card score-${getColorClass('bearish')}`}>
          <div className="score-header">
            <span className="direction-icon">🔴</span>
            <h3 className="score-direction">Bearish</h3>
          </div>
          <div className="score-value">
            <span className="score-number">{scores.bearish_total.toFixed(0)}</span>
            <span className="score-max">/100</span>
          </div>
          <div className="score-stars">
            {renderStars(scores.bearish_total)}
          </div>
          <div className="score-rating">
            {getScoreRating(scores.bearish_total)}
          </div>
          <div className="score-bar">
            <div 
              className="score-bar-fill" 
              style={{ width: `${scores.bearish_total}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const getScoreRating = (score: number): string => {
  if (score >= 85) return 'Elite';
  if (score >= 70) return 'High';
  if (score >= 55) return 'Acceptable';
  if (score >= 40) return 'Marginal';
  return 'Poor';
};

export default React.memo(DualScoreDisplay);
```

### 3. ComponentBreakdown Component

```typescript
// ComponentBreakdown.tsx
interface ComponentBreakdownProps {
  scores: ScoreData;
}

const components = [
  { key: 'htf_bias', label: 'HTF Bias', max: 30 },
  { key: 'kill_zone', label: 'Kill Zone', max: 20 },
  { key: 'pd_array', label: 'PD Array', max: 25 },
  { key: 'liquidity', label: 'Liquidity', max: 15 },
  { key: 'structure', label: 'Structure', max: 10 },
  { key: 'equilibrium', label: 'Equilibrium', max: 5 }
];

const ComponentBreakdown: React.FC<ComponentBreakdownProps> = ({ scores }) => {
  const [expandedComponent, setExpandedComponent] = useState<string | null>(null);

  const renderComponentCards = (direction: 'bullish' | 'bearish') => {
    const directionData = direction === 'bullish' ? 'bullish' : 'bearish';
    
    return components.map(comp => {
      const score = scores[`${directionData}_${comp.key}`] || 0;
      const percentage = (score / comp.max) * 100;
      const status = percentage >= 70 ? '✓' : percentage >= 40 ? '⚠️' : '✗';

      return (
        <div key={comp.key} className="col-12 col-sm-6 col-md-4 col-lg-auto">
          <button
            className="component-card btn"
            onClick={() => setExpandedComponent(expandedComponent === comp.key ? null : comp.key)}
            aria-expanded={expandedComponent === comp.key}
          >
            <div className="component-header">
              <span className="component-label">{comp.label}</span>
              <span className={`component-status status-${status.replace('⚠️', 'warning')}`}>
                {status}
              </span>
            </div>
            <div className="component-score">
              <strong>{score.toFixed(1)}</strong>
              <span>/{comp.max}</span>
            </div>
            <div className="component-bar">
              <div 
                className={`component-bar-fill bar-${direction}`}
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
          </button>

          {/* Tooltip/Detail View */}
          {expandedComponent === comp.key && (
            <div className="component-tooltip">
              <p>{getComponentExplanation(comp.key, direction)}</p>
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="component-breakdown-section">
      <h4 className="mb-3">Component Breakdown</h4>
      
      {/* Bullish Components */}
      <div className="mb-4">
        <h5 className="text-success mb-2">Bullish Components</h5>
        <div className="row g-2">
          {renderComponentCards('bullish')}
        </div>
      </div>

      {/* Bearish Components */}
      <div>
        <h5 className="text-danger mb-2">Bearish Components</h5>
        <div className="row g-2">
          {renderComponentCards('bearish')}
        </div>
      </div>
    </div>
  );
};

const getComponentExplanation = (component: string, direction: string): string => {
  const explanations: Record<string, Record<string, string>> = {
    htf_bias: {
      bullish: 'Measures alignment with higher timeframe trend. Price above key opens (weekly, daily) scores higher.',
      bearish: 'Measures alignment with bearish bias. Price below key opens (weekly, daily) scores higher.'
    },
    kill_zone: {
      bullish: 'Scores based on trading during high-probability sessions (London, NY AM/PM) with time decay.',
      bearish: 'Scores based on trading during high-probability sessions with better odds during London/NY windows.'
    },
    // ... more explanations
  };
  
  return explanations[component]?.[direction] || '';
};

export default React.memo(ComponentBreakdown);
```

### 4. Auto-Refresh Timer Component

```typescript
// AutoRefreshTimer.tsx
const AutoRefreshTimer: React.FC = () => {
  const { timeUntilRefresh, manualRefresh } = useScore();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());

  useEffect(() => {
    setLastUpdateTime(new Date());
  }, [timeUntilRefresh === 180]); // Reset when timer resets

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await manualRefresh();
    setIsRefreshing(false);
  };

  const urgency = timeUntilRefresh <= 10;

  return (
    <div className="timer-widget mt-4">
      <div className={`timer-display ${urgency ? 'urgent' : ''}`}>
        <span className="timer-icon">⏱️</span>
        <div className="timer-info">
          <span className="timer-text">
            Auto-refresh in <strong>{formatTime(timeUntilRefresh)}</strong>
          </span>
          <span className="timer-secondary">
            Last update: {formatTimeAgo(lastUpdateTime)}
          </span>
        </div>
      </div>
      
      <button 
        className="btn btn-sm btn-outline-primary mt-2"
        onClick={handleManualRefresh}
        disabled={isRefreshing}
      >
        {isRefreshing ? '⏳ Refreshing...' : '🔄 Refresh Now'}
      </button>
    </div>
  );
};

export default React.memo(AutoRefreshTimer);
```

### 5. Styling Examples (SCSS/CSS)

```scss
// _dashboard.scss

// Color utility functions
@function get-bullish-color($opacity: 1) {
  @return rgba(34, 139, 34, $opacity);
}

@function get-bearish-color($opacity: 1) {
  @return rgba(139, 0, 0, $opacity);
}

// Score Card Styles
.score-card {
  position: relative;
  padding: 24px 20px;
  border-radius: 12px;
  border: 1px solid #E5E5E5;
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }

  &.score-elite {
    border-left: 5px solid get-bullish-color();
    background: linear-gradient(135deg, rgba(34, 139, 34, 0.05) 0%, transparent 100%);
  }

  &.score-high {
    border-left: 5px solid get-bullish-color(0.7);
  }

  &.score-acceptable {
    border-left: 5px solid #FFC107;
  }

  &.score-marginal {
    border-left: 5px solid #FFA500;
  }

  &.score-poor {
    border-left: 5px solid get-bearish-color();
  }
}

// Score Number Styling
.score-number {
  font-size: 72px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -1px;
  color: #212529;
  margin-bottom: 4px;

  @media (max-width: 768px) {
    font-size: 48px;
  }
}

// Component Card Grid
.component-card {
  position: relative;
  width: 100%;
  padding: 16px;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  background: #FFFFFF;
  text-align: left;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: #228B22;
    box-shadow: 0 2px 8px rgba(34, 139, 34, 0.1);
  }

  &:focus {
    outline: 2px solid #228B22;
    outline-offset: 2px;
  }

  .component-bar-fill {
    background: linear-gradient(90deg, get-bullish-color(), #90EE90);
    height: 4px;
    border-radius: 2px;
    transition: width 0.6s ease;

    &.bar-bearish {
      background: linear-gradient(90deg, get-bearish-color(), #FFB6C6);
    }
  }
}

// Timer Widget
.timer-widget {
  padding: 16px;
  background: #F8F9FA;
  border-radius: 8px;
  border-left: 4px solid get-bullish-color();

  .timer-display {
    display: flex;
    align-items: center;
    gap: 12px;

    &.urgent {
      animation: pulse 1s infinite;

      .timer-text {
        color: get-bearish-color();
        font-weight: 600;
      }
    }
  }

  .timer-icon {
    font-size: 20px;
  }

  .timer-text {
    font-size: 14px;
    font-weight: 500;
    color: #495057;
    transition: color 0.3s ease;
  }

  .timer-secondary {
    display: block;
    font-size: 12px;
    color: #6C757D;
    margin-top: 4px;
  }
}

// Responsive Grid
.dashboard-container {
  @media (max-width: 575px) {
    // Single column, stacked
    .score-card {
      margin-bottom: 16px;
      
      .score-number {
        font-size: 48px;
      }
    }
  }

  @media (min-width: 1200px) {
    // 3-column layout
    display: grid;
    grid-template-columns: 200px 1fr 250px;
    gap: 24px;
  }
}

// Dark mode support
@media (prefers-color-scheme: dark) {
  .score-card,
  .component-card {
    background: #2D2D2D;
    border-color: #404040;
    color: #E5E5E5;

    .score-number {
      color: #E5E5E5;
    }
  }

  .timer-widget {
    background: #1A1A1A;
    border-color: get-bullish-color(0.5);

    .timer-text {
      color: #B0B0B0;
    }
  }
}

// Loading animation
@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

// Focus states for accessibility
:focus-visible {
  outline: 2px solid #228B22;
  outline-offset: 2px;
}
```

---

## Summary & Next Steps

This comprehensive dashboard design document provides:

1. **Visual Architecture**: Responsive layouts for mobile, tablet, and desktop with clear hierarchy
2. **Component Specifications**: Detailed designs for scores, components, reference levels, and controls
3. **Real-Time Integration**: Supabase subscription patterns and WebSocket-ready architecture
4. **Interactive Features**: Filtering, instrument selection, auto-refresh mechanisms
5. **Accessibility**: WCAG 2.1 AA compliance with semantic HTML and ARIA support
6. **Performance**: Memoization, lazy loading, subscription optimization strategies
7. **Implementation Code**: React/TypeScript patterns and working component examples

### Implementation Priority

**Phase 1 (MVP - Week 1-2)**:
- Header with instrument selector
- Dual score display cards
- Directional bias badge
- Component breakdown grid
- Action buttons (generate, history)
- Auto-refresh timer
- Basic Bootstrap responsive layout
- Supabase subscriptions for real-time updates

**Phase 2 (Enhancement - Week 3)**:
- Left/right panels with reference levels and liquidity events
- Price chart with Chart.js
- Historical data modal with filtering
- Dark mode support
- Mobile touch optimizations
- Loading states and error handling

**Phase 3 (Polish - Week 4+)**:
- Component tooltips with ICT explanations
- Accessibility audit and fixes
- Performance optimization
- Advanced filtering (date range, score range, component filters)
- Export/share functionality
- User preferences/settings modal

---

**Document prepared for**: ICT Quantitative Prediction Model Dashboard
**Status**: Ready for React/Next.js implementation
**Last Updated**: November 16, 2025

