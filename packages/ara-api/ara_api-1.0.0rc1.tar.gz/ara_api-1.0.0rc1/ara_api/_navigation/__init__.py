import logging
import os
from math import sin, cos, e
import numpy as np
from datetime import datetime
import time
import logging
import os


class PID(object):
    """
    PID Controller

    This class implements a PID controller with three different computation methods:
    classic, windup, and feedforward.

    Attributes:
        kp (float): Proportional gain.
        ki (float): Integral gain.
        kd (float): Derivative gain.
        name (str): Name of the PID controller for logging purposes.
    """

    def __init__(
        self, kp: float = 0, ki: float = 0, kd: float = 0, name: str = "PID", log=False
    ):
        """
        Initializes the PID controller with the given gains and name.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
            name (str): Name of the PID controller.
        """
        self.windup_guard = 1
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.err = 0

        self.p_term = 0
        self.i_term = 0
        self.d_term = 0

        self.pid = 0
        self.smoothed_pid = 0
        self.alpha = 0.2

        self.dt = 0.1

        self.prev_err = 0

        self.curr_time = None
        self.prev_time = time.time()

        self.name = name

        if log:
            self.__init_logging__()
        else:
            self.logger = logging.getLogger(self.name)
            self.logger.disabled = True

    def __init_logging__(self, log_directory="log/pids"):
        """
        Initializes the logging for the PID controller.

        Args:
            log_directory (str): Directory where the log files will be stored.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_name = f"{self.name}_pid_works_{timestamp}.log"

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler = logging.FileHandler(os.path.join(log_directory, log_file_name))
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def compute_classic(self, setpoint, value):
        """
        Computes the PID output using the classic PID formula.

        Args:
            setpoint (float): The desired value.
            value (float): The current value.

        Returns:
            float: The computed PID output.
        """
        self.curr_time = time.time() if self.curr_time is None else self.curr_time
        self.err = setpoint - value

        self.dt = (
            (self.curr_time - self.prev_time)
            if (self.curr_time - self.prev_time) > 0
            else 0.1
        )

        self.p_term = self.err * self.kp
        self.i_term += self.err * self.dt
        self.d_term = (self.err - self.prev_err) / (self.dt * 1000)
        self.prev_time = self.curr_time
        self.curr_time = time.time()

        self.pid = self.p_term + self.ki * self.i_term + self.d_term * self.kd

        self.constrain(-2, 2)

        self.smoothed_pid = self.alpha * self.pid + (1 - self.alpha) * self.smoothed_pid

        self.logger.info(
            f"PID: {self.pid}, Error: {self.err}, P: {self.p_term}, I: {self.i_term}, D: {self.d_term}"
        )

        return self.smoothed_pid

    def compute_windup(self, setpoint, value):
        """
        Computes the PID output using the windup guard to prevent integral windup.

        Args:
            setpoint (float): The desired value.
            value (float): The current value.

        Returns:
            float: The computed PID output.

        """
        self.curr_time = time.time() if self.curr_time is None else self.curr_time
        self.err = setpoint - value

        self.dt = (
            (self.curr_time - self.prev_time)
            if (self.curr_time - self.prev_time) > 0
            else 0.1
        )

        self.p_term = self.err * self.kp
        self.i_term += self.err * self.dt

        self.i_term = self.constrain(self.i_term, -self.windup_guard, self.windup_guard)

        self.d_term = (self.err - self.prev_err) / (self.dt * 1000)
        self.prev_time = self.curr_time
        self.curr_time = time.time()

        self.pid = self.p_term + self.ki * self.i_term + self.d_term * self.kd

        self.smoothed_pid = self.alpha * self.pid + (1 - self.alpha) * self.smoothed_pid

        self.logger.info(
            f"PID: {self.pid}, Error: {self.err}, P: {self.p_term}, I: {self.i_term}, D: {self.d_term}"
        )

        return self.smoothed_pid

    def compute_feedforward(self, setpoint, value):
        """
        Computes the PID output with an additional feedforward term.

        Args:
            setpoint (float): The desired value.
            value (float): The current value.

        Returns:
            float: The computed PID output.
        """
        self.curr_time = time.time() if self.curr_time is None else self.curr_time
        self.err = setpoint - value

        self.dt = (
            (self.curr_time - self.prev_time)
            if (self.curr_time - self.prev_time) > 0
            else 0.1
        )

        self.p_term = self.err * self.kp
        self.i_term += self.err * self.dt
        self.d_term = (self.err - self.prev_err) / (self.dt * 1000)
        self.prev_time = self.curr_time
        self.curr_time = time.time()

        feedforward_term = setpoint * self.kp

        self.pid = (
            self.p_term
            + self.ki * self.i_term
            + self.d_term * self.kd
            + feedforward_term
        )

        self.smoothed_pid = self.alpha * self.pid + (1 - self.alpha) * self.smoothed_pid

        self.logger.info(
            f"PID: {self.pid}, Error: {self.err}, P: {self.p_term}, I: {self.i_term}, D: {self.d_term}, Feedforward: {feedforward_term}"
        )

        return self.smoothed_pid

    def set_kp(self, proportional_gain):
        """
        Sets the proportional gain.

        Args:
            proportional_gain (float): The new proportional gain.
        """
        self.kp = proportional_gain

    def set_ki(self, integral_gain):
        """
        Sets the integral gain.

        Args:
            integral_gain (float): The new integral gain.
        """
        self.ki = integral_gain

    def set_kd(self, derivative_gain):
        """
        Sets the derivative gain.

        Args:
            derivative_gain (float): The new derivative gain.
        """
        self.kd = derivative_gain

    def constrain(self, max_value: float, min_value: float) -> float:
        """
        Constrains the PID output to be within the given range.

        Args:
            max_value (float): The maximum value.
            min_value (float): The minimum value.

        Returns:
            float: The constrained PID output.
        """
        if self.pid > max_value:
            return max_value
        elif self.pid < min_value:
            return min_value
        else:
            return self.pid


def transform_multirotor_speed(roll, pitch, yaw, speed_roll, speed_pitch, speed_yaw):
    syaw = sin(yaw)
    cyaw = cos(yaw)

    spitch = sin(pitch)
    cpitch = cos(pitch)

    sroll = sin(roll)
    croll = cos(roll)

    r_matrix = np.array(
        [
            [
                cyaw * cpitch,
                cyaw * spitch * sroll - syaw * croll,
                cyaw * spitch * croll + syaw * sroll,
            ],
            [
                syaw * cpitch,
                syaw * spitch * sroll + cyaw * croll,
                syaw * spitch * croll - cyaw * sroll,
            ],
            [-spitch, cpitch * sroll, cpitch * croll],
        ]
    )

    r_transposed = np.transpose(r_matrix)

    v_local = np.matmul(r_transposed, np.array([speed_roll, speed_pitch, speed_yaw]))

    return (
        constrain(v_local[0], -2, 2),  # roll velocity
        constrain(v_local[1], -2, 2),  # pitch velocity
        constrain(v_local[2], -2, 2),
    )  # yaw velocity


def transform_multirotor_speed_second(
    roll, pitch, yaw, speed_roll, speed_pitch, speed_yaw
):
    from math import sin, cos

    cφ = cos(roll)
    sφ = sin(roll)
    cθ = cos(pitch)
    sθ = sin(pitch)
    cψ = cos(-yaw)
    sψ = sin(-yaw)

    u = speed_roll
    v = speed_pitch
    w = speed_yaw

    # Уравнения для преобразования в локальной системе
    u_prime = cψ * cθ * u + (cψ * sθ * sφ - sψ * cφ) * v + (cψ * sθ * cφ + sψ * sφ) * w
    v_prime = sψ * cθ * u + (sψ * sθ * sφ + cψ * cφ) * v + (sψ * sθ * cφ - cψ * sφ) * w
    w_prime = -sθ * u + cθ * sφ * v + cθ * cφ * w

    return (u_prime, v_prime, w_prime)


def exponential_ramp(
    target_value: float = 0, lower_threshold: int = 1000, upper_threshold: int = 2000
):
    target_value = min(target_value, upper_threshold)

    num_steps = (target_value / 200) * e

    k = np.log(target_value / lower_threshold) / (num_steps - 1)
    values = lower_threshold * np.exp(k * np.arange(num_steps))

    return np.int32(np.minimum(values, upper_threshold))


def normalize_radians(angle):
    return (angle + 2 * np.pi) % (2 * np.pi)


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def remap(x, min_old, max_old, min_new, max_new):
    return (x - min_old) * (max_new - min_new) / (max_old - min_old) + min_new


def expo(start, end):
    """Generate exponential ramp array from start value to end value

    Args:
        start (int): start value of exponential ramp
        end (int): end value of exponential ramp
    """
    step = int((abs(start - end) / 50) * e)
    return np.int32([start + (end - start) * (1 - e ** (-i / 10)) for i in range(step)])
