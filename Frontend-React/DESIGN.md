# Constaty Design System

## Direction

A quiet, document-like conversation for bright outdoor use. It feels familiar to users of high-quality mobile assistants while remaining distinctly Constaty through warm neutrals, petrol ink, restrained turquoise voice controls, and precise claim-understanding rows.

## Color

- Warm tinted off-white background, never pure white.
- Deep petrol and ink for text and navigation.
- Restrained turquoise for voice and active interaction.
- Moss green for confirmed information, paired with an icon and text.
- Amber for missing or uncertain information, paired with explicit wording.
- Muted red only for safety and blocking errors.

## Typography

- Latin: Inter. Arabic: Noto Sans Arabic.
- Body text is at least 16px with a comfortable line height.
- Assistant prompts range from 17px to 20px.
- Labels and metadata range from 12px to 14px and never carry critical meaning alone.
- Hierarchy comes from scale and spacing before bold weight.

## Layout

- Mobile-first full-height shell with safe-area support.
- Compact sticky header, scrollable conversation, sticky keyboard-aware composer.
- Assistant turns are mostly unboxed. User turns use compact petrol bubbles.
- Structured understanding uses semantic rows and quiet rules, not nested cards.
- Desktop centers the phone-width conversation in a subtle canvas without dashboard chrome.

## Components

- Compact header with Constaty mark, saved/offline state, and language control.
- Assistant and user message turns.
- Large quick replies that wrap safely.
- Editable transcript review with record-again and use-transcript actions.
- Extraction summary with confirmed, uncertain, and missing rows.
- Neutral clarification prompts.
- Composer with attachment, expanding text input, send, and dominant microphone.
- Expanded recording composer with timer, live amplitude bars, cancel, and stop.
- Human status language instead of generic loading spinners.

## Motion

- 160ms to 240ms state transitions using ease-out curves.
- Animate opacity and transform for message arrival and composer expansion.
- Waveform motion reflects live input amplitude.
- Respect reduced motion and never delay task completion for choreography.

## Voice & Copy

Use short, direct, supportive sentences. Begin with safety and empathy. Avoid blame, fraud language, extraction jargon, and bureaucratic phrasing. Say what was heard and understood, then let the driver correct it.
