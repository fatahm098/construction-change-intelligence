---
name: Margin Guardian
colors:
  surface: '#131316'
  surface-dim: '#131316'
  surface-bright: '#39393c'
  surface-container-lowest: '#0e0e11'
  surface-container-low: '#1b1b1e'
  surface-container: '#1f1f22'
  surface-container-high: '#2a2a2d'
  surface-container-highest: '#353438'
  on-surface: '#e4e1e6'
  on-surface-variant: '#d8c3ad'
  inverse-surface: '#e4e1e6'
  inverse-on-surface: '#303033'
  outline: '#a08e7a'
  outline-variant: '#534434'
  surface-tint: '#ffb95f'
  primary: '#ffc174'
  on-primary: '#472a00'
  primary-container: '#f59e0b'
  on-primary-container: '#613b00'
  inverse-primary: '#855300'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffbcb7'
  on-tertiary: '#68000a'
  tertiary-container: '#ff938c'
  on-tertiary-container: '#8d0012'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffddb8'
  primary-fixed-dim: '#ffb95f'
  on-primary-fixed: '#2a1700'
  on-primary-fixed-variant: '#653e00'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#131316'
  on-background: '#e4e1e6'
  surface-variant: '#353438'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 2rem
    fontWeight: '600'
    lineHeight: 2.5rem
    letterSpacing: -0.025em
  display-lg-mobile:
    fontFamily: Geist
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.015em
  title-sm:
    fontFamily: Geist
    fontSize: 0.9375rem
    fontWeight: '500'
    lineHeight: 1.375rem
    letterSpacing: -0.01em
  body-default:
    fontFamily: Geist
    fontSize: 0.8125rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: -0.005em
  body-compact:
    fontFamily: Geist
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.125rem
    letterSpacing: '0'
  data-tabular-lg:
    fontFamily: JetBrains Mono
    fontSize: 1.125rem
    fontWeight: '500'
    lineHeight: 1.5rem
    letterSpacing: -0.02em
  data-tabular-md:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.25rem
    letterSpacing: -0.01em
  data-tabular-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '400'
    lineHeight: 1rem
    letterSpacing: '0'
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 0.625rem
    fontWeight: '600'
    lineHeight: 0.875rem
    letterSpacing: 0.06em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.5rem
  gutter-desktop: 0.75rem
  margin: 0.75rem
  margin-desktop: 1rem
  space-xs: 0.125rem
  space-sm: 0.25rem
  space-md: 0.5rem
  space-lg: 0.75rem
  space-xl: 1rem
---

## Brand & Style

This design system is engineered for mission-critical construction change intelligence, structural variance audits, and quantitative risk management. It serves Senior Quantity Surveyors, Structural Engineers, and Commercial Project Managers who operate within complex financial and physical tolerances where single-millimeter or fractional-basis-point discrepancies carry substantial liability.

The aesthetic fuses the high-density keyboard-first efficiency of modern developer tooling with the technical rigor of precision CAD and blueprint analysis environments (AutoCAD, Bluebeam Revu). It avoids decorative fluff, consumer-grade whitespace, and soft blurred lighting in favor of mechanical precision, razor-sharp edge demarcations, high tabular legibility, and immediate visual hierarchy under extreme data density.

Key characteristics:
- **Utilitarian & Instrumental:** Interfaces function as physical-grade digital consoles with high information density, calibrated contrast, and visible structural dividers.
- **Parametric Status Signaling:** Color is restricted to functional indicators—amber for change-order liabilities, emerald for positive margin gains, and laser red for CAD delta and clash detections.
- **Mechanical Authority:** The workspace evokes precision instrumentation, blueprint overlays, and financial audit durability.

## Colors

The palette enforces a pure dark-mode architecture engineered to reduce optical fatigue during multi-hour blueprint reviews and tabular cost comparisons. The dark base relies on layered deep zinc tones:

- **Canvas & Base Tiers:**
  - Viewport & Canvas Background: `#09090b` (Deep Base Void)
  - Primary Structural Containers & Panels: `#121215` (Mid Console Tier)
  - Elevated Cards, Toolbars & Flyouts: `#18181b` (Surface High)
  - Active Row / Inspector Hover: `#222226`

