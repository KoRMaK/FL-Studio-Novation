# Custom Enhancements Branch - Agent Handoff Document

**Branch Comparison:** `origin/oem` → `custom-enhancements`
**Total Changes:** 40 files, +8277 insertions, -122 deletions
**Commits:** 33 commits
**Last Updated:** 2026-02-14

---

## Executive Summary

The `custom-enhancements` branch extends the OEM Novation Launchkey/FLkey integration with significant UX improvements focused on **independent channel selection**, **plugin parameter pagination**, **custom plugin integrations** (MODO DRUM, Arturia Analog Lab), and extensive **user-defined parameter mappings** for dozens of third-party plugins.

The enhancements prioritize **controller-centric workflows** where the hardware can operate semi-independently from FL Studio's UI state, enabling more fluid performance and production workflows.

---

## Interjected notes from a human
  Architecture Flow: How MIDI Events Flow Through The System

  FL Studio (OnMidiIn callback with eventData)
      ↓
  device_novation_lk_daw.py (OnMidiIn in global namespace)
      ↓
  FLToApplicationAdapter.on_midi(fl_event)
      ↓
  SurfaceActionGenerator.handle_midi_event(fl_event)
      ↓
  Dispatches ControlChangedAction (contains: control, position)
      ↓
  PluginParameterView.handle_ControlChangedAction(action)

  The Problem

  - eventData is only available at the top level (OnMidiIn callback in the device file)
  - By the time it reaches PluginParameterView, it's been converted to a ControlChangedAction which only contains control and position - the original eventData is lost
  - There's no existing processMIDICC function in this architecture - the script uses its own action-based architecture instead of FL Studio's device callbacks


script/device_adapters/fl_to_application_adapter/fl_to_application_adapter.py#on_midi used to have a line to set the eventData.handled to True - which was getting
in the way of passing notes onto fl studio. commenting this out allows fl studio to handle  cc messages

## Core Architectural Enhancements

### 1. Independent Channel Selection System
**Files:** `script/device_independent/channel_selection_manager.py` (new)

**Problem Solved:** FL Studio's MIDI scripting API runs in a separate Python context from the DAW's UI. Controllers were previously bound to FL Studio's global channel selection, forcing the UI and controller to stay in sync.

**Solution:** A channel selection manager that marks the controller's selected channel by appending ` | lk` to the channel name. This suffix acts as a communication mechanism between the DAW and the MIDI script.

**Key Features:**
- `get_active_channel()` - Returns controller's selected channel (may differ from FL Studio UI)
- `set_active_channel(index)` - Changes controller focus without changing FL Studio UI
- `select_next_channel()` / `select_previous_channel()` - Navigation
- `sync_with_fl_studio_ui()` - Manually sync controller to DAW
- `is_synced_with_fl_studio_ui()` - Check sync state

**Integration Points:**
- `Default` view: Sends MIDI notes to controller's active channel
- `PluginParameterView`: Controls pots for controller's active channel
- `ModoDrum` view: Sends drum pads to controller's active channel
- All views now accept optional `channel_selection_manager` parameter

**Trade-offs:**
- Marker suffix visible in FL Studio UI (cosmetic)
- Requires manual sync if user changes channel via FL Studio UI

---

### 2. Plugin Parameter Pagination with Visual Feedback
**Files:**
- `script/device_independent/view/plugin_parameter_view.py` (enhanced)
- `script/device_independent/view/default.py` (pad indicator integration)
- `script/model.py` (added `plugin_parameter_active_page`)

**Problem Solved:** Plugins like Arturia V Collection instruments have 50+ parameters but controllers only have 8 pots. No way to access parameters beyond the first 8.

**Solution:** Multi-page parameter access with **top-row pad indicators** (pads 0-7) that show and switch between parameter pages.

**Architecture:**
- **Page Calculation:** `(total_params + 8 - 1) // 8` pages + 1 custom page
- **Visual Indicators:**
  - Plugin pages: Blue color family (dim → active → pressed)
  - Custom page (last): Seafoam/teal color family (distinct visual cue)
- **Navigation:** Press top-row pad to switch page instantly
- **Page Types:**
  1. Plugin parameter pages (uses user-defined mappings)
  2. Custom CC page (sends CC 4096+52 through 4096+59)

