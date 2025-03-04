import time
import json
import logging
import threading

from .defines import CK
from .utils import Utils

PROTOCOL_MSG_PACK = 'msgPack'
PROTOCOL_JSON_API = 'json'


class UserApp(object):
    _guard_thread = None
    _guard_timeout = 0.01
    _last_poll_time = None
    _connected = False
    _poll_active = False
    _initialized = False
    _data_available = False

    def __init__(self, **kwargs):
        self._callback = kwargs.get('callback')
        self._get_connection_handle = kwargs.get('getConnectionHandle')
        self._guard_multiplier = kwargs.get('disconnectOnMissedPolls', 3)

        self._protocol = PROTOCOL_MSG_PACK

        self._variable_values = {}
        self._awaiting_response = False

        self._program_id = None
        self._ntp_poll_time = 0

        self._poll_time = kwargs.get('pollTime', 1)
        self._poll_running = False

        self._thread = None
        self._thread_running = False

        self._guard_thread = None
        self._guard_running = False

        self._callback.on('connect', self._on_connect)
        self._callback.on('disconnect', self._on_disconnect)
        self._callback.on('error', self._on_error)

    @property
    def _connection_handle(self):
        return self._get_connection_handle()

    @property
    def callback(self):
        return self._callback

    @property
    def on(self):
        return self._callback.on

    def dispose(self):
        self.stop_poll()

    def get_variable(self, id=None):
        try:
            for var_name, var_props in self._variable_values.items():
                if type(id) is str and id == var_name:
                    return var_props
                if type(id) is int and var_props['id'] == id:
                    return var_props

        except Exception as ex:
            logging.exception(ex)

        return None

    def get_variable_c_type(self, type):
        return Utils.get_var_c_type(type)

    def start_poll(self, timeout=None):
        if self._thread:
            return

        if timeout:
            self._poll_time = timeout

        self._last_poll_time = int(time.time())

        # Retrieve the data from the module first
        self._poll()

        self._thread = threading.Thread(target=self._thread_loop, daemon=True)
        self._thread_running = True
        self._thread.start()

        self._guard_thread = threading.Thread(target=self._poll_guard_loop, daemon=True)
        self._guard_running = True
        self._guard_thread.start()

    def stop_poll(self):
        if not self._thread:
            return

        self._thread_running = False
        self._thread.join()
        self._thread = None

        self._guard_running = False
        self._guard_thread.join()
        self._guard_thread = None

    def wait_for_data_available(self, timeout=None):
        timeout = timeout or 5

        logging.debug(f"Timeout: {timeout}")

        begin = int(time.time())
        while (int(time.time()) - begin) < timeout:
            if len(self._variable_values) > 0:
                break
            time.sleep(0.1)

    def get_variables_list(self, access=None):
        try:
            var_list = []

            if access is None:
                access = [CK.API_VAR_ACCESS['read'], CK.API_VAR_ACCESS['readWrite']]

            if type(access) is not list:
                access = list(access)

            for var_name, var_props in self._variable_values.items():
                if access and var_props['access'] in access:
                    var_list.append(var_name)

            return var_list
        except Exception as ex:
            logging.exception(ex)

        return []

    def get_all_variables(self):
        result = {
            'timestamp': self._ntp_poll_time,
            'programId': self._program_id,
            'items': {},
        }

        for var_name, var_props in self._variable_values.items():
            result['items'].update({var_name: {
                'id': var_props['id'],
                'access': CK.API_VAR_ACCESS[var_props['access']],
                'type': var_props['type'],
                'value': var_props['value'],
            }})

        return result

    def update_variables_list(self):
        try:
            program_id = None
            data = None

            if self._protocol == PROTOCOL_MSG_PACK:
                resp = self._connection_handle.msg_pack_request([CK.MSG_PACK.LIST_VARIABLES])

                error = resp.get('error')
                if error:
                    if error in [CK.RESULT.UNKNOWN_TYPE, CK.RESULT.MSG_PACK_NOT_SUPPORTED]:
                        # Unsupported TLV or Msg Pack
                        # Target device is using old firmware switch to JSON_API
                        self._protocol = PROTOCOL_JSON_API
                    else:
                        logging.error(f"Retrieving variables list failed. Error: {str(error)}")
                        return False
                else:
                    program_id = resp['data'][0]
                    data = resp['data'][1]

            if self._protocol == PROTOCOL_JSON_API:
                msg = Utils.get_tlv(CK.SPECIAL.JSON_API)
                msg += Utils.get_tlv(CK.TYPE.STRING, {'id': Utils.get_token(8, bytes=False), 'request': CK.JSON_API.VAR_LIST})

                resp = self._connection_handle.request(msg)

                if resp.get('error'):
                    logging.error(f"Retrieving variables list failed...")
                    return False

                if len(resp['items']) == 0:
                    logging.error(f"Missing data.")
                    return False

                if resp['items'][0]['ctpType'] != CK.TYPE.STRING:
                    logging.error(f"Unsupported response type: {resp['items'][0]['ctpType']}")
                    return False

                json_response = json.loads(resp['items'][0]['data'])

                program_id = json_response['program_id']
                data = json_response['data']

            if not program_id:
                logging.error("Program ID is missing...")
                return False

            if not data:
                logging.error("Variable list data is missing...")
                return False

            self._program_id = program_id
            self._update_variables_list(data)

            return self._variable_values
        except Exception as ex:
            logging.exception(ex)

        return False

    def read_var(self, argv=None, **kwargs):
        try:
            if self._connection_handle.connected() and not self._initialized:
                self._poll()

            request_data = []
            var_list = []

            if type(argv) is str or type(argv) is int:
                var_list.append(argv)
            elif type(argv) is list:
                var_list = argv
            else:
                logging.error("Unsupported argument type...")
                return None

            for var_name in var_list:
                variable = self.get_variable(var_name)
                if not variable:
                    logging.error(f"Variable < {var_name} > not found...")
                    return None

                if self._protocol == PROTOCOL_MSG_PACK:
                    request_data.append([variable['id'], False])
                elif self._protocol == PROTOCOL_JSON_API:
                    request_data.append({'id': variable['id']})
                else:
                    logging.error("Unsupported protocol...")
                    return None

            if len(request_data) == 0:
                logging.error("Invalid Request Data...")
                return None

            resp = self._var_access_request(request_data)

            if resp.get('error'):
                logging.error(resp['error'])
                return None

            result = {}

            for item in resp['data']:
                variable = self.get_variable(item[0])
                if variable:
                    var_name = self._get_variable_name_by_id(variable['id'])

                    precision = kwargs.get('floatPrecision')
                    if (variable['type'] == 'float' or variable['type'] == 'double') and type(precision) is int:
                        var_value = round(item[1], precision)
                    else:
                        var_value = item[1]

                    variable['value'] = var_value

                    result.update({var_name: var_value})

            if len(result) > 0:
                if type(argv) is list:
                    return result
                else:
                    return list(result.values())[0]
        except Exception as ex:
            logging.exception(ex)

        return None

    def write_var(self, argv=None, value=None, **kwarg):
        try:
            if self._connection_handle.connected() and not self._initialized:
                self._poll()

            var_dict = {}
            request_data = []

            if type(argv) is str or type(argv) is int:
                if value is None:
                    logging.error("Missing new value for argument...")
                    return False

                var_dict.update({argv: value})
            elif type(argv) is dict:
                var_dict = argv
            else:
                logging.error("Unsupported argument type...")
                return False

            for var_name, var_value in var_dict.items():
                variable = self.get_variable(var_name)
                if variable:
                    is_c_type = Utils.is_proper_c_type(var_value, variable['type'])
                    if is_c_type:
                        # Message Pack protocol enforces true/false values for boolean variables.
                        # We make sure for boolean type we always send true/false
                        if variable['type'] == 'bool':
                            var_value = True if var_value else False

                        variable['value'] = var_value
                        if self._protocol == PROTOCOL_MSG_PACK:
                            request_data.append([variable['id'], True, var_value])
                        elif self._protocol == PROTOCOL_JSON_API:
                            request_data.append({'id': variable['id'], 'val': var_value})
                        else:
                            logging.error("Unsupported protocol...")
                            return False
                else:
                    logging.error(f"Variable < {var_name} > not found...")
                    return False

            resp = self._var_access_request(request_data)

            if resp.get('error'):
                logging.error(resp['error'])
                return False

            return resp.get('success')
        except Exception as ex:
            logging.exception(ex)

        return False

    def get_var(self, argv=None, **kwargs):
        try:
            var_list = []
            result = {}

            if type(argv) is str or type(argv) is int:
                var_list.append(argv)
            elif type(argv) is list:
                var_list = argv
            else:
                logging.error("Unsupported argument type...")
                return None

            for var_name in var_list:
                variable = self.get_variable(var_name)

                if not variable:
                    logging.error(f"Variable < {var_name} > not found...")
                    return False

                variable_name = self._get_variable_name_by_id(variable['id'])
                precision = kwargs.get('floatPrecision')
                if (variable['type'] == 'float' or variable['type'] == 'double') and type(precision) is int:
                    result.update({variable_name: round(variable['value'], precision)})
                else:
                    result.update({variable_name: variable['value']})

            if len(result) > 0:
                if type(argv) is list:
                    return result
                else:
                    return list(result.values())[0]
        except Exception as ex:
            logging.exception(ex)

        return None

    def set_var(self, argv=None, value=None, **kwargs):
        try:
            var_dict = {}

            if type(argv) is str or type(argv) is int:
                if value is None:
                    logging.error("Missing new value for argument...")
                    return False

                var_dict.update({argv: value})
            elif type(argv) is dict:
                var_dict = argv
            else:
                logging.error("Unsupported argument type...")
                return False

            for var_name, var_value in var_dict.items():
                variable = self.get_variable(var_name)
                if not variable:
                    logging.error(f"Variable < {var_name} > not found...")
                    return False

                is_c_type = Utils.is_proper_c_type(var_value, variable['type'])
                if is_c_type:
                    # Message Pack protocol enforces true/false values for boolean variables.
                    # We make sure for boolean type we always send true/false
                    if variable['type'] == 'bool':
                        var_value = True if var_value else False

                    variable.update({
                        'value': var_value,
                        'write': True,
                    })

            return True
        except Exception as ex:
            logging.exception(ex)

        return False

    def _on_connect(self, wsapp):
        try:
            if not self._connected:
                self._callback.dispatch("appStatus", {'state': "connected"})
                self._connected = True
        except Exception as ex:
            logging.exception(ex)

    def _on_disconnect(self, wsapp, close_status_code, close_msg):
        try:
            if self._connected:
                self._callback.dispatch("appStatus", {'state': "disconnected"})
                self._connected = False
        except Exception as ex:
            logging.exception(ex)

    def _on_error(self, wsapp, evt):
        try:
            if self._connected:
                self._callback.dispatch("appStatus", {'state': "disconnected"})
                self._connected = False
        except Exception as ex:
            logging.exception(ex)

    def _thread_loop(self):
        while self._thread_running:
            if self._thread is None:
                return
            self._thread_worker_message(msg={'cmd': "poll"})
            time.sleep(self._poll_time)

    def _thread_worker_message(self, msg):
        try:
            if not msg:
                return

            match msg['cmd']:
                case "poll":
                    if self._poll_running:
                        return
                    self._poll_running = True
                    self._poll()
                    self._poll_running = False
        except Exception as ex:
            logging.exception(ex)

    def _get_variable_name_by_id(self, id=None):
        if id is None:
            return None

        for var_name, var_props in self._variable_values.items():
            if var_props['id'] == id:
                return var_name

        return None

    def _update_variables_list(self, variable_list=None):
        try:
            if variable_list is None:
                return
            # See if we need to reset all variables or keep some of them
            # self._variable_values = {}

            # Remove all old variables which are no longer in the user application
            items_to_remove = []
            for var_name, var_data in self._variable_values.items():
                in_var_list = False
                for item in variable_list:
                    if var_name == item['name']:
                        in_var_list = True
                        continue

                if not in_var_list:
                    items_to_remove.append(var_name)

            for var_name in items_to_remove:
                self._variable_values.pop(var_name, None)

            # Create new or refresh variables if they do not exist already
            for item in variable_list:
                variable = self._variable_values.get(item['name'])
                if not variable:
                    self._variable_values.update({item['name']: {
                        'id': item['id'],
                        'type': Utils.get_var_c_type(item['type']),
                        'access': item['access'],
                        'value': None,
                        'write': False,
                    }})
                else:
                    variable.update({
                        'id': item['id'],
                        'type': Utils.get_var_c_type(item['type']),
                        'access': item['access'],
                        'value': variable['value'],
                    })

            self._initialized = True
            self._callback.dispatch("appStatus", {'state': "varUpdated"})

        except Exception as ex:
            logging.exception(ex)

    def _var_access_request(self, data):
        try:
            if self._protocol == PROTOCOL_MSG_PACK:
                resp = self._connection_handle.msg_pack_request([CK.MSG_PACK.ACCESS_VARIABLES, data])

                if resp.get('error'):
                    return {'success': False, 'error': resp['error']}

                return {
                    'success': True,
                    'token': resp['token'],
                    'program_id': resp['data'][0],
                    'ntpTime': resp['ntpTime'],
                    'data': resp['data'][1],
                }
            elif self._protocol == PROTOCOL_JSON_API:
                msg = Utils.get_tlv(CK.SPECIAL.JSON_API)
                msg += Utils.get_tlv(CK.TYPE.STRING, {'id': Utils.get_token(8, bytes=False), 'request': CK.JSON_API.VAR_ACCESS, 'data': data})

                resp = self._connection_handle.request(msg)

                # Check if we got error during decoding process
                if resp.get('error'):
                    return {'success': False, 'error': resp['error']}

                if len(resp['items']) == 0:
                    return {'success': False, 'error': "Missing data."}

                if resp['items'][0]['ctpType'] != CK.TYPE.STRING:
                    return {'success': False, 'error': "Unsupported response type..."}

                json_response = json.loads(resp['items'][0]['data'])

                # Error
                if json_response.get('error'):
                    return {'success': False, 'error': json_response['error']}

                resp_data = []
                for item in json_response.get('data', []):
                    resp_data.append([item['id'], item['val']])

                return {
                    'success': True,
                    'token': resp['token'],
                    'program_id': json_response['program_id'],
                    'ntpTime': resp['ntpTime'],
                    'data': resp_data,
                }
            else:
                # Unknown protocol
                return {'success': False, 'error': "Unknown protocol."}

        except Exception as ex:
            return {'success': False, 'error': str(ex)}

    def _poll(self):
        try:
            if not self._connection_handle.connected():
                return

            if not self._initialized:
                self.update_variables_list()
                return

            data = []
            write_list = []

            # Write Variables
            # ===========================================================================================
            for var_name in self.get_variables_list([CK.API_VAR_ACCESS['write'], CK.API_VAR_ACCESS['readWrite']]):
                variable = self.get_variable(var_name)
                if variable and variable['write']:
                    if self._protocol == PROTOCOL_MSG_PACK:
                        data.append([variable['id'], True, variable['value']])
                    elif self._protocol == PROTOCOL_JSON_API:
                        data.append({
                            'id': variable['id'],
                            'val': variable['value'],
                        })

                    write_list.append(variable)
            # ===========================================================================================

            # Read Variables
            # ===========================================================================================
            for var_name in self.get_variables_list([CK.API_VAR_ACCESS['read'], CK.API_VAR_ACCESS['readWrite']]):
                variable = self.get_variable(var_name)
                if variable:
                    if self._protocol == PROTOCOL_MSG_PACK:
                        data.append([variable['id'], False])
                    elif self._protocol == PROTOCOL_JSON_API:
                        data.append({
                            'id': variable['id']
                        })
            # ===========================================================================================

            # Send Message
            # ===========================================================================================
            resp = self._var_access_request(data)
            # ===========================================================================================

            # Set new poll time
            self._last_poll_time = int(time.time())

            # Error
            if resp.get('error'):
                logging.error(f"Poll request error: {resp['error']}")
                self._initialized = False
                return

            # Check if this is new program
            if self._program_id != resp.get('program_id'):
                self._callback.dispatch("appStatus", {'state': "newProgram"})
                self._initialized = False
                return

            # Variables are successfully written, so now we can remove the write flag
            for variable in write_list:
                variable['write'] = False

            # Current module time
            if resp.get('ntpTime'):
                self._ntp_poll_time = resp['ntpTime']

            # Update variable values
            if resp.get('data'):
                for item in resp['data']:
                    variable = self.get_variable(item[0])
                    if variable:
                        variable.update({'value': item[1]})

            self._data_available = True
            self._callback.dispatch("appPoll", self.get_all_variables())

        except Exception as ex:
            logging.exception(ex)

    def _poll_guard_loop(self):
        while self._guard_running:
            try:
                timeout = self._poll_time * self._guard_multiplier

                if (int(time.time()) - self._last_poll_time) > timeout:
                    # Lost connection
                    if self._poll_active:
                        self._callback.dispatch("appStatus", {'state': "lostPoll"})
                        self._poll_active = False
                else:
                    # Resume connection
                    if not self._poll_active:
                        self._callback.dispatch("appStatus", {'state': "resumePoll"})
                        self._poll_active = True
                time.sleep(self._guard_timeout)

            except Exception as ex:
                logging.exception(ex)
