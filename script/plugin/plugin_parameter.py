from script.constants import PluginParameterType
from util.plain_data import PlainData


@PlainData
class PluginParameter:
    index: int
    name: str
    parameter_type = PluginParameterType.Plugin
    deadzone_centre = None
    deadzone_width = 0.1
    discrete_regions = []
