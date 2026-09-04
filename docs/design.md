# Design Specification

## 1. Layout

### Desktop

```text
┌───────────────────────────────────────────────────────────────────┐
│ Lenny Growth Assistant     [Ollama ▾]      [New session]          │
├───────────────────────────────┬───────────────────────────────────┤
│ Chat / history                │ Artifact Preview                 │
│                               │                                   │
│ user message                  │ Markdown or HTML artifact        │
│ assistant + citations         │                                   │
│                               │                                   │
│ [Ask a growth question...]    │ [collapse]                        │
└───────────────────────────────┴───────────────────────────────────┘
```

The split is approximately 56/44 and the artifact pane is collapsible.

## 2. State machine

```text
IDLE
  │ send
  ▼
RETRIEVING
  │ sources
  ▼
STREAMING ── error ──> ERROR
  │ done
  ▼
COMPLETE
  │ artifact event
  ▼
ARTIFACT_VISIBLE
```

Session creation is lazy: the frontend creates a session on first use.

## 3. Message states

- Sending: disabled submit + spinner.
- Streaming: assistant bubble updates incrementally.
- Complete: sources displayed as compact cards.
- Error: user-readable retry state.
- Empty: prompt examples and explanation of grounded behavior.

## 4. Artifact behavior

- Markdown: `react-markdown` + `remark-gfm`.
- HTML: DOMPurify -> `srcDoc` -> `<iframe sandbox="allow-scripts">`.
- No `allow-same-origin`.
- Artifact pane shows a "Sandboxed Preview" badge.

## 5. Responsive behavior

- >= 1100px: two panes.
- 768–1099px: 60/40 split with smaller padding.
- < 768px: single chat pane; artifact is a drawer/modal.
- Touch targets are at least 40px.

## 6. Visual hierarchy

- Neutral dark/gray shell.
- High-contrast readable message text.
- Source citations are visually distinct but not distracting.
- Provider badge is always visible so local/cloud state is obvious.

## 7. Accessibility

- Semantic buttons and labels.
- Keyboard-focusable controls.
- `aria-label` for icon-only controls.
- Artifact iframe has a descriptive title.
- Reduced motion is respected by avoiding animation-dependent interactions.
