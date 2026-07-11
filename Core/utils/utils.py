import random
import string
import threading
import time
import sys
import ctypes

from threading import Lock
from typing import Callable

from Core.NexusColors.color import NexusColor

VATOS = threading.Semaphore(28)

class Utils:

    @staticmethod
    def random_password(length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def random_string(length: int = 16) -> str:
        if length <= 0:
            return ""

        first_chars = string.ascii_lowercase + string.digits + "_"
        first_char = random.choice(first_chars)

        if length == 1:
            return first_char

        middle_chars = first_chars + "."
        middle = []
        remaining = length - 2 

        for _ in range(remaining):
            if middle and middle[-1] == ".":
                next_char = random.choice(first_chars)
            else:
                next_char = random.choice(middle_chars)
            middle.append(next_char)

        last_char = random.choice(first_chars)

        return first_char + "".join(middle) + last_char

    @staticmethod
    def random_birthday():
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = random.randint(1990, 2005)
        return year, month, day

    @staticmethod
    def load_proxy(file_path: str) -> str | None:
        with open(file_path, encoding="utf-8") as f:
            proxies = f.read().splitlines()

        if not proxies:
            return None

        proxy = random.choice(proxies)
        proxies.remove(proxy)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(proxies))

        return proxy
    
    @staticmethod
    def has_fingerprints() -> bool:
        try:
            with open("io/input/fingerprints.txt", encoding="utf-8") as f:
                return bool(f.read().strip())
        except FileNotFoundError:
            return False

    @staticmethod
    def get_fingerprint() -> str | None:
        try:
            with open("io/input/fingerprints.txt", encoding="utf-8") as f:
                fps = [line.strip() for line in f if line.strip()]

            if not fps:
                return None

            fp = fps.pop()

            return fp

        except FileNotFoundError:
            return None
        

class TitleBarUpdater:
    def __init__(self, stats_provider: Callable[[], str], interval: float = 0.5):
        self.stats_provider = stats_provider
        self.interval = interval

        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="TitleBarUpdater",
                daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                title = self.stats_provider()
                if title:
                    self._set_title(title)
            except Exception:
                pass

            time.sleep(self.interval)

    @staticmethod
    def _set_title(title: str) -> None:
        if sys.platform == "win32":
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        else:
            sys.stdout.write(f"\33]0;{title}\a")
            sys.stdout.flush()

class VatosLogger:
    
    def __init__(self, config):
        self.LC = f"{NexusColor.MAIN_COLOR}[{NexusColor.LIGHTBLACK}t.me/cfvatos{NexusColor.MAIN_COLOR}] "
        self.config = config
        
    def log(self, msg: str) -> None:
        print(self.LC + NexusColor.LIGHTBLACK + msg)

    def log_token(self, msg: str, token: str) -> None:
        if self.config["logs"]["censor_token"]:
            parts = token.split(".")

            if len(parts) == 3:
                part1, part2, part3 = parts

                censored_part1 = part1[:6] + "******"
                censored_part3 = "*******" + part3[-6:]

                token = f"{censored_part1}.{part2}.{censored_part3}"
    
        print(self.LC + NexusColor.LIGHTBLACK + msg + token)
        

class ProxyProvider:
    def __init__(self, file: str):
        self.file = file
        self.lock = Lock()

    def get(self) -> str | None:
        with self.lock:
            try:
                with open(self.file, "r+", encoding="utf-8") as f:
                    proxies = [p.strip() for p in f if p.strip()]

                    if not proxies:
                        return None

                    proxy = proxies.pop(0)

                    f.seek(0)
                    f.truncate()
                    f.write("\n".join(proxies))

                    return proxy
            except FileNotFoundError:
                return None

class TokenStorage:
    def save(self, ctx, file: str):
        with open(f"io/output/{file}.txt", "a", encoding="utf-8") as f:
            f.write(f"{ctx.email}:{ctx.password}:{ctx.token}\n")
            