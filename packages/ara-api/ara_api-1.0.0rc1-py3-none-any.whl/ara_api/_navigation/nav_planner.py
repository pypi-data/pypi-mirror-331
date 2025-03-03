"""
NavigationMultirotorPlanner module.

This module contains the NavigationMultirotorPlanner class, which is responsible for controlling a multirotor drone.
It uses PID controllers for roll, pitch, and yaw stabilization and communicates with a gRPC server to fetch odometry
and attitude data.

Classes:
    NavigationMultirotorPlanner: A class to control a multirotor drone using PID controllers.
"""

import time
import os
import logging
from math import radians

from _navigation import *
from _navigation.nav_fetcher import DataFetcher


class NavigationMultirotorPlanner:
    """
    A class to control a multirotor drone using PID controllers.

    Attributes:
        roll_pid (PID): PID controller for roll stabilization.
        pitch_pid (PID): PID controller for pitch stabilization.
        yaw_pid (PID): PID controller for yaw stabilization.
        drone (Drone): The drone object.
        grpc_driver (DataFetcher): The gRPC driver to fetch data.
        target (dict): The target position and yaw.
        channels (dict): The control channels for roll, pitch, throttle, and yaw.
        odometry (dict): The odometry data including position, orientation, and velocity.
        imu (dict): The IMU data including gyroscope and accelerometer readings.
        altitude (dict): The altitude data from sonar and barometer.
        optical_flow (dict): The optical flow data.
        flags (dict): Various flags for sensors, arming, and mode.
        approx_koeff (float): Approximation coefficient.
        alt_expo (list): Exponential ramp for altitude.
        time_delay (float): Time delay between control updates.
    """

    def __init__(self, log: bool = False):
        """
        Initializes the NavigationMultirotorPlanner with the given drone.
        """
        if log:
            self.__init_logging__("log")
        else:
            self.logger = logging.getLogger("nav_multirotor_planner")
            self.logger.disabled = True

        self.roll_pid = PID(kp=2, kd=1, name="roll")
        self.pitch_pid = PID(kp=2, kd=1, name="pitch")
        self.yaw_pid = PID(kp=2, kd=1, name="yaw")

        self.grpc_driver = DataFetcher(log=log)

        self.drone_altitude = {
            "min": 0.0,
            "max": 2.3,
        }

        self.target = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "yaw": 0.0,
        }

        self.target_speed = {
            "x": 0.0,
            "y": 0.0,
            "yaw": 0.0,
        }

        self.channels = {
            "ail": 1500.0,
            "ele": 1500.0,
            "thr": 1000.0,
            "rud": 1500.0,
            "aux1": 1000.0,
            "aux2": 1000.0,
            "aux3": 1000.0,
            "aux4": 1000.0,
        }

        self.odometry = self.odometry_zero = {
            "position": [0.0, 0.0, 0.0],
            "orientation": [0.0, 0.0, 0.0],
            "velocity": [0.0, 0.0, 0.0],
        }

        self.grpc_odom = {
            "position": [0, 0, 0],
            "velocity": [0, 0, 0],
        }
        self.grpc_att = {
            "orientation": [0, 0, 0],
        }

        self.imu = {
            "gyroscope": [0.0, 0.0, 0.0],
            "accelerometer": [0.0, 0.0, 0.0],
        }

        self.altitude = {
            "sonar": 0.0,
            "barometer": 0.0,
        }

        self.optical_flow = {
            "quality": 0.0,
            "flow_rate_x": 0.0,
            "flow_rate_y": 0.0,
            "body_rate_x": 0.0,
            "body_rate_y": 0.0,
        }

        self.flags = {
            "activeSensors": 0,
            "armingDisableFlags": 0,
            "mode": 0,
        }

        self.upper_threshold = 2000
        self.lower_threshold = 1000

        self.approx_koeff = 0.2
        self.alt_expo = [0]

        self.itterator = 0
        self.itterator_takeoff = False
        self.itterator_land = False
        self.itterator_changing_altitude = False

        self.inflight = False

        self.odometry_zero_flag = False

        self.time_delay = 0.1

    def __init_logging__(self, log_directory="log"):
        """
        Initializes logging for the NavigationMultirotorPlanner class.

        Args:
            log_directory (str): The directory where log files will be stored.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.logger = logging.getLogger("nav_multirotor_planner")
        self.logger.setLevel(logging.INFO)
        self.logger_formater = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger_handler = logging.FileHandler(
            os.path.join(log_directory, "nav_multirotor_planner.log")
        )
        self.logger_handler.setFormatter(self.logger_formater)
        self.logger.addHandler(self.logger_handler)

    def takeoff(self):
        """
        Initiates the takeoff sequence for the drone.

        Returns:
            bool: True if takeoff is successful, False otherwise.
        """
        if self.inflight:
            self.logger.error("Now in flight")
            return False

        if not self.itterator_takeoff and not self.inflight:
            self.logger.warning("Start TakeOFF")
            self.itterator = 0
            self.itterator_takeoff = True
            self.alt_expo = expo(1000, self.scale_altitude(self.target["z"]))

        return self.throttle_loop()

    def land(self):
        """
        Initiates the landing sequence for the drone.

        Returns:
            bool: True if landing is successful, False otherwise.
        """
        if self.inflight:
            self.logger.error("Now in flight")
            return False

        if not self.itterator_land:
            self.logger.warning("Start Landing")
            self.itterator = 0
            self.itterator_land = True
            self.alt_expo = expo(self.channels["thr"], 1000)

        return self.throttle_loop()

    def change_altitude(self):
        """
        Initiates the changing altitude sequence for the drone.

        Returns:
            bool: True if changing is successful, False otherwise.
        """
        if not self.inflight:
            self.logger.error("Now not in flight")
            return False

        if self.itterator_changing_altitude:
            self.logger.warning("Start Changing Altitude")
            self.itterator = 0
            self.itterator_changing_altitude = True
            self.alt_expo = expo(
                self.channels["thr"], self.scale_altitude(self.target["z"])
            )

        return self.throttle_loop()

    def throttle_loop(self):
        try:
            time.sleep(self.time_delay)
            self.channels["thr"] = int(self.alt_expo[self.itterator])
            if (self.itterator + 1) >= len(self.alt_expo):
                self.itterator_takeoff = False
                self.itterator_land = False
                self.itterator_changing_altitude = False
                return True
            else:
                self.itterator += 1
        except Exception as err:
            self.logger.error(f"Throttle loop error: {err}")
            return False
        return False

    def move(self):
        """
        Moves the drone towards the target position using PID controllers.
        """
        if not self.inflight:
            self.logger.error("Now not in flight")
            return False

        if (
            self.target["z"] == 0.0
            and self.target["x"] == 0.0
            and self.target["y"] == 0.0
        ):
            return False

        self.grpc_odom = self.grpc_driver.get_odometry_data()
        self.grpc_att = self.grpc_driver.get_attitude_data()

        if not self.odometry_zero_flag:
            self.odometry_zero["position"][0] = self.grpc_odom["position"][0]
            self.odometry_zero["position"][1] = self.grpc_odom["position"][1]
            self.odometry_zero["position"][2] = self.grpc_odom["position"][2]
            self.odometry_zero["orientation"][0] = self.grpc_att["orientation"][0]
            self.odometry_zero_flag = True

        self.odometry["position"][0] = (
            self.grpc_odom["position"][0] - self.odometry_zero["position"][0]
        )
        self.odometry["position"][1] = (
            self.grpc_odom["position"][1] - self.odometry_zero["position"][1]
        )
        self.odometry["position"][2] = (
            self.grpc_odom["position"][2] - self.odometry_zero["position"][2]
        )

        self.odometry["orientation"][0] = radians(
            self.grpc_att["orientation"][0] - self.odometry_zero["orientation"][0]
        )
        self.odometry["orientation"][1] = radians(self.grpc_att["orientation"][1])
        self.odometry["orientation"][2] = radians(self.grpc_att["orientation"][2])

        pitch_computed = self.pitch_pid.compute_classic(
            setpoint=self.target["x"], value=self.odometry["position"][0]
        )

        roll_computed = self.roll_pid.compute_classic(
            setpoint=self.target["y"], value=self.odometry["position"][1]
        )

        yaw_computed = constrain(
            self.yaw_pid.compute_classic(
                setpoint=0, value=self.odometry["orientation"][2]
            ),
            min_val=-2,
            max_val=2,
        )

        self.channels["ail"], self.channels["ele"], self.channels["rud"] = (
            transform_multirotor_speed_second(
                roll=self.odometry["orientation"][0],
                pitch=self.odometry["orientation"][1],
                yaw=self.odometry["orientation"][2],
                speed_roll=roll_computed,
                speed_pitch=pitch_computed,
                speed_yaw=yaw_computed,
            )
        )

        self.channels["ail"] = 1500 + int(remap(self.channels["ail"], -3, 3, -300, 300))
        self.channels["ele"] = 1500 + int(remap(self.channels["ele"], -3, 3, -300, 300))
        self.channels["rud"] = 1500

        self.logger.info(
            f"Move: Roll={self.channels['ail']}, "
            f"Pitch={self.channels['ele']}, "
            f"Yaw={self.channels['rud']}"
        )

    def set_zero_odometry(self):
        self.odometry_zero_flag = False

    def set_velocity(self):
        """
        Sets the velocity for the drone.

        Args:
            vx (float): Velocity in the x-direction.
            vy (float): Velocity in the y-direction.
            vz (float): Velocity in the z-direction.
        """
        if not self.inflight:
            self.logger.error("Now not in flight")
            return False

        self.channels["ail"] = self.target_speed["x"]
        self.channels["ele"] = self.target_speed["y"]
        self.channels["rud"] = self.target_speed["yaw"]

    def set_point_to_move(self, x: float, y: float, z: float):
        """
        Sets the target position for the drone to move to.

        Args:
            x (float): Target x-coordinate.
            y (float): Target y-coordinate.
            z (float): Target z-coordinate.
        """
        self.target["x"] = x
        self.target["y"] = y
        self.target["z"] = z
        self.logger.info(f"Set point to move: x={x}, y={y}, z={z}")

    def set_target_alt(self, alt):
        self.target["z"] = alt
        self.logger.info(f"Set alt to takeoff/land: alt={self.target['z']}")

    def set_target_speed(self, vx: float = 0, vy: float = 0, vz: float = 0):
        self.target_speed["x"] = 1500 + int(remap(vx, -3, 3, -500, 500))
        self.target_speed["y"] = 1500 + int(remap(vy, -3, 3, -500, 500))
        self.target_speed["yaw"] = 1500 + int(remap(vz, -3, 3, -500, 500))

        self.logger.info(f"Set target speed to vx={vx}, vy={vy}, vz={vz}")

    def check_desired_altitude(self, alt: int = None) -> bool:
        """
        Checks if the drone has reached the desired altitude.

        Args:
            alt (int, optional): The desired altitude. Defaults to None.

        Returns:
            bool: True if the desired altitude is reached, False otherwise.
        """
        if alt is None:
            check_alt = self.alt_expo[len(self.alt_expo) - 1]
        elif self.inflight_altitude_change:
            check_alt = alt
        else:
            check_alt = 1000 + 500 * alt

        if self.channels["thr"] == check_alt:
            self.logger.info(f"Check desired altitude: Reached {check_alt}")
            return True
        else:
            self.logger.info(f"Check desired altitude: Not reached {check_alt}")
            return False

    def check_desired_position(self) -> bool:
        """
        Checks if the drone has reached the desired position.

        Returns:
            bool: True if the desired position is reached, False otherwise.
        """
        if (
            (self.target["x"] - 0.15)
            < self.odometry["position"][0]
            < (self.target["x"] + 0.15)
        ):
            if (
                self.target["y"] - 0.15
                < self.odometry["position"][1]
                < self.target["y"] + 0.15
            ):
                self.logger.info("Check desired position: Reached")
                self.odometry_zero = False
                return True
            else:
                return False
        else:
            return False

    def check_desired_speed(self):
        if (self.target_speed["x"] == self.channels["ail"]) and (
            self.target_speed["y"] == self.channels["ele"]
        ):
            return True
        else:
            return False

    def scale_altitude(self, x):
        return (x - self.drone_altitude["min"]) * (
            self.upper_threshold - self.lower_threshold
        ) / (
            self.drone_altitude["max"] - self.drone_altitude["min"]
        ) + self.lower_threshold
