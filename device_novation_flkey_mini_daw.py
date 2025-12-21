# name=Novation FLkey Mini DAW
# supportedHardwareIds=00 20 29 3B 01 00 01
# url=https://forum.image-line.com/viewtopic.php?f=1914&t=277142
from script.constants import DeviceId
from script.device_adapters.fl_to_application_adapter import (
    add_fl_callbacks_to_namespace,
    make_fl_to_application_adapter,
)

device_id = DeviceId.FLkeyMini
fl_to_application_adapter = make_fl_to_application_adapter(device_id)
add_fl_callbacks_to_namespace(globals(), fl_to_application_adapter)