**User Experience:**
- When plugin has mapped parameters → pads show page indicators
- When plugin has no mappings → pads show normal instrument layout
- Current page highlighted in brighter color
- Pressed pad shows teal/aqua feedback

**Integration:**
- `Default` view checks `_calculate_num_pot_pages()` to decide layout
- `PluginParameterView` handles page switching via `handle_PluginParameterPageChangedAction`
- Model stores `plugin_parameter_active_page` (resets on channel/preset change)

**Custom CC Page:**
- Final page sends CC 4096+52 through CC 4096+59 to selected channel
- Allows real-time modulation of any plugin parameter via MIDI learn
- Uses `plugins.setParamValue()` for channel-specific control

---

### 3. User-Defined Plugin Parameter Mappings
**Files:**
- `user/user_defined_plugin_mappings.py` (3259 lines!)
- `user/example/user_defined_plugin_mappings.py` (examples)

**Problem Solved:** Third-party plugins don't have standardized parameter layouts. Generic CC mappings are unusable for instruments like Analog Lab V, MODO BASS, etc.

**Solution:** Curated, hand-mapped parameter definitions for 30+ plugins covering:
- Arturia V Collection (Analog Lab V, SEM V3, Prophet V3, etc.)
- IK Multimedia (MODO BASS, MODO DRUM)
- U-he (Zebra2, Diva)
- Native Instruments
- And many more

**Mapping Structure:**
```python
{
    "PluginName": [
        PluginParameter(name="Filter Cutoff", parameter_index=123, deadzone_centre=None),
        PluginParameter(name="Resonance", parameter_index=124, deadzone_centre=0.5, deadzone_width=0.1),
        # ...
    ]
}
```

**Features:**
- **Meaningful Names:** "Filter Cutoff" instead of "Param 123"
- **Deadzone Support:** Center-detent behavior for bidirectional controls (pan, pitch, etc.)
- **Pagination:** Parameters automatically paginated across multiple 8-pot pages
- **Extensible:** Users can add their own mappings

**Coverage Examples:**
- Analog Lab V: 24 parameters (3 pages)
- MODO BASS: 32 parameters (4 pages)
- SEM V3: 40+ parameters (5+ pages)

---

## Plugin-Specific Integrations

### 4. MODO DRUM Integration
**Files:**
- `script/device_independent/view/modo_drum.py` (new, 159 lines)
- `script/constants.py` (added `ModoDrumPadMapping` and `ModoDrumPadColors`)

**Architecture:**
- Custom view class with **static pad-to-MIDI-note mapping**
- Unlike FPC (which queries plugin), uses predefined layout for predictability
- Supports custom color mapping for visual feedback

**Customization:**
```python
ModoDrumPadMapping = [
    40,  # Pad 0 -> Snare Rim
    63,  # Pad 1 -> Snare Hit
    # ... 16 total
]

ModoDrumPadColors = {
    0: (77, 134, 153),  # Blue for snare
    9: (153, 96, 77),   # Red for kick
    # ...
}
```

**Features:**
- 16-pad layout (4x4 grid)
- Static MIDI note assignment (no plugin queries needed)
- RGB color mapping for visual organization
- Fallback to plugin colors or default orange
- Independent channel selection support

**Integration Point:**
- Application detects "MODO DRUM" plugin name
- Switches to `ModoDrum` view automatically
- Works on both Launchkey and FLkey

---

### 5. Arturia Plugin Preset Navigation
**Files:**
- `script/device_independent/view/analog_lab_preset_button_view.py` (new, 98 lines)
- Enhanced support in `script/device_independent/view/default.py`

**Problem Solved:** Arturia plugins (Analog Lab V, SEM V3) have hundreds of presets. No way to browse them from controller.

**Solution:** Repurpose mixer bank buttons (Launchkey) or plugin page buttons (FLkey) for preset navigation when Arturia plugin is selected.

Note from human: This code is vestigial, I've left it in place but am no longer using it and am leaving it for now. 
Analog lab preset navigation is now offered and used in practice via the custom pot page and the last two knobs.

**Button Mappings:**
- **Launchkey:** MixerBankLeft/Right → Previous/Next preset
- **FLkey:** ChannelPluginPageLeft/Right → Previous/Next preset

**Technical Implementation:**
- Sends MIDI CC 28 (previous) / CC 29 (next) to selected channel
- Calls `ui.up()` / `ui.down()` for UI navigation
- Only active when Arturia plugin is selected
- Supports multiple button sets per device

