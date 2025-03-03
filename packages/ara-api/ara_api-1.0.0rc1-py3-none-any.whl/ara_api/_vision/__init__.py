import cv2
import numpy as np
from ara_api._protos import api_pb2

ArucoDictionary = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_16H5": cv2.aruco.DICT_APRILTAG_16H5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_25H9": cv2.aruco.DICT_APRILTAG_25H9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36H10": cv2.aruco.DICT_APRILTAG_36H10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11,
    "DICT_APRILTAG_36H11": cv2.aruco.DICT_APRILTAG_36H11,
    "DICT_ARUCO_MIP_36h12": cv2.aruco.DICT_ARUCO_MIP_36h12,
    "DICT_ARUCO_MIP_36H12": cv2.aruco.DICT_ARUCO_MIP_36H12,
}


class ImageProcessor:
    """
    A class to process images using OpenCV.
    """

    def __init__(self):
        """
        Initialize the ImageProcessor with default parameters.
        """
        self.debug = False

        self.parameters = None
        self.lower_color = None
        self.upper_color = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_ARUCO_ORIGINAL
        )
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_struct = {
            "id": None,
            "position": {"x": None, "y": None, "z": None},
            "orientation": {"x": None, "y": None, "z": None},
        }
        self.qr_struct = {"data": None, "position": {"x": None, "y": None, "z": None}}
        self.blob_struct = {
            "id": None,
            "position": {"x": None, "y": None, "z": None},
            "size": None,
        }
        self.camera_matrix = np.array(
            [[1000, 0, 320], [0, 1000, 240], [0, 0, 1]], dtype=np.float32
        )
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)
        self.marker_size = 0.05  # Example marker size in meters

    def process_image(self, mode: str, image):
        """
        Process an image using the specified mode.

        Args:
            mode: The processing mode to use.
            image: The image to process.

        Returns:
            list: A list of objects detected in the image
        """
        processor = ImageProcessor.__dict__.get("process_" + mode)
        if processor:
            if image is not None:
                return processor(self, image)
            else:
                raise ValueError("Image is required")
        else:
            raise ValueError("Invalid mode")

    def process_settings(self, setting: str, value):
        """
        Process settings for the image processor.

        Args:
            setting: The setting to change.
            value: The value to set.
        """
        processor = ImageProcessor.__dict__.get("set_settings_" + setting)

        if processor:
            if setting is not None:
                return processor(self, value)
            else:
                raise ValueError("Setting is required")
        else:
            raise ValueError("Invalid setting")

    def process_aruco(self, image):
        """
        Process an image to detect Aruco markers.

        Args:
            image: The image to process.

        Returns:
            list: A list of Aruco markers detected in the image.
        """
        aruco_list = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(image, corners, ids)
            for i, corner in enumerate(corners):
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corner, 0.05, self.camera_matrix, self.dist_coeffs
                )

                aruco_list.append(
                    api_pb2.ArucoMarker(
                        id=int(ids[i][0]),
                        position=api_pb2.Vector3(
                            x=float(tvec[0][0][0]),
                            y=float(tvec[0][0][1]),
                            z=float(tvec[0][0][2]),
                        ),
                        orientation=api_pb2.Vector3(
                            x=float(rvec[0][0][0]),
                            y=float(rvec[0][0][1]),
                            z=float(rvec[0][0][2]),
                        ),
                    )
                )
                print(f"[ARUCO] Marker detected: {aruco_list}")

        return aruco_list

    def process_qr(self, image):
        """
        Process an image to detect QR codes.

        Args:
            image: The image to process.

        Returns:
            api_pb2.QRData: The QR code detected in the image.
        """
        qr_list = []
        qr_detector = cv2.QRCodeDetector()
        data, points, _ = qr_detector.detectAndDecode(image)
        if points is not None and len(points) > 0:
            points = points[0]
            if data:
                qr_list.append(
                    api_pb2.QRCode(
                        data=data,
                        position=api_pb2.Vector3(
                            x=float(points[0][0]), y=float(points[0][1]), z=0.0
                        ),
                    )
                )
        return qr_list if not self.debug else image

    def process_blob(self, image):
        """
        Process an image to detect blobs.

        Args:
            image: The image to process.

        Returns:
            list: A list of blobs detected in the image.
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([40, 40, 40])
        upper = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        blob_list = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                blob_list.append(
                    api_pb2.Blob(
                        id=i,
                        position=api_pb2.Vector3(x=x + w / 2, y=y + h / 2, z=0.0),
                        size=area,
                    )
                )
        return blob_list if not self.debug else image

    # TODO: need to test this
    def set_settings_aruco_dict(self, aruco_dict: str = "DICT_ARUCO_ORIGINAL"):
        """
        Set the Aruco dictionary to use.

        Args:
            aruco_dict: The Aruco dictionary to use.
        """
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            ArucoDictionary.get(aruco_dict)
        )
        self.aruco_params = cv2.aruco.DetectorParameters()

    # TODO: need to test this
    def set_settings_aruco_marker_size(self, marker_size: float):
        """
        Set the Aruco marker size.

        Args:
            marker_size: The size of the marker in meters.
        """
        self.marker_size = marker_size

    # TODO: need to test thiss
    def set_settings_lower_color(self, lower_color: np.array):
        """
        Set the lower color for blob detection.

        Args:
            lower_color: The lower color to use.
        """
        self.lower_color = lower_color

    # TODO: need to test this
    def set_settings_upper_color(self, upper_color: np.array):
        """
        Set the upper color for blob detection.

        Args:
            upper_color: The upper color to use.
        """
        self.upper_color = upper_color
