from script.constants import Faders, Pots
from util.enum import Enum

__all__ = ["FLkeyProductDefs"]


class PadLayout(Enum):
    ChannelRack = 2
    Instrument = 9
    Sequencer = 11
    Patterns = 12
    ScaleChord = 3
    UserChord = 4
    Custom = 5


class PotLayout(Enum):
    MixerVolume = 1
    Plugin = 2
    MixerPan = 3
    ChannelVolume = 4
    ChannelPan = 5

    Momentary = 10
    Revert = 127


class FaderLayout(Enum):
    MixerVolume = 1
    Plugin = 2
    ChannelVolume = 4


class Constants(Enum):
    DisplayedDeviceName = "FLkey"
    MinimumApiVersion = 28

    NovationProductId = 0x11

    LightingTargetNote = 0x40
    LightingTargetCC = 0x50
    LightingTypeStatic = 0x00
    LightingTypePulsing = 0x02
    LightingTypeRGB = 0x03

    Scales = {
        0: "minor",
        1: "major",
        2: "dorian",
        3: "mixolydian",
        4: "phrygian",
        5: "harmonic_minor",
        6: "minor_pentatonic",
        7: "major_pentatonic",
    }
    NotesForPadLayout = {
        PadLayout.ChannelRack: [96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119],
        PadLayout.Instrument: [64, 65, 66, 67, 68, 69, 70, 71, 80, 81, 82, 83, 84, 85, 86, 87],
        PadLayout.Sequencer: [32, 33, 34, 35, 36, 37, 38, 39, 48, 49, 50, 51, 52, 53, 54, 55],
        PadLayout.Patterns: [0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23],
    }
    PadForLayoutNote = {
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.ChannelRack])},
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Instrument])},
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Sequencer])},
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Patterns])},
    }


class Button(Enum):
    Shift = 0
    MixerRight = 1
    MixerLeft = 2
    ChannelRackUp = 3
    ChannelRackDown = 4
    PresetUp = 5
    PresetDown = 6
    PresetUpShift = 7
    PresetDownShift = 8
    PageLeft = 9
    PageRight = 10
    TransportPlay = 11
    TransportStop = 12
    TransportRecord = 13
    ScoreLog = 14
    Quantise = 15
    Metronome = 16
    Undo = 17
    Redo = 18
    TapTempo = 19
    SoloMute = 20
    Fader_1 = 21
    Fader_2 = 22
    Fader_3 = 23
    Fader_4 = 24
    Fader_5 = 25
    Fader_6 = 26
    Fader_7 = 27
    Fader_8 = 28
    MixerRightShift = 29
    MixerLeftShift = 30
    ChannelRackUpShift = 31
    ChannelRackDownShift = 32


class SurfaceEvent(Enum):
    EnterDawMode = 0x9F, 0x0C, 0x7F
    ExitDawMode = 0x9F, 0x0C, 0x00
    QueryScaleModeEnabled = 0xBF, 0x2E, 0x00
    QueryScaleType = 0xBF, 0x2F, 0x00
    QueryScaleRoot = 0xBF, 0x30, 0x00
    ScaleModeEnabled = 0xBF, 0x0E
    ScaleTypeChanged = 0xBF, 0x0F
    ScaleRootChanged = 0xBF, 0x10
    PadLayout = 0xBF, 0x03
    PotLayout = 0xBF, 0x09
    PotFirst = 0xBF, 0x15
    PotLast = 0xBF, 0x22
    FaderFirst = 0xBF, 0x35
    FaderLast = 0xBF, 0x3D
    FaderLayout = 0xBF, 0x0A
    ButtonMixerRight = 0xBF, 0x33
    ButtonMixerLeft = 0xBF, 0x34
    ButtonTransportPlay = 0xBF, 0x73
    ButtonTransportStop = 0xBF, 0x74
    ButtonTransportRecord = 0xBF, 0x75
    ButtonScoreLog = 0xBF, 0x76
    ButtonChannelRackUp = 0xB0, 0x68
    ButtonChannelRackDown = 0xB0, 0x69
    ButtonPresetUp = 0xBF, 0x6A
    ButtonPresetDown = 0xBF, 0x6B
    ButtonPageLeft = 0xBF, 0x67
    ButtonPageRight = 0xBF, 0x66
    ButtonShift = 0xB0, 0x6C
    ButtonQuantise = 0xBF, 0x4A
    ButtonMetronome = 0xBF, 0x4B
    ButtonUndo = 0xBF, 0x4C
    ButtonRedo = 0xBF, 0x4D
    ButtonTapTempo = 0xBF, 0x41
    ButtonSoloMute = 0xBF, 0x2D
    ButtonFader_1 = 0xBF, 0x25
    ButtonFader_2 = 0xBF, 0x26
    ButtonFader_3 = 0xBF, 0x27
    ButtonFader_4 = 0xBF, 0x28
    ButtonFader_5 = 0xBF, 0x29
    ButtonFader_6 = 0xBF, 0x2A
    ButtonFader_7 = 0xBF, 0x2B
    ButtonFader_8 = 0xBF, 0x2C