**Supported Plugins:**
- Analog Lab V
- SEM V3
- Extensible to other Arturia V Collection instruments

---

### 6. Mixer Bank Button View
**Files:**
- `script/device_independent/view/mixer_bank_button_view.py` (new, 42 lines)

**Purpose:** Enables mixer bank navigation via dedicated hardware buttons (Launchkey only)

**Features:**
- Left/Right buttons navigate mixer tracks
- Defers to `AnalogLabPresetButtonView` when Arturia plugin is selected
- Clean separation of concerns (mixer nav vs preset nav)

---

## FL Studio API Enhancements

### 7. Group Channel Support
**Files:** `script/fl.py` (extensive updates)

**Changes:** All FL API wrapper methods now accept optional `group_channel` parameter:

**Updated Methods:**
- `send_note_on(note, velocity, group_channel=None)`
- `send_note_off(note, group_channel=None)`
- `channel.set_parameter_value(param, value, group_channel=None)`
- `channel.set_pitch(value, group_channel=None)`
- `plugin.set_parameter_value(param, value, group_channel=None)`
- `reset_parameter_pickup(param, group_channel=None)`

**Impact:** Enables independent channel selection without breaking existing code (backward compatible via default `None` values)

---

## Color System Enhancements

### 8. Plugin Page Indicator Colors
**Files:** `script/colours.py`

**New Colors:**
- `plugin_page_indicator` - Deep blue (dim)
- `plugin_page_indicator_active` - Brighter blue (current page)
- `plugin_page_indicator_pressed` - Teal/aqua (pressed feedback)
- `custom_page_indicator` - Dim seafoam (custom CC page)
- `custom_page_indicator_active` - Chill blue (active custom page)
- `custom_page_indicator_pressed` - Bright teal (pressed custom page)

**Design Philosophy:** Blue family for plugin pages, seafoam/teal for custom page (distinct visual language)

---

## Launchkey-Specific Enhancements

### 9. Drum Pad Layout Improvements
**Files:** `script/device_dependent/LaunchkeyRange/drum_pad_layout_manager.py`

**Changes:**
- Updated to use independent channel selection
- Integration with `ChannelSelectionManager`
- Sends pads to controller's active channel instead of FL Studio's selected channel

---

## Constants and Configuration

### 10. New Constants
**Files:** `script/constants.py`

**Added:**
- `Pots` enum (already existed, now heavily used)
- `ModoDrumPadMapping` - 16-element MIDI note mapping
- `ModoDrumPadColors` - RGB color dictionary for pads

**Added:**
- `PluginParameterPageChangedAction` - Dispatched when page changes
- Integration into action dispatcher system

---

## Stashed Proposals (Not Implemented)

### 11. Session Mode Proposal
**File:** `session_proposal.claude.md`

**Status:** Defined but not implemented

**Summary:**
- Hardware "Session" button exists but does nothing
- Proposal to implement `SessionPadLayoutManager` for clip launching
- Would enable pattern/playlist triggering from pads
- Integration with FL Studio's playlist system
- 16-pad grid for clip launching with LED feedback

**Blockers:** Requires implementing full session view behavior (significant scope)

---

### 12. Omni CC Page Attempts
**File:** `omni_plugin_page.claude.md`

**Status:** Attempted but **did not work**

**Goal:** Send CC 52-59 globally to all plugins (not channel-specific)

**Attempts:**
1. `device.midiOutMsg()` - ❌ Sends to hardware, not FL Studio
2. `device.processMIDICC()` with duck-typed object - ❌ **Crashed FL Studio**
3. `general.processRECEvent()` to channel 0 - ⚠️ Works but channel-specific
4. `device.forwardMIDICC(message, 0)` - ❌ Did not work

**Conclusion:** FL Studio's Python MIDI API doesn't support generating global MIDI messages. Current implementation uses channel-specific CC (4096+52-59) instead.

**Lesson:** FL Studio MIDI API is designed for receiving/forwarding MIDI, not generating internal MIDI events.

---

## Device Support

### 13. Device Configuration Files
**Files:** All `device_novation_*.py` files updated

**Changes:**
- Added `channel_selection_manager` integration
- Updated imports and initialization
- Consistent across FLkey Mini, FLkey 37, FLkey 49, FLkey 61, Launchkey ranges

