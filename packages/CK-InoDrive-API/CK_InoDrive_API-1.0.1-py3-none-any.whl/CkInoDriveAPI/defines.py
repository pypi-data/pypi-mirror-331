class _MsgTypes(object):
    STRING = 0x11
    BLOB = 0x12
    INT_NUM = 0x13
    FLOAT_NUM = 0x14
    IPv4 = 0x15
    IPv4_CIDR = 0x16
    IPv6 = 0x17
    IPv6_CIDR = 0x18
    NTP_TIME = 0x19
    PTP_TIME = 0x2a
    RESERVED_TIME = 0x2b
    MSG_PACK = 0x2c


class _MsgModule(object):
    NAME = 0x101
    IP_CFG = 0x102
    IP = 0x103
    IP_MASK = 0x104
    IP_CIDR = 0x105
    GATEWAY = 0x106
    DNS_1 = 0x107
    DNS_2 = 0x108
    DHCP = 0x109
    FACTORY_DEFAULTS = 0x10a


class _MsgFile(object):
    UAPP_TRANSFER = 0x201
    FIRMWARE_TRANSFER = 0x202
    BACKUP_FW_TRANSFER = 0x203
    TRANSFER = 0x204
    LIST = 0x205
    WEBPAGE_TRANSFER = 0x208


class _MsgSpecial(object):
    UPGRADE_FIRMWARE = 0x301
    START_UAPP = 0x302
    STOP_UAPP = 0x303
    DELETE_UAPP = 0x304
    GET_DISCOVER_INFO = 0x305
    JSON_API = 0x306
    CONSOLE = 0x307


class _MsgResult(object):
    OK = 0x0
    OUT_OF_MEM = 0x1
    LENGTH_EXCEEDS_FRAME = 0x2
    UNKNOWN_TYPE = 0x3
    BAD_LENGTH_FOR_TYPE = 0x4
    UNIQUE_TOKEN_TOO_LONG = 0x5
    STRING_TOO_LONG = 0x6
    MULTIPLE_COMMANDS = 0x7
    FILE_ERROR = 0x8
    UPGRADE_ERROR = 0x9
    MSG_PACK_NOT_SUPPORTED = 0xB


class _MsgCommand(object):
    FILE_READ = 0x0
    FILE_WRITE = 0x1


class _MsgJsonApi(object):
    KEEP_ALIVE = 0
    VAR_LIST = 1
    VAR_ACCESS = 2
    DISCONNECT = 255


class _MsgPack(object):
    INVALID = 0x0
    BEACON = 0x1
    CONSOLE_ENABLE = 0x2
    TAKE_CONTROL = 0x3
    MODULE_INFO = 0x4

    GET_INPUTS = 0x10
    GET_OUTPUTS = 0x11
    GET_METRICS = 0x12
    LIST_VARIABLES = 0x16
    ACCESS_VARIABLES = 0x17

    SET_INPUT_POLARITY = 0x20
    SET_OUTPUTS = 0x21
    SET_HOLDING_BRAKE = 0x22


class _MsgPackErrors(object):
    NONE = 0x0
    OUT_OF_MEMORY = 0x1
    INTERNAL_ERROR = 0x2
    BAD_INPUT = 0x3
    BAD_VALUES = 0x4
    NOT_IMPLEMENTED = 0x5
    NOT_ALLOWED = 0x6


class _OPState(object):
    STATES = {
        "invalid": 0,
        "initializing": 1,
        "initFailed":  2,
        "faulted": 3,
        "operational": 4,

        "inFailSafeMode": 10,
        "connectingToPeers": 11,

        "motorNotConfigured": 20,
        "motorDisabled": 21,
        "motorI2tLimited": 22,
        "motorInSto": 23,
        "motorLimitSwitchActive": 24,
        "motorHoldingBrakeFault": 25,
        "motorStopped": 26,
        "motorRunning": 27,

        "externalControl": 40,
        "uAppNotPresent": 41,
        "uAppStartDelay": 42,
    }

    def get_state_by_value(self, state):
        for key, value in self.STATES.items():
            if state == value:
                return key
        return "invalid"


