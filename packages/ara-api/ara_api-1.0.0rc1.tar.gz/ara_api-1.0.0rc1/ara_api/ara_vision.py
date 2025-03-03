import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import grpc

from ara_api._protos import api_pb2
from ara_api._protos.api_pb2_grpc import VisionManagerStub


class ARAVisionManager:
    """
    Provides an interface to call RPC services for vision.
    """

    def __init__(self):
        """
        Initializes the ARAVisionManager.
        """
        self.channel = grpc.insecure_channel("localhost:50053")
        self.vision_stub = VisionManagerStub(self.channel)

    def get_color(self):
        """
        Calls the GetBlobData service from VisionManagerGRPC
        """
        try:
            response = self.vision_stub.GetBlobData(api_pb2.GetRequest(req=""))
            return response.blobs
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None

    def get_aruco_data(self):
        """
        Calls the GetArucoData service from VisionManagerGRPC
        """
        try:
            response = self.vision_stub.GetArucoData(api_pb2.GetRequest(req=""))
            return response.markers
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None

    def get_qr_data(self):
        """
        Calls the GetQRData service from VisionManagerGRPC
        """
        try:
            response = self.vision_stub.GetQRData(api_pb2.GetRequest(req=""))
            return response.codes
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None

    # TODO: need to create methods
    def get_image(self):
        """
        Calls the GetImage service from VisionManagerGRPC
        """
        raise NotImplementedError("Method not realized yet")

    # TODO: need to create methods on stage (SETTINGS)
    def send_settings(self, settings):
        """
        Calls the SetSettings service from VisionManagerGRPC
        """
        raise NotImplementedError("Method not realized yet")


def main():
    vision_manager = ARAVisionManager()
    print(vision_manager.get_color())
    print(vision_manager.get_aruco_data())
    print(vision_manager.get_qr_data())
