# Agent Handoff: fl-event-passthru Branch

**Branch:** `fl-event-passthru`
**Base:** `main` (which includes all `custom-enhancements` work)
**Date:** 2026-02-16 (updated session 2)
**Status:** Custom CC page + hybrid page fully implemented with LCD feedback

---

## Session 2: Custom Page LCD Feedback + Page Ordering Fix

### Goal
Fix two issues: (1) page ordering mismatch between `plugin_parameter_view.py` and `plugin_parameter_screen_view.py`, and (2) add live LCD feedback when turning knobs on the custom CC page.

### Changes Made

#### 1. `script/actions.py` — Added `CustomCcValueChangedAction`
New action dataclass for dispatching custom CC knob changes to the screen view:
```python
@PlainData
class CustomCcValueChangedAction:
    control: int
    cc_number: int
    midi_channel: int
    port: int
    value: int
```

#### 2. `script/device_independent/view/plugin_parameter_view.py`
- Added `CustomCcValueChangedAction` to imports
- `_send_custom_cc()` now dispatches `CustomCcValueChangedAction` after setting parameter value, so the LCD updates with CC number + value info
- Added `_send_hybrid_cc()` for hybrid page CC pass-thru knobs (knobs 7-8) — sets `fl_event.handled = False` and uses `skip_claiming_handled` flag

#### 3. `script/device_independent/view/plugin_parameter_screen_view.py`
- **Fixed page ordering**: `is_custom_page` now correctly maps to `plugin_pages` (first extra page), `is_hybrid_page` to `plugin_pages + 1` (second extra page) — matching `plugin_parameter_view.py`
- **Per-knob labels on custom page**: Instead of blanket "CC Thru", each knob shows its CC number ("CC 52" through "CC 59")
- **Added `handle_CustomCcValueChangedAction`**: Shows live feedback when custom CC knobs are turned — displays `CC {num}` as name and `ch{N} p{port} v{value}` as value

#### 4. `script/device_adapters/fl_to_application_adapter/fl_to_application_adapter.py`
- Added `skip_claiming_handled` module-level flag used by hybrid page CC pass-thru to prevent the adapter from re-setting `handled = True` after the view sets it to `False`

### Page Structure (Current)
For a plugin with N pages of parameters:
- Pages 0 to N-1: Regular plugin parameter pages
- Page N: **Custom page** (all 8 knobs send CC 52-59 via `handled=False`)
- Page N+1: **Hybrid page** (6 plugin params + 2 CC pass-thru knobs)

---

## Session 1: FL Event Passthrough (Original Work)

### Goal
Give `PluginParameterView` access to FL Studio's `eventData` object so the custom CC page can send generic MIDI CC messages (CC 52-59) that FL Studio processes globally/omni, rather than targeting specific plugins directly.

### The Solution (Simpler Than Expected)

The key discovery: **setting `fl_event.handled = False` is all that's needed**. No `device.processMIDICC()` required.

#### The Critical Customization
The manufacturer's original code in `fl_to_application_adapter.py` set `fl_event.handled = True` as the **last line** of `on_midi()`, meaning all MIDI was unconditionally marked as handled. This was **intentional manufacturer design**, NOT a bug.

**The customization:** Move `fl_event.handled = True` to the **first line** of `on_midi()`. This allows downstream code to selectively set `fl_event.handled = False` to pass specific events back to FL Studio.

---

## Files Changed (This Session Only)

### 1. `script/action_generators/surface_action_generator/surface_actions.py`
- Added `fl_event: object = None` field to `ControlChangedAction`
- Carries the original FL eventData through the action pipeline

### 2. `script/action_generators/surface_action_generator/keyboard_controller_common/keyboard_controller_common_pot_action_generator.py`
- Updated to pass `fl_event=fl_event` when creating `ControlChangedAction`

### 3. `script/action_generators/surface_action_generator/keyboard_controller_common/keyboard_controller_common_fader_action_generator.py`
- Updated to pass `fl_event=fl_event` when creating `ControlChangedAction`

### 4. `script/device_adapters/fl_to_application_adapter/fl_to_application_adapter.py`
- Moved `fl_event.handled = True` from last line to first line of `on_midi()`
- Added debug logging for incoming MIDI (print statement)

