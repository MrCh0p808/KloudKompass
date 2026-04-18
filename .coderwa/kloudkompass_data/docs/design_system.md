# StatWoX Design System

Canonical neuromorphic design tokens and styling guidelines.

## V3ND377A 5Y573M5 Neon Dark Palette
- **Background Dim**: `#09090b` (`--n-bg-dark`)
- **Panel Surface**: `#121214` (`--n-bg-panel`)
- **Elevated UI**: `#1a1a1e` (`--n-bg-elevated`)

## Secondary Accents
- **Cyan**: `#00d4ff` (Primary Glow)
- **Purple**: `#a855f7` (Secondary Interaction)
- **Green**: `#00ff88` (Success/Verification)

## Neuromorphic Shadow Invariants
- **Outset**: `4px 4px 10px rgba(0, 0, 0, 0.6), -2px -2px 6px rgba(255, 255, 255, 0.04)`
- **Inset**: `inset 2px 2px 5px rgba(0, 0, 0, 0.5), inset -1px -1px 3px rgba(255, 255, 255, 0.03)`
- **Glow**: `0 0 15px rgba(0, 212, 255, 0.15)`

## Standard Classes
- `.neuro-panel`: Standard container with outset shadows.
- `.neuro-inset`: Recursive inset container for inputs/fields.
- `.neuro-button`: Tactile button with spring-based scale transitions.
- `.neuro-glow-text`: Forced white text with cyan outer glow.

## Typography
- **Display**: Outfit / Inter (Strict letter-spacing: `-0.02em`)
- **Body**: Inter
- **Code**: JetBrains Mono

## Motion
- **Easing**: `cubic-bezier(0.175, 0.885, 0.32, 1.275)` (Spring)
- **Transitions**: Fragmented slide-up and scale-in as session standards.