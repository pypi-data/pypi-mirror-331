import multiprocessing
import os
import time
import logging
import asyncio
import platform
from importlib.metadata import version

import colorama
import pyfiglet
from colorama import Fore

from _navigation.nav_service import serve as nav_serve
from _driver.msp_service import main as msp_main

import argparse

system = "win"
system = platform.system()
if system in ["Linux", "Darwin"]:  # Darwin is macOS
    system = "unix"
    multiprocessing.set_start_method("fork")


class ServiceManager:
    """
    Manages the lifecycle of multiple services running in parallel.
    """

    def __init__(self):
        """
        Initializes the ServiceManager with necessary configurations.
        """
        self.ascii_art = pyfiglet.figlet_format(
            "ARA MINI API {}".format(version("ara_api")), font="slant", width=50
        )
        self.summary = (
            "{cyan}Поздравляем! Вы запустили API для программирования ARA MINI\n\n"
            "{cyan}Для подключения в конфигураторе к квадрокоптеру:\n"
            "{cyan}\tUDP: \t{magenta}http://192.168.2.113:14550\n"
            "{cyan}\tTCP: \t{magenta}http://192.168.2.113:5760\n\n"
            "{cyan}Изображение с камеры: \t\t{magenta}http://192.168.2.113:81/stream\n"
        ).format(cyan=Fore.CYAN, magenta=Fore.MAGENTA)
        self.docs = (
            "{magenta}Applied Robotics Avia API {cyan}— это современный API для управления линейкой дронов и самолетов компании "
            "{magenta}Applied Robotics Avia, {cyan}а также для работы с симулятором {magenta}AgroTechSim.\n\n"
            "{cyan}### Основные особенности:\n"
            "{cyan}1. Экранирование работы от конечного пользователя.\n"
            "{cyan}2. Интегрированная документация, загружаемая вместе с API.\n"
            "{cyan}3. Высокая скорость работы благодаря использованию HTTP/2 и gRPC.\n"
            "{cyan}4. Простота запуска и настройки.\n"
            "{cyan}5. Поддержка анализаторов для выполнения лабораторных работ.\n"
            "{cyan}6. Предохранительные меры для безопасности автономных полетов.\n\n"
            "{cyan}### Команды:\n"
            "{cyan}- Запуск API: {magenta}ara-api-core\n"
            "{cyan}- Запуск анализатора: {magenta}ara-api-analyzer\n"
            "{cyan}- Запуск vision-сервиса: {magenta}ara-api-vision\n\n"
            "{cyan}### Для запуска документации к командам нужно добавить флаг при вызове: {magenta}--help\n"
        ).format(cyan=Fore.CYAN, magenta=Fore.MAGENTA)

        self.processes = []
        self.parser = argparse.ArgumentParser(
            description="Запуск приложения и сервисов для автономного полета и управления ARA MINI"
        )
        self.parser.add_argument(
            "--sensor-output",
            action="store_true",
            help="Вывод данных с датчиков в терминал",
        )
        self.parser.add_argument(
            "--logging",
            action="store_true",
            help="Включение логирования",
        )
        self.parser.add_argument(
            "--docs",
            action="store_true",
            help="Отображение документации",
        )
        self.parser.add_argument(
            "--analyzer",
            action="store_true",
            help="Запуск чтения данных для только для анализатора",
        )
        self.parser.add_argument(
            "--only-msp",
            action="store_true",
            help="Запуск чтения данных c полетного контроллера ARA MINI",
        )
        self.parser.add_argument(
            "--serial",
            type=str,
            default=None,
            help="Подключение по Serial-порту (по умолчанию /dev/ttyACM0)",
        )  # TODO: дореализовать флаг
        self.parser.add_argument(
            "--ip",
            type=str,
            default=None,
            help="Подключение по TCP с явным указанием IP (по умолчанию 192.168.2.113)",
        )  # TODO: дореализовать флаг

        self.args = self.parser.parse_args()

        if self.args.logging:
            self.__init_logging__("log")
        else:
            self.logger = logging.getLogger("service_manager")
            self.logger.disabled = True

    def __init_logging__(self, log_directory="log"):
        """
        Sets up logging configuration for the service manager.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.logger = logging.getLogger("service_manager")
        self.logger.setLevel(logging.INFO)
        self.logger_formater = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger_handler = logging.FileHandler(
            os.path.join(log_directory, "service_manager.log")
        )
        self.logger_handler.setFormatter(self.logger_formater)
        self.logger.addHandler(self.logger_handler)

    def gui_run(self):
        colorama.init()

        print(Fore.BLUE + self.ascii_art)
        print("=" * 60)
        print("\n")
        print(Fore.CYAN + self.summary)

        if self.args.sensor_output:
            print(Fore.RED + "Data output:")

        print(Fore.MAGENTA)
        colorama.deinit()

    def show_quick_docs(self):
        print(Fore.CYAN + self.docs)

    def run_nav_service(self):
        """
        Runs the Navigation service.
        """
        try:
            self.logger.info("Starting Navigation service")
            asyncio.run(nav_serve(log=self.args.logging))
        except Exception as e:
            self.logger.error("Error starting Navigation service: %s", e)

    def run_msp_service(self):
        """
        Runs the MSP service.
        """
        try:
            self.logger.info("Starting MSP service")
            if self.args.ip:
                raise Exception("Only one connection type can be specified")

            if self.args.ip is not None:
                type = "TCP"
            elif self.args.serial is not None:
                type = "SERIAL"
            else:
                type = "TCP"
                self.args.ip = "192.168.2.113"
                self.args.serial = None

            msp_main(
                ip=self.args.ip,
                type=type,
                serial=self.args.serial,
                analyzer=self.args.analyzer,
                logging=self.args.logging,
                output=self.args.sensor_output,
            )
        except Exception as e:
            self.logger.error("Error starting MSP service: %s", e)

    def start_services(self):
        """
        Starts all the services as separate processes.
        """
        self.processes.append(
            multiprocessing.Process(
                target=self.run_msp_service, name="MSP", daemon=True
            )
        )

        if not self.args.only_msp:
            self.processes.append(
                multiprocessing.Process(
                    target=self.run_nav_service, name="NAV", daemon=True
                )
            )

        for process in self.processes:
            try:
                self.logger.info("Starting process %s", process.name)
                process.start()
            except Exception as e:
                self.logger.error("Error starting process %s: %s", process.name, e)

    def monitor_services(self):
        """
        Monitors the services and logs their status.
        """
        try:
            while True:
                for process in self.processes:
                    if not process.is_alive():
                        self.logger.warning("%s process has terminated.", process.name)
                        return
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Terminating processes due to KeyboardInterrupt")
            self.terminate_services()
        except Exception as e:
            self.logger.error("Error monitoring services: %s", e)
            self.terminate_services()

    def terminate_services(self):
        """
        Terminates all running services.
        """
        for process in self.processes:
            try:
                self.logger.info("Terminating process %s", process.name)
                process.terminate()
                process.join()
            except Exception as e:
                self.logger.error("Error terminating process %s: %s", process.name, e)
        self.logger.info("All processes terminated.")

    def mainloop(self):
        self.gui_run()
        if self.args.docs:
            self.show_quick_docs()
        else:
            self.start_services()
            self.monitor_services()


def main():
    if platform.system() == "Windows":
        if multiprocessing.get_start_method(allow_none=True) != "spawn":
            multiprocessing.set_start_method("spawn")
    manager = ServiceManager()
    manager.mainloop()


if __name__ == "__main__":
    main()
