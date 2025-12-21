from itertools import islice

from script.constants import PatternSelectBank
from script.fl_constants import FlConstants, PatternGroups


class ActivePatternBank:
    def __init__(self, fl, model):
        self.fl = fl
        self.model = model

    def get_patterns(self):
        if self.fl.get_active_pattern_group() == PatternGroups.AllPatterns.value:
            return self._patterns_for_bank_in_all_group()
        return self._patterns_for_bank_in_active_user_group()

    def _patterns_for_bank_in_active_user_group(self):
        first_index_in_next_bank = self._first_index_in_bank + PatternSelectBank.NumPerBank.value
        return list(
            islice(self.fl.get_patterns_for_active_group(), self._first_index_in_bank, first_index_in_next_bank)
        )

    def _patterns_for_bank_in_all_group(self):
        patterns = (
            pattern
            for pattern in range(FlConstants.FirstPatternIndex.value, self.fl.get_last_pattern_index() + 1)
            if not self.fl.is_pattern_default(pattern) or pattern == self.fl.get_selected_pattern_index()
        )
        return list(
            islice(patterns, self._first_index_in_bank, self._first_index_in_bank + PatternSelectBank.NumPerBank.value)
        )

    @property
    def _first_index_in_bank(self):
        return self.model.pattern_select_active_bank * PatternSelectBank.StepsPerBankingIncrement.value