class _CkDefines(object):
    NOP = 0x0
    RESPONSE = 0x1
    UNIQUE_TOKEN = 0x2

    TYPE = _MsgTypes()
    MODULE = _MsgModule()
    FILE = _MsgFile()
    SPECIAL = _MsgSpecial()
    RESULT = _MsgResult()
    COMMAND = _MsgCommand()
    JSON_API = _MsgJsonApi()
    MSG_PACK = _MsgPack()
    MSG_PACK_ERRORS = _MsgPackErrors()

    API_VAR_ACCESS = {
        'none': 0,
        'read': 1,
        'write': 2,
        'readWrite': 3,
        0: "none",
        1: "read",
        2: "write",
        3: "readWrite",
    }
    API_C_TYPES = {
        'bool': {'type': 0, 'size': 1},
        's_byte': {'type': 1, 'size': 8},
        'u_byte': {'type': 2, 'size': 8},
        's_int': {'type': 3, 'size': 16},
        'u_int': {'type': 4, 'size': 16},
        's_dint': {'type': 5, 'size': 32},
        'u_dint': {'type': 6, 'size': 32},
        's_long': {'type': 7, 'size': 64},
        'u_long': {'type': 8, 'size': 64},
        'float': {'type': 9, 'size': 32},
        'double': {'type': 10, 'size': 64},
        'timer': {'type': 11, 'size': 0},
        'counter': {'type': 12, 'size': 0},
    }


