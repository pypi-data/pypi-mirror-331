"""
This module provides the MSPDriverManagerGRPC class which implements the gRPC server for managing the multirotor control system.

Classes:
    MSPDriverManagerGRPC: Implements the gRPC server for managing the multirotor control system.
"""

import grpc
import time
import os
import asyncio
from threading import Thread
import logging

from _driver.msp_controller import MultirotorControl
from _driver import serialize, UDPTransmitter, TCPTransmitter, SerialTransmitter
from _protos import api_pb2 as api_pb2
from _protos import api_pb2_grpc as api_pb2_grpc
from _protos.api_pb2_grpc import add_DriverManagerServicer_to_server


# TODO: перевести сервис на наследников от процессов multiprocessing
class MSPDriverManagerGRPC(api_pb2_grpc.DriverManagerServicer):
    """
    Implements the gRPC server for managing the multirotor control system.

    Methods:
        __init__: Initializes the MSPDriverManagerGRPC class.
        __init_logging__: Initializes logging for the MSPDriverManagerGRPC class.
        update_data: Continuously updates sensor data from the multirotor controller.
        GetImuDataRPC: Handles gRPC requests for IMU data.
        GetSonarDataRPC: Handles gRPC requests for sonar data.
        GetAnalogDataRPC: Handles gRPC requests for analog data.
        GetAttitudeDataRPC: Handles gRPC requests for attitude data.
        GetOdometryDataRPC: Handles gRPC requests for odometry data.
        GetOpticalFlowDataRPC: Handles gRPC requests for optical flow data.
        GetFlagsDataRPC: Handles gRPC requests for flags data.
        SendRcDataRPC: Handles gRPC requests to send RC data.
    """

    def __init__(
        self,
        ip="192.168.2.113",
        type="TCP",
        serial=None,
        analyzer_flag=False,
        log=False,
        output=False,
    ):
        """
        Initializes the MSPDriverManagerGRPC class, sets up logging, and connects to the multirotor controller.
        """
        if log:
            self.__init_logging__("log")
        else:
            self.data_logging = logging.getLogger("msp_data")
            self.state_logging = logging.getLogger("state")
            self.driver_logging = logging.getLogger("state")
            self.data_logging.disabled = True
            self.state_logging.disabled = True
            self.driver_logging.disabled = True

        if type == "TCP":
            if ip is not None:
                self.transmitter = TCPTransmitter((ip, 5760))

        if type == "SERIAL":
            if serial is not None:
                self.transmitter = SerialTransmitter(serial, 115200)

        self.msp_controller = MultirotorControl(self.transmitter)
        self.state_logging.info("[MSP]: Initialize multirotor controller")

        self.state_logging.info(
            "[MSP]: Connecting to {type} transmitter".format(type=type)
        )
        self.state_logging.info(
            "[MSP]: Connecting to {ip}".format(ip=ip if type == "TCP" else serial)
        )
        self.state_logging.info(
            "[MSP]: Analyzer optimization data: {type}".format(type=analyzer_flag)
        )

        self.state_logging.info("[MSP]: Connecting to the multirotor controller")
        self.msp_controller.connect()
        self.state_logging.info("[MSP]: Connected to the multirotor controller")

        self.rc_send = self.rc_get = [1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000]
        self.analyzer_state = analyzer_flag

        self.output_mode = output

        self.start_time = time.time()

    def __init_logging__(self, log_directory="log"):
        """
        Initializes logging for the MSPDriverManagerGRPC class.

        Args:
            log_directory (str): The directory where log files will be stored.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.data_logging = logging.getLogger("msp_data")
        self.data_logging.setLevel(logging.INFO)
        self.data_formater = logging.Formatter("%(asctime)s - %(message)s")
        self.data_handler = logging.FileHandler(
            os.path.join(log_directory, "msp_data.log")
        )
        self.data_handler.setFormatter(self.data_formater)
        self.data_logging.addHandler(self.data_handler)

        self.state_logging = logging.getLogger("state")
        self.state_logging.setLevel(logging.INFO)
        self.state_formater = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.state_handler = logging.FileHandler(
            os.path.join(log_directory, "msp_state.log")
        )
        self.state_handler.setFormatter(self.state_formater)
        self.state_logging.addHandler(self.state_handler)

        self.state_logging.info("[MSP]: Initialize logging")

    def update_data(self):
        """
        Continuously updates sensor data from the multirotor controller.
        """
        while True:
            if self.analyzer_state:
                self.msp_controller.msp_read_motor_data()
                self.msp_controller.msp_read_analog_data()
                self.msp_controller.msp_read_imu_data()
            else:
                self.msp_controller.msp_read_attitude_data()
                self.msp_controller.msp_read_odom_data()
                self.msp_controller.msp_send_rc_cmd(self.rc_send)
                logging.info("[RC_DATA]:" + str(self.rc_send))

            if self.output_mode:
                print(self.msp_controller.SENSOR_DATA)
                print("\n")

            self.data_logging.info(
                "[SENSOR_DARA]:" + str(self.msp_controller.SENSOR_DATA)
            )
            time.sleep(1 / 50)

    async def GetImuDataRPC(self, request, context):
        """
        Handles gRPC requests for sonar data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.SonarData: The sonar data.
        """
        self.state_logging.info(f"[IMU]: Request from: {context.peer()}")
        try:
            data = api_pb2.IMUData(
                gyro=api_pb2.Vector3(
                    x=self.msp_controller.SENSOR_DATA["gyroscope"][0],
                    y=self.msp_controller.SENSOR_DATA["gyroscope"][1],
                    z=self.msp_controller.SENSOR_DATA["gyroscope"][2],
                ),
                acc=api_pb2.Vector3(
                    x=self.msp_controller.SENSOR_DATA["accelerometer"][0],
                    y=self.msp_controller.SENSOR_DATA["accelerometer"][1],
                    z=self.msp_controller.SENSOR_DATA["accelerometer"][2],
                ),
            )
            time.sleep(0.05)
            return data
        except Exception as e:
            self.state_logging.error("[IMU]: " + str(e))

    async def GetSonarDataRPC(self, request, context):
        """
        Handles gRPC requests for sonar data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.SonarData: The sonar data.
        """
        self.state_logging.info(f"[SONAR]: Request from: {context.peer()}")
        try:
            data = api_pb2.SonarData(
                sonar=self.msp_controller.SENSOR_DATA["sonar"],
            )
            time.sleep(0.01)
            return data
        except Exception as e:
            self.state_logging.error("[SONAR]: " + str(e))

    async def GetMotorDataRPC(self, request, context):
        """
        Handles gRPC requests for motor data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.MotorData: The motor data.
        """
        if self.analyzer_state:
            self.state_logging.info(f"[MOTOR]: Request from: {context.peer()}")
            try:
                data = api_pb2.MotorData(
                    motor_1=self.msp_controller.MOTOR_DATA[0],
                    motor_2=self.msp_controller.MOTOR_DATA[1],
                    motor_3=self.msp_controller.MOTOR_DATA[2],
                    motor_4=self.msp_controller.MOTOR_DATA[3],
                )
                time.sleep(0.01)
                return data

            except Exception as e:
                self.state_logging.error("[MOTOR]: " + str(e))
        else:
            self.state_logging.error(
                "[MOTOR]: " + "Get error, only available with analyzer"
            )

    async def GetAnalogDataRPC(self, request, context):
        """
        Handles gRPC requests for analog data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.AnalogData: The analog data.
        """
        if self.analyzer_state:
            self.state_logging.info(f"[ANALOG]: Request from: {context.peer()}")
            try:
                data = api_pb2.AnalogData(
                    voltage=self.msp_controller.ANALOG["voltage"],
                    mAhdrawn=self.msp_controller.ANALOG["mAhdrawn"],
                    rssi=self.msp_controller.ANALOG["rssi"],
                    amperage=self.msp_controller.ANALOG["amperage"],
                )
                time.sleep(0.01)
                return data
            except Exception as e:
                self.state_logging.error("[ANALOG]: " + str(e))
        else:
            self.state_logging.error(
                "[ANALOG]: " + "Get error, only available with analyzer"
            )

    async def GetAttitudeDataRPC(self, request, context):
        """
        Handles gRPC requests for attitude data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.AttitudeData: The attitude data.
        """
        self.state_logging.info(f"[ATTITUDE]: Request from: {context.peer()}")
        try:
            data = api_pb2.AttitudeData(
                orient=api_pb2.Vector3(
                    x=self.msp_controller.SENSOR_DATA["kinematics"][0],
                    y=self.msp_controller.SENSOR_DATA["kinematics"][1],
                    z=self.msp_controller.SENSOR_DATA["kinematics"][2],
                ),
            )
            time.sleep(0.01)
            return data
        except Exception as e:
            self.state_logging.error("[ATTITUDE]: " + str(e))

    async def GetOdometryDataRPC(self, request, context):
        """
        Handles gRPC requests for odometry data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.OdometryData: The odometry data.
        """
        self.state_logging.info(f"[ODOM]: Request from: {context.peer()}")
        try:
            data = api_pb2.OdometryData(
                pos=api_pb2.Vector3(
                    x=self.msp_controller.SENSOR_DATA["odom"]["position"][0],
                    y=self.msp_controller.SENSOR_DATA["odom"]["position"][1],
                    z=self.msp_controller.SENSOR_DATA["odom"]["position"][2],
                )
            )
            time.sleep(0.01)
            return data
        except Exception as e:
            self.state_logging.error("[ODOM]: " + str(e))

    async def GetOpticalFlowDataRPC(self, request, context):
        """
        Handles gRPC requests for odometry data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.OdometryData: The odometry data.
        """
        self.state_logging.info(f"[OPTFLOW]: Request from: {context.peer()}")
        try:
            data = api_pb2.OpticalFlowData(
                quality=self.msp_controller.SENSOR_DATA["optical_flow"][0],
                flow_rate_x=self.msp_controller.SENSOR_DATA["optical_flow"][1],
                flow_rate_y=self.msp_controller.SENSOR_DATA["optical_flow"][2],
                body_rate_x=self.msp_controller.SENSOR_DATA["optical_flow"][3],
                body_rate_y=self.msp_controller.SENSOR_DATA["optical_flow"][4],
            )
            time.sleep(0.01)
            return data
        except Exception as e:
            self.state_logging.error("[OPTFLOW]: " + str(e))

    async def GetFlagsDataRPC(self, request, context):
        """
        Handles gRPC requests for flags data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.FlagsData: The flags data.
        """
        self.state_logging.info(f"[FLAGS]: Request from: {context.peer()}")
        try:
            data = api_pb2.FlagsData(
                activeSensors=self.msp_controller.CONFIG["activeSensors"],
                armingDisableFlags=self.msp_controller.CONFIG["armingDisableFlags"],
                mode=self.msp_controller.CONFIG["mode"],
            )
            time.sleep(0.01)
            return data
        except Exception as e:
            self.state_logging.error("[FLAGS]: " + str(e))

    async def SendRcDataRPC(self, request, context):
        """
        Handles gRPC requests to send RC data.

        Args:
            request: The gRPC request object.
            context: The gRPC context object.

        Returns:
            api_pb2.StatusData: The status of the RC data send operation.
        """
        if not self.analyzer_state:
            self.state_logging.info(f"[RCIN]: Request from: {context.peer()}")
            try:
                self.rc_send = [
                    request.ail,
                    request.ele,
                    request.thr,
                    request.rud,
                    request.aux_1,
                    request.aux_2,
                    request.aux_3,
                    request.aux_4,
                ]

                response = api_pb2.StatusData(status="RC data send")

                time.sleep(0.01)
                return response
            except Exception as e:
                self.state_logging.error("[RCIN]: " + str(e))
        else:
            self.start_logging.error(
                "[RCIN]: " + "Send error, not available when the analyzer is on"
            )


async def serve(manager):
    """
    Starts the gRPC server and adds the DriverManagerServicer to it.

    Args:
        manager: The DriverManagerServicer instance.
    """
    server = grpc.aio.server()
    add_DriverManagerServicer_to_server(manager, server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)

    await server.start()
    await server.wait_for_termination()


def main(*args, **kwargs):
    """
    The main entry point for the MSPDriverManagerGRPC service.
    """
    msp_service = MSPDriverManagerGRPC(
        ip=kwargs["ip"],
        type=kwargs["type"],
        serial=kwargs["serial"],
        analyzer_flag=kwargs["analyzer"],
        log=kwargs["logging"],
        output=kwargs["output"],
    )
    update_thread = Thread(target=msp_service.update_data, args=(), daemon=True)

    update_thread.start()
    asyncio.run(serve(msp_service))

    update_thread.join()


if __name__ == "__main__":
    main()
