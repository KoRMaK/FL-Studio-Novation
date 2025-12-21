from script.actions import SequencerStepEditGroupChangedAction
from script.commands import ExitStepEditModeCommand
from script.constants import Pads, SequencerStepEditState
from script.device_independent.util_view.view import View
from script.fl_constants import RefreshFlags


class SequencerStepToggleView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, command_dispatcher, fl, product_defs, model, view):
        super().__init__(action_dispatcher)
        self.command_dispatcher = command_dispatcher
        self.fl = fl
        self.product_defs = product_defs
        self.model = model
        self.view = view
        self.steps_to_deactivate_on_step_release = set()
        self.current_global_channel = None
        self.current_pattern = None

    def _on_show(self):
        self.steps_to_deactivate_on_step_release = set()
        self.current_global_channel = self.fl.get_selected_global_channel()
        self.current_pattern = self.fl.get_selected_pattern_index()

    def _on_hide(self):
        self._reset_tracked_step_state()
        self.current_global_channel = None
        self.current_pattern = None

    def _set_sequencer_step_to_active(self, step):
        self.fl.set_step_active(step, True)
        self._focus_steps_in_channelrack()

    def _set_sequencer_step_to_inactive(self, step):
        self.fl.set_step_active(step, False)
        self._focus_steps_in_channelrack()

    def _focus_steps_in_channelrack(self):
        first_step = self.num_steps_per_page * self.model.sequencer_active_page
        self.fl.focus_channelrack_steps(
            first_channel=self.fl.selected_channel(),
            num_channels=1,
            first_step=first_step,
            num_steps=self.num_steps_per_page,
        )

    def _prevent_step_deactivation_on_step_release(self):
        return (
            self.model.sequencer.step_edit_group.edited
            or self.model.sequencer.step_edit_state == SequencerStepEditState.EditLatch
        )

    def handle_SequencerStepPressAction(self, action):
        step = action.step
        step_is_active = self.fl.get_step_active(step)

        self.model.sequencer.held_steps.append(step)

        if not step_is_active:
            self._set_sequencer_step_to_active(step)
        elif not self._prevent_step_deactivation_on_step_release():
            self.steps_to_deactivate_on_step_release.add(step)

        if step in self.model.sequencer.step_edit_group.get_steps():
            self.model.sequencer.step_edit_group.remove_step(step)
        else:
            self.model.sequencer.step_edit_group.add_step(step)

        self.action_dispatcher.dispatch(SequencerStepEditGroupChangedAction())
        self.view.redraw(steps=step)

    def handle_SequencerStepReleaseAction(self, action):
        step = action.step

        if step not in self.model.sequencer.held_steps:
            return

        self.model.sequencer.held_steps.remove(step)

        if step in self.steps_to_deactivate_on_step_release:
            self.steps_to_deactivate_on_step_release.discard(step)
            self._set_sequencer_step_to_inactive(step)

        if action.step in self.model.sequencer.step_edit_group.get_steps():
            if self.model.sequencer.step_edit_state != SequencerStepEditState.EditLatch:
                self.model.sequencer.step_edit_group.remove_step(action.step)
                self.action_dispatcher.dispatch(SequencerStepEditGroupChangedAction())
        self.view.redraw(steps=step)

    def handle_SequencerStepEditStateChangedAction(self, action):
        if self._prevent_step_deactivation_on_step_release():
            self.steps_to_deactivate_on_step_release.clear()

    def handle_SequencerStepEditGroupChangedAction(self, action):
        if self._prevent_step_deactivation_on_step_release():
            self.steps_to_deactivate_on_step_release.clear()

    def handle_SequencerPageChangedAction(self, action):
        self._reset_tracked_step_state()

    def handle_OnRefreshAction(self, action):
        if action.flags & (
            RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value | RefreshFlags.Pattern.value
        ):
            selected_global_channel = self.fl.get_selected_global_channel()
            pattern = self.fl.get_selected_pattern_index()
            if self.current_global_channel != selected_global_channel or self.current_pattern != pattern:
                self._handle_pattern_switch(selected_global_channel, pattern)
            elif self.current_pattern == pattern and action.flags & RefreshFlags.Pattern.value:
                self._handle_changes_in_current_pattern()
        if action.flags & RefreshFlags.PerformanceLayout.value:
            self.view.redraw()

    def _handle_pattern_switch(self, selected_global_channel, pattern):
        self.current_global_channel = selected_global_channel
        self.current_pattern = pattern
        self._reset_tracked_step_state()
        self.command_dispatcher.dispatch(ExitStepEditModeCommand())

    def _handle_changes_in_current_pattern(self):
        for held_step in self.model.sequencer.held_steps:
            if not self.fl.get_step_active(held_step):
                self.model.sequencer.held_steps.remove(held_step)
        for editing_step in self.model.sequencer.step_edit_group.get_steps():
            if not self.fl.get_step_active(editing_step):
                self.model.sequencer.step_edit_group.remove_step(editing_step)
                self.action_dispatcher.dispatch(SequencerStepEditGroupChangedAction())
        self.view.redraw()

    def _reset_tracked_step_state(self):
        self.steps_to_deactivate_on_step_release.clear()
        self.model.sequencer.held_steps = []
        self.view.redraw()
