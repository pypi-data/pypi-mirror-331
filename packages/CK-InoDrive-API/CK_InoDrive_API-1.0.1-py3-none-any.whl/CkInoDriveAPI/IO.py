import logging

from .defines import CK
from .defines import OP_STATE


class IO(object):
    def __init__(self, **kwargs):
        self._get_connection_handle = kwargs.get('getConnectionHandle')

    @property
    def _connection_handle(self):
        return self._get_connection_handle()

    def dispose(self):
        return

    def get_metrics(self):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.GET_METRICS])

            if response.get('error'):
                return {'success': False, 'Error': f"InoDrive GetMetrics Error: {str(response.get('error'))}"}

            data = response['data'][0]

            # Operational State
            if data.get('state'):
                for key, value in data['state'].items():
                    data['state'][key] = OP_STATE.get_state_by_value(value)

            # Ethernet Ports
            ports = {}
            for port in data['eth_ports']:
                ports.update({
                    port['name']: {
                        'link': port['link'],
                        'errors': port['errors'],
                    }
                })
            data['eth_ports'] = ports

            data.update({'success': True})

            return data
        except Exception as ex:
            return {'success': False, 'error': str(ex)}

    def get_temperatures(self):
        try:
            data = self.get_metrics()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return {
                'case': data['temperatures']['case'],
                'cpu': data['temperatures']['cpu'],
                'fets': data['temperatures']['fets'],
                'outputs': data['temperatures']['outputs'],
                'regen': data['temperatures']['regen']
            }
        except Exception as ex:
            logging.exception(ex)
            return None

    def get_input_voltage(self):
        try:
            data = self.get_metrics()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return data['v_in']
        except Exception as ex:
            logging.exception(ex)
            return None

    def get_operational_state(self):
        try:
            data = self.get_metrics()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return data['state']
        except Exception as ex:
            logging.exception(ex)
            return None

    def get_ethernet_ports(self):
        try:
            data = self.get_metrics()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return data['eth_ports']
        except Exception as ex:
            logging.exception(ex)
            return None

    def get_inputs_data(self):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.GET_INPUTS])

            if response.get('error'):
                return {'success': False, 'Error': f"InoDrive GetInputData Error: {str(response.get('error'))}"}

            data = response['data'][0]
            data.update({'success': True})

            return data
        except Exception as ex:
            return {'success': False, 'error': str(ex)}

    def get_accelerometer(self):
        try:
            data = self.get_inputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return {'x': data['g_forces'][0], 'y': data['g_forces'][1], 'z': data['g_forces'][2]}
        except Exception as ex:
            logging.exception(ex)
            return None

    def get_input(self, input=None):
        try:
            data = self.get_inputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            if type(input) is int and 0 <= input <= 3:
                return 1 if (data['digital'] >> input) & 0x1 else 0
            else:
                return data['digital']
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_safety_input(self, input=None):
        try:
            data = self.get_inputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            if type(input) is int and 0 <= input <= 1:
                return 1 if (data['safety'] >> input) & 0x1 else 0
            else:
                return data['safety']
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_analog_input(self):
        try:
            data = self.get_inputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return data['analog']
        except Exception as ex:
            logging.exception(ex)

        return None

    def set_input_polarity(self, target=None, state=None):
        try:

            if target == 'all' and state is not None:
                target = -1
                if type(state) is str:
                    state = 0xf if state.upper() == 'NPN' else 0x0
                else:
                    state = 0xf if state else 0x0
            elif target == 'val' and type(state) is int:
                target = -1
            elif type(target) is int and 0 <= target <= 3 and state is not None:
                if type(state) is str:
                    state = 0x1 if state.upper() == 'NPN' else 0x0
                else:
                    state = 0x1 if state else 0x0
            else:
                logging.error(f"InoDrive SetInputPolarity Error: target or state not supported...")
                return None

            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.SET_INPUT_POLARITY, target, state])

            if response.get('error'):
                logging.error(f"InoDrive SetInputPolarity Error: {str(response)}")
                return None

            return True
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_input_polarity(self, input=None):
        try:
            data = self.get_inputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            if type(input) is int and 0 <= input <= 3:
                return 'NPN' if (data['polarity'] >> input) & 0x1 else 'PNP'
            else:
                return data['polarity']
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_outputs_data(self):
        try:
            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.GET_OUTPUTS])

            if response.get('error'):
                return {'success': False, 'Error': f"InoDrive GetOutputData Error: {str(response.get('error'))}"}

            data = response['data'][0]
            data.update({'success': True})

            return data
        except Exception as ex:
            return {'success': False, 'error': str(ex)}

    def set_output(self, target=None, state=None):
        try:
            if target == 'all' and state is not None:
                target = -1
                state = 0x7 if state else 0x0
            elif target == 'val' and type(state) is int:
                target = -1
            elif type(target) is int and 0 <= target <= 2 and state is not None:
                state = 0x1 if state else 0x0
            else:
                logging.error(f"InoDrive SetOutput Error: target os state not supported...")
                return None

            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.SET_OUTPUTS, target, state])

            if response.get('error'):
                logging.error(f"InoDrive SetOutput Error: {str(response)}")
                return False

            return True
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_output(self, output=None):
        try:

            data = self.get_outputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            if type(output) is int and 0 <= output <= 2:
                return 1 if (data['digital'] >> output) & 0x1 else 0
            else:
                return data['digital']

        except Exception as ex:
            logging.exception(ex)

        return None

    def get_output_fault(self, output=None):
        try:

            data = self.get_outputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            if type(output) is int and 0 <= output <= 2:
                return 1 if (data['digital_faults'] >> output) & 0x1 else 0
            else:
                return data['digital_faults']

        except Exception as ex:
            logging.exception(ex)

        return None

    def set_holding_brake(self, state=False):
        try:

            response = self._connection_handle.msg_pack_request([CK.MSG_PACK.SET_HOLDING_BRAKE, True if state else False])

            if response.get('error'):
                logging.error(f"InoDrive SetHoldingBrake Error: {str(response)}")
                return False

            return True
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_holding_brake(self):
        try:
            data = self.get_outputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return 0x1 if data['brake'] else 0x0
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_holding_brake_fault(self):
        try:
            data = self.get_outputs_data()
            if data.get('error'):
                logging.error(data['error'])
                return None

            return 0x1 if data['brake_fault'] else 0x0
        except Exception as ex:
            logging.exception(ex)

        return None
