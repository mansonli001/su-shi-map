---
name: Ink & Path
colors:
  surface: '#fef8f6'
  surface-dim: '#ded9d7'
  surface-bright: '#fef8f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f8f2f0'
  surface-container: '#f3edea'
  surface-container-high: '#ede7e5'
  surface-container-highest: '#e7e1df'
  on-surface: '#1d1b1a'
  on-surface-variant: '#4e453f'
  inverse-surface: '#32302f'
  inverse-on-surface: '#f5efed'
  outline: '#80756e'
  outline-variant: '#d1c4bc'
  surface-tint: '#6b5b50'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#241911'
  on-primary-container: '#928174'
  inverse-primary: '#d7c3b5'
  secondary: '#7b5800'
  on-secondary: '#ffffff'
  secondary-container: '#fdc34d'
  on-secondary-container: '#715000'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#171c23'
  on-tertiary-container: '#7f848d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#f4ded0'
  primary-fixed-dim: '#d7c3b5'
  on-primary-fixed: '#241911'
  on-primary-fixed-variant: '#52443a'
  secondary-fixed: '#ffdea6'
  secondary-fixed-dim: '#f7bd48'
  on-secondary-fixed: '#271900'
  on-secondary-fixed-variant: '#5d4200'
  tertiary-fixed: '#dee2ed'
  tertiary-fixed-dim: '#c2c6d1'
  on-tertiary-fixed: '#171c23'
  on-tertiary-fixed-variant: '#42474f'
  background: '#fef8f6'
  on-background: '#1d1b1a'
  surface-variant: '#e7e1df'
typography:
  display-lg:
    fontFamily: notoSerif
    fontSize: 42px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: notoSerif
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: notoSerif
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: sourceSansThree
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: sourceSansThree
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: sourceSansThree
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  vertical-header:
    fontFamily: notoSerif
    fontSize: 20px
    fontWeight: '500'
    lineHeight: '1.5'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  container-margin: 24px
  gutter: 16px
  touch-target-min: 44px
  stack-sm: 12px
  stack-md: 24px
  stack-lg: 48px
---

## Brand & Style

This design system embodies the intersection of ancient literary heritage and modern digital performance. It is tailored for a scholarly audience that values quiet contemplation, historical depth, and refined aesthetics.

The visual style is **Contemporary Minimalism with Calligraphic Influence**. It leverages expansive whitespace to evoke the "negative space" (*liubai*) found in traditional ink-wash paintings. The interface should feel as tactile as high-grade rice paper yet as fluid as a modern PWA. Design decisions prioritize legibility and a sense of "digital silk"—smooth transitions, deliberate pacing, and a premium, curated feel.

## Colors

The palette is derived from the traditional Four Treasures of the Study. 

- **Deep Ink Black:** Used for primary text and structural grounding. It is not a pure black, but a warm, carbon-based ink tone.
- **Warm Parchment:** The canvas of the application. This off-white provides a soft, low-fatigue reading environment that feels archival yet fresh.
- **Refined Bronze Gold:** Reserved for markers of excellence, interactive highlights, and high-level navigation cues.
- **Cinnabar Red:** Used sparingly for "seals" (logos/stamps) and critical emphasis, mimicking the wax seals on ancient scrolls.
- **Jade Celadon & Misty Grey:** Utilized for secondary data visualization, such as travel paths on maps or subtle metadata labels.

## Typography

The typography system creates a rhythmic contrast between the editorial authority of the serif and the functional clarity of the sans-serif.

- **Headlines:** Use high-contrast Serifs to anchor the page. For decorative headers, implement **vertical text orientation** (right-to-left) to mimic traditional scroll layouts, ensuring they are used for short titles only.
- **Body:** Use a modern Sans-Serif for maximum legibility on mobile screens. Line heights are generous to prevent visual crowding.
- **Labels:** Small-caps are used for metadata and category tags to differentiate from narrative text without increasing weight.

## Layout & Spacing

The design system utilizes a **12-column fluid grid** for desktop and a **single-column fluid stack** for mobile. 

- **PWA Constraints:** All interactive elements must maintain a minimum touch target of 44px. Bottom navigation is mandatory for reachability.
- **Rhythm:** Use an 8px base grid. Larger vertical gaps (48px+) should be used between major sections to emphasize the "minimalist" personality.
- **Safe Areas:** Ensure content respects the "notch" and "home indicator" areas on modern mobile devices by using dynamic padding-bottom on the navigation bar.

## Elevation & Depth

Depth is conveyed through **tonal layering and subtle outlines** rather than heavy shadows.

- **Tiers:** The background is `Warm Parchment`. Cards and modal sheets use a slightly lighter, pure-white tint or a very subtle `Misty Grey` border (0.5px).
- **Shadows:** Only use shadows for "floating" elements like FABs (Floating Action Buttons) or active menus. Use a high-diffusion, low-opacity (8%) shadow tinted with the `Deep Ink Black` to keep it soft and natural.
- **Dividers:** Use thin (1px or 0.5px) hairlines in `Misty Grey` with 40% opacity to separate content without breaking the flow.

## Shapes

The shape language is **Soft (0.25rem)**. This subtle rounding removes the harshness of digital corners while maintaining a structured, scholarly discipline. 

- **Standard Elements:** Buttons and input fields use a 4px (0.25rem) radius.
- **Cards:** Content containers use 8px (0.5rem) to feel distinct from the page background.
- **Seals:** Brand icons or "seal" elements may use a 0px radius or a rough, organic "ink-bleed" mask to contrast against the clean UI.

## Components

- **Buttons:** Primary buttons are `Deep Ink Black` with `Warm Parchment` text. Secondary buttons are outlined in `Bronze Gold`. All buttons must have a height of at least 48px for PWA ergonomics.
- **Bottom Navigation:** A frosted `Warm Parchment` bar with `Deep Ink Black` icons. The active state is indicated by a `Cinnabar Red` dot above the icon, mimicking a stamped mark.
- **Cards:** Cards should have no shadow by default, instead using a 1px `Misty Grey` border. On press, they may lift slightly with a soft shadow.
- **Input Fields:** Bottom-aligned borders only (like a underline) are preferred to evoke a sense of writing on a line, though full boxes are acceptable for high-density forms.
- **Chips/Tags:** Small, pill-shaped elements using `Jade Celadon` backgrounds with a 10% opacity and `Deep Ink Black` text for a "botanical" or "earthy" accent.
- **Interactive Maps:** Use a custom "ink-wash" map style with `Misty Grey` terrain and `Bronze Gold` paths to track the poets' journeys.