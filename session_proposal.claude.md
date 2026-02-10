# Launchkey Session View Implementation Proposal

## Current Status

Session view is **defined but not implemented** in the Launchkey integration. The hardware supports it, but the script doesn't handle it.

## What Currently Exists

### 1. Hardware Support
The Launchkey hardware has a physical "Session" button that sends MIDI message `0xBF, 0x03, 0x02` when pressed.

### 2. Enum Definition
In `script/product_defs/launchkey_product_defs.py:5-8`:
```python
class PadLayout(Enum):
    Custom = 0
    Drum = 1
    Session = 2  # Defined but not implemented
```

### 3. Action Handler
The `PadLayoutChangedAction` is dispatched when the user presses the Session button on the hardware via `KeyboardControllerCommonPadLayoutActionGenerator`.

## What's Missing

### No Session Layout Manager
In `script/device_dependent/Launchkey/application.py:146-157`, the `_create_pad_layout_manager()` method only handles Drum mode:

```python
def _create_pad_layout_manager(self, layout):
    if layout == self.product_defs.PadLayout.Drum:
        return DrumPadLayoutManager(...)
    return None  # Session and Custom return None - pads disabled
```

### Current Behavior
- On initialization, the script **forces Drum mode** (`script/device_adapters/device_setup/launchkey_device_setup.py:26-29`)
- If the user presses the Session button on the hardware, the pads become **inactive** because no `SessionPadLayoutManager` exists
- The Launchkey is effectively **locked to Drum mode** for pad functionality

## Implementation Requirements

### 1. Create SessionPadLayoutManager Class
Location: `script/device_dependent/LaunchkeyRange/session_pad_layout_manager.py`

Similar structure to `DrumPadLayoutManager`, but with session-specific behavior:
- 16-pad grid for clip launching
- Integration with FL Studio's playlist/pattern system
- LED feedback for clip states (empty, filled, playing, recording)

### 2. Update Application.py
Add Session case to `_create_pad_layout_manager()`:

```python
def _create_pad_layout_manager(self, layout):
    if layout == self.product_defs.PadLayout.Drum:
        return DrumPadLayoutManager(...)
    if layout == self.product_defs.PadLayout.Session:
        return SessionPadLayoutManager(...)
    return None
```

### 3. Define Session Note Mappings
Add to `script/product_defs/launchkey_product_defs.py`:

```python
NotesForPadLayout = {
    PadLayout.Drum: [40, 41, 42, 43, 48, 49, 50, 51, 36, 37, 38, 39, 44, 45, 46, 47],
    PadLayout.Session: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # Example
}
```

### 4. Implement Session Behavior
Typical session view features:
- **Clip Launching**: Press pad to trigger pattern/playlist clip
- **LED States**:
  - Off: No clip
  - Dim: Clip present but not playing
  - Bright: Clip playing
  - Flashing: Clip recording/queued
- **Scene Launch**: Potentially use arrow buttons to launch full scenes
- **Stop Clips**: Shift + Pad to stop individual clips

### 5. FL Studio API Integration
Leverage existing FL Studio methods:
- `fl.pattern.trigger()` - Launch patterns
- `fl.playlist.get_track_activity()` - Check what's playing
- Pattern/playlist selection methods
- Transport control integration

## Design Considerations

### Grid Layout
4x4 grid (16 pads):
- Rows could represent tracks
- Columns could represent scenes/patterns
- OR: Each pad maps to a specific pattern number

### Navigation
- Use left/right arrow buttons to navigate pages of clips
- Use up/down to scroll through tracks/patterns
- Shift modifiers for additional functions

### Visual Feedback
- Color-code by pattern color
- Brightness indicates state
- Special colors for recording vs playing

## Benefits

1. **Full Hardware Utilization**: Users can access the Session button functionality
2. **Workflow Enhancement**: Clip launching is a core DAW workflow
3. **Consistency**: Matches expected behavior from other Novation integrations
4. **User Choice**: Let users switch between Drum and Session modes freely

## Next Steps

1. Define exact session view behavior (clip launching strategy)
2. Implement `SessionPadLayoutManager` class
3. Add session note mappings to product definitions
4. Test with various FL Studio project configurations
5. Document user-facing behavior
