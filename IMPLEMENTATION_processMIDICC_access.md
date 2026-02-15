# Implementation: eventData Access and FL Studio MIDI Passthrough in PluginParameterView

## Key Discovery: The Real Solution

**The solution to sending global MIDI CCs is much simpler than initially thought:**

Setting `fl_event.handled = False` is all you need. No `device.processMIDICC()` required!

### The Critical Customization

The manufacturer's original implementation in `fl_to_application_adapter.py` had:

```python
def on_midi(self, fl_event):
    self.surface_action_generator.handle_midi_event(fl_event)
    self.firmware_version_validation_controller.handle_midi_event(fl_event)
    fl_event.handled = True  # <-- Last line: ALL MIDI marked as handled
```

**This was intentional** - the script handles all MIDI from the controller by default, preventing FL Studio from processing it.

**The customization** - move `fl_event.handled = True` to the beginning:

```python
def on_midi(self, fl_event):
    fl_event.handled = True  # <-- First line: default to handled
    self.surface_action_generator.handle_midi_event(fl_event)
    self.firmware_version_validation_controller.handle_midi_event(fl_event)
    # Now downstream code can set handled=False to pass events to FL Studio
```

This allows downstream code to selectively set `fl_event.handled = False`, passing those events back to FL Studio for normal processing.

## What's Actually Needed vs. What's Not

### ✓ Actually Needed:

1. **Access to `fl_event` in PluginParameterView**
   - Modified `ControlChangedAction` to carry `fl_event`
   - Updated surface action generators to pass `fl_event`
   - This allows downstream code to modify and control the event

2. **Ability to modify eventData properties**
   - `fl_event.controlNum` - Set the CC number (e.g., 52-59)
   - `fl_event.controlVal` - Set the CC value (0-127)
   - `fl_event.midiChan` - Set the MIDI channel
   - `fl_event.handled` - **The key property!** Set to `False` to pass to FL Studio

3. **The customization to `on_midi()`**
   - Moving `fl_event.handled = True` to the beginning of the method

### ✗ Not Actually Needed:

1. **`device.processMIDICC()` calls**
   - The complex logic in `_send_custom_cc()` isn't necessary
   - Simply setting `handled = False` is sufficient

### ✗ Not Actually Needed (But Implemented):

1. **Device reference module** (`device_reference.py`)
   - Created for accessing `device.processMIDICC()`
   - Not required for the current solution
   - Could be useful for future features that need other device functions

2. **Passing device to PluginParameterView**
   - All the layout manager updates to pass `device=get_device()`
   - Not needed for this specific feature
   - Doesn't hurt to have for future use

## Summary

Implemented access to FL Studio's `eventData` object in `PluginParameterView`, enabling the custom CC page to send generic MIDI CC messages that FL Studio can route naturally through its standard MIDI handling, instead of targeting specific plugins directly.

The solution: modify `eventData` properties and set `handled = False`.

## Changes Made

### 1. Modified `ControlChangedAction` to carry `fl_event`
**File**: `script/action_generators/surface_action_generator/surface_actions.py`

```python
@PlainData
class ControlChangedAction:
    control: int
    position: float
    fl_event: object = None  # Added: carries the original FL eventData
```

### 2. Updated Surface Action Generators to pass `fl_event`
**Files**:
- `script/action_generators/surface_action_generator/keyboard_controller_common/keyboard_controller_common_pot_action_generator.py`
- `script/action_generators/surface_action_generator/keyboard_controller_common/keyboard_controller_common_fader_action_generator.py`

Modified to include `fl_event=fl_event` when creating `ControlChangedAction`.

### 3. Customized `on_midi()` in FLToApplicationAdapter
**File**: `script/device_adapters/fl_to_application_adapter/fl_to_application_adapter.py`

Moved `fl_event.handled = True` to the beginning of the method, allowing downstream code to set `handled = False` to pass events back to FL Studio.

### 4. Created Device Reference Module (Optional)
**File**: `script/device_reference.py` (new file)

Module to hold a reference to the `device` module from FL Studio's global namespace. Created for `processMIDICC()` access but turned out to be unnecessary for the current solution. May be useful for future features.

