import time
from abc import ABC, abstractmethod
from threading import Lock
import logging
import socket
import serial


class Transmitter(ABC):
    @abstractmethod
    def __init__(self):
        self.is_connect = False

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self, bufView, blocking=True, timeout=-1):
        pass

    @abstractmethod
    def receive(self, size, timeout=10):
        pass

    @abstractmethod
    def local_read(self, size):
        pass


class UDPTransmitter(Transmitter):
    def __init__(self, address):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffersize = 4096  # Default buffer size for UDP
        self.closed = False
        self.timeout_exception = socket.timeout
        self.host, self.port = address
        self.timeout = None

    def connect(self, timeout=1 / 500):
        self.sock.settimeout(timeout)
        self.closed = False
        self.timeout = timeout

    def disconnect(self):
        if not self.sock:
            raise Exception("Cannot close, socket never created")
        self.closed = True
        self.sock.close()

    def reconnect(self):
        self.sock.settimeout(self.timeout)
        self.closed = False

    def send(self, bufView: bytearray, blocking: bool = True, timeout: int = -1):
        sent = self.sock.sendto(bufView, (self.host, self.port))
        if not sent:
            raise RuntimeError("socket connection broken (send)?")
        return sent

    def receive(self, size: int):
        recvbuffer = b""
        try:
            if size:
                recvbuffer, _ = self.sock.recvfrom(size)
            else:
                recvbuffer, _ = self.sock.recvfrom(self.buffersize)
        except socket.timeout:
            return recvbuffer
        if not recvbuffer:
            raise RuntimeError("socket connection broken (recv)?")

        return recvbuffer

    def local_read(self, size=1):
        return self.sock.recvfrom(size)[0]


class TCPTransmitter(Transmitter):
    def __init__(self, address):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.buffersize = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

        self.closed = False
        self.timeout_exception = socket.timeout
        self.host = address[0]
        self.port = address[1]
        self.timeout = None

        print(self.host, self.port)

    def connect(self, timeout=1 / 500):
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(timeout)
        self.closed = False
        self.timeout = timeout

    def disconnect(self):
        if not self.sock:
            raise Exception("Cannot close, socket never created")
        self.closed = True
        self.sock.close()

    def reconnect(self, attempts=3, delay=1):
        for attempt in range(attempts):
            try:
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.sock.connect((self.host, self.port))
                self.sock.settimeout(self.timeout)
                self.closed = False
                return
            except (ConnectionResetError, OSError) as e:
                if attempt < attempts - 1:
                    time.sleep(delay)
                else:
                    raise e

    def send(self, bufView: bytearray, blocking: bool = True, timeout: int = -1):
        try:
            sent = self.sock.send(bufView)
            if not sent:
                raise RuntimeError("socket connection broken (send)?")
            return sent
        except (BrokenPipeError, ConnectionResetError, OSError):
            self.reconnect()
            sent = self.sock.send(bufView)
            if not sent:
                raise RuntimeError("socket connection broken (send)?")
            return sent

    def receive(self, size: int):
        recvbuffer = b""
        try:
            if size:
                recvbuffer = self.sock.recv(size)
            else:
                recvbuffer = self.sock.recv(self.buffersize)
        except socket.timeout:
            return recvbuffer
        if not recvbuffer:
            raise RuntimeError("socket connection broken (recv)?")

        return recvbuffer

    def local_read(self, size=1):
        return self.sock.recv(size)


