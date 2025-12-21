from script.constants import Pots
from util.enum import Enum


class PadLayout(Enum):
    ChannelRack = 2
    Instrument = 9
    Sequencer = 11
    Custom = 5


class PotLayout(Enum):
    MixerVolume = 1
    Plugin = 2
    MixerPan = 3

    Momentary = 10
    Revert = 127


class Constants(Enum):
    DisplayedDeviceName = "FLkey Mini"

    NovationProductId = 0x10

    LightingTargetNote = 0x40
    LightingTargetCC = 0x50
    LightingTypeStatic = 0x00
    LightingTypePulsing = 0x02
    LightingTypeRGB = 0x03

    Scales = {0: "minor", 1: "major", 2: "dorian", 3: "phrygian"}
    NotesForPadLayout = {
        PadLayout.ChannelRack: [96, 97, 98, 99, 100, 101, 102, 103, 112, 113, 114, 115, 116, 117, 118, 119],
        PadLayout.Instrument: [64, 65, 66, 67, 68, 69, 70, 71, 80, 81, 82, 83, 84, 85, 86, 87],
        PadLayout.Sequencer: [32, 33, 34, 35, 36, 37, 38, 39, 48, 49, 50, 51, 52, 53, 54, 55],
    }
    PadForLayoutNote = {
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.ChannelRack])},
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Instrument])},
        **{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Sequencer])},
    }


class Button(Enum):
    Shift = 0
    MixerLeftShift = 1
    MixerRightShift = 2
    ChannelRackUp = 3
    ChannelRackUpShift = 4
    ChannelRackDown = 5
    ChannelRackDownShift = 6
    PresetUpShift = 7
    PresetDownShift = 8
    TransportPlay = 9
    TransportRecord = 10
    TapTempo = 11


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
    ButtonMixerRight = 0xBF, 0x66
    ButtonMixerLeft = 0xBF, 0x67
    ButtonTransportPlay = 0xBF, 0x73
    ButtonTransportRecord = 0xBF, 0x75
    ButtonChannelRackUp = 0xB0, 0x68
    ButtonChannelRackDown = 0xB0, 0x69
    ButtonPresetUp = 0xBF, 0x6A
    ButtonPresetDown = 0xBF, 0x6B
    ButtonShift = 0xB0, 0x6C
    ButtonTapTempo = 0xBF, 0x41


ButtonToLedIndex = {
    Button.MixerLeftShift: 0x67,
    Button.MixerRightShift: 0x66,
    Button.ChannelRackUp: 0x68,
    Button.ChannelRackUpShift: 0x68,
    Button.ChannelRackDown: 0x69,
    Button.ChannelRackDownShift: 0x69,
    Button.PresetUpShift: 0x6A,
    Button.PresetDownShift: 0x6B,
    Button.TransportPlay: 0x73,
    Button.TransportRecord: 0x75,
}

FunctionToButton = {
    "ShiftModifier": Button.Shift,
    "ExitStepEditLatchMode": Button.ChannelRackDown,
    "ChannelPluginPageRight": Button.ChannelRackDownShift,
    "ChannelPluginPageLeft": Button.ChannelRackUpShift,
    "ChannelPluginOctaveDown": Button.ChannelRackDownShift,
    "ChannelPluginOctaveUp": Button.ChannelRackUpShift,
    "SequencerStepsPageLeft": Button.ChannelRackUpShift,
    "SequencerStepsPageRight": Button.ChannelRackDownShift,
    "MixerBankRight": Button.MixerRightShift,
    "MixerBankLeft": Button.MixerLeftShift,
    "SelectPreviousChannel": Button.ChannelRackUp,
    "SelectNextChannel": Button.ChannelRackDown,
    "SelectPreviousPreset": Button.PresetUpShift,
    "SelectNextPreset": Button.PresetDownShift,
    "TransportTogglePlayStop": Button.TransportPlay,
    "TransportToggleRecording": Button.TransportRecord,
    "ShowHighlights": Button.Shift,
    "TapTempo": Button.TapTempo,
}

PotIndexToControlIndex = {
    index: Pots.FirstControlIndex.value + control for index, control in enumerate(range(Pots.Num.value))
}


class FLkeyMiniProductDefs:
    def __init__(self):
        self.PadLayout = PadLayout
        self.PotLayout = PotLayout
        self.Constants = Constants
        self.Button = Button
        self.SurfaceEvent = SurfaceEvent
        self.FunctionToButton = FunctionToButton
        self.ButtonToLedIndex = ButtonToLedIndex
        self.PotIndexToControlIndex = PotIndexToControlIndex

    def IsShiftButton(self, button):
        return (
            button == self.Button.MixerLeftShift
            or button == self.Button.MixerRightShift
            or button == self.Button.ChannelRackUpShift
            or button == self.Button.ChannelRackDownShift
            or button == self.Button.PresetUpShift
            or button == self.Button.PresetDownShift
        )

    def ForwardButtonLedGivenShift(self, button, shift_pressed):
        if (
            button == self.Button.MixerLeftShift
            or button == self.Button.MixerRightShift
            or button == self.Button.PresetUpShift
            or button == self.Button.PresetDownShift
        ):
            return True
        return self.IsShiftButton(button) == shift_pressed
