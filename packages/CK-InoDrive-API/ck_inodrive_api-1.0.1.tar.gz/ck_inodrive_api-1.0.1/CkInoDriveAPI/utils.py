import re
import time
import json
import uuid
import struct
import logging

import msgpack

from .defines import CK


class CkUtils(object):

    def get_target_url(self, target='', props={}):
        try:
            secure = props.get('secure', False)
            port_number = props.get('port')
            path = props.get('path')
            timestamp = props.get('timestamp', True)
            dot_local = props.get('dotLocal', True)

            protocol_type = props.get('protocolType', "")
            if len([key for key in ['ws', 'http'] if key in protocol_type]) == 0:
                protocol_type = "ws"

            has_dot_local = target.find('.local') >= 0
            if has_dot_local:
                target = target.replace('.local', '')

            protocol = f"{protocol_type}{'s' if secure == True else ''}"
            port = None

            if port_number is not None and type(port_number) is not int:
                port_number = None

            if port_number is not None:
                port = f":{port_number}"

            if path is not None:
                path = path.replace('\\', '/')
                if path[0] == '/':
                    path = path[1:]

            cmd_delimiter = '--'
            is_ipv4 = True if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', target) else False
            if is_ipv4:
                for octet in target.split("."):
                    if int(octet) not in range(0, 255):
                        logging.error("Target has an octet out of the range from 0 to 255.")
                        break

            url = f"{protocol}://{target}"
            if not is_ipv4:
                if timestamp and secure == False:
                    url += f"{cmd_delimiter}T{int(time.time())}"

                if has_dot_local or dot_local:
                    url += '.local'

            url += f"{port if port is not None else ''}/{path if path is not None else ''}"

            return url
        except Exception as ex:
            logging.exception(ex)
            return ''

    def get_token(self, length=8, bytes=True):
        """Returns a random string of length string_length."""

        # Convert UUID format to a Python string.
        random = str(uuid.uuid4())

        # Make all characters uppercase.
        random = random.upper()

        # Remove the UUID '-'.
        random = random.replace("-", "")

        # Return the random string.
        token = random[0:length]
        return token.encode('ascii') if bytes else token

    def get_tlv(self, tlv_type=None, value=None, length=None):
        '''
        Creates -> Type Length CRC32 Value
        CRC32 is calculated over the value only.
        :param tlv_type: TLV type
        :param value: Byte string
        :param length: Optional. Value length
        :return: TLV byte string
        '''
        try:
            if tlv_type is None:
                logging.error('TLV type not provided...')
                return b''

            if value is None:
                # If there is no value size is 0
                return struct.pack('>II', tlv_type, 0)

            if type(value) is dict:
                value = json.dumps(value)

            if type(value) is int:
                value = bytes([value])

            if type(value) is list:
                value = bytes(value)

            if type(value) is not bytes:
                value = bytes(str(value), 'utf-8')

            # Value length
            length = length if length else len(value)
            if length > len(value):
                # If required length is larger then value length
                value = (bytes([0] * (length - len(value)))) + value

            return struct.pack('>II', tlv_type, length) + value

        except Exception as ex:
            logging.exception(ex)

        return b''

    def is_proper_c_type(self, data=None, data_type=None):
        try:
            if data is None or data_type is None:
                return False

            types = {
                'int8': 'b',
                's_byte': 'b',
                'uint8': 'B',
                'bool': 'B',
                'u_byte': 'B',
                'int16': 'h',
                's_int': 'h',
                'uint16': 'H',
                'u_int': 'H',
                'int32': 'i',
                's_dint': 'i',
                'uint32': 'I',
                'u_dint': 'I',
                'int64': 'q',
                's_long': 'q',
                'uint64': 'Q',
                'u_long': 'Q',
                'float': 'f',
                'double': 'd',
                'string': True,
                'macAddress': True,
                'ipV4': True,
            }

            if data_type not in types:
                return None

            value = struct.pack(f"{types.get(data_type)}", data)

            return True

        except Exception as ex:
            pass

        return False

    def get_typed_value(self, data=None, data_type=None, endian=False):
        try:
            if type(data) is not bytes:
                return None

            types = {
                'int8': 'b',
                's_byte': 'b',
                'uint8': 'B',
                'bool': 'B',
                'u_byte': 'B',
                'int16': 'h',
                's_int': 'h',
                'uint16': 'H',
                'u_int': 'H',
                'int32': 'i',
                's_dint': 'i',
                'uint32': 'I',
                'u_dint': 'I',
                'int64': 'q',
                's_long': 'q',
                'uint64': 'Q',
                'u_long': 'Q',
                'float': 'f',
                'double': 'd',
                'string': True,
                'macAddress': True,
                'ipV4': True,
            }

            if data_type not in types:
                return None

            endian_opt = '<' if endian else '>'

            if data_type == 'string':
                item = data.split(b'\x00')[0]
                return item.decode("utf-8")

            if data_type == 'macAddress':
                items = []
                for item in data:
                    items.append(f"{item:0>2X}")

                return ':'.join(items)

            if data_type == 'ipV4':
                items = []
                for item in data:
                    items.append(str(item))

                return '.'.join(items)

            value = struct.unpack(f"{endian_opt}{types.get(data_type)}", data)[0]
            return value

        except Exception as ex:
            logging.exception(ex)

        return None

    def decode_tlv_message(self, msg=None):
        try:
            if type(msg) is not bytes:
                return {'error': 'Message is not bytes'}

            if len(msg) < 8:
                return {'error': 'Message length is less then 8 bytes'}

            # Create decoded response object
            response = {'error': None, 'items': []}

            while len(msg) >= 8:
                # Get TLV type
                msg_type = self.get_typed_value(msg[0:4], 'uint32')
                # Get TLV length
                msg_length = self.get_typed_value(msg[4:8], 'uint32')

                data = b''
                if msg_length > 0:
                    data = msg[8:8 + msg_length]

                match msg_type:
                    case CK.UNIQUE_TOKEN:
                        response.update({'token': data})
                    case CK.TYPE.NTP_TIME:
                        seconds = self.get_typed_value(data[0:4], 'uint32')
                        milliseconds = self.get_typed_value(data[4:8], 'uint32')
                        ntp_time = seconds + round(milliseconds / pow(2, 32), 3)
                        response.update({'ntpTime': ntp_time})
                    case CK.RESPONSE:
                        resp = self.get_typed_value(data, 'uint8')
                        if resp != 0:
                            response.update({'error': resp})

                        response.update({
                            'type': msg_type,
                            'response': resp,
                        })
                    case CK.SPECIAL.CONSOLE:
                        response.update({'type': msg_type})
                    case CK.TYPE.MSG_PACK:
                        response['items'].append({'ctpType': msg_type, 'ctpLength': msg_length, 'data': self.msg_unpack(data)})
                    case _:
                        # Default
                        response['items'].append({'ctpType': msg_type, 'ctpLength': msg_length, 'data': data})

                # Get the rest of the message
                msg = msg[8 + msg_length:]

            return response
        except Exception as ex:
            logging.exception(ex)
            return {'error': str(ex)}

    def msg_pack(self, msg=None):
        try:
            return msgpack.packb(msg, use_bin_type=True)
        except Exception as ex:
            logging.exception(ex)

    def msg_unpack(self, msg=None):
        try:
            return msgpack.unpackb(msg, raw=False)
        except Exception as ex:
            logging.exception(ex)

    def get_msg_pack_tlv(self, payload):
        try:
            return self.get_tlv(CK.TYPE.MSG_PACK, self.msg_pack(payload))
        except Exception as ex:
            logging.exception(ex)

        return b''

    def get_var_c_type(self, var_type=None):
        try:
            if var_type is None:
                return None

            for c_type, type_props in CK.API_C_TYPES.items():
                if type_props['type'] == var_type:
                    return c_type
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_result_name_by_value(self, value):
        try:
            for result_name in CK.RESULT:
                if CK.RESULT[result_name] == value:
                    return result_name
        except Exception as ex:
            logging.exception(ex)

        return None

    def get_firmware_flags(self, flags):
        try:
            return {
                'production': True if flags & (1 << 6) else False,
                'failSafe': True if flags & (1 << 7) else False,
            }
        except Exception as ex:
            logging.exception(ex)

        return {}

    def get_pcb_flags(self, flags):
        try:
            return {}
        except Exception as ex:
            logging.exception(ex)

        return {}

    def get_fs_firmware_flags(self, flags):
        try:
            return {}
        except Exception as ex:
            logging.exception(ex)

        return {}

    def decode_discover_data(self, data):
        try:
            # Discover version
            # =======================================================================
            item_size = 1
            discover_version = Utils.get_typed_value(data[0:item_size], 'uint8')
            data = data[item_size:]
            # =======================================================================

            # SN
            # =======================================================================
            item_size = 25
            sn = Utils.get_typed_value(data[0:item_size], 'string')
            data = data[item_size:]
            # =======================================================================

            # PN
            # =======================================================================
            item_size = 25
            pn = Utils.get_typed_value(data[0:item_size], 'string')
            data = data[item_size:]
            # =======================================================================

            # Name
            # =======================================================================
            item_size = 33
            name = Utils.get_typed_value(data[0:item_size], 'string')
            data = data[item_size:]
            # =======================================================================

            # Firmware version
            # =======================================================================
            item_size = 1
            fw_major = Utils.get_typed_value(data[0:item_size], 'uint8')
            data = data[item_size:]

            item_size = 1
            fw_minor = Utils.get_typed_value(data[0:item_size], 'uint8')
            data = data[item_size:]

            item_size = 1
            fw_build = Utils.get_typed_value(data[0:item_size], 'uint8')
            data = data[item_size:]

            item_size = 1
            fw_type = Utils.get_typed_value(data[0:item_size], 'uint8')
            data = data[item_size:]

            firmware_flags = Utils.get_firmware_flags(fw_type)
            # =======================================================================

            # Networking
            # =======================================================================
            item_size = 6
            mac_address = Utils.get_typed_value(data[0:item_size], 'macAddress')
            data = data[item_size:]

            item_size = 4
            ip_address = Utils.get_typed_value(data[0:item_size], 'ipV4')
            data = data[item_size:]

            item_size = 4
            net_mask = Utils.get_typed_value(data[0:item_size], 'ipV4')
            data = data[item_size:]

            item_size = 4
            gateway = Utils.get_typed_value(data[0:item_size], 'ipV4')
            data = data[item_size:]

            item_size = 4
            dns = Utils.get_typed_value(data[0:item_size], 'ipV4')
            data = data[item_size:]
            # =======================================================================

            # PCB Version
            # =======================================================================
            pcb_major = 1
            pcb_minor = 1
            pcb_build = 1
            pcb_type = 0

            if discover_version >= 2:
                item_size = 1
                pcb_major = Utils.get_typed_value(data[0:item_size], 'uint8')
                data = data[item_size:]

                item_size = 1
                pcb_minor = Utils.get_typed_value(data[0:item_size], 'uint8')
                data = data[item_size:]

                item_size = 1
                pcb_build = Utils.get_typed_value(data[0:item_size], 'uint8')
                data = data[item_size:]

                if discover_version >= 3:
                    item_size = 1
                    pcb_type = Utils.get_typed_value(data[0:item_size], 'uint8')
                    data = data[item_size:]

            pcb_flags = Utils.get_pcb_flags(pcb_type)
            # =======================================================================

            return {
                'discoverVersion': discover_version,
                'sn': sn,
                'pn': pn,
                'name': name,
                'firmware': '.'.join([str(fw_major), str(fw_minor), str(fw_build)]),
                'firmwareFlags': firmware_flags,
                'network': {
                    'ip': ip_address,
                    'mask': net_mask,
                    'gw': gateway,
                    'dns': dns,
                    'mac': mac_address,
                },
                'pcb': '.'.join([str(pcb_major), str(pcb_minor), str(pcb_build)]),
                'pcbFlags': pcb_flags
            }
        except Exception as ex:
            logging.exception(ex)

        return None


Utils = CkUtils()