- **Dividers & Structural Rules:**
  - Hairline Boundaries & Inactive Grids: `#27272a`
  - High-Emphasis Borders, Selected Tabs & Active Splitters: `#3f3f46`
  - Focus Rings & Measurement Crosshairs: `#71717a`

- **Functional Signaling:**
  - **Amber (`#f59e0b`):** Warning states, margin slippage, pending change-order validations, and unresolved engineering requests for information (RFIs).
  - **Emerald (`#10b981`):** Positive cost variance, structural load confirmations, signed approvals, and credit adjustments.
  - **Cadmium Red (`#ef4444`):** Geometric clashes, negative cost overruns, deleted CAD primitives, and hard structural violations.
  - **Cyan / Technical Accent (`#06b6d4`):** Vector overlay diffs, active snapping nodes, and AI-detected dimension strings.

- **Text & Foreground Hierarchy:**
  - Primary Readout: `#fafafa` (Pure High Contrast)
  - Secondary Metadata & Spec Labels: `#a1a1aa`
  - Disabled / Grid Index / Axis Legends: `#52525b`

## Typography

The typographic system is built on a dual-engine architecture:
1. **Structural Interface Core (Geist):** Handles UI chrome, viewport titles, metadata descriptions, hierarchical menus, and status annotations. It offers exceptional neutral rendering at 11px–13px sizes.
2. **Precision Engineering Monospace (JetBrains Mono):** Mandated for all CAD coordinate systems (X/Y/Z), Bill of Quantities (BoQ) financial figures, structural variance percentages, material counts, timestamps, and model hashes.

Rules:
- Monospace figures must always render with standard tabular figures and full zero disambiguation.
- Use `label-caps` for all CAD tool properties, layer categories, and financial column headers with uppercase transformation.
- Compact vertical metrics prioritize screen efficiency, allowing 24–32 rows of cost or clash data without scrolling on standard 1080p displays.

## Layout & Spacing

The workspace implements an adaptive multi-panel fixed-docking grid optimized for multi-monitor desktop engineering setups, scaling gracefully down to field tablets:

- **Desktop (>= 1280px):**
  - **Left Rail (Fixed 240px–320px):** Drawing sheet sets, model tree, BoQ trade hierarchy.
  - **Center Viewport (Fluid flex-grow):** CAD/BIM drawing space, vector delta diff engine, split-screen compare.
  - **Right Inspector (Fixed 340px–420px):** AI delta analysis, financial impact breakdown, RFI tracker.
  - **Bottom Tray (Collapsible 180px–280px):** Interactive tabular log, clash register, schedule timeline.
- **Tablet / Field Inspection (768px – 1279px):**
  - Left and Right panels convert to slide-over drawers with persistent 44px collapsed tool rails.
  - Viewport retains priority with gestures enabled for pan/zoom.
- **Mobile (< 768px):**
  - Read-only emergency change approval mode; stacked single-column layout prioritizing financial deltas and visual approval actions.

Rhythm:
- Component spacing follows a strict 4px sub-grid (`space-xs` = 2px, `space-sm` = 4px, `space-md` = 8px, `space-lg` = 12px, `space-xl` = 16px).
- Gutters and margins are kept deliberately dense (`0.5rem` to `1rem`) to maximize canvas visibility for 2D plans and 3D IFC/BIM models.

## Elevation & Depth

This design system avoids blurry drop shadows, colored ambient glows, and skeuomorphic bevels. Elevation is established exclusively through **tonal stratification, hairline border contrast, and z-index coordinate clipping**:

- **Tier 0 (Drawing Canvas & Viewport Base - `#09090b`):** The absolute bottom. Infinite blueprint grid, vector delta geometry, and model viewers sit here.
- **Tier 1 (Structural Toolbars & Docked Panels - `#121215`):** Separated from Tier 0 by a 1px solid border (`#27272a`). No shadow.
- **Tier 2 (Floating Precision Tool Palettes & Snapping Flyouts - `#18181b`):** Outlined with `#3f3f46`. Uses a hairline hard offset: `box-shadow: 0 4px 0 0 rgba(0, 0, 0, 0.4)`.
- **Tier 3 (Active Overlays, Modal Dialogs & Delta Diff Inspections - `#18181b`):** Bordered with `#3f3f46` or context colors (`#f59e0b` / `#ef4444`). Elevated with a crisp, low-diffusion ambient shadow: `box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.7), 0 0 0 1px #3f3f46`.

