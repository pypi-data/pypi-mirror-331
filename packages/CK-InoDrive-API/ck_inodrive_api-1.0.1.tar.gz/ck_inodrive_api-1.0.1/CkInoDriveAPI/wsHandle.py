import time
import logging
import uuid
import threading
import websocket
import ssl
import os

from .defines import CK
from .utils import Utils


class InoDriveWS(object):
    _connecting = False
    _disconnecting = False

    def __init__(self, **kwargs):
        # Connection ID
        self._id = kwargs.get('id', str(uuid.uuid4()))

        # Connection Properties
        key = [key for key in ['target', 'host'] if key in kwargs]
        if key:
            self._target = kwargs.get(key[0])
        else:
            self._target = ""

        if type(self._target) is not str or self._target == "":
            raise Exception(f"Target device not provided...")

        self._port = kwargs.get('port')
        self._path = kwargs.get('path', 'cmd')
        self._secure = kwargs.get('secure', False)

        # Other
        self._reconnect_attempts = kwargs.get('reconnectAttempts', 3)

        # Timeouts
        # connectTimeout should be 3 - 15 seconds. Low values like 3-5 should be good, even over the internet.
        # socketTimeout should be ~10. When a file transfer overwrites a file, there could be 2-3 seconds of
        # filesystem overhead and the transfer of 300k+ firmware file takes 2+ seconds.
        # Maybe we need separate file transfer and variable API timeouts.
        self._create_timeout = kwargs.get('createTimeout', 15)
        self._connect_timeout = kwargs.get('connectTimeout', 15)
        self._socket_timeout = kwargs.get('socketTimeout', 10)
        self._request_timeout = kwargs.get('requestTimeout', 10)
        self._keep_alive_timeout = kwargs.get('keepAliveTimeout', 5)
        self._reconnect_timeout = (self._connect_timeout / 3) - 0.5
        if self._reconnect_timeout <= 0:
            raise Exception(f"Connect timeout too small. Has to be at least: 5")
            self._reconnect_timeout = 1

        self._ws_input_buff_size = kwargs.get('wsInputBuffer', None)

        # Flags
        self._auto_connect = kwargs.get('autoConnect', False)
        self._reconnect = kwargs.get('reconnect', True)
        self._keep_alive = kwargs.get('keepAlive', True)
        self._binary = kwargs.get('binary', True)

        if self._keep_alive_timeout < 1:
            self._keep_alive_timeout = 1

        self._target_url = self.get_target()

        self._reconnect_count = self._reconnect_attempts

        self._last_request_time = int(time.time())

        self._msg_queue = {}

        self._msg_send_allowed_timeout = 0.1
        self._msg_send_allowed = True

        self._cmd_state = None
        self._state = 'disconnected'

        self._wsapp = None
        self._ws_thread = None
        self._ws_thread_running = False

        self._connection_guard_timeout = 0.1
        self._connection_guard_timer = None

        # Callbacks
        self._callback = kwargs.get("callback")

    @property
    def callback(self):
        return self._callback

    @property
    def on(self):
        return self._callback.on

    def dispose(self):
        try:
            logging.debug(f"Dispose connection -> host [{self._target}]...")
            self._cmd_state = "dispose"

            self.disconnect()

            self._msg_queue = {}

        except Exception as ex:
            logging.error(str(ex))

    def get_target(self, **kwargs):
        if not isinstance(kwargs, dict):
            kwargs = {}
        url = Utils.get_target_url(self._target, {'port': self._port, 'path': self._path, 'secure': self._secure, **kwargs})
        if self._ws_input_buff_size is not None:
            url = f"{url}?ibs={self._ws_input_buff_size}"
        return url

    def set_target(self, target=None):
        try:
            if type(target) is not str:
                logging.error(f"Target is not string: {target}")
                return
            self._target = target
            self._target_url = Utils.get_target_url(self._target, {'port': self._port, 'path': self._path, 'secure': self._secure})
        except Exception as ex:
            logging.exception(ex)

    def connect(self, target=None):
        try:
            self._connecting = True

            if self._state == "connected":
                self._connecting = False
                return True

            if type(target) is str:
                self._target_url = self._target

            timeout = False

            attempt = 1
            while attempt <= self._reconnect_attempts:
                self._state = "connecting"
                self._cmd_state = "connect"

                if self._connection_guard_timer is None:
                    self._guard_start()

                if not getattr(self, "_wsapp", None):
                    logging.warning(f"Connect to: ---> {self._target_url}")
                    timestamp = True if attempt == self._reconnect_attempts else False
                    url = self.get_target(timestamp=timestamp, secure=self._secure)
                    # WebSocket instance
                    self._wsapp = websocket.WebSocketApp(
                        url,
                        on_open=self.on_connect,
                        on_close=self.on_disconnect,
                        on_error=self.on_error,
                        on_message=self.on_message
                    )

                    # Secure Socket Options
                    sslopt = None
                    if self._secure:
                        ca = f"{os.path.join(os.path.dirname(__file__))}\\ck_ca.crt"

                        sslopt = {
                            "ca_certs": ca,
                            "cert_reqs": ssl.CERT_REQUIRED
                        }

                    websocket.setdefaulttimeout(self._connect_timeout)
                    self._ws_thread = threading.Thread(
                        target=self._wsapp.run_forever,
                        args=(
                            None,
                            sslopt,
                        ),
                        daemon=True)
                    self._ws_thread_running = True
                    self._ws_thread.start()

                time_begin = int(time.time())
                while (int(time.time()) - time_begin) < self._reconnect_timeout:
                    if timeout or self._state != "connecting":
                        break
                    time.sleep(1)

                if not self.connected():
                    if self._wsapp is not None:
                        self._wsapp.close()
                        self._dispose_ws()

                    if timeout:
                        break

                    attempt += 1
                    continue

                break

            timeout_interval = self._connect_timeout
            while not self.connected() and timeout_interval > 0:
                timeout_interval -= 1
                time.sleep(1)

            if not self.connected():
                timeout = True

            if self.connected():
                self._guard_start()
                return True
            else:
                if timeout:
                    logging.error(f"Connecting to: {self._target} timeout...")
                elif attempt >= self._reconnect_attempts:
                    logging.error(f"Connecting to: {self._target} reconnect...")
                else:
                    logging.error(f"Connecting to: {self._target} failed...")
            self._connecting = False

        except Exception as ex:
            logging.info(str(ex))

        return False

    def disconnect(self, timeout=None):
        try:
            if self._state == "disconnected":
                self._dispose_ws()
                return

            self._disconnecting = True

            self._state = 'disconnecting'
            self._cmd_state = 'disconnect'
            self._guard_stop()

            # Close Websocket App
            if self._wsapp:
                self._wsapp.close()

            timeout = False
            timeout_interval = self._connect_timeout
            while not self.disconnected() and timeout_interval > 0:
                timeout_interval -= 1
                time.sleep(1)

            if not self.disconnected():
                timeout = True

            if timeout:
                logging.error(f"Disconnecting from: {self._target} timeout...")
            else:
                self._dispose_ws()

            return self.disconnected()

        except Exception as ex:
            logging.error(str(ex))

        return False

    def connected(self):
        return True if self._state == "connected" else False

    def disconnected(self):
        return True if self._state == "disconnected" else False

    def set_binary(self, flag):
        return {}

    def send(self, data):
        logging.exception("Method not implemented")

    def request(self, payload=None, timeout=None, blocking=True):
        try:
            if type(payload) is not bytes:
                return {'success': False, 'error': 'Payload is None...'}

            self._last_request_time = int(time.time())

            token = Utils.get_token(8, bytes=False)

            msg = b''
            msg += Utils.get_tlv(CK.UNIQUE_TOKEN, token)
            msg += payload

            queue_item = {
                'state': "sent",
                'time': self._last_request_time,
                'error': None,
                'response': None,
            }

            if blocking:
                # If we are going to wait for response addi the item to the queue
                self._msg_queue_put(token, queue_item)

            if not self._send(msg):
                # Send failed for some reason
                return {'success': False, 'error': 'Send failed...'}

            # If we are not going to wait for response just return success
            if not blocking:
                return {'success': True}

            if timeout:
                timeout = timeout * 100
            else:
                timeout = self._socket_timeout * 100

            while queue_item['response'] is None and timeout > 0:
                timeout -= 1
                time.sleep(0.01)

            if queue_item['response'] is None and timeout <= 0:
                return {'success': False, 'error': 'timeout'}

            response = queue_item['response']

            # Remove this request item from the queue
            self._msg_queue.pop(token, None)

            return response

        except Exception as ex:
            logging.error(str(ex))
            return {'success': False, 'error': ex}

    def msg_pack_request(self, msg=[]):
        try:
            msg_tlv = Utils.get_msg_pack_tlv(msg)
            response = self.request(msg_tlv)

            if response.get('error'):
                return {
                    'success': False,
                    'error': response['error'],
                }

            if len(response['items']) == 0:
                return {
                    'success': False,
                    'error': 'Response items are missing...'
                }

            if response['items'][0]['ctpType'] != CK.TYPE.MSG_PACK:
                return {
                    'success': False,
                    'error': 'Response item is not MsgPack...'
                }

            msg_pack_data = response['items'][0]['data']

            if len(msg_pack_data) < 2:
                return {
                    'success': False,
                    'error': 'MsgPack returns less then required two items - success and error'
                }

            if not msg_pack_data[0]:
                # todo: Decode the message -> msg_pack_data[1]
                return {
                    'success': False,
                    'error': msg_pack_data[1],
                }

            response_msg = {
                'success': True,
                'token': response.get('token'),
                'data': msg_pack_data[2:],
            }

            if response.get('ntpTime'):
                response_msg.update({'ntpTime': response['ntpTime']})

            return response_msg
        except Exception as ex:
            return {
                'success': False,
                'error': str(ex)
            }

    def on_message(self, wsapp, msg):
        try:
            if self._binary:
                msg = Utils.decode_tlv_message(msg)

            msg_token = None
            if msg.get("token"):
                msg_token = Utils.get_typed_value(msg['token'][0:], 'string')

            msg_request = self._msg_queue_get(msg_token)
            if msg_request:
                msg_request['state'] = "received"
                if msg.get('error'):
                    logging.error(msg['error'])
                    msg_request['error'] = True
                elif msg['response'] != CK.RESULT.OK:
                    result_name = Utils.get_result_name_by_value(msg['response'])
                    logging.error(f"Unexpected response type [{msg['response']}]: {result_name}")
                    msg_request['error'] = True
                else:
                    msg_request['response'] = msg

                self._msg_queue_pull(msg_token)

            self._callback.dispatch("message", msg)
        except Exception as ex:
            logging.exception(str(ex))

    def on_connect(self, wsapp):
        logging.debug(f"Connection connected: {self._target_url}")

        self._state = "connected"
        self._connecting = False

        self._callback.dispatch("connect", wsapp)

    def on_disconnect(self, wsapp, close_status_code, close_msg):
        logging.debug(f"Connection disconnected: {self._target_url}")

        self._disconnecting = False

        self._state = "disconnected"

        self._callback.dispatch("disconnect", wsapp, close_status_code, close_msg)

    def on_error(self, wsapp, evt):
        logging.exception(f"Connection error: {self._target_url}")

        if "errno" in evt:
            errno = evt.errno
            if errno == 10061:
                if self._secure:
                    # Tried secure websocket connection and got active connection refusal, try unsecure websocket connection
                    self._secure = False
                    self._target_url = self.get_target()

        self._state = "error"

        self._callback.dispatch("error", wsapp, evt)

    def _connect(self):
        logging.exception("Method not implemented...")

    def _disconnect(self):
        logging.exception("Method not implemented...")

    def _msg_queue_get(self, token):
        try:
            return self._msg_queue.get(token)
        except Exception as ex:
            pass
        return None

    def _msg_queue_put(self, token, props):
        if token in self._msg_queue:
            # Should never happen
            logging.warning(f"Message with token [ {token} ] already exist...")
            logging.warning(f"Connection message queue [ {token} ] -> Duplicated token...")
            return
        self._msg_queue.update({token: props})

    def _msg_queue_pull(self, token):
        try:
            self._msg_queue.pop(token)
        except Exception as ex:
            pass

    def _dispose_ws(self):
        try:
            if self._wsapp:
                self._wsapp.on_open = {}
                self._wsapp.on_close = {}
                self._wsapp.on_error = {}
                self._wsapp.on_message = {}
                self._wsapp = None

            if self._ws_thread:
                self._ws_thread.join()
                self._ws_thread_running = False
                self._ws_thread = None
        except Exception as ex:
            logging.exception(ex)

    def _send(self, data=None):
        try:
            if self.connected():
                self._wsapp.sock.send_binary(data)
                return True
        except Exception as ex:
            logging.error(str(ex))

            return False

    def _guard_start(self):
        if not self._connection_guard_timer:
            logging.warning(f"Start guard [ {self._target_url} ]")
            self._connection_guard_timer = threading.Thread(target=self._connection_guard_loop, daemon=True)
            self._connection_guard_running = True
            self._connection_guard_timer.start()

    def _guard_stop(self):
        logging.warning(f"Stop guard [ {self._target_url} ]")
        self._connection_guard_running = False
        self._connection_guard_timer.join()
        self._connection_guard_timer = None

    def _connection_guard_loop(self):
        while self._connection_guard_running:
            try:
                if self._cmd_state == "dispose":
                    return

                expire_list = []
                ws_time = int(time.time())

                # Garbage Collect Message Queues Which Timeout
                # =====================================================================================================
                for token, props in self._msg_queue.items():
                    if props and type(props) is dict:
                        if (ws_time - props['time']) >= self._request_timeout:
                            props['state'] = "timeout"
                            expire_list.append(token)

                for token in expire_list:
                    logging.warning(f"Connection {self._target_url} token [ {token} ] timeout -> Garbage collected...")
                    if self._msg_queue[token]['error']:
                        logging.error(f"Request ID:{token} timeout...")
                    del self._msg_queue[token]

                # Keep Alive
                # =====================================================================================================
                if self.connected():
                    time_delta = int(time.time()) - self._last_request_time
                    if time_delta >= self._keep_alive_timeout:
                        try:
                            self.request(Utils.get_tlv(CK.NOP), blocking=False)
                            logging.debug(f"Keep alive: {self._target_url}")
                        except Exception as ex:
                            logging.error(str(ex))

                # Reconnect
                # =====================================================================================================
                if self._reconnect and self._cmd_state == "connect" and not self.connected():
                    if getattr(self, "_reconnect_time", 0):
                        if (int(time.time()) - self._reconnect_time) >= self._reconnect_timeout:
                            self._reconnect_time = None
                            if not self._connecting:
                                self.connect()
                    else:
                        self._reconnect_time = int(time.time())
                        # Unhandled exception - give it some time to recover
                        time.sleep(1)
                time.sleep(self._connection_guard_timeout)
            except Exception as ex:
                logging.error(str(ex))
