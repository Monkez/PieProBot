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
- Navigation lives in a floating rounded topbar with pill links.
- Do not add a separate sidebar unless the user explicitly asks for it.
- Dashboard uses a modular multi-widget grid with asymmetrical but balanced sections.
- Cards should have generous internal spacing and clear visual hierarchy.

## Components

Preferred components:

- Rounded pastel cards.
- Rounded pills and capsules.
- Chunky circular icon buttons.
- Cute progress bars.
- Avatar stacks with soft colors.
- Rounded toggles and segmented controls.
- Operational status cards for runtime, tasks, memory, tools, providers, and self-update.

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
- Decorative widgets that do not serve PiePro operations.
- Filling the dashboard with fake productivity modules just to match the style.

## Typography

- Use rounded, bold sans-serif styling.
- Headings should be oversized and friendly.
- Body labels should be medium to bold.
- Preserve large readable labels and strong hierarchy.

## Implementation Notes

- Shared shell is in `frontend/app/layout.tsx`.
- Topbar navigation is in `frontend/components/nav.tsx`.
- Shared cards, pills, progress bars, and avatars are in `frontend/components/card.tsx`.
- Dashboard widgets are in `frontend/app/dashboard/page.tsx`.

Any frontend change must preserve this design language unless the user explicitly changes the visual direction.

Style is a visual system, not a content requirement. Only include components that support real PiePro operations or navigation.
