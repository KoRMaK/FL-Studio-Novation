import util.math

try:
    import channels
    import general
    import midi
    import plugins
except ImportError:
    pass


class MidiBypass:
    # Map of plugin names to their mod wheel parameter indices
    PLUGIN_MOD_WHEEL_MAP = {
        "SEM V3": 248,
        "Mini V4": 4097,
        "Analog Lab V": 4097
        # Add more plugins here as you discover their mod wheel parameters:
        # "Plugin Name": parameter_index,
    }

    def __init__(self, fl):
        self.fl = fl

    def _get_target_channel(self, launchkey_selected_channel):
        """
        Get the target channel for MIDI routing.
        Uses launchkey_selected_channel if available, otherwise FL Studio UI selection.
        """
        if launchkey_selected_channel is not None:
            return launchkey_selected_channel
        return self.fl.selected_channel()

    def on_note_on(self, eventData, launchkey_selected_channel=None):
        """Handle MIDI note on events and route to Launchkey's selected channel"""
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        note = eventData.data1
        velocity = eventData.data2

        self.fl.send_note_on(note, velocity, group_channel=target_channel)

    def on_note_off(self, eventData, launchkey_selected_channel=None):
        """Handle MIDI note off events and route to Launchkey's selected channel"""
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        note = eventData.data1

        self.fl.send_note_off(note, group_channel=target_channel)

    def on_pitch_bend(self, eventData, launchkey_selected_channel=None):
        eventData.handled = True

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        value = eventData.data1 | eventData.data2 << 7
        normalised_pitch = util.math.normalise(value=value, lower_bound=0, upper_bound=1 << 14)
        self.fl.channel.set_pitch(normalised_pitch, group_channel=target_channel)

    def on_mod_wheel(self, eventData, launchkey_selected_channel=None):
        """Handle MIDI mod wheel (CC#1) events and route to selected plugin"""
        eventData.handled = False

        target_channel = self._get_target_channel(launchkey_selected_channel)
        if target_channel is None:
            return

        # Check if there's a valid plugin on the target channel
        if not plugins.isValid(target_channel, -1):
            return

        # Get the plugin name
        plugin_name = plugins.getPluginName(target_channel, -1)

        # Look up the mod wheel parameter index for this plugin
        print(plugin_name)
        mod_wheel_param_index = self.PLUGIN_MOD_WHEEL_MAP.get(plugin_name)
        print(mod_wheel_param_index)

        if mod_wheel_param_index is None:
            mod_wheel_param_index = 4096 + 1 # default_cc_offset + default_mod_cc


        eventData.handled = True
        # Get mod wheel value from MIDI event
        cc_value = eventData.data2
        normalized_value = cc_value / 127.0

        # Set the plugin parameter directly
        from script.fl_constants import PickupFollowMode
        plugins.setParamValue(
            normalized_value,
            mod_wheel_param_index,
            target_channel,
            -1,
            PickupFollowMode.FollowUserSetting.value
        )


    def scan_plugin_parameters(self, launchkey_selected_channel=None):
        """Scan and print all parameters for the currently selected plugin"""
        try:
            target_channel = self._get_target_channel(launchkey_selected_channel)
            if target_channel is None:
                print("No channel selected")
                return

            channel_or_track = target_channel
            slot = -1

            if not plugins.isValid(channel_or_track, slot):
                print(f"No valid plugin on channel {target_channel}")
                return

            param_count = plugins.getParamCount(channel_or_track, slot)
            plugin_name = plugins.getPluginName(channel_or_track, slot)
            print(f"\n=== Plugin: {plugin_name} ===")
            print(f"Channel: {target_channel}")
            print(f"Total parameters: {param_count}\n")

            for i in range(700):
                param_name = plugins.getParamName(i, channel_or_track, slot)
                param_value = plugins.getParamValue(i, channel_or_track, slot)
                param_value_str = plugins.getParamValueString(i, channel_or_track, slot)

                # Check if this might be mod wheel related
                is_mod_wheel = "mod" in param_name.lower() or "modulation" in param_name.lower()
                marker = " <-- MOD WHEEL?" if is_mod_wheel else ""

                print(f"[{i:3d}] {param_name:30s} = {param_value:.3f} ({param_value_str}){marker}")

        except Exception as e:
            print(f"Error scanning parameters: {e}")
