---
name: Literati Manuscript
colors:
  surface: '#fff8f5'
  surface-dim: '#e3d8d1'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fef1ea'
  surface-container: '#f8ece4'
  surface-container-high: '#f2e6df'
  surface-container-highest: '#ece0d9'
  on-surface: '#201b16'
  on-surface-variant: '#4f453d'
  inverse-surface: '#362f2a'
  inverse-on-surface: '#fbeee7'
  outline: '#81756b'
  outline-variant: '#d3c4b9'
  surface-tint: '#79573a'
  primary: '#765538'
  on-primary: '#ffffff'
  primary-container: '#916d4e'
  on-primary-container: '#fffbff'
  inverse-primary: '#eabe9a'
  secondary: '#7f5539'
  on-secondary: '#ffffff'
  secondary-container: '#fec6a3'
  on-secondary-container: '#795035'
  tertiary: '#75593a'
  on-tertiary: '#ffffff'
  tertiary-container: '#ac8b68'
  on-tertiary-container: '#3b250a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdcc1'
  primary-fixed-dim: '#eabe9a'
  on-primary-fixed: '#2d1601'
  on-primary-fixed-variant: '#5f4025'
  secondary-fixed: '#ffdcc7'
  secondary-fixed-dim: '#f2bb98'
  on-secondary-fixed: '#301401'
  on-secondary-fixed-variant: '#643e24'
  tertiary-fixed: '#ffddbb'
  tertiary-fixed-dim: '#e5c099'
  on-tertiary-fixed: '#2b1701'
  on-tertiary-fixed-variant: '#5c4224'
  background: '#fff8f5'
  on-background: '#201b16'
  surface-variant: '#ece0d9'
typography:
  display-lg:
    fontFamily: EB Garamond
    fontSize: 48px
    fontWeight: '500'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: EB Garamond
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: EB Garamond
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 36px
  title-md:
    fontFamily: EB Garamond
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0.05em
  body-lg:
    fontFamily: Source Serif 4
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 32px
  body-md:
    fontFamily: Source Serif 4
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 28px
  label-sm:
    fontFamily: Source Serif 4
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
spacing:
  unit: 8px
  gutter: 24px
  margin-mobile: 20px
  margin-desktop: 64px
  container-max: 1040px
---

## Brand & Style
This design system draws inspiration from the Song Dynasty's aesthetic peaks: restraint, intellectual depth, and the "scholar's studio" (Wenfang Sibao) atmosphere. It targets an audience that values slow consumption, contemplative reading, and historical continuity.

The style is a refined **Minimalist-Tactile** hybrid. It rejects modern high-gloss interfaces in favor of a "digital parchment" experience. The visual narrative centers on the textures of handmade paper, the precision of woodblock printing, and the organic flow of ink. Every element should feel curated and intentional, evoking the emotional response of unrolling a precious scroll or opening a hand-bound volume.

## Colors
The palette is rooted in natural pigments and organic materials.
- **Primary (Golden-Brown):** Used for structural accents, borders, and call-to-action highlights. It represents polished sandalwood and aged lacquer.
- **Secondary (Ink-Wash):** A deep, warm brown used for secondary actions and subtle iconography.
- **Neutral (Charcoal):** Reserved for primary typography, mimicking the matte finish of high-quality soot-based ink.
- **Backgrounds:** Use `#F4F1DE` for main content areas to mimic fresh rice paper and `#EAE2B7` for sidebars or recessed areas to suggest aged silk or parchment.

## Typography
The typography system prioritizes the "verticality" and elegance of classical typesetting. 
- **Headlines:** Use **EB Garamond** for its graceful, historical serifs that echo the stroke variation of a brush. High-level displays should use increased tracking to evoke the spatial rhythm of a manuscript.
- **Body Text:** **Source Serif 4** provides exceptional legibility while maintaining a scholarly tone. Line heights are intentionally generous (1.6x - 1.8x) to allow the "breath" of the paper to show through.
- **Orientation:** For special editorial blocks, explore vertical text alignment with right-to-left flow for decorative quotes or headings.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy, centering content like a physical leaf in a book. 
- **Rhythm:** Use an 8px base unit. Margins should be exceptionally wide on desktop to focus the eye and simulate the "empty space" (Ma) essential to Song Dynasty art.
- **Grid:** A 12-column grid for desktop, but content typically occupies only the center 8 columns. 
- **Dividers:** Instead of simple lines, use double-ruled borders or subtle "lattice" patterns for section breaks. Vertical dividers should be used sparingly to separate side-notes from the main text body.

## Elevation & Depth
This design system rejects shadows. Depth is communicated through **Tonal Layering** and **Line Weight**.
- **Surfaces:** Higher-tier elements (like modals or floating menus) are defined by a slightly lighter paper tint and a 1px solid border in `#B08968`.
- **Texture:** Apply a very low-opacity ink-wash texture or a subtle fiber grain to the background layers. 
- **Interaction:** "Elevation" on hover is signaled by a color shift (e.g., from paper-tan to a soft gold tint) or the appearance of a decorative "bracket" frame around the element, rather than a shadow.

## Shapes
The shape language is strictly **Sharp (0)**. 
Corners should be crisp to mimic the edges of cut paper or carved woodblocks. To avoid harshness, visual softness is achieved through the organic nature of the font serifs and the warmth of the color palette, rather than rounded corners. Decorative elements may use "window lattice" geometry—complex octagons or floral cutouts—but the primary UI containers remain rectangular.

## Components
- **Buttons:** Rectangular with a 1px border. Primary buttons use a solid `#B08968` fill with Charcoal text. Secondary buttons use a transparent fill with a border. 
- **Inputs:** Simple bottom-border only, mimicking a line on a writing tablet. Labels sit above in a small-caps serif.
- **Cards:** Defined by a "double-line" border (a thin outer line and a thicker inner line). Use a subtle texture overlay on the card background.
- **Chips/Labels:** Small, rectangular tags with a slight background tint, resembling red vermillion seals (Hanko) when used for status or alerts.
- **Special Elements:** Include a "Scroll Indicator" that looks like a silk ribbon. Use "Cloud Motifs" (Xiangyun) as subtle background watermarks for empty states.
- **Navigation:** Top navigation should be sparse; consider using a "vertical tab" style on the left side for deep-level navigation, reminiscent of traditional book spines.