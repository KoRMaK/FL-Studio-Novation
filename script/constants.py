from util.enum import Enum
from util.plain_data import PlainData


class DeviceId(Enum):
    FLkey37 = 0
    FLkeyMini = 1
    LaunchkeyMini = 2
    Launchkey = 3
    Launchkey88 = 4
    FLkey49 = 5
    FLkey61 = 6


class ValidationState(Enum):
    Idle = 0
    InProgress = 1
    Success = 2
    Failure = 3


class Pads(Enum):
    Num = 16


class Pots(Enum):
    FirstControlIndex = 0
    Num = 8


class Faders(Enum):
    FirstControlIndex = 100
    NumRegularFaders = 8
    MasterFaderIndex = 8
    Num = 9


class SoloMuteEditState(Enum):
    SingleTrackSolo = 0
    SingleTrackSoloMomentary = 1
    Mute = 2
    Suspended = 3


class MixerSoloMuteMode(Enum):
    Mute = 0
    Solo = 1


class ChannelSoloMuteMode(Enum):
    Mute = 0
    Solo = 1


class PatternSelectBank(Enum):
    StepsPerBankingIncrement = 8
    NumPerBank = 16


class ChannelNavigationSteps(Enum):
    Bank = 8


class ChannelNavigationMode(Enum):
    Single = 0
    Bank = 1


class Notes(Enum):
    Default = 60
    Min = 0
    Max = 127


class HighlightDuration(Enum):
    WithoutEnd = -1
    Default = 3000


class ScrollingSpeed(Enum):
    Default = 0
    Slow = 1


class ButtonFunction(Enum):
    Quantise = 0
    Undo = 1
    Redo = 2
    DumpScoreLog = 3


class LedLightingType(Enum):
    Static = 0
    Pulsing = 1
    RGB = 2


class PatternSelectionMethod(Enum):
    Explicit = 0
    ThroughNew = 1
    ThroughClone = 2


class ArrowButtonChangeDirection(Enum):
    Decrement = 0
    Increment = 1


class SelectedSequencerStepState:
    def __init__(self, *, edited=False, toggled=False):
        self.edited = edited
        self.toggled = toggled


class SequencerStepEditGroup:
    def __init__(self):
        self.edited = False
        self._steps = []
        self.displayed_step_edit_parameter = StepEditParameters.Velocity.value.index

    def get_steps(self):
        return self._steps

    def add_step(self, step):
        self._steps.append(step)

    def remove_step(self, step):
        self._steps.remove(step)
        if len(self._steps) == 0:
            self.edited = False

    def remove_all_steps(self):
        self._steps.clear()
        self.edited = False


class SequencerStepEditState(Enum):
    EditIdle = 0
    EditWaiting = 1
    EditQuick = 2
    EditLatch = 3


class PluginParameterType(Enum):
    Plugin = 0
    Channel = 1


class StepEditParameters(Enum):
    @PlainData
    class Parameter:
        index: int
        minimum: int
        maximum: int
        is_bipolar: bool

    Pitch = Parameter(index=0, minimum=30, maximum=90, is_bipolar=False)
    Velocity = Parameter(index=1, minimum=0, maximum=128, is_bipolar=False)
    Release = Parameter(index=2, minimum=0, maximum=128, is_bipolar=False)
    PitchFine = Parameter(index=3, minimum=0, maximum=240, is_bipolar=True)
    Pan = Parameter(index=4, minimum=0, maximum=128, is_bipolar=True)
    ModX = Parameter(index=5, minimum=0, maximum=255, is_bipolar=True)
    ModY = Parameter(index=6, minimum=0, maximum=255, is_bipolar=True)
    Shift = Parameter(index=7, minimum=0, maximum=22, is_bipolar=False)


class SysEx(Enum):
    MessageHeader = [0x00, 0x20, 0x29, 0x02]
    DeviceEnquiryRequest = [0x7E, 0x7F, 0x06, 0x01]
    DeviceEnquiryResponseHeader = [0x7E, 0x00, 0x06, 0x02, 0x00, 0x20, 0x29]


PluginsWithExplicitlyDisabledPresetNavigation = {"Slicex"}

Scales = {
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "major_pentatonic": [0, 2, 4, 7, 9],
}

# MODO DRUM pad-to-MIDI-note mapping
# Customize this list to match your MODO DRUM kit layout
# Default mapping uses standard drum MIDI note assignments
# ModoDrumPadMapping = [
#     36,  # Pad 0  -> C1  (Kick)
#     38,  # Pad 1  -> D1  (Snare)
#     42,  # Pad 2  -> F#1 (Closed Hi-Hat)
#     46,  # Pad 3  -> A#1 (Open Hi-Hat)
#     41,  # Pad 4  -> F1  (Low Tom)
#     43,  # Pad 5  -> G1  (Low-Mid Tom)
#     45,  # Pad 6  -> A1  (Mid Tom)
#     47,  # Pad 7  -> B1  (High Tom)
#     48,  # Pad 8  -> C2  (High Tom Alt)
#     50,  # Pad 9  -> D2  (High Tom Alt 2)
#     49,  # Pad 10 -> C#2 (Crash 1)
#     51,  # Pad 11 -> D#2 (Ride)
#     52,  # Pad 12 -> E2  (China)
#     53,  # Pad 13 -> F2  (Ride Bell)
#     54,  # Pad 14 -> F#2 (Tambourine)
#     55,  # Pad 15 -> G2  (Splash)
# ]

ModoDrumPadMapping = [
     40,  # Pad  0 -> Pad 4
     38,  # Pad  1 -> Pad 5
     44,  # Pad  2 -> Pad 6
     65,  # Pad  3 -> Pad 7
     68,  # Pad  4 -> Pad 12
     29,  # Pad  5 -> Pad 13
     73,  # Pad  6 -> Pad 14
     71,  # Pad  7 -> Pad 15
     63,  # Pad  8 -> Pad 0
     36,  # Pad  9 -> Pad 1
     42,  # Pad 10 -> Pad 2
     35,  # Pad 11 -> Pad 3
     74,  # Pad 12 -> Pad 8
     76,  # Pad 13 -> Pad 9
     77,  # Pad 14 -> Pad 10
     79,  # Pad 15 -> Pad 11
]

# MODO DRUM pad color mapping (RGB tuples)
# Customize this to set static colors for each pad
# If not provided, colors will be read from the plugin or use default orange
# Use the dump_fpc_layout.py script to generate this from your FPC kit
pad_red = (153, 96, 77)
pad_orange = (153, 125, 77)
pad_blue = (77, 134, 153)
pad_green = (96, 153, 77)
pad_dark_green = (77, 153, 86)
ModoDrumPadColors = {
    # Example (uncomment and customize):
    #0: pad_blue,   # Pad 0 - Kick (orange)
    # 1: (128, 255, 64),   # Pad 1 - Snare (green)
    # 2: (64, 128, 255),   # Pad 2 - Hi-Hat (blue)
    # ... etc
    0: pad_blue, # snare rim
    1: pad_blue, # snare hit
    2: pad_dark_green, # half hihat
    3: pad_dark_green, # pedal hi hat
    4: pad_green, # crash
    5: pad_green, # splash
    6: pad_blue, # ride
    7: pad_dark_green, # open hihat
    8: pad_blue, # snare side
    9: pad_red, # kick 1
    10: pad_green, # closed hihsy
    11: pad_orange, # kick 2
    12: pad_orange, # hi tom
    13: pad_orange, # mid tom
    14: pad_orange, # lo tom
    15: pad_orange, # floor tom
}

# To populate this, run dump_fpc_layout.py in FL Studio and copy the output