---

## Debugging and Development

### 14. Print Logger Cleanup
**Commit:** `07e8e6d - Clean up print loggers`

**Changes:**
- Removed excessive debug print statements
- Kept strategic logging for preset navigation
- Cleaner console output during operation

---

## Code Quality

### 15. Removed Obsolete Code
**Examples:**
- Removed deference to `AnalogLabPadView` (no longer exists)
- Cleaned up commented-out code
- Removed arrow key pot pagination (obsolete)

---

## Integration Strategies

### Key Design Patterns

#### 1. Optional Dependency Injection
All views accept `channel_selection_manager=None` parameter:
- If provided → use independent channel selection
- If `None` → fall back to FL Studio global selection
- **Benefit:** Backward compatibility with OEM behavior

#### 2. Model-Driven State
`script/model.py` stores shared state:
- `plugin_parameter_active_page` - Current pot page
- `selected_channel_index` - Controller's active channel
- Prevents state fragmentation across views

#### 3. Action-Based Communication
All state changes dispatch actions:
- `PluginParameterPageChangedAction` - Page switched
- `ChannelSelectAction` - Channel changed
- Views listen and react accordingly

#### 4. View Composition
Complex behaviors built from multiple views:
- `AnalogLabPresetButtonView` + `MixerBankButtonView` = Context-aware buttons
- `Default` view + `PluginParameterView` = Pads show page indicators

---

## Migration from OEM

### Breaking Changes
None - all enhancements are **opt-in** via initialization parameters.

### Opt-In Features
1. Pass `channel_selection_manager` to enable independent selection
2. Populate `user_defined_plugin_mappings.py` to enable pagination
3. Add MODO DRUM mappings to `constants.py` for custom layouts

### Backward Compatibility
- Without user-defined mappings → behaves like OEM
- Without channel selection manager → uses FL Studio global selection
- Existing OEM workflows unchanged

---

## File Change Summary

### New Files (6)
1. `script/device_independent/channel_selection_manager.py` - Independent channel selection
2. `script/device_independent/view/analog_lab_preset_button_view.py` - Arturia preset nav
3. `script/device_independent/view/mixer_bank_button_view.py` - Mixer bank buttons
4. `script/device_independent/view/modo_drum.py` - MODO DRUM integration
5. `omni_plugin_page.claude.md` - Failed omni CC attempts (documentation)
6. `session_proposal.claude.md` - Session mode proposal (not implemented)

### Heavily Modified Files (10)
1. `script/device_independent/view/default.py` - Page indicators, channel selection
2. `script/device_independent/view/plugin_parameter_view.py` - Pagination, custom CC page
3. `script/fl.py` - Group channel support across all methods
4. `script/constants.py` - MODO DRUM mappings/colors
5. `script/colours.py` - Page indicator colors
6. `user/user_defined_plugin_mappings.py` - 3259 lines of plugin defs
7. `script/device_dependent/Launchkey/application.py` - Manager integration
8. `script/device_dependent/LaunchkeyRange/drum_pad_layout_manager.py` - Channel selection
9. `script/model.py` - State management
10. `script/actions.py` - New action types

### Updated Files (24)
- All device configuration files (`device_novation_*.py`)
- MIDI bypass logic
- Product definitions
- View base classes
- Various screen views

---

## Agent Guidelines

### When Extending This Code

#### DO:
- ✅ Use `channel_selection_manager` for channel operations
- ✅ Pass `group_channel` to FL API methods when available
- ✅ Dispatch actions for state changes
- ✅ Add user-defined mappings for new plugins
- ✅ Use existing color schemes for consistency
- ✅ Test with and without optional managers (backward compatibility)

