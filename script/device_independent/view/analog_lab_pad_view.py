from script.colours import Colours
from script.colour_utils import scale_colour
from script.device_independent.util_view.view import View
import time

try:
    import channels
    import general
    import midi
except ImportError:
    pass


class AnalogLabPadView(View):
    """
    Manages pad display and interaction when Analog Lab V is selected.
    - All pads are turned off except top-left pad (pad 0)
    - Top-left pad glows green - when pressed, iterates through MIDI messages

    Physical layout:
    Row 1 (top):     0   1   2   3   4   5   6   7
    Row 2 (bottom):  8   9  10  11  12  13  14  15
    """

    ANALOG_LAB_PLUGIN_NAMES = ["Analog Lab", "Analog Lab V"]
    TOP_LEFT_PAD = 0  # Physical top-left position

    # Colors
    DIM_GREEN = scale_colour((0, 255, 0), 0.3)  # Dim green (30% brightness)
    BRIGHT_GREEN = (0, 255, 0)  # Bright green

    def __init__(self, action_dispatcher, pad_led_writer, fl, channel_selection_manager=None):
        super().__init__(action_dispatcher)
        self.pad_led_writer = pad_led_writer
        self.fl = fl
        self.channel_selection_manager = channel_selection_manager
        self.is_active = False
        self.pad_pressed = False
        self.midi_iteration_running = False

    def _is_analog_lab_selected(self):
        """Check if Analog Lab V is the currently selected plugin"""
        selected_plugin = self.fl.get_selected_plugin()
        if selected_plugin is None:
            return False
        return any(name in selected_plugin for name in self.ANALOG_LAB_PLUGIN_NAMES)

    def _update_pad_display(self):
        """Update pad LEDs based on Analog Lab selection state"""
        if self._is_analog_lab_selected():
            if not self.is_active:
                # Activate Analog Lab pad mode
                self.is_active = True
                self._show_analog_lab_pads()
        else:
            if self.is_active:
                # Deactivate Analog Lab pad mode
                self.is_active = False
                self._hide_analog_lab_pads()

    def _show_analog_lab_pads(self):
        """Turn off all pads except top-left (pad 0) which shows dim green"""
        for pad in range(16):
            if pad == self.TOP_LEFT_PAD:
                self.pad_led_writer.set_pad_colour(pad, self.DIM_GREEN)
            else:
                self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def _hide_analog_lab_pads(self):
        """Turn off all pads when leaving Analog Lab mode"""
        for pad in range(16):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)
        self.pad_pressed = False

    def _iterate_through_midi_messages(self):
        """Iterate through all possible MIDI messages to find favorite toggle"""
        if self.midi_iteration_running:
            print("MIDI iteration already running, skipping...")
            return

        self.midi_iteration_running = True
        print("=" * 60)
        print("Starting MIDI message iteration for Analog Lab favorite discovery")
        print("=" * 60)

        if self.channel_selection_manager:
            selected_channel = self.channel_selection_manager.get_active_channel()
        else:
            selected_channel = self.fl.selected_channel()

        if selected_channel is None:
            print("ERROR: No channel selected")
            self.midi_iteration_running = False
            return

        # Get the rec event ID for this channel
        rec_event_id = channels.getRecEventId(selected_channel)

        # Iterate through all CC messages (0-127) with various values
        print("\n--- Testing CC (Control Change) Messages ---")
        for cc_num in range(128):
            for value in [0, 64, 127]:  # Test off, mid, on
                # Skip CC 18 value 0 - causes FL Studio crash
                if cc_num == 18: # and value == 0:
                    print(f"CC {cc_num:3d} = {value:3d} (SKIPPED - causes crash)")
                    continue

                rec_event_parameter = cc_num + rec_event_id
                midi_value = int((value / 127.0) * midi.FromMIDI_Max)
                mask = midi.REC_MIDIController

                print(f"CC {cc_num:3d} = {value:3d} (MIDI val: {midi_value})")
                general.processRECEvent(rec_event_parameter, midi_value, mask)
                time.sleep(0.2)  # 200ms pause between messages

        # Test Note On messages
        print("\n--- Testing Note On Messages ---")
        for note in range(128):
            for velocity in [64, 127]:
                print(f"Note On: {note:3d}, Velocity: {velocity:3d}")
                self.fl.send_note_on(note, velocity)
                time.sleep(0.1)
                # Send note off immediately
                self.fl.send_note_off(note)
                time.sleep(0.1)

        print("=" * 60)
        print("MIDI iteration complete!")
        print("=" * 60)
        self.midi_iteration_running = False

    def _on_show(self):
        self._update_pad_display()

    def _on_hide(self):
        if self.is_active:
            self._hide_analog_lab_pads()

    def handle_OnRefreshAction(self, action):
        """Update pads when plugin selection changes"""
        self._update_pad_display()

    def handle_PadPressAction(self, action):
        """Handle pad press events"""
        if not self.is_active:
            return

        if action.pad == self.TOP_LEFT_PAD:
            # Change to bright green and start MIDI iteration
            self.pad_led_writer.set_pad_colour(self.TOP_LEFT_PAD, self.BRIGHT_GREEN)
            self.pad_pressed = True
            print("\n[TOP LEFT PAD (0) PRESSED] Starting MIDI message iteration...")
            self._iterate_through_midi_messages()

    def handle_PadReleaseAction(self, action):
        """Handle pad release events"""
        if not self.is_active:
            return

        if action.pad == self.TOP_LEFT_PAD and self.pad_pressed:
            # Return to dim green
            self.pad_led_writer.set_pad_colour(self.TOP_LEFT_PAD, self.DIM_GREEN)
            self.pad_pressed = False
