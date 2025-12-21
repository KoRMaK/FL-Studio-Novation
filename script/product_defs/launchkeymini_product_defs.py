from script.constants import Pots
from util.enum import Enum


class PadLayout(Enum):
    Custom = 0
    Drum = 1
    Session = 2


class PotLayout(Enum):
    Volume = 1
    Pan = 3


class Constants(Enum):
    DisplayedDeviceName = "Launchkey Mini"
    MinimumFirmwareVersion = (0, 4, 1, 7)

    NovationProductId = 0x0B

    LightingTargetNote = 0x60
    LightingTargetCC = 0x50
    LightingTypeStatic = 0x00
    LightingTypeRGB = 0x03

    NotesForPadLayout = {
        PadLayout.Drum: [40, 41, 42, 43, 48, 49, 50, 51, 36, 37, 38, 39, 44, 45, 46, 47],
    }

    PadForLayoutNote = {**{note: pad for pad, note in enumerate(NotesForPadLayout[PadLayout.Drum])}}


class Button(Enum):
    MixerLeftShift = 1
    MixerRightShift = 2
    SceneLaunch = 4
    StopSoloMute = 6
    TransportPlay = 9
    TransportRecord = 10


class SurfaceEvent(Enum):
    EnterDawMode = 0x9F, 0x0C, 0x7F
    ExitDawMode = 0x9F, 0x0C, 0x00
    PadLayout = 0xBF, 0x03
    PotLayout = 0xBF, 0x09
    PotFirst = 0xBF, 0x15
    PotLast = 0xBF, 0x22
    ButtonMixerRight = 0xBF, 0x66
    ButtonMixerLeft = 0xBF, 0x67
    ButtonTransportPlay = 0xBF, 0x73
    ButtonTransportRecord = 0xBF, 0x75
    ButtonSceneLaunch = 0xB0, 0x68
    ButtonStopSoloMute = 0xB0, 0x69


ButtonToLedIndex = {
    Button.MixerLeftShift: 0x67,
    Button.MixerRightShift: 0x66,
    Button.SceneLaunch: 0x68,
    Button.StopSoloMute: 0x69,
    Button.TransportRecord: 0x75,
    Button.TransportPlay: 0x73,
}

FunctionToButton = {
    "SelectPreviousChannel": Button.SceneLaunch,
    "SelectNextChannel": Button.StopSoloMute,
    "TransportToggleRecording": Button.TransportRecord,
    "TransportTogglePlayStop": Button.TransportPlay,
    "MixerBankRight": Button.MixerRightShift,
    "MixerBankLeft": Button.MixerLeftShift,
}

PotIndexToControlIndex = {
    index: Pots.FirstControlIndex.value + control for index, control in enumerate(range(Pots.Num.value))
}


class LaunchkeyMiniProductDefs:
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
        return False

    def ForwardButtonLedGivenShift(self, button, shift_pressed):
        return True
