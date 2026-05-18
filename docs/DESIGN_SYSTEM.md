# Design System

PiePro uses a bright minimal fintech dashboard aesthetic.

## Visual Identity

- Soft white/light-gray application background.
- Large rounded shell with a light border and soft shadow.
- White and soft-gray panels with primary blue, warm yellow/orange, and light pastel support accents.
- Rounded geometry everywhere, typically 20-32px radius.
- Blue is the primary action and active-control color.
- Warm yellow/orange is used for highlights and secondary calls to action.
- Soft neumorphic shadows and subtle depth.
- Calm, polished, premium SaaS mood.

## Layout

- Main UI sits inside a large rounded framed workspace.
- Navigation lives in a floating rounded topbar with pill links.
- Do not add a separate sidebar unless the user explicitly asks for it.
- Dashboard uses a modular multi-widget grid with asymmetrical but balanced sections.
- Cards should have generous internal spacing and clear visual hierarchy.

## Components

Preferred components:

- Rounded white and light-gray cards.
- Rounded pills and capsules.
- Chunky circular icon buttons.
- Smooth progress bars.
- Avatar stacks with blue/yellow/orange/green accents.
- Rounded toggles and segmented controls.
- Operational status cards for runtime, tasks, memory, tools, providers, and self-update.

## Palette

- Background: soft white and light gray.
- Surfaces: white and soft gray.
- Primary accent: `#2D8CFF`.
- Warm accent: yellow/orange around `#FFC247`.
- Supporting accents: soft green, light blue, soft coral.
- Text: near-black gray, with muted gray supporting text.

Avoid:

- Dark cyberpunk UI.
- Sharp enterprise tables.
- Oversaturated colors.
- Dense gray admin dashboards.
- Heavy black accents or dark-mode styling.
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