### 5. `script/device_independent/view/plugin_parameter_view.py`
- `handle_ControlChangedAction()` passes `action.fl_event` to `_send_custom_cc()`
- `_send_custom_cc()` accepts `fl_event` parameter, modifies its properties, sets `handled = False`
- User stated they will manually tailor the `_send_custom_cc()` implementation details

### 6. `IMPLEMENTATION_processMIDICC_access.md`
- Documentation of the solution, data flow, and what was/wasn't needed

---

## Data Flow

```
FL Studio sends MIDI event
  ↓
OnMidiIn callback receives eventData
  ↓
FLToApplicationAdapter.on_midi(fl_event)
  - Sets fl_event.handled = True (default, first line)
  ↓
SurfaceActionGenerator.handle_midi_event(fl_event)
  ↓
Creates ControlChangedAction(control, position, fl_event=fl_event)
  ↓
PluginParameterView.handle_ControlChangedAction(action)
  ↓
If custom page: _send_custom_cc(index, position, action.fl_event)
  ↓
Modifies fl_event properties:
  - fl_event.controlNum = CC number (52-59)
  - fl_event.controlVal = MIDI value (0-127)
  - fl_event.midiChan = desired channel
  - fl_event.handled = False  ← THE KEY STEP
  ↓
FL Studio processes the event through its normal MIDI handling
```

---

## What Was Tried and Removed

### Over-Engineered Device Reference Passing (REMOVED)
Initially implemented a complex system to pass the FL Studio `device` module through the entire architecture so `device.processMIDICC()` could be called from `PluginParameterView`. This involved:
- Creating `script/device_reference.py` (singleton holder)
- Modifying all 7 `device_novation_*.py` files to store device references
- Adding device parameters to `PluginParameterView` and layout managers
- Complex `_send_custom_cc()` logic with `processMIDICC()` calls

**All of this was unnecessary and has been completely removed.** The simple `fl_event.handled = False` approach replaced all of it.

### Key lesson: `device.processMIDICC()` is NOT needed. Just set `handled = False`.

---

## What NOT To Do (Learned From Prior Sessions)

1. **Don't use `device.midiOutMsg()`** — not FL Studio, didnt seem to work and handled = False lets fl studio take care of it more simply
2. **Don't duck-type FL Studio objects** — crashes FL Studio
3. **Don't use `device.processMIDICC()` with custom objects** — crashed FL Studio
4. **Don't use `device.forwardMIDICC()`** — didn't work
5. **Don't try to generate global MIDI messages via API** — FL Studio's Python API doesn't support it
6. **DO use `fl_event.handled = False`** — this is the correct approach


---

## Current State of `_send_custom_cc()`

The user confirmed the approach works and stated they will manually customize the implementation. The current code is:

```python
def _send_custom_cc(self, index, position, fl_event=None):
    """Send CC message for custom page by passing event back to FL Studio."""
    if fl_event is None:
        return
    fl_event.controlNum = 52 + index  # CC 52-59
    fl_event.controlVal = int(position * 127)  # 0-127
    fl_event.midiChan = 0  # Channel 1 (0-indexed)
    fl_event.handled = False  # Let FL Studio process it
```

The user may have already modified this manually.

---

## Important Context

- **This is a custom alteration, not a bug fix.** The manufacturer intentionally set `handled = True` for all events. The user is deliberately overriding this behavior for specific events.
- **The user prefers minimal changes.** Over-engineering was explicitly called out and removed.
- **Existing handoff docs:** `AGENT_HANDOFF_custom-enhancements.md` covers the broader branch history (independent channel selection, pagination, MODO DRUM, etc.)
- **Related docs:** `IMPLEMENTATION_processMIDICC_access.md` has detailed technical documentation of the solution.

---

## Pending / User-Owned Tasks

- Custom CC page and hybrid page are fully implemented with LCD feedback
- User may want to test and verify in FL Studio
- No explicit pending requests from user

---

## Branch Relationship

```
main (OEM baseline)
  └── custom-enhancements (33 commits: channel selection, pagination, MODO DRUM, etc.)
        └── fl-event-passthru (current: fl_event passthrough for MIDI CC control)
```

**End of Handoff Document**