Panels never blur background CAD drawings. Background vectors remain visible through viewport masks, maintaining situational spatial awareness during inspection.

## Shapes

The design uses an ultra-tight border-radius token set (`roundedness: 1`), conveying technical instrument precision:

- Buttons, segmented toggles, inputs, and chips utilize `0.25rem` (4px).
- Internal tabular row selections and context flyout items utilize `0.125rem` (2px).
- Panels, docking windows, and overlay frames utilize `0.375rem` (6px) maximum.
- Floating command bars and status pills utilize micro-fillets, strictly avoiding 9999px pill rounding. Fully circular geometry is restricted to coordinate snap nodes, pinpoint crosshairs, and radial variance needles.

## Components

### Buttons & Action Controls
- **Primary Technical Action:** Background `#f59e0b`, text `#09090b`, font `Geist` weight 500, height 28px (compact) or 32px (standard), border-radius 4px. On hover: `#d97706`.
- **Secondary / Panel Action:** Background `#18181b`, border 1px solid `#3f3f46`, text `#fafafa`. On hover: border `#71717a`, background `#222226`.
- **Destructive Delta Action:** Background `#ef4444` with 15% opacity, border 1px solid `#ef4444`, text `#ef4444`. On hover: Background `#ef4444`, text `#fafafa`.
- **Icon Tool Button:** 28px × 28px square, background transparent, border 1px solid transparent, text `#a1a1aa`. When active/selected: background `#27272a`, border 1px solid `#71717a`, text `#fafafa`.

### Badges, Delta Indicators & Chips
- **Amber Change-Order Pill:** Background `#f59e0b` at 12% opacity, border 1px solid `#f59e0b`, text `#f59e0b`, font `JetBrains Mono` 11px uppercase, padding 2px 6px.
- **Emerald Margin Gain Badge:** Background `#10b981` at 12% opacity, border 1px solid `#10b981`, text `#10b981`, font `JetBrains Mono` 11px uppercase, prefixed with `+` sign.
- **Red CAD Delta Alert Badge:** Background `#ef4444` at 15% opacity, border 1px solid `#ef4444`, text `#ef4444`, font `JetBrains Mono` 11px.

### Data Tables & Bill of Quantities (BoQ) Grids
- **Header:** Height 28px, background `#121215`, border-bottom 1px solid `#3f3f46`, typography `label-caps` in `#a1a1aa`.
- **Row:** Height 26px (ultra-dense) or 32px (default), alternating border-bottom 1px solid `#27272a`. Hover state `#1c1c20`.
- **Numeric Cells:** Monospace font (`JetBrains Mono`), right-aligned, zero-padded when necessary. Color denotes status: emerald (`#10b981`) for savings, red (`#ef4444`) for budget overrun.

### Input Fields & Parameter Steppers
- Background `#09090b`, border 1px solid `#27272a`, text `#fafafa`, font `JetBrains Mono` 12px.
- Focus: Border 1px solid `#f59e0b`, outline none.
- Measurement Inputs: Feature trailing fixed-width unit labels (`mm`, `kN/m²`, `m³`, `USD`, `GBP`) styled in `#71717a`.

### Specialized Domain Components
- **Vector Delta Compare Splitter:** 2px high-contrast divider in `#06b6d4` with central drag diamond, permitting live wipe comparisons between revision drawings (Drawing Rev A in red, Drawing Rev B in emerald).
- **Coordinate Crosshair HUD:** Minimal floating 18px badge showing live CAD coordinates `X: 4210.22 Y: 1980.50` in `JetBrains Mono` 10px on `#121215` with `#27272a` boundary.
- **Clash Severity Matrix Cards:** Surface `#121215`, 1px border `#27272a`, left status border 3px in alert color (`#ef4444` for structural hard clashes, `#f59e0b` for MEP soft clearances).