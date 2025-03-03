import customtkinter
import time
from _navigation.nav_fetcher import DataFetcher
import threading
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk


class MotorOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/motor_data.csv"

        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.bind(sequence="<Map>", func=self.update_canvas)
        self.canvas.pack(fill="both", expand=True)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())

        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        df = pd.read_csv(self.csv_file)

        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        rect_w, rect_h = 120, 20

        colors = {
            "motor_1": (255, 0, 0),
            "motor_2": (0, 255, 0),
            "motor_3": (0, 0, 255),
            "motor_4": (255, 0, 255),
        }

        legend_x = width - 150
        legend_y = 30

        for motor, color in colors.items():
            y_data = np.array(df[f"{motor}"], dtype=np.int16)
            y_data = np.interp(
                y_data, [1000, 2000], [height - margin_bottom, margin_bottom]
            )
            x_data = np.array(df["time"], dtype=np.int16)

            # draw axis
            cv2.line(
                img=img,
                pt1=(margin_left, margin_bottom),
                pt2=(margin_left, height - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )
            cv2.line(
                img=img,
                pt1=(margin_left, height - margin_bottom),
                pt2=(width - margin_left, height - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )

            for y in range(1000, 2001, 100):
                y_pos = int(
                    np.interp(y, [1000, 2000], [height - margin_bottom, margin_bottom])
                )
                cv2.putText(
                    img=img,
                    text=str(y),
                    org=(10, y_pos),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for x in range(0, len(x_data), 200):
                x_pos = int(
                    np.interp(
                        x, [0, len(df["time"])], [margin_left, width - margin_left]
                    )
                )
                cv2.putText(
                    img=img,
                    text=f"{round(x_data[x]) + (0 if (x_data[x] == 0 or x_data[x] == 500) else 1)}",
                    org=(x_pos, height - 10),
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            end = int(y_data[len(y_data) - 1])
            for j in range(1, len(y_data)):
                cv2.line(
                    img=img,
                    pt1=(
                        margin_left
                        + int(np.interp(j, [0, end], [0, width - 2 * margin_left])),
                        int(y_data[j - 1]),
                    ),
                    pt2=(
                        margin_left
                        + int(np.interp(j + 1, [0, end], [0, width - 2 * margin_left])),
                        int(y_data[j]),
                    ),
                    color=color,
                    thickness=2,
                )

        for motor, color in colors.items():
            cv2.rectangle(
                img,
                (legend_x, legend_y + 4),
                (legend_x + rect_w, legend_y - rect_h + 2),
                color=(140, 138, 138),
                thickness=-1,
            )
            cv2.putText(
                img,
                f"{motor}: {round(np.mean(df[f'{motor}']))}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )
            legend_y += 25

        return img


class GyroPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = DataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.gyro_data = {"X": [], "Y": [], "Z": []}
        self.label = customtkinter.CTkLabel(self)
        self.label.pack(fill="both", expand=True)
        self.lock = threading.Lock()
        self.csv_lock = threading.Lock()
        self.running = True
        self.header_added = False
        self.update_graphs()
        self.start_csv_saving()

    def update_graphs(self):
        if self.running:
            threading.Thread(target=self.fetch_data).start()
            threading.Thread(target=self.update_image).start()
            self.after(100, self.update_graphs)  # Schedule the next update

    def fetch_data(self):
        with self.lock:
            if not hasattr(self, "start_time"):
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            new_data = self.data_fetcher.get_imu_data()["gyro"]
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            for axis in self.gyro_data.keys():
                self.gyro_data[axis].append(new_data[axis])
                # Keep only the last 100 gyro data points
                if len(self.gyro_data[axis]) > 100:
                    self.gyro_data[axis].pop(0)

    def update_image(self):
        with self.lock:
            img = self.create_image()
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)

    def create_image(self):
        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        colors = {"X": (255, 0, 0), "Y": (0, 255, 0), "Z": (0, 0, 255)}
        name = ["X", "Y", "Z"]

        for i, axis in enumerate(name):
            y_data = np.array(self.gyro_data[axis][-100:], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )
            x_data = np.arange(len(y_data))

            # Draw Y axis
            cv2.line(
                img,
                (margin_left, height // 3 * i + margin_bottom),
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )
            # Draw X axis
            cv2.line(
                img,
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (width - margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )

            # Draw Y axis labels
            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
                    )
                )
                cv2.putText(
                    img,
                    str(y),
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

            # Draw X axis labels
            x_start = max(0, len(self.time_data) - 100)
            for x in range(x_start, x_start + 101, 10):
                if x < len(self.time_data):
                    x_pos = int(
                        np.interp(
                            x - x_start, [0, 100], [margin_left, width - margin_left]
                        )
                    )
                    cv2.putText(
                        img,
                        f"{self.time_data[x]:.1f}",
                        (x_pos, height // 3 * (i + 1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 0, 0),
                        1,
                    )

            for j in range(1, len(y_data)):
                cv2.line(
                    img,
                    (
                        margin_left
                        + int(np.interp(j, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j - 1]),
                    ),
                    (
                        margin_left
                        + int(np.interp(j + 1, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j]),
                    ),
                    colors[axis],
                    2,
                )

            # Draw legend
            legend_x = width - 150
            legend_y = height // 3 * i + 20
            current_value = self.gyro_data[axis][-1] if self.gyro_data[axis] else 0
            cv2.putText(
                img,
                f"{axis}: {current_value}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                colors[axis],
                1,
            )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()

    def save_to_csv(self):
        while self.running:
            time.sleep(10)  # Save data every 10 seconds
            with self.csv_lock:
                data = {
                    "time": self.time_data,
                    "gyro_x": self.gyro_data["X"],
                    "gyro_y": self.gyro_data["Y"],
                    "gyro_z": self.gyro_data["Z"],
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/gyro_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class GyroOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/gyro_data.csv"

        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.bind(sequence="<Map>", func=self.update_canvas)
        self.canvas.pack(fill="both", expand=True)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())

        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        df = pd.read_csv(self.csv_file)

        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        rect_w, rect_h = 120, 20

        margin_left = 60
        margin_bottom = 30

        colors = {"gyro_x": (255, 0, 0), "gyro_y": (0, 255, 0), "gyro_z": (0, 0, 255)}
        name = ["gyro_x", "gyro_y", "gyro_z"]

        for i, axis in enumerate(name):
            y_data = np.array(df[axis], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )
            x_data = np.array(df["time"], dtype=np.int16)

            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * i + margin_bottom),
                pt2=(margin_left, height // 3 * (i + 1) - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )
            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * (i + 1) - margin_bottom - 100),
                pt2=(
                    width - margin_bottom,
                    height // 3 * (i + 1) - margin_bottom - 100,
                ),
                color=(0, 0, 0),
                thickness=1,
            )

            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
                    )
                )
                cv2.putText(
                    img=img,
                    text=str(y),
                    org=(10, y_pos),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for x in range(0, len(x_data), 200):
                x_pos = int(
                    np.interp(
                        x, [0, len(df["time"])], [margin_left, width - margin_left]
                    )
                )
                cv2.putText(
                    img=img,
                    text=f"{round(x_data[x])}" if x_data[x] != 0 else "",
                    org=(x_pos, height // 3 * (i + 1) - 110),
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            # TODO: need to fix it
            for j in range(1, len(y_data)):
                cv2.line(
                    img=img,
                    pt1=(
                        margin_left
                        + int(
                            np.interp(
                                j - 1,
                                [0, len(y_data) - 1],
                                [0, width - 2 * margin_left],
                            )
                        ),
                        int(y_data[j - 1]),
                    ),
                    pt2=(
                        margin_left
                        + int(
                            np.interp(
                                j, [0, len(y_data) - 1], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j]),
                    ),
                    color=colors[axis],
                    thickness=2,
                )

        return img


class AccelPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = DataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.accel_data = {"X": [], "Y": [], "Z": []}
        self.label = customtkinter.CTkLabel(self)
        self.label.pack(fill="both", expand=True)
        self.lock = threading.Lock()
        self.csv_lock = threading.Lock()
        self.running = True
        self.header_added = False
        self.update_graphs()
        self.start_csv_saving()

    def update_graphs(self):
        if self.running:
            threading.Thread(target=self.fetch_data).start()
            threading.Thread(target=self.update_image).start()
            self.after(100, self.update_graphs)  # Schedule the next update

    def fetch_data(self):
        with self.lock:
            if not hasattr(self, "start_time"):
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            new_data = self.data_fetcher.get_imu_data()["accel"]
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            for axis, value in zip(self.accel_data.keys(), new_data):
                self.accel_data[axis].append(value)
                # Keep only the last 100 accel data points
                if len(self.accel_data[axis]) > 100:
                    self.accel_data[axis].pop(0)

    def update_image(self):
        with self.lock:
            img = self.create_image()
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)

    def create_image(self):
        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        colors = {"X": (255, 0, 0), "Y": (0, 255, 0), "Z": (0, 0, 255)}
        name = ["X", "Y", "Z"]

        for i, axis in enumerate(name):
            y_data = np.array(self.accel_data[axis][-100:], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )
            x_data = np.arange(len(y_data))

            # Draw Y axis
            cv2.line(
                img,
                (margin_left, height // 3 * i + margin_bottom),
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )
            # Draw X axis
            cv2.line(
                img,
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (width - margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )

            # Draw Y axis labels
            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
                    )
                )
                cv2.putText(
                    img,
                    str(y),
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

            # Draw X axis labels
            x_start = max(0, len(self.time_data) - 100)
            for x in range(x_start, x_start + 101, 10):
                if x < len(self.time_data):
                    x_pos = int(
                        np.interp(
                            x - x_start, [0, 100], [margin_left, width - margin_left]
                        )
                    )
                    cv2.putText(
                        img,
                        f"{self.time_data[x]:.1f}",
                        (x_pos, height // 3 * (i + 1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 0, 0),
                        1,
                    )

            for j in range(1, len(y_data)):
                cv2.line(
                    img,
                    (
                        margin_left
                        + int(np.interp(j, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j - 1]),
                    ),
                    (
                        margin_left
                        + int(np.interp(j + 1, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j]),
                    ),
                    colors[axis],
                    2,
                )

            # Draw legend
            legend_x = width - 150
            legend_y = height // 3 * i + 20
            current_value = self.accel_data[axis][-1] if self.accel_data[axis] else 0
            cv2.putText(
                img,
                f"{axis}: {current_value}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                colors[axis],
                1,
            )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()

    def save_to_csv(self):
        while self.running:
            time.sleep(10)  # Save data every 10 seconds
            with self.csv_lock:
                data = {
                    "time": self.time_data,
                    "accel_x": self.accel_data["X"],
                    "accel_y": self.accel_data["Y"],
                    "accel_z": self.accel_data["Z"],
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/accel_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class AccelOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/accel_data.csv"

        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.bind(sequence="<Map>", func=self.update_canvas)
        self.canvas.pack(fill="both", expand=True)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())

        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        df = pd.read_csv(self.csv_file)

        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        rect_w, rect_h = 120, 20

        margin_left = 60
        margin_bottom = 30

        colors = {
            "accel_x": (255, 0, 0),
            "accel_y": (0, 255, 0),
            "accel_z": (0, 0, 255),
        }
        name = ["accel_x", "accel_y", "accel_z"]

        for i, axis in enumerate(name):
            y_data = np.array(df[axis], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )
            x_data = np.array(df["time"], dtype=np.int16)

            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * i + margin_bottom),
                pt2=(margin_left, height // 3 * (i + 1) - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )
            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * (i + 1) - margin_bottom - 100),
                pt2=(
                    width - margin_bottom,
                    height // 3 * (i + 1) - margin_bottom - 100,
                ),
                color=(0, 0, 0),
                thickness=1,
            )

            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
                    )
                )
                cv2.putText(
                    img=img,
                    text=str(y),
                    org=(10, y_pos),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for x in range(0, len(x_data), 200):
                x_pos = int(
                    np.interp(
                        x, [0, len(df["time"])], [margin_left, width - margin_left]
                    )
                )
                cv2.putText(
                    img=img,
                    text=f"{round(x_data[x])}" if x_data[x] != 0 else "",
                    org=(x_pos, height // 3 * (i + 1) - 110),
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for j in range(1, len(y_data)):
                cv2.line(
                    img=img,
                    pt1=(
                        margin_left
                        + int(
                            np.interp(
                                j - 1,
                                [0, len(y_data) - 1],
                                [0, width - 2 * margin_left],
                            )
                        ),
                        int(y_data[j - 1]),
                    ),
                    pt2=(
                        margin_left
                        + int(
                            np.interp(
                                j, [0, len(y_data) - 1], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j]),
                    ),
                    color=colors[axis],
                    thickness=2,
                )

        return img


class MotorPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = DataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.motor_data = {"motor_1": [], "motor_2": [], "motor_3": [], "motor_4": []}
        self.label = customtkinter.CTkLabel(self)
        self.label.pack(fill="both", expand=True)
        self.lock = threading.Lock()
        self.csv_lock = threading.Lock()
        self.running = True
        self.header_added = False
        self.update_graphs()
        self.start_csv_saving()

    def update_graphs(self):
        if self.running:
            threading.Thread(target=self.fetch_data).start()
            threading.Thread(target=self.update_image).start()
            self.after(100, self.update_graphs)  # Schedule the next update

    def fetch_data(self):
        with self.lock:
            if not hasattr(self, "start_time"):
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            new_data = self.data_fetcher.get_motor_data()
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            for motor in self.motor_data.keys():
                self.motor_data[motor].append(new_data[motor])
                # Keep only the last 100 motor data points
                if len(self.motor_data[motor]) > 100:
                    self.motor_data[motor].pop(0)

    def update_image(self):
        with self.lock:
            img = self.create_image()
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)

    def create_image(self):
        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        colors = {
            "motor_1": (255, 0, 0),
            "motor_2": (0, 255, 0),
            "motor_3": (0, 0, 255),
            "motor_4": (255, 0, 255),
        }

        # Draw legend
        legend_x = width - 150
        legend_y = 30
        for motor, color in colors.items():
            current_value = self.motor_data[motor][-1] if self.motor_data[motor] else 0
            cv2.putText(
                img,
                f"{motor}: {current_value}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )
            legend_y += 20

        for motor, color in colors.items():
            y_data = np.array(self.motor_data[motor][-100:], dtype=np.int32)
            y_data = np.interp(
                y_data, [1000, 2000], [height - margin_bottom, margin_bottom]
            )
            x_data = np.arange(len(y_data))

            # Draw Y axis
            cv2.line(
                img,
                (margin_left, margin_bottom),
                (margin_left, height - margin_bottom),
                (0, 0, 0),
                1,
            )
            # Draw X axis
            cv2.line(
                img,
                (margin_left, height - margin_bottom),
                (width - margin_left, height - margin_bottom),
                (0, 0, 0),
                1,
            )

            # Draw Y axis labels
            for y in range(1000, 2000, 100):
                y_pos = int(
                    np.interp(y, [1000, 2000], [height - margin_bottom, margin_bottom])
                )
                cv2.putText(
                    img,
                    str(y),
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

            # Draw X axis labels
            x_start = max(0, len(self.time_data) - 100)
            for x in range(x_start, x_start + 101, 10):
                if x < len(self.time_data):
                    x_pos = int(
                        np.interp(
                            x - x_start, [0, 100], [margin_left, width - margin_left]
                        )
                    )
                    cv2.putText(
                        img,
                        f"{self.time_data[x]:.1f}",
                        (x_pos, height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 0, 0),
                        1,
                    )

            for j in range(1, len(y_data)):
                cv2.line(
                    img,
                    (
                        margin_left
                        + int(np.interp(j, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j - 1]),
                    ),
                    (
                        margin_left
                        + int(np.interp(j + 1, [0, 100], [0, width - 2 * margin_left])),
                        int(y_data[j]),
                    ),
                    color,
                    2,
                )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()

    def save_to_csv(self):
        while self.running:
            time.sleep(10)  # Save data every 10 seconds
            with self.csv_lock:
                data = {
                    "time": self.time_data,
                    "motor_1": self.motor_data["motor_1"],
                    "motor_2": self.motor_data["motor_2"],
                    "motor_3": self.motor_data["motor_3"],
                    "motor_4": self.motor_data["motor_4"],
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/motor_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class AnalogPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = DataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.voltage_data = []
        self.current_data = []
        self.label = customtkinter.CTkLabel(self)
        self.label.pack(fill="both", expand=True)
        self.lock = threading.Lock()
        self.csv_lock = threading.Lock()
        self.running = True
        self.header_added = False
        self.update_graphs()
        self.start_csv_saving()

    def update_graphs(self):
        if self.running:
            threading.Thread(target=self.fetch_data).start()
            threading.Thread(target=self.update_image).start()
            self.after(100, self.update_graphs)  # Schedule the next update

    def fetch_data(self):
        with self.lock:
            if not hasattr(self, "start_time"):
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            new_data = self.data_fetcher.get_analog_data()
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            self.voltage_data.append(new_data["voltage"])
            self.current_data.append(new_data["current"])

            # Keep only the last 100 data points
            if len(self.voltage_data) > 100:
                self.voltage_data.pop(0)
            if len(self.current_data) > 100:
                self.current_data.pop(0)

    def update_image(self):
        with self.lock:
            img = self.create_image()
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)

    def create_image(self):
        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30
        margin_top = 30

        # Draw voltage graph
        y_data = np.array(self.voltage_data[-100:], dtype=np.float32)
        y_data = np.interp(y_data, [0, 5], [height // 2 - margin_bottom, margin_top])
        x_data = np.arange(len(y_data))

        # Draw Y axis for voltage
        cv2.line(
            img,
            (margin_left, margin_top),
            (margin_left, height // 2 - margin_bottom),
            (0, 0, 0),
            1,
        )
        # Draw X axis for voltage
        cv2.line(
            img,
            (margin_left, height // 2 - margin_bottom),
            (width - margin_left, height // 2 - margin_bottom),
            (0, 0, 0),
            1,
        )

        # Draw Y axis labels for voltage
        for y in range(0, 6):
            y_pos = int(np.interp(y, [0, 5], [height // 2 - margin_bottom, margin_top]))
            cv2.putText(
                img, str(y), (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

        # Draw X axis labels
        x_start = max(0, len(self.time_data) - 100)
        for x in range(x_start, x_start + 101, 10):
            if x < len(self.time_data):
                x_pos = int(
                    np.interp(x - x_start, [0, 100], [margin_left, width - margin_left])
                )
                cv2.putText(
                    img,
                    f"{self.time_data[x]:.1f}",
                    (x_pos, height // 2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )

        for j in range(1, len(y_data)):
            cv2.line(
                img,
                (
                    margin_left
                    + int(np.interp(j, [0, 100], [0, width - 2 * margin_left])),
                    int(y_data[j - 1]),
                ),
                (
                    margin_left
                    + int(np.interp(j + 1, [0, 100], [0, width - 2 * margin_left])),
                    int(y_data[j]),
                ),
                (0, 0, 255),
                2,
            )

        # Draw legend for voltage
        legend_x = width - 150
        legend_y = 30
        current_voltage = self.voltage_data[-1] if self.voltage_data else 0
        cv2.putText(
            img,
            f"Voltage: {current_voltage:.2f}V",
            (legend_x, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )

        # Draw current graph
        y_data = np.array(self.current_data[-100:], dtype=np.float32)
        y_data = np.interp(
            y_data, [0, 15], [height - margin_bottom, height // 2 + margin_top]
        )
        x_data = np.arange(len(y_data))

        # Draw Y axis for current
        cv2.line(
            img,
            (margin_left, height // 2 + margin_top),
            (margin_left, height - margin_bottom),
            (0, 0, 0),
            1,
        )
        # Draw X axis for current
        cv2.line(
            img,
            (margin_left, height - margin_bottom),
            (width - margin_left, height - margin_bottom),
            (0, 0, 0),
            1,
        )

        # Draw Y axis labels for current
        for y in range(0, 16, 3):
            y_pos = int(
                np.interp(
                    y, [0, 15], [height - margin_bottom, height // 2 + margin_top]
                )
            )
            cv2.putText(
                img, str(y), (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

        for j in range(1, len(y_data)):
            cv2.line(
                img,
                (
                    margin_left
                    + int(np.interp(j, [0, 100], [0, width - 2 * margin_left])),
                    int(y_data[j - 1]),
                ),
                (
                    margin_left
                    + int(np.interp(j + 1, [0, 100], [0, width - 2 * margin_left])),
                    int(y_data[j]),
                ),
                (0, 0, 255),
                2,
            )

        # Draw legend for current
        legend_y = height // 2 + 50
        current_current = self.current_data[-1] if self.current_data else 0
        cv2.putText(
            img,
            f"Current: {current_current:.2f}A",
            (legend_x, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()

    def save_to_csv(self):
        while self.running:
            time.sleep(10)  # Save data every 10 seconds
            with self.csv_lock:
                data = {
                    "time": self.time_data,
                    "voltage": self.voltage_data,
                    "amperage": self.current_data,
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/amper_voltage_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class AnalogOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/amper_voltage_data.csv"

        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.bind(sequence="<Map>", func=self.update_canvas)
        self.canvas.pack(fill="both", expand=True)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())

        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        df = pd.read_csv(self.csv_file)

        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        rect_w, rect_h = 120, 20

        colors = {"voltage": (255, 0, 0), "amperage": (255, 0, 0)}

        time_data = np.array(df["time"])

        voltage_data = np.array(df["voltage"], dtype=np.int32)
        voltage_data = np.interp(
            voltage_data, [0, 5], [height // 2 - margin_bottom, margin_bottom]
        )
        amperage_data = np.array(df["amperage"], dtype=np.int32)
        amperage_data = np.interp(
            amperage_data, [0, 15], [height // 2 - margin_bottom, margin_bottom]
        )

        # axis for voltage
        cv2.line(
            img=img,
            pt1=(margin_left, margin_bottom),
            pt2=(margin_left, height // 2 - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        cv2.line(
            img=img,
            pt1=(margin_left, height // 2 - margin_bottom),
            pt2=(width - margin_left, height // 2 - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        # axis for amperage
        cv2.line(
            img=img,
            pt1=(margin_left, height // 2 + margin_bottom),
            pt2=(margin_left, height - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        cv2.line(
            img=img,
            pt1=(margin_left, height - margin_bottom),
            pt2=(width - margin_left, height - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        # Draw Y axis labels for voltage
        for y in range(0, 6):
            y_pos = int(
                np.interp(y, [0, 5], [height // 2 - margin_bottom, margin_bottom])
            )
            cv2.putText(
                img, str(y), (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

        # Draw Y axis labels for amperage
        for y in range(0, 16, 3):
            y_pos = int(
                np.interp(
                    y, [0, 15], [height - margin_bottom, height // 2 + margin_bottom]
                )
            )
            cv2.putText(
                img, str(y), (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

        # Draw X axis labels
        x_start = max(0, len(time_data) - 100)
        for x in range(x_start, x_start + 101, 10):
            if x < len(time_data):
                x_pos = int(
                    np.interp(x - x_start, [0, 100], [margin_left, width - margin_left])
                )
                cv2.putText(
                    img,
                    f"{time_data[x]:.1f}",
                    (x_pos, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )

        for j in range(1, len(voltage_data)):
            cv2.line(
                img=img,
                pt1=(
                    margin_left
                    + int(
                        np.interp(
                            j - 1,
                            [0, len(voltage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(voltage_data[j - 1]),
                ),
                pt2=(
                    margin_left
                    + int(
                        np.interp(
                            j, [0, len(voltage_data) - 1], [0, width - 2 * margin_left]
                        )
                    ),
                    int(voltage_data[j]),
                ),
                color=colors["voltage"],
                thickness=2,
            )

        for j in range(1, len(amperage_data)):
            cv2.line(
                img=img,
                pt1=(
                    margin_left
                    + int(
                        np.interp(
                            j - 1,
                            [0, len(amperage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(amperage_data[j - 1] + height // 2),
                ),
                pt2=(
                    margin_left
                    + int(
                        np.interp(
                            j, [0, len(amperage_data) - 1], [0, width - 2 * margin_left]
                        )
                    ),
                    int(amperage_data[j] + height // 2),
                ),
                color=colors["amperage"],
                thickness=2,
            )

        return img


class FrequencyOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_gyro_file = csv_dir + "/gyro_data.csv"
        self.csv_accel_file = csv_dir + "/accel_data.csv"

        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.update_canvas)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())
        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        sampling_rate = 400.0
        img_height, img_width = self.canvas.winfo_height(), self.canvas.winfo_width()
        if img_height < 1 or img_width < 1:
            img_height, img_width = 400, 600

        img = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255

        # Считываем данные
        df_gyro = pd.read_csv(self.csv_gyro_file)
        df_accel = pd.read_csv(self.csv_accel_file)

        # Выбираем примеры столбца: gyro_x, acc_x
        gyro_data = np.array(df_gyro["gyro_x"], dtype=np.float32)
        accel_data = np.array(df_accel["accel_x"], dtype=np.float32)

        # Вычисляем FFT
        gyro_fft = np.fft.fft(gyro_data)
        accel_fft = np.fft.fft(accel_data)

        freqs_gyro = np.fft.fftfreq(len(gyro_data), d=1.0 / sampling_rate)
        freqs_accel = np.fft.fftfreq(len(accel_data), d=1.0 / sampling_rate)

        # Берем положительные частоты
        pos_mask_gyro = freqs_gyro >= 0
        pos_mask_accel = freqs_accel >= 0

        freqs_gyro = freqs_gyro[pos_mask_gyro]
        gyro_amp = np.abs(gyro_fft[pos_mask_gyro])
        gyro_phase = np.angle(gyro_fft[pos_mask_gyro])

        freqs_accel = freqs_accel[pos_mask_accel]
        accel_amp = np.abs(accel_fft[pos_mask_accel])
        accel_phase = np.angle(accel_fft[pos_mask_accel])

        # Координаты для двух графиков (амплитуда вверху, фаза внизу)
        half_height = img_height // 2
        margin_left = 60
        margin_bottom_amp = half_height - 20
        margin_bottom_phase = img_height - 20

        # Рисуем оси (верхняя для амплитуды, нижняя для фазы)
        cv2.line(img, (margin_left, 20), (margin_left, margin_bottom_amp), (0, 0, 0), 1)
        cv2.line(
            img,
            (margin_left, margin_bottom_amp),
            (img_width - margin_left, margin_bottom_amp),
            (0, 0, 0),
            1,
        )
        cv2.line(
            img,
            (margin_left, half_height + 20),
            (margin_left, margin_bottom_phase),
            (0, 0, 0),
            1,
        )
        cv2.line(
            img,
            (margin_left, margin_bottom_phase),
            (img_width - margin_left, margin_bottom_phase),
            (0, 0, 0),
            1,
        )

        # Рисуем график амплитуды
        max_amp = float(max(gyro_amp.max(), accel_amp.max(), 1))

        def scale_amp(amp):
            return np.interp(amp, [0, max_amp], [0, margin_bottom_amp - 20])

        for i in range(1, len(gyro_amp)):
            x1 = int(
                np.interp(
                    freqs_gyro[i - 1],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y1 = margin_bottom_amp - int(scale_amp(gyro_amp[i - 1]))
            x2 = int(
                np.interp(
                    freqs_gyro[i],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y2 = margin_bottom_amp - int(scale_amp(gyro_amp[i]))
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        for i in range(1, len(accel_amp)):
            x1 = int(
                np.interp(
                    freqs_accel[i - 1],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y1 = margin_bottom_amp - int(scale_amp(accel_amp[i - 1]))
            x2 = int(
                np.interp(
                    freqs_accel[i],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y2 = margin_bottom_amp - int(scale_amp(accel_amp[i]))
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Рисуем график фазы (нижний)
        phase_min, phase_max = -np.pi, np.pi
        y_range_phase = margin_bottom_phase - (half_height + 20)

        def scale_phase(ph):
            return np.interp(ph, [phase_min, phase_max], [0, y_range_phase])

        for i in range(1, len(gyro_phase)):
            x1 = int(
                np.interp(
                    freqs_gyro[i - 1],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph1 = margin_bottom_phase - int(scale_phase(gyro_phase[i - 1]))
            x2 = int(
                np.interp(
                    freqs_gyro[i],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph2 = margin_bottom_phase - int(scale_phase(gyro_phase[i]))
            cv2.line(img, (x1, ph1), (x2, ph2), (255, 0, 0), 2)

        for i in range(1, len(accel_phase)):
            x1 = int(
                np.interp(
                    freqs_accel[i - 1],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph1 = margin_bottom_phase - int(scale_phase(accel_phase[i - 1]))
            x2 = int(
                np.interp(
                    freqs_accel[i],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph2 = margin_bottom_phase - int(scale_phase(accel_phase[i]))
            cv2.line(img, (x1, ph1), (x2, ph2), (0, 255, 0), 2)

        # Добавляем ось X: частоты
        max_freq = (
            max(freqs_gyro[-1], freqs_accel[-1])
            if len(freqs_gyro) > 1 and len(freqs_accel) > 1
            else sampling_rate
        )
        num_ticks_x = 6
        for tick in np.linspace(0, max_freq, num_ticks_x):
            x_pos = int(
                np.interp(tick, [0, max_freq], [margin_left, img_width - margin_left])
            )
            cv2.putText(
                img,
                f"{tick:.1f}",
                (x_pos, img_height - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )

        cv2.putText(
            img,
            "Frequency [Hz]",
            (img_width // 2 - 50, img_height - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        # Добавляем ось Y для амплитуды (upper plot)
        num_ticks_amp = 4
        for tick in np.linspace(0, max_amp, num_ticks_amp):
            y_pos = margin_bottom_amp - int(
                np.interp(tick, [0, max_amp], [0, margin_bottom_amp - 20])
            )
            cv2.putText(
                img,
                f"{tick:.1f}",
                (margin_left - 35, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )
        cv2.putText(
            img,
            "Amplitude",
            (margin_left + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        # Добавляем ось Y для фазы (lower plot)
        num_ticks_phase = 5
        for tick in np.linspace(phase_min, phase_max, num_ticks_phase):
            tick_deg = np.degrees(tick)
            # ограничим текст в интервале ±180
            y_pos = margin_bottom_phase - int(
                np.interp(tick, [phase_min, phase_max], [0, y_range_phase])
            )
            cv2.putText(
                img,
                f"{tick_deg:.0f}",
                (margin_left - 35, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )
        cv2.putText(
            img,
            "Phase [deg]",
            (margin_left + 10, half_height + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        return img
