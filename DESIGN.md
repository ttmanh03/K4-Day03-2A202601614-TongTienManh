---
name: Cupid Agent
colors:
  surface: '#f7f9ff'
  surface-dim: '#d7dadf'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4f9'
  surface-container: '#ebeef3'
  surface-container-high: '#e5e8ee'
  surface-container-highest: '#e0e3e8'
  on-surface: '#181c20'
  on-surface-variant: '#5a4042'
  inverse-surface: '#2d3135'
  inverse-on-surface: '#eef1f6'
  outline: '#8e6f71'
  outline-variant: '#e2bec0'
  surface-tint: '#ba1340'
  primary: '#b60e3d'
  on-primary: '#ffffff'
  primary-container: '#da3054'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb2b8'
  secondary: '#8433c4'
  on-secondary: '#ffffff'
  secondary-container: '#bd6efe'
  on-secondary-container: '#450073'
  tertiary: '#5a5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#737575'
  on-tertiary-container: '#fcfcfc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b8'
  on-primary-fixed: '#40000f'
  on-primary-fixed-variant: '#91002d'
  secondary-fixed: '#f2daff'
  secondary-fixed-dim: '#e0b6ff'
  on-secondary-fixed: '#2e004e'
  on-secondary-fixed-variant: '#6a0baa'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c7'
  on-tertiary-fixed: '#1a1c1c'
  on-tertiary-fixed-variant: '#454747'
  background: '#f7f9ff'
  on-background: '#181c20'
  surface-variant: '#e0e3e8'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1200px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is engineered to evoke a sense of sophisticated matchmaking, blending high-end technology with human-centric warmth. The brand personality is "The Intuitive Concierge"—intelligent, discreet, and deeply empathetic. The aesthetic leans heavily into **Modern Minimalism** with a **Glassmorphic** touch, prioritizing clarity and emotional resonance over algorithmic complexity.

The interface should feel airy and premium. We achieve this through generous white space (macro-spacing), a refined color palette, and soft, organic shapes that mirror the fluidity of human relationships. The goal is to move the user from the "stress" of dating into the "ease" of assisted compatibility.

## Colors

This design system utilizes a high-romance, high-tech palette. The **Primary Accent** (Rose) is used for calls to action and heart-centric interactions. The **Secondary Accent** (Lavender) provides a mystical, AI-driven feel, often appearing in gradients alongside the primary color to represent the "spark" of compatibility.

**Gradients:**
- **Primary Spark:** Linear gradient (45deg) from `#FF4D6D` to `#9D4EDD`.
- **Subtle Surface:** Linear gradient (bottom to top) from `#F8F9FA` to `#FFFFFF`.

**Semantic Colors:**
- **Success:** Soft Emerald (#2DCE89) for compatibility matches.
- **Surface:** Pure White (#FFFFFF) for cards and interactive containers.
- **Text:** Dark Charcoal (#212529) for primary content; Medium Grey (#6C757D) for secondary metadata.

## Typography

The design system utilizes **Inter** exclusively to maintain a clean, systematic, and modern aesthetic. The hierarchy relies on tight letter-spacing for headlines to create a "locked-in" premium feel, while body text remains spacious for maximum legibility.

- **Headlines:** Use Bold (700) or Semi-Bold (600) weights. High-impact headlines should use the Primary Spark gradient as a text fill on dark or high-contrast backgrounds.
- **Body:** Use Regular (400) weight. Avoid pure black text; use Dark Charcoal to keep the look "soft."
- **Labels:** Use Medium (500) or Semi-Bold (600) for UI controls, buttons, and navigation elements.

## Layout & Spacing

The layout philosophy follows a **Fluid Grid** with a strict 8px base unit. 

- **Desktop:** 12-column grid with a 1200px max-width. Use generous vertical padding (64px–128px) between sections to maintain the "Minimalist" brand promise.
- **Mobile:** 4-column grid with 16px side margins. Horizontal scrolling "peek" cards are preferred for profile browsing to save vertical real estate.
- **Rhythm:** Spacing between related elements (e.g., label and input) should be 8px. Spacing between unrelated groups should be 32px or greater.

## Elevation & Depth

Depth is communicated through **Soft Ambient Shadows** and **Tonal Layering**. 

1.  **Level 0 (Base):** Off-white (#F8F9FA) background.
2.  **Level 1 (Cards):** Pure White (#FFFFFF) surfaces with a subtle shadow: `0px 4px 20px rgba(0, 0, 0, 0.04)`.
3.  **Level 2 (Active/Hover):** Lifted state with a more pronounced shadow: `0px 12px 32px rgba(255, 77, 109, 0.08)`. 
4.  **Glassmorphism:** Use for navigation bars and overlays. Apply a `backdrop-filter: blur(12px)` with a 80% opacity white fill. This creates a sense of the interface "floating" over the user's content.

## Shapes

The shape language is "Hyper-Rounded," leaning into the friendlier end of the professional spectrum. 

- **Standard Elements:** Use `16px` (rounded-lg) for standard cards and large buttons.
- **Small Elements:** Use `8px` for input fields and smaller chips.
- **Feature Components:** For high-engagement items like "Match" buttons or "AI Agent" chat bubbles, use `24px` or full pill-shaping to distinguish them from structural UI.

## Components

- **Buttons:**
    - **Primary:** "Primary Spark" gradient fill with white text. 16px radius.
    - **Secondary:** Ghost style with a 1px Lavender border.
- **Input Fields:** Soft grey background (#F1F3F5) in resting state, moving to a White background with a 1px Primary Rose border on focus. 12px radius.
- **Cards:** White background, 16-20px radius, soft ambient shadow. No borders.
- **Chips:** Used for "Interests" or "Compatibility Traits." Subtle Lavender tint (#F3EBFA) with Lavender text. Full pill-shape.
- **Compatibility Meter:** A circular or linear progress bar using the Primary Spark gradient, representing the AI's confidence in a match.
- **AI Chat Bubble:** Distinguished by a very subtle Lavender glow effect (`box-shadow: 0 0 15px rgba(157, 78, 221, 0.15)`).