### 5. Updated All Device Files to Set Device Reference (Optional)
**Files**:
- `device_novation_lk_daw.py`
- `device_novation_lk_88_daw.py`
- `device_novation_lk_mini_daw.py`
- `device_novation_flkey_37_daw.py`
- `device_novation_flkey_49_daw.py`
- `device_novation_flkey_61_daw.py`
- `device_novation_flkey_mini_daw.py`

All DAW device files now import and call `set_device(device)`. Not required for current solution but available for future use.

### 6. Updated `PluginParameterView` to Accept Device Reference and fl_event
**File**: `script/device_independent/view/plugin_parameter_view.py`

- Added `device=None` parameter to `__init__` (optional for current solution)
- Stores device reference as `self.device` (optional)
- Updated `_send_custom_cc()` to accept `fl_event` parameter (**required**)
- Can modify `fl_event` properties and set `handled = False` (**the actual solution**)

### 7. Updated All PluginParameterView Instantiations (Optional)
**Files**:
- `script/device_dependent/LaunchkeyRange/plugin_pot_layout_manager.py`
- `script/device_dependent/FLkeyRange/plugin_pot_layout_manager.py`
- `script/device_dependent/FLkey/plugin_fader_layout_manager.py`

All instantiations now pass `device=get_device()`. Optional for current solution.

## How It Works (Simplified)

### Data Flow

```
1. FL Studio sends MIDI event
   ↓
2. OnMidiIn callback receives eventData
   ↓
3. FLToApplicationAdapter.on_midi(fl_event)
   - Sets fl_event.handled = True (default)
   ↓
4. SurfaceActionGenerator.handle_midi_event(fl_event)
   ↓
5. Creates ControlChangedAction(control, position, fl_event=fl_event)
   ↓
6. PluginParameterView.handle_ControlChangedAction(action)
   ↓
7. If custom page: _send_custom_cc(index, position, action.fl_event)
   ↓
8. Modifies fl_event properties:
   - fl_event.controlNum = CC number (52-59)
   - fl_event.controlVal = MIDI value (0-127)
   - fl_event.midiChan = desired channel
   - fl_event.handled = False  ← THE KEY STEP!
   ↓
9. FL Studio processes the event as if it received it from hardware
   ↓
10. Event routes through FL's normal MIDI handling (global/omni routing)
```

### Minimal Implementation Example

```python
def _send_custom_cc(self, index, position, fl_event=None):
    """Send CC message for custom page by passing event back to FL Studio."""
    if fl_event is None:
        return  # Can't do anything without the event

    # Modify the event properties
    fl_event.controlNum = 52 + index  # CC 52-59
    fl_event.controlVal = int(position * 127)  # 0-127
    fl_event.midiChan = 0  # Channel 1 (0-indexed)

    # The magic: let FL Studio process it
    fl_event.handled = False
```

That's it! No `processMIDICC()` needed.

## What This Unlocks

1. **Generic MIDI CC Messages**: The custom page sends CC 52-59 that FL Studio routes through its normal MIDI handling
2. **Plugin-Agnostic Control**: CCs are processed globally/omni rather than targeting a specific plugin/channel
3. **Standard FL MIDI Processing**: CCs go through FL's automation, recording, and plugin mapping systems
4. **Modified eventData Usage**: Any part of the script can now modify eventData and pass it back to FL Studio
5. **Future Flexibility**: This pattern can be extended to other MIDI message types (note on/off, pitch bend, etc.)

## Testing Results

✓ **Confirmed working**: Setting `fl_event.handled = False` successfully passes MIDI events back to FL Studio for global/omni processing.

## Debugging MIDI Events

To observe incoming MIDI in the Python environment, add logging to `on_midi()`:

```python
def on_midi(self, fl_event):
    # Log all incoming MIDI
    print(f"MIDI IN: status={fl_event.status:#04x} data1={fl_event.data1} " +
          f"data2={fl_event.data2} midiChan={fl_event.midiChan} " +
          f"controlNum={fl_event.controlNum} controlVal={fl_event.controlVal}")

    fl_event.handled = True
    # ... rest of method
```

This shows all MIDI messages from the controller, useful for comparing:
- What the hardware sends in custom pot mode (e.g., CC 52-59)
- What your code is trying to send via modified eventData
- Whether `handled` flag is being set correctly

## Related Documentation

- `omni_plugin_page.claude.md` - Original attempts to send global CCs using various FL Studio API methods
- `AGENT_HANDOFF_custom-enhancements.md` - Background on the custom CC page feature and previous attempts
