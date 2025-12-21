import util.math
from script.constants import HighlightDuration
from script.fl_constants import (
    ChannelRackDisplayFlags,
    ChannelType,
    DockSide,
    GlobalTransportCommand,
    PickupFollowMode,
    PluginType,
    UndoType,
    WindowType,
)
from util.decorators import suppress_unsafe_api_error
from util.print import print_to_script_output

try:
    import arrangement
    import channels
    import device
    import general
    import midi
    import mixer
    import patterns
    import plugins
    import transport
    import ui
except ImportError as e:
    print_to_script_output(e)


__all__ = ["FL"]


class Channel:
    def __init__(self, fl):
        self.fl = fl

    def get_type(self, group_channel=None):
        if group_channel is None:
            return ChannelType(channels.getChannelType(channels.selectedChannel()))
        return ChannelType(channels.getChannelType(group_channel))

    def set_parameter_value(self, parameter, value):
        rec_event_parameter = parameter + channels.getRecEventId(channels.selectedChannel())
        value = int(value * midi.FromMIDI_Max)
        mask = midi.REC_MIDIController
        general.processRECEvent(rec_event_parameter, value, mask)

    def set_pitch(self, value):
        """
        value: Normalised pitch value in range 0 to 1
        """
        bipolar_pitch_value = util.math.normalised_unipolar_to_bipolar(value)
        channels.setChannelPitch(channels.selectedChannel(), bipolar_pitch_value)


class Plugin:
    def __init__(self, fl):
        self.fl = fl

    def get_colour(self, group_channel, param_index):
        fpc_pad_colour_param_index = midi.GC_Semitone
        colour_long = plugins.getColor(group_channel, -1, fpc_pad_colour_param_index, param_index)
        b, g, r, a = colour_long.to_bytes(4, "little", signed=True)
        return r, g, b

    def get_note_name(self, group_channel, note):
        note_name_param_index = 2
        return plugins.getName(group_channel, -1, note_name_param_index, note)

    def get_midi_note_for_pad(self, group_channel, pad_index):
        parameter_index_midi_note = 1
        return plugins.getPadInfo(group_channel, -1, parameter_index_midi_note, pad_index)

    def set_parameter_value(self, parameter, value):
        plugins.setParamValue(
            value, parameter, *self.fl.get_selected_plugin_position(), PickupFollowMode.FollowUserSetting.value
        )


class UI:
    def __init__(self, fl):
        self.fl = fl

    @suppress_unsafe_api_error
    def focus_mixer_window(self):
        if not ui.getFocused(WindowType.Mixer.value):
            ui.showWindow(WindowType.Mixer.value)
            ui.setFocused(WindowType.Mixer.value)

    @suppress_unsafe_api_error
    def focus_channel_window(self):
        if not ui.getFocused(WindowType.ChannelRack.value):
            ui.showWindow(WindowType.ChannelRack.value)
            ui.setFocused(WindowType.ChannelRack.value)

    @suppress_unsafe_api_error
    def focus_channel_plugin_window(self):
        channels.showCSForm(channels.selectedChannel(), 1)

    @suppress_unsafe_api_error
    def hide_channel_plugin_window(self, *, channel=None):
        channels.showCSForm(channels.selectedChannel() if channel is None else channel, 0)

    @suppress_unsafe_api_error
    def focus_mixer_plugin_window(self, track_index, slot_index):
        mixer.focusEditor(track_index, slot_index)

    def is_any_plugin_window_focused(self):
        return ui.getFocused(WindowType.Plugin.value)

    def is_any_channel_plugin_window_focused(self):
        return ui.getFocused(WindowType.PluginGenerator.value)

    def set_hint_message(self, message):
        return ui.setHintMsg(message)


