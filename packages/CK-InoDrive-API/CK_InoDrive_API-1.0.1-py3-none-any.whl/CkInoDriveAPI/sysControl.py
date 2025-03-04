import logging

from .defines import CK
from .utils import Utils


class SysControl(object):
    def __init__(self, **kwargs):
        self._get_connection_handle = kwargs.get('getConnectionHandle')

    @property
    def _connection_handle(self):
        return self._get_connection_handle()

    def dispose(self):
        return

    def console_enable(self, state=False):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.CONSOLE_ENABLE, True if state else False])

            if response.get('error'):
                logging.error(f"InoDrive ConsoleEnable Error: {str(response)}")
                return None

            return True
        except Exception as ex:
            logging.exception(ex)

    def take_control(self, state=False):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.TAKE_CONTROL, True if state else False])

            if response.get('error'):
                logging.error(f"InoDrive TakeControl Error: {str(response)}")
                return None

            return True
        except Exception as ex:
            logging.exception(ex)

    def get_module_info(self):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.MODULE_INFO])

            if response.get('error'):
                logging.error(f"InoDrive GetModuleInfo Error: {str(response)}")
                return None

            data = response['data'][0]

            # Firmware
            if data.get('firmware'):
                data['firmwareFlags'] = Utils.get_firmware_flags(data['firmware']['type'])
                data['firmware'] = ".".join([
                    str(data['firmware']["major"]),
                    str(data['firmware']["minor"]),
                    str(data['firmware']["build"])
                ])
            else:
                data['firmwareFlags'] = Utils.get_firmware_flags(0)
                data['firmware'] = "0.0.0"

            # PCB
            if data.get('pcb'):
                data['pcbFlags'] = Utils.get_pcb_flags(data['pcb']['type'])
                data['pcb'] = ".".join([
                    str(data['pcb']["major"]),
                    str(data['pcb']["minor"]),
                    str(data['pcb']["build"])
                ])
            else:
                data['pcbFlags'] = Utils.get_pcb_flags(0)
                data['pcb'] = "1.1.1"

            # Web
            if data.get('web'):
                data['webpage'] = data['web']['version']
            else:
                data['webpage'] = None

            if 'web' in data:
                del data['web']

            # Failsafe Firmware
            if data.get('failsafe_fw'):
                data['fsFirmwareFlags'] = Utils.get_fs_firmware_flags(data['failsafe_fw']['type'])
                data['fsFirmware'] = ".".join([
                    str(data['failsafe_fw']['major']),
                    str(data['failsafe_fw']['minor']),
                    str(data['failsafe_fw']['build'])
                ])
            else:
                data['fsFirmwareFlags'] = Utils.get_fs_firmware_flags(0)
                data['fsFirmware'] = None

            if 'failsafe_fw' in data:
                del data['failsafe_fw']

            return data
        except Exception as ex:
            logging.exception(ex)

        return None
