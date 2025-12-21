# name=Novation Launchkey Mini MK3
from script.constants import DeviceId
from script.device_adapters.fl_to_application_adapter import (
    add_fl_callbacks_to_namespace,
    make_fl_to_application_adapter,
)

device_id = DeviceId.LaunchkeyMini
fl_to_application_adapter = make_fl_to_application_adapter(device_id)
add_fl_callbacks_to_namespace(globals(), fl_to_application_adapter)