#### DON'T:
- ❌ Break backward compatibility (always use optional parameters)
- ❌ Attempt to generate global MIDI messages (doesn't work - see omni_plugin_page.claude.md)
- ❌ Call `ui.setHintMsg()` excessively (causes FL Studio lag)
- ❌ Use `device.midiOutMsg()` for internal FL Studio communication
- ❌ Duck-type FL Studio objects (causes crashes)

### Common Tasks

#### Adding a New Plugin Mapping
1. Identify plugin name via print debugging
2. Determine parameter indices (use MIDI learn + observation)
3. Add to `user/user_defined_plugin_mappings.py`:
```python
"Plugin Name": [
    PluginParameter(name="Param 1", parameter_index=0),
    # ...
]
```
4. Test pagination works automatically

#### Adding a New View
1. Inherit from `View` base class
2. Accept optional `channel_selection_manager=None`
3. Use `_get_selected_channel()` helper pattern
4. Implement `_on_show()` and `_on_hide()`
5. Register action handlers via `handle_ActionName()`

#### Debugging Channel Selection
- Check for ` | lk` suffix in channel name
- Use `is_synced_with_fl_studio_ui()` to verify state
- Print `get_active_channel()` vs `fl.selected_channel()`

---

## Known Limitations

### 1. Channel Name Marker Visibility
The ` | lk` suffix is visible in FL Studio UI. Trade-off for cross-context communication.

### 2. No Global MIDI Messages
Cannot send "omni" CC messages to all plugins simultaneously. Custom CC page sends to selected channel only.

### 3. Manual Sync Required
If user changes channel via FL Studio UI, controller doesn't auto-sync. User must press channel select button to resync.

### 4. Session Mode Not Implemented
Hardware button exists but functionality is stubbed. Requires significant development (see `session_proposal.claude.md`).

### 5. MODO DRUM Requires Manual Mapping
Static mapping must be updated in `constants.py` for each kit. No automatic detection like FPC.

---

## Testing Checklist

### Independent Channel Selection
- [ ] Select channel via controller buttons
- [ ] Verify ` | lk` marker appears in channel name
- [ ] Play notes - should go to marked channel
- [ ] Change channel in FL Studio UI - controller shouldn't follow
- [ ] Press channel select to resync

### Plugin Parameter Pagination
- [ ] Load plugin with user-defined mapping (e.g., Analog Lab V)
- [ ] Top row pads show blue page indicators
- [ ] Press different page pads - pots control different parameters
- [ ] Last page (seafoam) sends custom CCs (4096+52-59)
- [ ] MIDI learn from custom page works

### MODO DRUM
- [ ] Load MODO DRUM plugin
- [ ] Pads trigger correct drum sounds
- [ ] Pad colors match `ModoDrumPadColors` mapping
- [ ] Independent channel selection works with MODO DRUM

### Arturia Preset Navigation
- [ ] Load Analog Lab V
- [ ] Mixer bank buttons (LK) or plugin page buttons (FLkey) change presets
- [ ] Preset name updates in FL Studio UI
- [ ] Works with independent channel selection

---

## Performance Considerations

### Memory
- User-defined mappings add ~200KB to script memory
- Negligible impact on FL Studio performance

### CPU
- Action dispatching is lightweight
- No continuous polling (event-driven architecture)
- Rate limiting on CC messages prevents FL Studio overload

### Latency
- Independent channel selection adds no latency (name suffix is async)
- Page switching is instant (no FL Studio API calls)
- Preset navigation uses UI automation (slight delay expected)

---

## Future Enhancement Ideas

### Not Implemented (Potential Additions)
1. **Session Mode** - Full clip launching system (see `session_proposal.claude.md`)
2. **Macro Mappings** - User-definable CC → multi-parameter control
3. **Preset Save/Load** - Store/recall pot mappings per project
4. **Auto-Detect Plugin Parameters** - Scan plugin and auto-generate mappings
5. **Multi-Page Drum Kits** - Bank switching for MODO DRUM (like FPC)

---

## Version History

### v2.0 - Custom Enhancements (Current)
- Independent channel selection
- Plugin parameter pagination
- MODO DRUM integration
- Arturia preset navigation
- 30+ plugin mappings
- Custom CC page

### v1.0 - OEM (Baseline)
- Basic Launchkey/FLkey integration
- FPC drum pad support
- Standard channel/mixer control
- No pagination
- No independent selection

---

## Contact and Support

### Documentation
- `omni_plugin_page.claude.md` - Failed attempts log (what NOT to do)
- `session_proposal.claude.md` - Future feature proposal
- `user/example/user_defined_plugin_mappings.py` - Mapping examples

### Agent Notes
This branch represents ~2 months of iterative development with extensive trial-and-error on FL Studio's MIDI API. The stashed `.claude.md` files document what **doesn't work** - use them to avoid repeating failed attempts.

Key insight: FL Studio's Python MIDI API is asymmetric - great for receiving/forwarding MIDI, limited for generating internal messages.

---

**End of Handoff Document**
