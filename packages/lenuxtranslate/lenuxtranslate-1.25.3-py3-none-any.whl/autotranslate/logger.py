import logging
from colorama import Fore, Style

# Log dosyası ayarları
logging.basicConfig(filename="lenuxtranslate.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

def log_info(message):
    print(Fore.GREEN + "[INFO]" + Style.RESET_ALL + f" {message}")
    logging.info(message)

def log_warning(message):
    print(Fore.YELLOW + "[WARNING]" + Style.RESET_ALL + f" {message}")
    logging.warning(message)

def log_error(message):
    print(Fore.RED + "[ERROR]" + Style.RESET_ALL + f" {message}")
    logging.error(message)
