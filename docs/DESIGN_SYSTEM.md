# Design System

PiePro uses a soft-modern productivity dashboard aesthetic.

## Visual Identity

- Soft sage green application background.
- Large rounded shell with a thick black outline.
- Off-white panels with pastel yellow, baby blue, blush pink, sage, and light gray accents.
- Rounded geometry everywhere, typically 20-32px radius.
- Thick black accents used selectively for active controls, icon rails, and high-contrast buttons.
- Soft neumorphic shadows and subtle depth.
- Playful but still professional workspace mood.

## Layout

- Main UI sits inside a large rounded framed workspace.
- Left navigation is a vertical black pill with stacked circular icon buttons.
- Top navigation is a floating rounded bar with pill links.
- Dashboard uses a modular multi-widget grid with asymmetrical but balanced sections.
- Cards should have generous internal spacing and clear visual hierarchy.

## Components

Preferred components:

- Rounded pastel cards.
- Rounded pills and capsules.
- Chunky circular icon buttons.
- Cute progress bars.
- Calendar blocks with colorful active dates.
- Avatar stacks with soft colors.
- Sticky note cards with subtle rotation.
- Rounded timer and focus widgets.
- Folder/file cards with upload status.
- Mobile preview cards for compact layouts.
- Rounded toggles and segmented controls.

## Palette

- Background: soft sage green.
- Surfaces: off-white and light gray.
- Accents: pastel yellow, baby blue, blush pink, gentle violet, muted green.
- Contrast: black and near-black only for important controls.

Avoid:

- Dark cyberpunk UI.
- Sharp enterprise tables.
- Oversaturated colors.
- Dense gray admin dashboards.
- Flat black backgrounds except for accent pills/rails/cards.

## Typography

- Use rounded, bold sans-serif styling.
- Headings should be oversized and friendly.
- Body labels should be medium to bold.
- Preserve large readable labels and strong hierarchy.

## Implementation Notes

- Shared shell is in `frontend/app/layout.tsx`.
- Sidebar/topbar are in `frontend/components/nav.tsx`.
- Shared cards, pills, progress bars, and avatars are in `frontend/components/card.tsx`.
- Dashboard widgets are in `frontend/app/dashboard/page.tsx`.

Any frontend change must preserve this design language unless the user explicitly changes the visual direction.

