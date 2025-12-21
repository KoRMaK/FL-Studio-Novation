from script.exceptions import UserMappingValidationError, UserParameterValidationError
from script.plugin.plugin_parameter import PluginParameter
from util.enum import Enum
from util.print import print_to_script_output

__all__ = ["user_plugin_parameter_mappings"]

user_plugin_parameter_mappings = {}


class UserParameter:
    class Field(Enum):
        parameter_index = "parameter_index"
        name = "name"
        center = "center"

    def __init__(self, data: dict):
        self.data = data

    @property
    def parameter_index(self):
        return self.data.get(self.Field.parameter_index)

    @property
    def name(self):
        return self.data.get(self.Field.name)

    @property
    def center(self):
        return self.data.get(self.Field.center)

    def validate(self):
        if not isinstance(self.data, dict):
            raise UserParameterValidationError(
                f"Could not read parameter. Expected a dict but found a {type(self.data)}"
            )

        if self.parameter_index is not None:
            if not isinstance(self.parameter_index, int):
                raise UserParameterValidationError(
                    f'"{self.Field.parameter_index}" expects an integer. Found "{self.parameter_index}"'
                )

        if self.name is not None:
            if not isinstance(self.name, str):
                raise UserParameterValidationError(f'"{self.Field.name}" expects a string. Found "{self.name}"')

        if self.center is not None:
            if not isinstance(self.center, float) or self.center < 0.0 or self.center > 1.0:
                raise UserParameterValidationError(
                    f'"{self.Field.center}" expects a value between 0.0 and 1.0. Found "{self.center}"'
                )

    def to_internal_plugin_parameter(self):
        if self.parameter_index is None:
            return None

        return PluginParameter(
            index=self.parameter_index,
            name=self.name,
            deadzone_centre=self.center,
        )


class UserMapping:
    class Field(Enum):
        plugin_name = "plugin_name"
        parameters = "parameters"

    def __init__(self, data: dict):
        self.data = data

    def validate(self):
        if not isinstance(self.data, dict):
            raise UserMappingValidationError(f"Could not read mapping. Expected a dict but found a {type(self.data)}")

        if self.plugin_name is None:
            raise UserMappingValidationError(f'"{self.Field.plugin_name}" was not declared')

        if not isinstance(self.plugin_name, str):
            raise UserMappingValidationError(f'"{self.Field.plugin_name}" expects a string. Found "{self.plugin_name}"')

        if self.parameters is None:
            raise UserMappingValidationError("'parameters' was not declared")

        if not isinstance(self.parameters, list):
            raise UserMappingValidationError(f'"{self.Field.parameters}" expects a list. Found "{self.parameters}"')

        for parameter in self.parameters:
            parameter.validate()

    def to_internal_plugin_mapping(self):
        return self.plugin_name, [parameter.to_internal_plugin_parameter() for parameter in self.parameters]

    @property
    def plugin_name(self):
        return self.data.get(self.Field.plugin_name)

    @property
    def parameters(self):
        if isinstance(self.data.get(self.Field.parameters), list):
            return [UserParameter(data=parameter) for parameter in self.data.get(self.Field.parameters)]
        return self.data.get(self.Field.parameters)


class UserDefinedPluginMappings:
    class Field(Enum):
        plugin_mappings = "plugin_mappings"

    def __init__(self, data: dict):
        self.data = data

    def validate(self):
        if not isinstance(self.data, dict):
            raise UserMappingValidationError(
                f"Could not read user-defined mappings. Expected a dict but found a {type(self.data)}"
            )

        if self.plugin_mappings is None:
            raise UserMappingValidationError(f'"{self.Field.plugin_mappings}" was not declared')

        if not isinstance(self.plugin_mappings, list):
            raise UserMappingValidationError(
                f'"{self.Field.plugin_mappings}" expects a list. Found a {type(self.plugin_mappings)}'
            )

    def __iter__(self):
        for mapping in self.plugin_mappings:
            if self.is_valid_mapping(mapping):
                yield UserMapping(mapping).to_internal_plugin_mapping()

    @staticmethod
    def is_valid_mapping(data: dict):
        try:
            user_mapping = UserMapping(data)
            user_mapping.validate()
        except (UserMappingValidationError, UserParameterValidationError) as e:
            print_to_script_output(e)
            return False
        return True

    @property
    def plugin_mappings(self):
        return self.data.get(self.Field.plugin_mappings)


def convert_and_store_user_defined_plugin_mappings(data: dict):
    try:
        user_defined_plugin_mappings = UserDefinedPluginMappings(data)
        user_defined_plugin_mappings.validate()
    except UserMappingValidationError as e:
        print_to_script_output(e)
        return

    print_to_script_output(f"Found {len(user_defined_plugin_mappings.plugin_mappings)} user-defined plugin mappings")

    user_plugin_parameter_mappings.clear()
    for name, parameters in user_defined_plugin_mappings:
        user_plugin_parameter_mappings[name] = parameters


try:
    from user.user_defined_plugin_mappings import user_defined_plugin_mappings as unconverted_user_plugin_mappings
except ImportError:
    pass
else:
    convert_and_store_user_defined_plugin_mappings(unconverted_user_plugin_mappings)
