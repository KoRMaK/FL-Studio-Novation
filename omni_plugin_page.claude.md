# Omni CC Page Implementation - Attempt Log

## Goal
Implement a second custom page (Omni CC) that sends CC 52-59 globally to FL Studio, allowing any plugin to receive and respond to these CC messages (not tied to a specific channel/plugin).

## Attempts

### Attempt 1: `device.midiOutMsg()` - WRONG DIRECTION
**Date:** Initial implementation

**Approach:**
```python
status = 0xB0  # CC on MIDI channel 1
device.midiOutMsg(status | (cc_number << 8) | (midi_value << 16))
```

**Result:** Failed - sends MIDI **OUT** to the hardware device, not INTO FL Studio

**Why it failed:** `midiOutMsg()` sends data to the physical MIDI output port (back to the Launchkey), not to FL Studio's internal processing.

---

### Attempt 2: `device.processMIDICC()` with Duck-Typed Object - CRASH
**Date:** Second attempt

**Approach:**
```python
class CCEvent:
    def __init__(self):
        self.status = 0xB0
        self.data1 = cc_number
        self.data2 = midi_value
        self.midiChan = 0
        self.controlNum = cc_number
        self.controlVal = midi_value
        self.handled = False

device.processMIDICC(CCEvent())
```

**Result:** **CRASHED FL STUDIO**

**Why it failed:** `processMIDICC()` requires a real FL Studio `eventData` object from the `OnMidiMsg` callback, not a duck-typed Python class. FL Studio likely performs type checking or accesses internal C++ structures that our class doesn't have.

---

### Attempt 3: `general.processRECEvent()` to Channel 0 - FALLBACK
**Date:** After crash

**Approach:**
```python
channel = 0  # Use channel 0 as "omni convention"
rec_event_parameter = cc_number + channels.getRecEventId(channel)
rec_midi_value = int((midi_value / 127.0) * midi.FromMIDI_Max)
mask = midi.REC_MIDIController
general.processRECEvent(rec_event_parameter, rec_midi_value, mask)
```

**Result:** Not tested (moved to attempt 4 before testing)

**Theory:** This would send CC to channel 0, creating a convention where "omni" CC is always channel 0. Users would MIDI-learn from channel 0 to any parameter.

**Limitation:** Still channel-specific, not truly "omni" - requires channel 0 to exist and be used as the convention.

---

### Attempt 4: `device.forwardMIDICC()` with `forwardTo = 0` - DID NOT WORK
**Date:** Final attempt

**Documentation Reference:** https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm

**Approach:**
```python
cc_number = 52 + index
midi_value = int(position * 127)

# Construct composite MIDI message: status + (data1 << 8) + (data2 << 16) + (port << 24)
status = 0xB0  # CC on MIDI channel 1
port = 0
message = status + (cc_number << 8) + (midi_value << 16) + (port << 24)

# Forward to all plugins (forwardTo = 0)
device.forwardMIDICC(message, 0)
```

**Expected behavior:** `forwardTo = 0` should send CC to **all plugins** according to documentation

**Result:** Did not work (specifics of failure not documented)

**Possible reasons:**
1. `forwardMIDICC()` may only work when called from within `OnMidiMsg` callback with real incoming MIDI
2. Port mismatch - documentation states "the midi input port of plugin must equal the port specified in message"
3. Message format may be incorrect
4. FL Studio may filter/ignore forwarded messages that don't originate from actual MIDI input

---

## Analysis

### What We Learned

1. **`device.midiOutMsg()`** - Sends MIDI OUT to hardware, not useful for our purpose
2. **`device.processMIDICC()`** - Requires real `eventData` objects, cannot be duck-typed
3. **`general.processRECEvent()`** - Works but is channel-specific
4. **`device.forwardMIDICC()`** - Documented to forward to all plugins but didn't work in practice

### The Core Problem

FL Studio's Python MIDI API appears to be designed primarily for:
- **Receiving** MIDI from hardware → processing in FL Studio
- **Sending** MIDI to hardware output

But **not** for:
- **Generating** internal MIDI messages that simulate hardware input

### Open Questions

1. Is there a way to truly send "global" CC in FL Studio that any plugin can receive?
2. Does `forwardMIDICC()` only work in specific contexts (e.g., inside `OnMidiMsg`)?
3. Is the channel-based architecture (via `processRECEvent`) the only viable option?
4. Could we store/replay an actual `eventData` object from a real MIDI event?

### Possible Next Steps

1. **Test `processRECEvent()` to channel 0** - Use as "omni convention"
2. **Research FL Studio MIDI architecture** - Check if global CC is even possible
3. **Ask Image-Line support** - Clarify the intended use of `forwardMIDICC()`
4. **Intercept real MIDI** - Store an actual `eventData` from hardware and replay it with modified values
5. **Use link to controller** - Document that users should use FL Studio's built-in MIDI learn instead

---

## Current Implementation Status

**Plugin CC Page (works):**
- Sends CC 4096+52 through CC 4096+59
- Uses `plugins.setParamValue()` to send to specific plugin
- Functions correctly

**Omni CC Page (does not work):**
- Intended to send CC 52-59 globally
- Current implementation uses `device.forwardMIDICC(message, 0)`
- Does not achieve desired effect

**Code Location:**
- `script/device_independent/view/plugin_parameter_view.py::_send_custom_cc_omni()`
