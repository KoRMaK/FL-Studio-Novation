"""
Channel Selection Manager for Launchkey independent channel selection.

Uses channel name suffixes to communicate selected channel between DAW and MIDI scripts.
"""

__all__ = ["ChannelSelectionManager"]

try:
    import channels
except ImportError:
    pass


class ChannelSelectionManager:
    """
    Manages controller-specific channel selection independent of FL Studio UI.

    Marks the selected channel by appending " | lk" to its name, which allows
    the MIDI script (running in a separate Python context) to identify it.
    """

    MARKER_SUFFIX = " | lk"

    def __init__(self, model, fl):
        self.model = model
        self.fl = fl

    def get_active_channel(self):
        """Get the controller's active channel (may differ from FL Studio UI)"""
        if self.model.selected_channel_index is not None:
            return self.model.selected_channel_index
        # Fallback to FL Studio's UI selection if controller hasn't selected anything
        return self.fl.selected_channel()

    def set_active_channel(self, channel_index):
        """Set the controller's active channel without changing FL Studio UI"""
        # Remove marker from old channel
        if self.model.selected_channel_index is not None:
            self._remove_marker_from_channel(self.model.selected_channel_index)

        # Update model
        self.model.selected_channel_index = channel_index

        # Add marker to new channel
        if channel_index is not None:
            self._add_marker_to_channel(channel_index)

    def select_next_channel(self):
        """Navigate to next channel"""
        current = self.get_active_channel()
        if current is not None and current < self.fl.channel_count() - 1:
            self.set_active_channel(current + 1)
        return self.get_active_channel()

    def select_previous_channel(self):
        """Navigate to previous channel"""
        current = self.get_active_channel()
        if current is not None and current > 0:
            self.set_active_channel(current - 1)
        return self.get_active_channel()

    def sync_with_fl_studio_ui(self):
        """Sync controller selection to match FL Studio's UI selection"""
        # Remove marker from old channel if any
        if self.model.selected_channel_index is not None:
            self._remove_marker_from_channel(self.model.selected_channel_index)

        # Update to FL Studio's selection
        self.model.selected_channel_index = self.fl.selected_channel()

        # Add marker to new channel
        if self.model.selected_channel_index is not None:
            self._add_marker_to_channel(self.model.selected_channel_index)

    def is_synced_with_fl_studio_ui(self):
        """Check if controller selection matches FL Studio UI"""
        return self.model.selected_channel_index == self.fl.selected_channel()

    def _add_marker_to_channel(self, channel_index):
        """Add the marker suffix to a channel's name"""
        try:
            current_name = channels.getChannelName(channel_index)
            if not current_name.endswith(self.MARKER_SUFFIX):
                new_name = current_name + self.MARKER_SUFFIX
                channels.setChannelName(channel_index, new_name)
        except Exception:
            pass  # Silently fail if we can't modify the name

    def _remove_marker_from_channel(self, channel_index):
        """Remove the marker suffix from a channel's name"""
        try:
            current_name = channels.getChannelName(channel_index)
            if current_name.endswith(self.MARKER_SUFFIX):
                new_name = current_name[:-len(self.MARKER_SUFFIX)]
                channels.setChannelName(channel_index, new_name)
        except Exception:
            pass  # Silently fail if we can't modify the name