class FL:
    def __init__(self):
        self.channel = Channel(self)
        self.plugin = Plugin(self)
        self.ui = UI(self)

    def api_is_unsafe(self):
        try:
            # From API 29
            return general.safeToEdit() != 1
        except AttributeError:
            pass

        try:
            # Fallback from API 24
            # Type error thrown when calling a setter indicates API is unsafe
            ui.setSnapMode(ui.getSnapMode())
        except TypeError:
            return True
        except AttributeError:
            # Back out for older versions
            pass
        return False

    def mixer_track_count(self):
        """
        Final track is the 'current' track, which is a special analysis track that has no
        volume or pan controls. We are not interested in this track as we cannot control it.
        """
        return mixer.trackCount() - 1

    def get_mixer_track_volume_dB(self, track):
        return mixer.getTrackVolume(track, 1)

    def reset_track_volume_pickup(self, track):
        mixer.setTrackVolume(track, mixer.getTrackVolume(track), PickupFollowMode.NoPickup.value)

    def reset_track_pan_pickup(self, track):
        mixer.setTrackPan(track, mixer.getTrackPan(track), PickupFollowMode.NoPickup.value)

    def set_mixer_track_volume(self, track, volume):
        mixer.setTrackVolume(track, volume, PickupFollowMode.FollowUserSetting.value)

    def set_mixer_track_pan(self, track, pan):
        mixer.setTrackPan(track, pan, PickupFollowMode.FollowUserSetting.value)

    def get_mixer_track_name(self, track):
        return mixer.getTrackName(track)

    def toggle_mixer_track_mute(self, track):
        mixer.muteTrack(track)

    def is_mixer_track_mute_enabled(self, track):
        return mixer.isTrackMuted(track)

    def toggle_mixer_track_solo(self, track):
        mixer.soloTrack(track)

    def is_mixer_track_solo_enabled(self, track):
        return mixer.isTrackSolo(track)

    def get_mixer_track_colour(self, track):
        colour_long = mixer.getTrackColor(track)
        b, g, r, a = colour_long.to_bytes(4, "little", signed=True)
        return r, g, b

    def select_mixer_track_exclusively(self, track_index):
        mixer.setActiveTrack(track_index)

    def get_selected_mixer_track(self):
        for track_index in range(self.mixer_track_count()):
            if mixer.isTrackSelected(track_index):
                return track_index

        return None

    def get_channel_volume_dB(self, channel):
        return channels.getChannelVolume(channel, 1)

    def reset_channel_volume_pickup(self, channel):
        channels.setChannelVolume(channel, channels.getChannelVolume(channel), PickupFollowMode.NoPickup.value)

    def reset_channel_pan_pickup(self, channel):
        channels.setChannelPan(channel, channels.getChannelPan(channel), PickupFollowMode.NoPickup.value)

    def reset_parameter_pickup(self, parameter):
        plugins.setParamValue(
            plugins.getParamValue(parameter, *self.get_selected_plugin_position()),
            parameter,
            *self.get_selected_plugin_position(),
            PickupFollowMode.NoPickup.value,
        )

    def set_channel_volume(self, channel, volume):
        channels.setChannelVolume(channel, volume, PickupFollowMode.FollowUserSetting.value)

    def set_channel_pan(self, channel, pan):
        channels.setChannelPan(channel, pan, PickupFollowMode.FollowUserSetting.value)

    def get_channel_name(self, channel):
        return channels.getChannelName(channel)

    def plugin_select_previous_preset(self):
        plugins.prevPreset(*self.get_selected_plugin_position())

    def plugin_select_next_preset(self):
        plugins.nextPreset(*self.get_selected_plugin_position())

    def get_plugin_preset_count(self):
        plugin_position = self.get_selected_plugin_position()
        if plugin_position is None or not plugins.isValid(*plugin_position):
            return 0
        return plugins.getPresetCount(*plugin_position)

    def get_preset_name(self):
        return plugins.getName(*self.get_selected_plugin_position(), 6)

    def selected_channel(self):
        """
        :return: group channel index of selected channel if channel selected
                 None if no channel is selected

        FL API params:
                canBeNone   == 1: None is returned if no channel selected
        """
        group_channel = channels.selectedChannel(1)
        return group_channel if group_channel != -1 else None

    def get_selected_global_channel(self):
        """
        :return: global channel index of selected channel if channel selected
                 None if no channel is selected

        FL API params:
                canBeNone   == 1: None is returned if no channel selected
                offset      == 0: No channel offset
                indexGlobal == 1: Returns global index
        """
        global_channel = channels.selectedChannel(1, 0, 1)
        return global_channel if global_channel != -1 else None

    def channel_count(self):
        return channels.channelCount()

    def get_global_channel(self, group_channel):
        return channels.getChannelIndex(group_channel)

    def select_channel_exclusively(self, channel):
        channels.selectOneChannel(channel)

    def is_any_channel_selected(self):
        return self.selected_channel() is not None

    def plugin_is_valid(self, channel_or_track_index, slot_index=-1):
        return plugins.isValid(channel_or_track_index, slot_index) == 1

    def get_selected_plugin_position(self):
        active_effect_index = mixer.getActiveEffectIndex()
        if active_effect_index is not None:
            return active_effect_index

        selected_channel = self.selected_channel()

        if selected_channel is None:
            return None, -1

        return selected_channel, -1

    def get_selected_plugin_type(self):
        track_or_channel_index, slot_index = self.get_selected_plugin_position()

        if track_or_channel_index is None:
            return None

        if slot_index != -1:
            return PluginType.Effect

        return PluginType.Instrument

    def get_plugin_for_channel(self, group_channel):
        channel_type = self.channel.get_type(group_channel=group_channel)
        if channel_type == ChannelType.Sampler:
            return "Sampler"
        if channel_type == ChannelType.AudioClip:
            return "AudioClip"
        if channel_type == ChannelType.Layer:
            return "Layer"
        if channel_type == ChannelType.Generator and plugins.isValid(group_channel):
            return plugins.getPluginName(group_channel)

        return None

    def get_selected_plugin(self):
        selected_plugin_type = self.get_selected_plugin_type()

        if selected_plugin_type == PluginType.Effect:
            return plugins.getPluginName(*self.get_selected_plugin_position())

        if selected_plugin_type == PluginType.Instrument:
            channel_index, _ = self.get_selected_plugin_position()
            return self.get_plugin_for_channel(channel_index)

        return None

    def send_note_on(self, note, velocity, *, group_channel=None, global_channel=None):
        if global_channel is not None:
            pass
        elif group_channel is not None:
            global_channel = self.get_global_channel(group_channel)
        else:
            global_channel = self.get_selected_global_channel()

        channels.midiNoteOn(global_channel, note, velocity)

    def send_note_off(self, note, *, group_channel=None, global_channel=None):
        if global_channel is not None:
            pass
        elif group_channel is not None:
            global_channel = self.get_global_channel(group_channel)
        else:
            global_channel = self.get_selected_global_channel()

        channels.midiNoteOn(global_channel, note, 0)

    def get_channel_colour(self, group_channel=None):
        if group_channel is None:
            group_channel = self.selected_channel()
        colour_long = channels.getChannelColor(group_channel)
        b, g, r, a = colour_long.to_bytes(4, "little", signed=True)
        return r, g, b

    def transport_toggle_playing(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Play.value, 1, midi.PME_System, midi.GT_Global)

    def transport_toggle_recording(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Record.value, 1, midi.PME_System, midi.GT_Global)

    def toggle_metronome(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Metronome.value, 1)

    def transport_stop(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Stop.value, 1, midi.PME_System, midi.GT_Global)

    def metronome_is_enabled(self):
        return ui.isMetronomeEnabled()

    def transport_is_playing(self):
        return transport.isPlaying()

    def transport_is_paused(self):
        if self.transport_is_playing():
            return False
        mode_absolute_ticks = 2
        return transport.getSongPos(mode_absolute_ticks) != 0

    def transport_is_recording(self):
        return transport.isRecording()

    def get_channel_rack_active_step(self):
        return arrangement.currentTimeHint(0)

    def set_step_active(self, step, active):
        self.store_current_state_in_undo_history(UndoType.PianoRoll.value, "Step seq edit")
        return channels.setGridBit(self.selected_channel(), step, active)

    def get_step_active(self, step):
        return channels.getGridBit(self.selected_channel(), step)

    def store_current_state_in_undo_history(self, undo_type, description):
        general.saveUndo(description, undo_type)

    def undo(self):
        general.undoUp()

    def redo(self):
        general.undoDown()

    def quantise_start_only(self):
        channels.quickQuantize(self.selected_channel(), 1)

    def turn_off_channelrack_steps_highlight(self):
        first_step, first_channel, num_steps, num_channels, duration_ms = 0, 0, 16, 1, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Steps.value,
        )

    def highlight_channelrack_steps(
        self, first_channel, num_channels, first_step, num_steps, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Steps.value,
        )

    def highlight_and_focus_channelrack_steps(
        self, first_channel, num_channels, first_step, num_steps, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Steps.value | ChannelRackDisplayFlags.ScrollToView.value,
        )

    def focus_channelrack_steps(self, first_channel, num_channels, first_step, num_steps):
        duration_ms = 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Steps.value | ChannelRackDisplayFlags.ScrollToView.value,
        )

    def turn_off_channelrack_names_highlight(self):
        first_step, first_channel, num_steps, num_channels, duration_ms = 0, 0, 0, 1, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Name.value,
        )

    def highlight_channelrack_names(
        self, first_channel, num_channels, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        first_step, num_steps = 0, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Name.value,
        )

    def highlight_and_focus_channelrack_names(
        self, first_channel, num_channels, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        first_step, num_steps = 0, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.Name.value | ChannelRackDisplayFlags.ScrollToView.value,
        )

    def turn_off_channelrack_controls_highlight(self):
        first_step, first_channel, num_steps, num_channels, duration_ms = 0, 0, 0, 1, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.PanAndVolume.value,
        )

    def highlight_channelrack_controls(
        self, first_channel, num_channels, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        first_step, num_steps = 0, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.PanAndVolume.value,
        )

    def highlight_and_focus_channelrack_controls(
        self, first_channel, num_channels, *, duration_ms=HighlightDuration.WithoutEnd.value
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt

        first_step, num_steps = 0, 0
        ui.crDisplayRect(
            first_step,
            first_channel,
            num_steps,
            num_channels,
            duration_ms,
            ChannelRackDisplayFlags.PanAndVolume.value | ChannelRackDisplayFlags.ScrollToView.value,
        )

    def highlight_tracks(
        self,
        relative_index_of_first_track_in_dock,
        num_tracks,
        first_track_index,
        last_track_index,
        duration_ms=HighlightDuration.WithoutEnd.value,
    ):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt
        ui.miDisplayDockRect(1 + relative_index_of_first_track_in_dock, num_tracks, DockSide.Center.value, duration_ms)
        if duration_ms > 1:
            # Check against 1 or 0 as mixer highlight does not yet accept 0 as duration
            ui.scrollWindow(0, last_track_index)
            ui.scrollWindow(0, first_track_index)

    def select_pattern(self, pattern_index):
        patterns.jumpToPattern(pattern_index)

    def clone_selected_pattern(self):
        # this is necessary because a pattern that has the red arrow marking which would be returned by
        # patterns.patternNumber() is not always selected.
        if not patterns.isPatternSelected(self.get_selected_pattern_index()):
            self.select_pattern(self.get_selected_pattern_index())
        patterns.clonePattern()

    def get_selected_pattern_index(self):
        return patterns.patternNumber()

    def get_pattern_name(self, pattern_index):
        return patterns.getPatternName(pattern_index)

    def get_pattern_colour(self, pattern_index):
        colour_long = patterns.getPatternColor(pattern_index)
        b, g, r, a = colour_long.to_bytes(4, "little", signed=True)
        return r, g, b

    def is_pattern_default(self, pattern_index):
        return patterns.isPatternDefault(pattern_index)

    def get_last_pattern_index(self):
        return patterns.patternMax()

    def get_number_of_occupied_patterns(self):
        return patterns.patternCount()

    def get_pattern_length_in_steps(self):
        return patterns.getPatternLength(patterns.patternNumber())

    def get_active_pattern_group(self):
        return patterns.getActivePatternGroup()

    def get_patterns_for_active_group(self):
        return patterns.getPatternsInGroup(self.get_active_pattern_group())

    def get_number_of_patterns_in_active_group(self):
        return len(self.get_patterns_for_active_group())

    def get_playing_step_in_current_pattern(self):
        playing_step = mixer.getSongStepPos()
        if playing_step == -1:
            return None
        if playing_step >= self.get_pattern_length_in_steps():
            return None
        return playing_step

    def get_dock_side_for_track(self, track):
        return mixer.getTrackDockSide(track)

    def dump_score_log(self, duration_seconds):
        general.dumpScoreLog(duration_seconds, 1)

    def get_parameter_name(self, parameter):
        return plugins.getParamName(parameter, *self.get_selected_plugin_position())

    def get_parameter_value(self, parameter):
        return plugins.getParamValue(parameter, *self.get_selected_plugin_position())

    def get_parameter_value_as_string(self, parameter):
        return plugins.getParamValueString(parameter, *self.get_selected_plugin_position())

    def send_tap_tempo_event(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.TapTempoEvent.value, 1, midi.PME_System, midi.GT_Global)

    def loop_record_is_active(self):
        return ui.isLoopRecEnabled()

    def toggle_loop_record(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.LoopRecord.value, 1, midi.PME_System, midi.GT_Global)

    def show_graph_editor(self, step, parameter):
        channels.showGraphEditor(False, parameter, step, self.get_selected_global_channel(), 1)

    def hide_graph_editor(self):
        channels.closeGraphEditor(True)

    def set_step_parameter(self, step, parameter, value, *, updateGraphEditor=True):
        channels.setStepParameterByIndex(self.selected_channel(), patterns.patternNumber(), step, parameter, value)
        if updateGraphEditor:
            channels.updateGraphEditor()

    def get_step_parameter(self, step, parameter):
        return channels.getCurrentStepParam(self.selected_channel(), step, parameter)

    def get_recording_pulses_per_second(self):
        return mixer.getRecPPS()

    def get_tempo(self):
        return mixer.getCurrentTempo(True)

    def enable_master_sync(self):
        device.setMasterSync(1)

    def get_master_sync_enabled(self):
        return device.getMasterSync()

    def get_api_version(self):
        return general.getVersion()

    def is_channel_mute_enabled(self, *, group_channel):
        return channels.isChannelMuted(group_channel)

    def is_channel_solo_enabled(self, *, group_channel):
        return channels.isChannelSolo(group_channel)

    def toggle_channel_mute(self, *, group_channel):
        channels.muteChannel(group_channel)

    def toggle_channel_solo(self, *, group_channel):
        channels.soloChannel(group_channel)
