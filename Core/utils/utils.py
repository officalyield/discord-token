import random
import string

from typing import Tuple


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