class SerialTransmitter(Transmitter):
    def __init__(self, port: str, baud):
        super().__init__()
        self.write_lock = Lock()
        self.read_lock = Lock()
        self.serial_client = serial.Serial()
        self.serial_client.port = port
        self.serial_client.baudrate = baud
        self.serial_client.bytesize = serial.EIGHTBITS
        self.serial_client.parity = serial.PARITY_NONE
        self.serial_client.stopbits = serial.STOPBITS_ONE
        self.serial_client.timeout = 1
        self.serial_client.xonxoff = False
        self.serial_client.rtscts = False
        self.serial_client.dsrdtr = False
        self.serial_client.writeTimeout = 1

    def connect(self):
        if self.is_connect is False:
            try:
                self.serial_client.open()
                self.is_connect = True

                logging.info("Serial connect")
            except:
                logging.error("Cant connect to serial")
        else:
            logging.info("Serial_client is connected already")

    def disconnect(self):
        if self.is_connect is True:
            try:
                self.serial_client.close()
                self.is_serial_open = False

                logging.info("Close serial")
            except:
                logging.error("Cant close serial")
        else:
            logging.info("Serial_client is disconnected already")

    def send(self, bufView: bytearray, blocking: bool = True, timeout: int = -1):
        res = 0
        if self.write_lock.acquire(blocking, timeout):
            try:
                res = self.serial_client.write(bufView)
            finally:
                self.write_lock.release()
                if res > 0:
                    logging.info("RAW message sent by serial: {0}".format(bufView))
                return res

    def receive(self, size: int, timeout: int = 10):
        with self.read_lock:
            local_read = self.serial_client.read
            timeout = time.time() + timeout
            while True:
                if time.time() >= timeout:
                    logging.warning("Timeout occured when receiving a message")
                    break
                msg_header = local_read()
                if msg_header:
                    if ord(msg_header) == 36:
                        break

            msg = local_read(size - 1)

            logging.info("Recived msg_header: {0}; msg: {1}".format(msg_header, msg))
            return msg_header, msg

    def local_read(self, size: int):
        return self.serial_client.read(size)


def serialize(address, type):
    match type:
        case "udp":
            return UDPTransmitter(address)
        case "tcp":
            return TCPTransmitter(address)
        case "serial":
            return SerialTransmitter(address, 115200)


