from script.constants import Faders, Pots
from util.enum import Enum


class PadLayout(Enum):
    Custom = 0
    Drum = 1
    Session = 2


class PotLayout(Enum):
    Volume = 1
    Pan = 3


class FaderLayout(Enum):
    Volume = 1
    SendA = 4


class Constants(Enum):
    DisplayedDeviceName = "Launchkey"
    MinimumFirmwareVersion = (0, 2, 0, 7)

    NovationProductId = 0x0F

    LightingTargetNote = 0x60
    LightingTargetCC = 0x50
    LightingTypeStatic = 0x00
    LightingTypeRGB = 0x03

    NotesForPadLayout = {
        PadLayout.Drum: [40, 41, 42, 43, 48, 49, 50, 51, 36, 37, 38, 39, 44, 45, 46, 47],
    }

    PadForLayoutNote = {**{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Drum])}}


class Button(Enum):
    MixerLeft = 1
    MixerRight = 2
    ChannelRackUp = 3
    ChannelRackDown = 4
    TransportPlay = 9
    TransportStop = 10
    TransportRecord = 11
    Metronome = 14
    Undo = 15


class SurfaceEvent(Enum):
    EnterDawMode = 0x9F, 0x0C, 0x7F
    ExitDawMode = 0x9F, 0x0C, 0x00
    PadLayout = 0xBF, 0x03
    PotLayout = 0xBF, 0x09
    FaderLayout = 0xBF, 0x0A
    PotFirst = 0xBF, 0x15
    PotLast = 0xBF, 0x22
    FaderFirst = 0xBF, 0x35
    FaderLast = 0xBF, 0x3D
    ButtonMixerRight = 0xBF, 0x66
    ButtonMixerLeft = 0xBF, 0x67
    ButtonTransportPlay = 0xBF, 0x73
    ButtonTransportStop = 0xBF, 0x74
    ButtonTransportRecord = 0xBF, 0x75
    ButtonChannelRackUp = 0xBF, 0x6A
    ButtonChannelRackDown = 0xBF, 0x6B
    ButtonMetronome = 0xBF, 0x4C
    ButtonUndo = 0xBF, 0x4D


FunctionToButton = {
    "MixerBankRight": Button.MixerRight,
    "MixerBankLeft": Button.MixerLeft,
    "SelectPreviousChannel": Button.ChannelRackUp,
    "SelectNextChannel": Button.ChannelRackDown,
    "TransportTogglePlayPause": Button.TransportPlay,
    "TransportStop": Button.TransportStop,
    "TransportToggleRecording": Button.TransportRecord,
    "ToggleMetronome": Button.Metronome,
    "Undo": Button.Undo,
}

ButtonToLedIndex = {
    Button.ChannelRackUp: 0x6A,
    Button.ChannelRackDown: 0x6B,
}

PotIndexToControlIndex = {
    index: Pots.FirstControlIndex.value + control for index, control in enumerate(range(Pots.Num.value))
}

FaderIndexToControlIndex = {
    index: Faders.FirstControlIndex.value + control for index, control in enumerate(range(Faders.Num.value))
}


class LaunchkeyProductDefs:
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
        return False

    def ForwardButtonLedGivenShift(self, button, shift_pressed):
        return True
