import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import grpc

from ara_api._protos import api_pb2
from ara_api._protos.api_pb2_grpc import DriverManagerStub, NavigationManagerStub


class ARALinkManager:
    """
    Provides an interface to call RPC services sequentially.
    """

    def __init__(self, nav_address="localhost:50052", driver_address="localhost:50051"):
        """
        Initializes the ARALinkManager.
        """
        self.nav_channel = grpc.insecure_channel(nav_address)
        self.driver_channel = grpc.insecure_channel(driver_address)

        self.attemps = 5

        self.nav_stub = NavigationManagerStub(self.nav_channel)
        self.driver_stub = DriverManagerStub(self.driver_channel)

    def takeoff(self, altitude):
        """
        Calls the takeoff service from NavigationManagerGRPC
        """
        print(f"TakeOFF on {altitude}", end="")

        for i in range(self.attemps):
            try:
                request = api_pb2.AltitudeSetData(altitude=altitude)
                response = self.nav_stub.TakeOFF(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def land(self):
        """
        Calls the land service from NavigationManagerGRPC
        """
        print("Landing", end="")
        for i in range(self.attemps):
            try:
                request = api_pb2.AltitudeSetData(altitude=0)
                response = self.nav_stub.Land(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def change_altitude(self, altitude):
        """
        Calls the change_altitude service from NavigationManagerGRPC
        """
        print(f"Change altitude to {altitude}", end="")

        for i in range(self.attemps):
            try:
                request = api_pb2.AltitudeSetData(altitude=altitude)
                response = self.nav_stub.SetAltitude(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def move_by_point(self, x, y):
        """
        Calls the move service from NavigationManagerGRPC
        """
        print(f"Move to ({x}, {y})", end="")

        for i in range(self.attemps):
            try:
                request = api_pb2.PointData(
                    point=api_pb2.Vector3(
                        x=x,
                        y=y,
                        z=0,  # not available now (TODO)
                    )
                )
                response = self.nav_stub.Move(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def set_velocity(self, vx, vy):
        """
        Calls the set_speed service from NavigationManagerGRPC
        """
        print(f"Set velocity as ({vy}, {vx})", end="")

        for i in range(self.attemps):
            try:
                request = api_pb2.VelocityData(
                    velocity=api_pb2.Vector3(
                        x=vy,
                        y=vx,
                        z=0,  # not available now (TODO)
                    )
                )
                response = self.nav_stub.SetVelocity(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def reset_velocity_state(self):
        print("Resetting state", end="")

        for i in range(self.attemps):
            try:
                request = api_pb2.VelocityData(
                    velocity=api_pb2.Vector3(
                        x=0,
                        y=0,
                        z=0,
                    )
                )
                response = self.nav_stub.SetVelocity(request)

                return response.status
            except Exception as e:
                print(".", end="")

    def get_imu_data(self):
        response = self.driver_stub.GetImuDataRPC(api_pb2.GetRequest(req=""))
        return {
            "gyro": (response.gyro.x, response.gyro.y, response.gyro.z),
            "accel": (response.acc.x, response.acc.y, response.acc.z),
        }

    def get_sonar_data(self):
        response = self.driver_stub.GetSonarDataRPC(api_pb2.GetRequest(req=""))
        return {"distance": response.sonar}

    def get_attitude_data(self):
        response = self.driver_stub.GetAttitudeDataRPC(api_pb2.GetRequest(req=""))

        return {
            "orientation": (response.orient.x, response.orient.y, response.orient.z),
        }

    def get_odometry_data(self):
        response = self.driver_stub.GetOdometryDataRPC(api_pb2.GetRequest(req=""))

        return {
            "position": (response.pos.x, response.pos.y, response.pos.z),
        }

    def get_optical_flow_data(self):
        response = self.driver_stub.GetOpticalFlowDataRPC(api_pb2.GetRequest(req=""))
        return {
            "quality": response.quality,
            "flow_rate_x": response.flow_rate_x,
            "flow_rate_y": response.flow_rate_y,
            "body_rate_x": response.body_rate_x,
            "body_rate_y": response.body_rate_y,
        }
