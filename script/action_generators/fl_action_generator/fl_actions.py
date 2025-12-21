from util.plain_data import PlainData


@PlainData
class OnRefreshAction:
    flags: int


@PlainData
class PlayingStepChangedAction:
    step: int


@PlainData
class AllMixerTracksChangedAction:
    pass


@PlainData
class TimerEventAction:
    pass


@PlainData
class ChannelSelectionToggleAction:
    any_channel_selected: bool


@PlainData
class TempoChangedAction:
    pass


@PlainData
class FirstTimeConnectedAction:
    pass


@PlainData
class DeviceInteractionResumedAction:
    pass


@PlainData
class DeviceInteractionSuspendedAction:
    pass
