import asyncio
import argparse
import requests
import os
import logging
import grpc
import time
import cv2
import numpy as np
import pyfiglet
import colorama
from colorama import Fore
from importlib.metadata import version
from ara_api._protos import api_pb2
from ara_api._protos import api_pb2_grpc

from ara_api._vision import ImageProcessor


# TODO: перевести сервис на наследников от процессов multiprocessing
class VisionManagerGRPC(api_pb2_grpc.VisionManagerServicer):
    """
    gRPC server for managing vision commands for a multirotor drone.
    """

    def __init__(
        self,
        ip: str = "192.168.2.113",
        port=81,
        lower_color: tuple = None,
        upper_color: tuple = None,
        aruco_dict: str = None,
    ):
        """
        Initialize the VisionManagerGRPC with a image processor and initial state.
        """
        self.url = f"http://{ip}:{port}/stream"
        self.processor = ImageProcessor()

        if lower_color is not None:
            self.processor.process_settings("lower_color", lower_color)
        if upper_color is not None:
            self.processor.process_settings("upper_color", upper_color)
        if aruco_dict is not None:
            self.processor.process_settings("aruco_dict", aruco_dict)

        self.ascii_art = pyfiglet.figlet_format(
            "ARA MINI VISION {}".format(version("ara_api")), font="slant", width=50
        )
        self.summary = (
            "{cyan}Поздравляем! Вы запустили пакет для обработки изображения ARA MINI\n"
            "{cyan}Пакет работает независимо от остальных сервисов. Для его работы необходимо только подключение к дрону по WiFi\n"
        ).format(cyan=Fore.CYAN)

        print(Fore.BLUE + self.ascii_art)
        print(self.summary)

        self.__init_logging__()

    def __init_logging__(self, log_directory="log"):
        """
        Initializes logging for the VisionManagerGRPC class.

        Args:
            log_directory (str): The directory where log files will be stored.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.vision_logging = logging.getLogger("vision")
        self.vision_logging.setLevel(logging.INFO)
        self.vision_formater = logging.Formatter("%(asctime)s - %(message)s")
        self.vision_handler = logging.FileHandler(
            os.path.join(log_directory, "vision.log")
        )
        self.vision_handler.setFormatter(self.vision_formater)
        self.vision_logging.addHandler(self.vision_handler)

    # TODO: проверить правильность работы и выкатить fix
    async def GetImageData(self, request, context):
        """
        Handle the GetImageData gRPC request.

        Args:
            request: The gRPC request containing the image data.
            context: The gRPC context.

        Returns:
            api_pb2.ImageData: The response containing the image data.
        """
        self.vision_logging.info(f"[IMAGE] Request from: {context.peer()}")
        try:
            image = self.getImage()
            height, width, noise = self.processor.analyze_image(image)
            _, buffer = cv2.imencode(".jpg", image)
            image_bytes = buffer.tobytes()
            data = api_pb2.ImageData(
                height=height,
                weight=width,
                data=image_bytes,
                noise=noise,
            )
            time.sleep(0.05)
            return data
        except Exception as e:
            self.vision_logging.error(f"[IMAGE] Error: {e}")

    # TODO: проверить правильность работы и выкатить fix
    async def GetImageStreamData(self, request, context):
        """
        Handle the GetImageStreamData gRPC request.

        Args:
            request: The gRPC request containing the image stream data.
            context: The gRPC context.

        Returns:
            api_pb2.ImageDataStream: The response containing the image stream data.
        """
        self.vision_logging.info(f"[IMAGE STREAM] Request from: {context.peer()}")
        try:
            cap = cv2.VideoCapture(self.url)
            if not cap.isOpened():
                raise Exception(f"Failed to open video stream from {self.url}")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                _, buffer = cv2.imencode(".jpg", frame)
                image_bytes = buffer.tobytes()

                yield api_pb2.ImageDataStream(image=image_bytes)
                time.sleep(0.05)

            cap.release()
        except Exception as e:
            self.vision_logging.error(f"[IMAGE STREAM] Error: {e}")

    async def GetArucoData(self, request, context):
        """
        Handle the GetArucoData gRPC request.

        Args:
            request: The gRPC request containing the aruco data.
            context: The gRPC context.

        Returns:
            api_pb2.ArucoData: The response containing the aruco data.
        """
        self.vision_logging.info(f"[ARUCO] Request from: {context.peer()}")
        try:
            image = self.getImage()
            self.vision_logging.info("[ARUCO] Image captured successfully")
            data = self.processor.process_image(mode="aruco", image=image)
            self.vision_logging.info(f"[ARUCO] Data processed: {data}")
            time.sleep(0.05)
            return api_pb2.ArucoData(markers=data)
        except Exception as e:
            self.vision_logging.error(f"[ARUCO] Error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return api_pb2.ArucoData()

    async def GetQRData(self, request, context):
        """
        Handle the GetQRData gRPC request.

        Args:
            request: The gRPC request containing the qr data.
            context: The gRPC context.

        Returns:
            api_pb2.QRData: The response containing the qr data.
        """
        self.vision_logging.info(f"[QR] Request from: {context.peer()}")
        try:
            image = self.getImage()
            data = self.processor.process_image(mode="qr", image=image)
            time.sleep(0.05)
            return api_pb2.QRData(blob=data)
        except Exception as e:
            self.vision_logging.error(f"[QR] Error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return api_pb2.QRData()

    async def GetBlobData(self, request, context):
        """
        Handle the GetBlobData gRPC request.

        Args:
            request: The gRPC request containing the blob data.
            context: The gRPC context.

        Returns:
            api_pb2.BlobData: The response containing the blob data.
        """
        self.vision_logging.info(f"[BLOB] Request from: {context.peer()}")
        try:
            image = self.getImage()
            data = self.processor.process_image(mode="blob", image=image)
            time.sleep(0.05)
            return api_pb2.BlobData(blobs=data)
        except Exception as e:
            self.vision_logging.error(f"[BLOB] Error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return api_pb2.BlobData()

    # TODO: realize this method
    async def SetSettings(self, request, context):
        """
        Handle the SetSettings gRPC request.

        Args:
            request: The gRPC request containing the settings data.
            context: The gRPC context.

        Returns:
            api_pb2.StatusData: The response indicating success."""
        pass

    def getImage(self):
        """
        Get an image from the camera stream.

        Returns:
            np.array: The image as a numpy array.
        """
        try:
            logging.info(f"Opening video stream from {self.url}")
            cap = cv2.VideoCapture(self.url)
            if not cap.isOpened():
                raise Exception(f"Failed to open video stream from {self.url}")

            ret, frame = cap.read()
            if not ret:
                raise Exception(f"Failed to read frame from video stream {self.url}")

            cap.release()
            return frame
        except Exception as e:
            logging.error(f"Error getting image: {e}")
            raise


async def serve(args):
    """
    Start the gRPC server to handle vision commands.
    """
    try:
        server = grpc.aio.server()
        api_pb2_grpc.add_VisionManagerServicer_to_server(
            VisionManagerGRPC(
                lower_color=tuple(args.lower_color) if args.lower_color else None,
                upper_color=tuple(args.upper_color) if args.upper_color else None,
                aruco_dict=args.aruco_dict if args.aruco_dict else None,
            ),
            server,
        )
        server.add_insecure_port("[::]:50053")
        await server.start()
        await server.wait_for_termination()
    except Exception as e:
        print(e)


def main():
    parser = argparse.ArgumentParser(description="Applied Robotics Avia Vision Service")
    parser.add_argument(
        "--lower-color",
        type=int,
        nargs=3,
        required=False,
        help="Lower color for blob detection (format: R G B)",
    )
    parser.add_argument(
        "--upper-color",
        type=int,
        nargs=3,
        required=False,
        help="Upper color for blob detection (format: R G B)",
    )
    parser.add_argument(
        "--aruco-dict",
        type=str,
        required=False,
        help="Aruco dictionary for marker detection",
    )
    asyncio.run(serve(parser.parse_args()))


if __name__ == "__main__":
    main()
