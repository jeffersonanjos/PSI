# Visual Tokens & Theme Guide

This project uses a modern, accessible design system layered on Bootstrap 5.

## Palette
- Primary: `#2563EB`
- Secondary: `#60A5FA`
- Accent: `#FACC15`
- Neutral background: `#F9FAFB`
- Text default: `#0F172A`
- Dark mode base: `#0F172A`
- Dark mode surface: `#1E293B`

## Typography
- Font stack: Poppins / Inter (Google Fonts), system fallbacks.
- Headings use tighter letter-spacing and heavier weights.

## Structure
- Fixed, translucent navbar with theme toggle.
- Minimal footer with social icons.
- Global loader overlay `#globalLoader` appears on navigation.

## Components
- Cards: rounded, subtle elevation; hover raises with shadow.
- Buttons: rounded corners, elevated hover, primary uses `--color-primary`.
- Forms: rounded inputs, focus ring tinted with Secondary.
- Lists: list-group items look like cards.

## Layouts
- Homepage can receive `homepage` class on `<body>` to enable a soft gradient background. Alternative: add `option-image` to use an abstract image with dark overlay.

## Dark Mode
- Applied by toggling `dark` class on `<html>`.
- Persisted in `localStorage` as `theme` (`dark` or `light`).

## AOS (Animate On Scroll)
- Included via CDN. Elements can add `data-aos="fade-up"` (or other effects).

## Usage in Templates
- Include `{{ url_for('static', filename='css/style-modern.css') }}` after legacy CSS.
- Ensure `<script src="{{ url_for('static', filename='js/theme.js') }}"></script>` is present.
- Add `data-aos` attributes to sections and cards for microinteractions.

## CSS Token Reference (in :root)
See `app/static/css/style-modern.css` for variables:
- `--color-primary`, `--color-secondary`, `--color-accent`, `--color-bg`, `--color-text`, `--color-surface`
- Shadows: `--shadow-sm`, `--shadow-md`
- Radii: `--radius-sm`, `--radius-md`, `--radius-lg`
- Transition: `--transition-fast`

## Notes
- Keep Bootstrap classes for responsiveness; the modern CSS adds a thematic layer.
- Prefer semantic HTML, ARIA labels for interactive elements.