FunctionToButton = {
    "ShiftModifier": Button.Shift,
    "ExitStepEditLatchMode": Button.ChannelRackDown,
    "ChannelPluginPageLeft": Button.PageLeft,
    "ChannelPluginPageRight": Button.PageRight,
    "ChannelPluginOctaveDown": Button.PageLeft,
    "ChannelPluginOctaveUp": Button.PageRight,
    "SequencerStepsPageLeft": Button.PageLeft,
    "SequencerStepsPageRight": Button.PageRight,
    "MixerBankRight": Button.MixerRight,
    "MixerBankLeft": Button.MixerLeft,
    "SelectPreviousMixerTrack": Button.MixerLeftShift,
    "SelectNextMixerTrack": Button.MixerRightShift,
    "SelectPreviousMixerTrackPlugin": Button.ChannelRackUpShift,
    "SelectNextMixerTrackPlugin": Button.ChannelRackDownShift,
    "SelectPreviousChannel": Button.ChannelRackUp,
    "SelectNextChannel": Button.ChannelRackDown,
    "SelectPreviousPreset": Button.PresetUp,
    "SelectNextPreset": Button.PresetDown,
    "SelectNewPattern": Button.PresetUpShift,
    "PreviousPatternBank": Button.PresetUp,
    "NextPatternBank": Button.PresetDown,
    "CloneCurrentPattern": Button.PresetDownShift,
    "TransportTogglePlayPause": Button.TransportPlay,
    "TransportStop": Button.TransportStop,
    "TransportToggleRecording": Button.TransportRecord,
    "Quantise": Button.Quantise,
    "ToggleMetronome": Button.Metronome,
    "Undo": Button.Undo,
    "Redo": Button.Redo,
    "DumpScoreLog": Button.ScoreLog,
    "ShowHighlights": Button.Shift,
    "TapTempo": Button.TapTempo,
    "ToggleSoloMode": Button.SoloMute,
    "ToggleSoloMute_1": Button.Fader_1,
    "ToggleSoloMute_2": Button.Fader_2,
    "ToggleSoloMute_3": Button.Fader_3,
    "ToggleSoloMute_4": Button.Fader_4,
    "ToggleSoloMute_5": Button.Fader_5,
    "ToggleSoloMute_6": Button.Fader_6,
    "ToggleSoloMute_7": Button.Fader_7,
    "ToggleSoloMute_8": Button.Fader_8,
}

ButtonToLedIndex = {
    Button.ChannelRackUp: 0x68,
    Button.ChannelRackUpShift: 0x68,
    Button.ChannelRackDown: 0x69,
    Button.ChannelRackDownShift: 0x69,
    Button.PresetUp: 0x6A,
    Button.PresetUpShift: 0x6A,
    Button.PresetDown: 0x6B,
    Button.PresetDownShift: 0x6B,
    Button.SoloMute: 0x2D,
    Button.Fader_1: 0x25,
    Button.Fader_2: 0x26,
    Button.Fader_3: 0x27,
    Button.Fader_4: 0x28,
    Button.Fader_5: 0x29,
    Button.Fader_6: 0x2A,
    Button.Fader_7: 0x2B,
    Button.Fader_8: 0x2C,
}

PotIndexToControlIndex = {
    index: Pots.FirstControlIndex.value + control for index, control in enumerate(range(Pots.Num.value))
}

FaderIndexToControlIndex = {
    index: Faders.FirstControlIndex.value + control for index, control in enumerate(range(Faders.Num.value))
}


class FLkeyProductDefs:
    def __init__(self):
        self.PadLayout = PadLayout
        self.PotLayout = PotLayout
        self.FaderLayout = FaderLayout
        self.Constants = Constants
        self.Button = Button
        self.SurfaceEvent = SurfaceEvent
        self.FunctionToButton = FunctionToButton
        self.ButtonToLedIndex = ButtonToLedIndex
        self.PotIndexToControlIndex = PotIndexToControlIndex
        self.ControlIndexToPotIndex = {v: k for k, v in self.PotIndexToControlIndex.items()}
        self.FaderIndexToControlIndex = FaderIndexToControlIndex
        self.ControlIndexToFaderIndex = {v: k for k, v in self.FaderIndexToControlIndex.items()}

    def IsShiftButton(self, button):
        return (
            button == Button.PresetUpShift
            or button == Button.PresetDownShift
            or button == Button.ChannelRackUpShift
            or button == Button.ChannelRackDownShift
        )

    def ForwardButtonLedGivenShift(self, button, shift_pressed):
        return self.IsShiftButton(button) == shift_pressed