MSPCodes = {
    "MSP_API_VERSION": 1,
    "MSP_FC_VARIANT": 2,
    "MSP_FC_VERSION": 3,
    "MSP_BOARD_INFO": 4,
    "MSP_BUILD_INFO": 5,
    "MSP_NAME": 10,
    "MSP_SET_NAME": 11,
    "MSP_BATTERY_CONFIG": 32,
    "MSP_SET_BATTERY_CONFIG": 33,
    "MSP_MODE_RANGES": 34,
    "MSP_SET_MODE_RANGE": 35,
    "MSP_FEATURE_CONFIG": 36,
    "MSP_SET_FEATURE_CONFIG": 37,
    "MSP_BOARD_ALIGNMENT_CONFIG": 38,
    "MSP_SET_BOARD_ALIGNMENT_CONFIG": 39,
    "MSP_CURRENT_METER_CONFIG": 40,
    "MSP_SET_CURRENT_METER_CONFIG": 41,
    "MSP_MIXER_CONFIG": 42,
    "MSP_SET_MIXER_CONFIG": 43,
    "MSP_RX_CONFIG": 44,
    "MSP_SET_RX_CONFIG": 45,
    "MSP_LED_COLORS": 46,
    "MSP_SET_LED_COLORS": 47,
    "MSP_LED_STRIP_CONFIG": 48,
    "MSP_SET_LED_STRIP_CONFIG": 49,
    "MSP_RSSI_CONFIG": 50,
    "MSP_SET_RSSI_CONFIG": 51,
    "MSP_ADJUSTMENT_RANGES": 52,
    "MSP_SET_ADJUSTMENT_RANGE": 53,
    "MSP_CF_SERIAL_CONFIG": 54,
    "MSP_SET_CF_SERIAL_CONFIG": 55,
    "MSP_VOLTAGE_METER_CONFIG": 56,
    "MSP_SET_VOLTAGE_METER_CONFIG": 57,
    "MSP_SONAR": 58,
    "MSP_PID_CONTROLLER": 59,
    "MSP_SET_PID_CONTROLLER": 60,
    "MSP_ARMING_CONFIG": 61,
    "MSP_SET_ARMING_CONFIG": 62,
    "MSP_RX_MAP": 64,
    "MSP_SET_RX_MAP": 65,
    # 'MSP_BF_CONFIG':                  66, # DEPRECATED
    # 'MSP_SET_BF_CONFIG':              67, # DEPRECATED
    "MSP_SET_REBOOT": 68,
    # 'MSP_BF_BUILD_INFO':              69, # Not used
    "MSP_DATAFLASH_SUMMARY": 70,
    "MSP_DATAFLASH_READ": 71,
    "MSP_DATAFLASH_ERASE": 72,
    "MSP_LOOP_TIME": 73,
    "MSP_SET_LOOP_TIME": 74,
    "MSP_FAILSAFE_CONFIG": 75,
    "MSP_SET_FAILSAFE_CONFIG": 76,
    "MSP_RXFAIL_CONFIG": 77,
    "MSP_SET_RXFAIL_CONFIG": 78,
    "MSP_SDCARD_SUMMARY": 79,
    "MSP_BLACKBOX_CONFIG": 80,
    "MSP_SET_BLACKBOX_CONFIG": 81,
    "MSP_TRANSPONDER_CONFIG": 82,
    "MSP_SET_TRANSPONDER_CONFIG": 83,
    "MSP_OSD_CONFIG": 84,
    "MSP_SET_OSD_CONFIG": 85,
    "MSP_OSD_CHAR_READ": 86,
    "MSP_OSD_CHAR_WRITE": 87,
    "MSP_VTX_CONFIG": 88,
    "MSP_SET_VTX_CONFIG": 89,
    "MSP_ADVANCED_CONFIG": 90,
    "MSP_SET_ADVANCED_CONFIG": 91,
    "MSP_FILTER_CONFIG": 92,
    "MSP_SET_FILTER_CONFIG": 93,
    "MSP_PID_ADVANCED": 94,
    "MSP_SET_PID_ADVANCED": 95,
    "MSP_SENSOR_CONFIG": 96,
    "MSP_SET_SENSOR_CONFIG": 97,
    # 'MSP_SPECIAL_PARAMETERS':         98, // DEPRECATED
    "MSP_ARMING_DISABLE": 99,
    # 'MSP_SET_SPECIAL_PARAMETERS':     99, // DEPRECATED
    # 'MSP_IDENT':                      100, // DEPRECTED
    "MSP_STATUS": 101,
    "MSP_RAW_IMU": 102,
    "MSP_SERVO": 103,
    "MSP_MOTOR": 104,
    "MSP_RC": 105,
    "MSP_RAW_GPS": 106,
    "MSP_COMP_GPS": 107,
    "MSP_ATTITUDE": 108,
    "MSP_ALTITUDE": 109,
    "MSP_ANALOG": 110,
    "MSP_RC_TUNING": 111,
    "MSP_PID": 112,
    # 'MSP_BOX':                        113, // DEPRECATED
    "MSP_MISC": 114,  # DEPRECATED
    "MSP_BOXNAMES": 116,
    "MSP_PIDNAMES": 117,
    "MSP_WP": 118,  # Not used
    "MSP_BOXIDS": 119,
    "MSP_SERVO_CONFIGURATIONS": 120,
    "MSP_MOTOR_3D_CONFIG": 124,
    "MSP_RC_DEADBAND": 125,
    "MSP_SENSOR_ALIGNMENT": 126,
    "MSP_LED_STRIP_MODECOLOR": 127,
    "MSP_VOLTAGE_METERS": 128,
    "MSP_CURRENT_METERS": 129,
    "MSP_BATTERY_STATE": 130,
    "MSP_MOTOR_CONFIG": 131,
    "MSP_GPS_CONFIG": 132,
    "MSP_COMPASS_CONFIG": 133,
    "MSP_GPS_RESCUE": 135,
    "MSP_STATUS_EX": 150,
    "MSP_UID": 160,
    "MSP_GPS_SV_INFO": 164,
    "MSP_GPSSTATISTICS": 166,
    "MSP_DISPLAYPORT": 182,
    "MSP_COPY_PROFILE": 183,
    "MSP_BEEPER_CONFIG": 184,
    "MSP_SET_BEEPER_CONFIG": 185,
    "MSP_SET_RAW_RC": 200,
    "MSP_SET_RAW_GPS": 201,  # Not used
    "MSP_SET_PID": 202,
    # 'MSP_SET_BOX':                    203, // DEPRECATED
    "MSP_SET_RC_TUNING": 204,
    "MSP_ACC_CALIBRATION": 205,
    "MSP_MAG_CALIBRATION": 206,
    "MSP_SET_MISC": 207,  # DEPRECATED
    "MSP_RESET_CONF": 208,
    "MSP_SET_WP": 209,  # Not used
    "MSP_SELECT_SETTING": 210,
    "MSP_SET_HEADING": 211,  # Not used
    "MSP_SET_SERVO_CONFIGURATION": 212,
    "MSP_SET_MOTOR": 214,
    "MSP_SET_MOTOR_3D_CONFIG": 217,
    "MSP_SET_RC_DEADBAND": 218,
    "MSP_SET_RESET_CURR_PID": 219,
    "MSP_SET_SENSOR_ALIGNMENT": 220,
    "MSP_SET_LED_STRIP_MODECOLOR": 221,
    "MSP_ODOM": 222,
    "MSP_BLACKBOX": 223,
    "MSP_SET_COMPASS_CONFIG": 224,
    "MSP_SET_GPS_RESCUE": 225,
    "MSP_MODE_RANGES_EXTRA": 238,
    "MSP_SET_ACC_TRIM": 239,
    "MSP_ACC_TRIM": 240,
    "MSP_SERVO_MIX_RULES": 241,
    "MSP_SET_SERVO_MIX_RULE": 242,  # Not used
    "MSP_SET_4WAY_IF": 245,  # Not used
    "MSP_SET_RTC": 246,
    "MSP_RTC": 247,  # Not used
    "MSP_SET_BOARD_INFO": 248,  # Not used
    "MSP_SET_SIGNATURE": 249,  # Not used
    "MSP_EEPROM_WRITE": 250,
    "MSP_DEBUGMSG": 253,  # Not used
    "MSP_DEBUG": 254,
    # INAV specific codes
    "MSPV2_SETTING": 0x1003,
    "MSPV2_SET_SETTING": 0x1004,
    "MSP2_COMMON_MOTOR_MIXER": 0x1005,
    "MSP2_COMMON_SET_MOTOR_MIXER": 0x1006,
    "MSP2_COMMON_SETTING_INFO": 0x1007,
    "MSP2_COMMON_PG_LIST": 0x1008,
    "MSP2_CF_SERIAL_CONFIG": 0x1009,
    "MSP2_SET_CF_SERIAL_CONFIG": 0x100A,
    "MSPV2_INAV_STATUS": 0x2000,
    "MSPV2_INAV_OPTICAL_FLOW": 0x2001,
    "MSPV2_INAV_ANALOG": 0x2002,
    "MSPV2_INAV_MISC": 0x2003,
    "MSPV2_INAV_SET_MISC": 0x2004,
    "MSPV2_INAV_BATTERY_CONFIG": 0x2005,
    "MSPV2_INAV_SET_BATTERY_CONFIG": 0x2006,
    "MSPV2_INAV_RATE_PROFILE": 0x2007,
    "MSPV2_INAV_SET_RATE_PROFILE": 0x2008,
    "MSPV2_INAV_AIR_SPEED": 0x2009,
    "MSPV2_INAV_OUTPUT_MAPPING": 0x200A,
    "MSP2_INAV_MIXER": 0x2010,
    "MSP2_INAV_SET_MIXER": 0x2011,
    "MSP2_INAV_OSD_LAYOUTS": 0x2012,
    "MSP2_INAV_OSD_SET_LAYOUT_ITEM": 0x2013,
    "MSP2_INAV_OSD_ALARMS": 0x2014,
    "MSP2_INAV_OSD_SET_ALARMS": 0x2015,
    "MSP2_INAV_OSD_PREFERENCES": 0x2016,
    "MSP2_INAV_OSD_SET_PREFERENCES": 0x2017,
    "MSP2_INAV_MC_BRAKING": 0x200B,
    "MSP2_INAV_SET_MC_BRAKING": 0x200C,
    "MSP2_INAV_SELECT_BATTERY_PROFILE": 0x2018,
    "MSP2_INAV_DEBUG": 0x2019,
    "MSP2_BLACKBOX_CONFIG": 0x201A,
    "MSP2_SET_BLACKBOX_CONFIG": 0x201B,
    "MSP2_INAV_TEMP_SENSOR_CONFIG": 0x201C,
    "MSP2_INAV_SET_TEMP_SENSOR_CONFIG": 0x201D,
    "MSP2_INAV_TEMPERATURES": 0x201E,
    "MSP2_INAV_SERVO_MIXER": 0x2020,
    "MSP2_INAV_SET_SERVO_MIXER": 0x2021,
    "MSP2_INAV_LOGIC_CONDITIONS": 0x2022,
    "MSP2_INAV_SET_LOGIC_CONDITIONS": 0x2023,
    "MSP2_INAV_LOGIC_CONDITIONS_STATUS": 0x2026,
    "MSP2_PID": 0x2030,
    "MSP2_SET_PID": 0x2031,
    "MSP2_INAV_OPFLOW_CALIBRATION": 0x2032,
}
