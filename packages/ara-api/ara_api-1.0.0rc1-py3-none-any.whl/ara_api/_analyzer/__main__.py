import os
import argparse

import colorama
import pyfiglet
from colorama import Fore
from importlib.metadata import version

from .analyzer_offline import main as offline_main
from .analyzer_online import main as online_main


def main():
    ansii_art = pyfiglet.figlet_format(
        "ARA MINI ANALYZER {}".format(version("ara_api")), font="slant", width=70
    )
    summary = (
        "{cyan}Поздравляем! Вы запустили анализатор для обработки данных с дрона ARA MINI\n"
        "{cyan}Анализатор работает в двух режимах: онлайн и оффлайн\n"
        "{cyan}Для работы в онлайн режиме необходимо подключение к дрону по WiFi и запущенное ядро API(ara-api-core)\n"
    ).format(cyan=Fore.CYAN)

    print(Fore.BLUE + ansii_art)
    print(summary)

    parser = argparse.ArgumentParser(
        description="Applied Robotics Avia Simple Analyzer"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        required=False,
        help="Directory to save CSV files",
    )
    parser.add_argument(
        "--csv-dir", type=str, required=True, help="Directory to save CSV files"
    )
    args = parser.parse_args()

    if not os.path.exists(args.csv_dir):
        os.makedirs(args.csv_dir)

    if not args.offline:
        online_main(args.csv_dir)

    if args.offline:
        offline_main(args.csv_dir)


if __name__ == "__main__":
    main()
