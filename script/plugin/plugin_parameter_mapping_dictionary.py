class PluginParameterMappingDictionary:
    def __init__(self, raw_dict):
        self.dict = self.replace_keys_with_lower_case_only_alpha_numeric(raw_dict)

    def __contains__(self, item):
        return self._filter_alpha_numeric_and_make_lower_case(item) in self.dict

    def __getitem__(self, item):
        return self.dict[self._filter_alpha_numeric_and_make_lower_case(item)]

    def get(self, key):
        return self.dict.get(self._filter_alpha_numeric_and_make_lower_case(key))

    @classmethod
    def _filter_alpha_numeric_and_make_lower_case(cls, key):
        if key is None:
            return None
        return "".join(filter(lambda letter: letter.isalnum(), key.lower()))

    @classmethod
    def replace_keys_with_lower_case_only_alpha_numeric(cls, raw_dict):
        return {cls._filter_alpha_numeric_and_make_lower_case(key): value for key, value in raw_dict.items()}
