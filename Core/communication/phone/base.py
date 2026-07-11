import time
import re

from abc import ABC, abstractmethod
from typing import Optional

class BasePhone(ABC):
    def __init__(self, session, logger, stats) -> None:
        self.session = session
        self.logger = logger
        self.stats = stats

    @abstractmethod
    def get_phone_number(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_sms_code(self, phone_number: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def finish_number(self, id: str) -> bool:
        pass