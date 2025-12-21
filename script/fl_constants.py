from util.enum import Enum


class FlConstants(Enum):
    MaxStepsPerPattern = 512
    FirstPatternIndex = 1
    MasterTrackIndex = 0
    CurrentTrackIndex = 126
    NumMixerEffectPluginSlots = 10


class ChannelType(Enum):
    Sampler = 0
    Hybrid = 1
    Generator = 2
    Layer = 3
    AudioClip = 4
    AutomationClip = 5


class InstrumentPlugin(Enum):
    Fpc = "FPC"
    FruitySlicer = "Fruity Slicer"
    SliceX = "Slicex"


class PluginType(Enum):
    Instrument = 0
    Effect = 1


class DockSide(Enum):
    Left = 0
    Center = 1
    Right = 2


class RefreshFlags(Enum):
    MixerSelection = 1
    MixerControls = 4
    RemoteLinks = 16
    ChannelSelection = 32
    PerformanceLayout = 64
    TransportStatus = 256
    LedUpdate = 256
    Pattern = 1024
    PluginColours = 8192
    PluginNames = 16384
    ChannelGroup = 32768
    ChannelEvent = 65536


class UndoType(Enum):
    PianoRoll = 2


class DirtyChannelUpdateType(Enum):
    New = 0
    Delete = 1
    Replace = 2
    Rename = 3
    Select = 4


class DirtyMixerTrackFlags(Enum):
    AllTracksChanged = -1


class GlobalTransportCommand(Enum):
    Play = 10
    Stop = 11
    Record = 12
    TapTempoEvent = 106
    Metronome = 110
    LoopRecord = 113


class SlicexNoteRange(Enum):
    Min = 0
    Max = 124


class PickupFollowMode(Enum):
    NoPickup = 0
    UsePickup = 1
    FollowUserSetting = 2


class ProjectLoadStatus(Enum):
    LoadStart = 0
    LoadFinished = 100
    LoadFailed = 101


class WindowType(Enum):
    Mixer = 0
    ChannelRack = 1
    Playlist = 2
    PianoRoll = 3
    Browser = 4
    Plugin = 5
    PluginEffect = 6
    PluginGenerator = 7


class ChannelRackDisplayFlags(Enum):
    Steps = 0
    ScrollToView = 2
    Mute = 4
    PanAndVolume = 8
    TrackSend = 16
    Name = 32
    Select = 64


class PatternGroups(Enum):
    AllPatterns = -1