# MessageTypes = _MsgDefines()
#
#
# class _VariableTypes(object):
#     def __init__(self):
#         self._types = [
#             self._Type(name='bool', type='bool', id=0, size=1),
#             self._Type(name='int8', type='int8', id=1, size=8),
#             self._Type(name='uint8', type='uint8', id=2, size=8),
#             self._Type(name='int16', type='int16', id=3, size=16),
#             self._Type(name='uint16', type='uint16', id=4, size=16),
#             self._Type(name='int32', type='int32', id=5, size=32),
#             self._Type(name='uint32', type='uint32', id=6, size=32),
#             self._Type(name='int64', type='int64', id=7, size=64),
#             self._Type(name='uint64', type='uint64', id=8, size=64),
#             self._Type(name='float32', type='float32', id=9, size=32),
#             self._Type(name='double64', type='double64', id=10, size=64),
#             self._Type(name='timer', type='timer', id=11, size=0),
#             self._Type(name='counter', type='counter', id=12, size=0),
#         ]
#
#         self.bool = self._types[0]
#         self.int8 = self._types[1]
#         self.uint8 = self._types[2]
#         self.int16 = self._types[3]
#         self.uint16 = self._types[4]
#         self.int32 = self._types[5]
#         self.uint32 = self._types[6]
#         self.int64 = self._types[7]
#         self.uint64 = self._types[8]
#         self.float32 = self._types[9]
#         self.double64 = self._types[10]
#         self.timer = self._types[11]
#         self.counter = self._types[12]
#
#     def index(self, index=None):
#         if index is None:
#             return None
#
#         if type(index) != int:
#             return None
#
#         if index > len(self._types) or index < 0:
#             return None
#
#         return self._types[index]
#
#     class _Type(object):
#         def __init__(self, **kwargs):
#             self.name = kwargs.get('name')
#             self.type = kwargs.get('type')
#             self.id = kwargs.get('id')
#             self.size = kwargs.get('size')
#
#
# VariableTypes = _VariableTypes()
#
#
# class _AccessTypes(object):
#     none = 0
#     read = 1
#     write = 2
#     readWrite = 3
#
#
# AccessTypes = _AccessTypes()
#
#
# class CK_CONST(object):
#     MOTION_INVALID_ATTR = float('-inf')
#
#
# class _CtpTypes(object):
#     CTP_TYPE_NOP = 0x00
#     CTP_TYPE_RESULT = 0x01
#     CTP_TYPE_UNIQUE_TOKEN = 0x02
#
#     CTP_TYPE_OPS = 0x0010
#     CTP_TYPE_STRING = 0x0011
#     CTP_TYPE_BLOB = 0x0012
#     CTP_TYPE_INT_NUM = 0x0013
#     CTP_TYPE_FLOAT_NUM = 0x0014
#     CTP_TYPE_IPv4 = 0x0015
#     CTP_TYPE_IPv4_CIDR = 0x0016
#     CTP_TYPE_IPv6 = 0x0017
#     CTP_TYPE_IPv6_CIDR = 0x0018
#
#     CTP_TYPE_MODULE_OPS = 0x0100
#     CTP_TYPE_MODULE_NAME = 0x0101
#     CTP_TYPE_MODULE_IP_CFG = 0x0102
#     CTP_TYPE_MODULE_IP = 0x0103
#     CTP_TYPE_MODULE_IP_MASK = 0x0104
#     CTP_TYPE_MODULE_IP_CIDR = 0x0105
#     CTP_TYPE_MODULE_GATEWAY = 0x0106
#     CTP_TYPE_MODULE_DNS_1 = 0x0107
#     CTP_TYPE_MODULE_DNS_2 = 0x0108
#     CTP_TYPE_MODULE_DHCP = 0x0109
#     CTP_TYPE_FACTORY_DEFAULTS = 0x010A
#
#     CTP_TYPE_FILE_OPS = 0x0200
#     CTP_TYPE_UAPP_TRANSFER = 0x0201
#     CTP_TYPE_FIRMWARE_TRANSFER = 0x0202
#     CTP_TYPE_BACKUP_FIRMWARE_TRANSFER = 0x0203
#     CTP_TYPE_FILE_TRANSFER = 0x0204
#     CTP_TYPE_FILE_LIST = 0x0205
#
#     CTP_TYPE_SPECIAL = 0x0300
#     CTP_TYPE_MODULE_UPGRADE_FIRMWARE = 0x0301
#     CTP_TYPE_MODULE_START_UAPP = 0x0302
#     CTP_TYPE_MODULE_STOP_UAPP = 0x0303
#     CTP_TYPE_MODULE_DELETE_UAPP = 0x0304
#     CTP_TYPE_GET_HW_INFO = 0x0305
#
#
# CtpTypes = _CtpTypes()
#
#
# class _InoDrivePorts(object):
#     SMEEX_UDP_PORT = 17737
#     INTER_MODULE_COMMS_UDP_PORT = 17738
#
#
# InoDrivePorts = _InoDrivePorts()
#
#
# class _LED_Mode(object):
#     OFF = 0
#     ON = 1
#     BLINK = 2
#     OSCILLATE = 3
#     STROBE = 4
#     PULSE = 5
#     DOUBLE_PULSE = 6
#     NUM_MODES = 7
#
#
# InoDrive_LedMode = _LED_Mode()
#
#
# class _InputsPolarity(object):
#     PNP = 0
#     NPN = 1
#
#
# InoDriveInputsPolarity = _InputsPolarity()
#
#
# class _Dimensions(object):
#     # Torque
#     DIM_TORQUE_RELATIVE_RATED = 0
#     DIM_TORQUE_RELATIVE_MAX = 1
#     DIM_TORQUE_NM = 2
#     DIM_TORQUE_FTLB = 3
#     DIM_TORQUE_INLB = 4
#
#     # Speed
#     DIM_SPEED_RELATIVE_RATED = 16
#     DIM_SPEED_RELATIVE_MAX = 17
#     DIM_SPEED_USER_UNITS_PER_SEC = 18
#     DIM_SPEED_ENC_COUNTS_PER_SEC = 19
#
#     # Accel / Decel
#     DIM_ACCEL_USER_UNITS_PER_SEC_SQUARED = 32
#     DIM_ACCEL_TIME_SECONDS = 33
#     DIM_ACCEL_DISTANCE_USER_UNITS = 34
#     DIM_ACCEL_DISTANCE_ENC_COUNTS = 35
#
#     # Distance
#     DIM_DISTANCE_USER_UNITS = 48
#     DIM_DISTANCE_ENC_COUNTS = 49
#
#     DIM_NONE = 127
#
#
# Dimensions = _Dimensions()
#
#
# class _MotionCommands(object):
#     MOTOR_COMMAND_NOP = 0
#     MOTOR_COMMAND_INIT_ENCODER = 1
#     MOTOR_COMMAND_RUN = 2
#     MOTOR_COMMAND_STOP = 3
#     MOTOR_COMMAND_POSITION_REL = 4
#     MOTOR_COMMAND_POSITION_ABS = 5
#     MOTOR_COMMAND_HOME_AXIS = 6
#     MOTOR_COMMAND_LEARN_KV = 7
#     MOTOR_COMMAND_LEARN_I = 8
#
#     MOTOR_COMMAND_INVALID = 9
#
#
# MotionCommands = _MotionCommands()
#
#
# class _PositionHold(object):
#     POS_HOLD_FREE_SPIN = 0
#     POS_HOLD_REGEN_BRAKE = 1
#     POS_HOLD_ACTIVE_HOLD = 2
#     POS_HOLD_WITH_HBRAKE = 3
#
#     POS_HOLD_INVALID = 4
#
#
# PositionHold = _PositionHold()
#
#
# class MotionProfile(object):
#     def __init__(self):
#         self.attributes = {}
#         self.attributes['torque'] = (100.0, Dimensions.DIM_TORQUE_RELATIVE_RATED)
#         self.attributes['speed'] = (50.0, Dimensions.DIM_SPEED_RELATIVE_RATED)
#         self.attributes['accel'] = (1.0, Dimensions.DIM_ACCEL_TIME_SECONDS)
#         self.attributes['decel'] = (1.0, Dimensions.DIM_ACCEL_TIME_SECONDS)
#         self.attributes['jerk_limiting'] = (0.5, Dimensions.DIM_NONE)
#         self.attributes['position'] = (CK_CONST.MOTION_INVALID_ATTR, Dimensions.DIM_DISTANCE_USER_UNITS)
#
#     def get_bytes(self):
#         padding = bytes([0, 0, 0, 0, 0, 0, 0, 0])
#         motion_profile_bytes = struct.pack("<fffffBBBBB3s", \
#                                            self.attributes['torque'][0], \
#                                            self.attributes['speed'][0], \
#                                            self.attributes['accel'][0], \
#                                            self.attributes['decel'][0], \
#                                            self.attributes['jerk_limiting'][0], \
#                                            self.attributes['torque'][1], \
#                                            self.attributes['speed'][1], \
#                                            self.attributes['position'][1], \
#                                            self.attributes['accel'][1], \
#                                            self.attributes['decel'][1], \
#                                            padding)
#         return motion_profile_bytes
#
#
# class InputsConfig(object):
#     def __init__(self):
#         self.inputs = {}
#         self.inputs["home"] = (-1, False)
#         self.inputs["positive_end"] = (-1, False)
#         self.inputs["negative_end"] = (-1, False)
#
#     def set(self, signal_name, input_number, inverted):
#         if type(signal_name) != str:
#             raise TypeError("signal_name must be a string")
#         if signal_name != "home" and signal_name != "positive_end" and signal_name != "negative_end":
#             raise ValueError("signal_name must be 'home', 'positive_end', or 'negative_end' ")
#         if type(input_number) != int:
#             raise TypeError("input_number must be int")
#         if input_number < -1 or input_number > 3:
#             raise ValueError("input_number must be 0 to 3, or -1 for disabled signals ")
#         if type(inverted) != bool:
#             raise TypeError("inverted must be bool")
#
#         self.inputs[signal_name] = (input_number, inverted)
#
#     def get_bytes(self):
#         padding = bytes([0, 0, 0, 0, 0, 0, 0, 0])
#         inputs_bytes = struct.pack("<bBbBbB2s",
#                                    self.inputs["home"][0],
#                                    self.inputs["home"][1],
#                                    self.inputs["positive_end"][0],
#                                    self.inputs["positive_end"][1],
#                                    self.inputs["negative_end"][0],
#                                    self.inputs["negative_end"][1],
#                                    padding)
#         return inputs_bytes
#
#
# class CkDefinitions(object):
#     MSG_TYPE = _MsgDefines()


CK = _CkDefines()
OP_STATE = _OPState()
