import grpc
import logging

from _protos import api_pb2
from _protos import api_pb2_grpc


class DataFetcher:
    def __init__(self, address="localhost:50051", log: bool = False):
        self.channel = grpc.insecure_channel(address)
        self.stub = api_pb2_grpc.DriverManagerStub(self.channel)
        if log:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.disable(logging.CRITICAL)

    def get_imu_data(self):
        try:
            logging.info("Fetching IMU data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetImuDataRPC(request)
            logging.info("IMU data fetched successfully")
            return {
                "gyro": {
                    "X": response.gyro.x,
                    "Y": response.gyro.y,
                    "Z": response.gyro.z,
                },
                "accel": (response.acc.x, response.acc.y, response.acc.z),
            }
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_sonar_data(self):
        try:
            logging.info("Fetching Sonar data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetSonarDataRPC(request)
            logging.info("Sonar data fetched successfully")
            return {"distance": response.sonar}
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_attitude_data(self):
        try:
            logging.info("Fetching Attitude data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetAttitudeDataRPC(request)
            logging.info("Attitude data fetched successfully")
            return {
                "orientation": (
                    response.orient.x,
                    response.orient.y,
                    response.orient.z,
                ),
            }
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_motor_data(self):
        try:
            logging.info("Fetching Motor data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetMotorDataRPC(request)
            logging.info("Motor data fetched successfully")
            return {
                "motor_1": response.motor_1,
                "motor_2": response.motor_2,
                "motor_3": response.motor_3,
                "motor_4": response.motor_4,
            }
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_analog_data(self):
        try:
            logging.info("Fetching Analog data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetAnalogDataRPC(request)
            logging.info("Analog data fetched successfully")
            self.mah = response.mAhdrawn
            return {"voltage": response.voltage, "current": response.amperage}
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_odometry_data(self):
        try:
            logging.info("Fetching Odometry data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetOdometryDataRPC(request)
            logging.info("Odometry data fetched successfully")
            return {"position": (response.pos.x, response.pos.y, response.pos.z)}
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_optical_flow_data(self):
        try:
            logging.info("Fetching Optical Flow data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetOpticalFlowDataRPC(request)
            logging.info("Optical Flow data fetched successfully")
            return {
                "quality": response.quality,
                "flow_rate_x": response.flow_rate_x,
                "flow_rate_y": response.flow_rate_y,
                "body_rate_x": response.body_rate_x,
                "body_rate_y": response.body_rate_y,
            }
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None

    def get_flags_data(self):
        try:
            logging.info("Fetching Flags data")
            request = api_pb2.GetRequest(req="")
            if request is None:
                logging.error("Request object is None")
                return None
            response = self.stub.GetFlagsDataRPC(request)
            logging.info("Flags data fetched successfully")
            return response
        except grpc.RpcError as e:
            logging.error(f"gRPC call failed: {e}")
            return None
