import requests

from typing import Optional
from Core.communication.phone.base import BasePhone


class OnlineSimApi(BasePhone):
    BASE_URL = "https://onlinesim.io/api"

    def __init__(self, api_key: str, country: str = "212"):
        super().__init__(None, None, None)
        self.api_key = api_key
        self.country = country

    def _request(self, endpoint: str, params: dict) -> dict:
        try:
            resp = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as e:
            raise RuntimeError(f"OnlineSim API request failed: {e}") from e

    def get_phone_number(self):
        data = self._request(
            "getNum.php",
            params={
                "apikey": self.api_key,
                "country": self.country,
                "service": "discord",
            },
        )

        if "tzid" not in data:
            raise RuntimeError(f"Failed to get number: {data}")

        tzid = data["tzid"]

        state = self._request(
            "getState.php",
            params={
                "apikey": self.api_key,
                "tzid": tzid,
            },
        )

        if not state or not isinstance(state, list):
            raise RuntimeError(f"Invalid state response: {state}")

        number = state[0].get("number")
        if not number:
            raise RuntimeError(f"No number returned: {state}")

        return number, tzid


    def get_sms_code(self, tzid: str) -> Optional[str]:
        data = self._request(
            "getState.php",
            params={
                "apikey": self.api_key,
                "tzid": tzid,
                "message_to_code": 1,
                "msg_list": 0,
                "clean": 1,
            },
        )

        if not data or not isinstance(data, list):
            return None

        state = data[0]
        response = state.get("response")

        if response not in (1, "1", "TZ_NUM_ANSWER"):
            return None

        code = state.get("msg")
        if code:
            return code

        for sms in state.get("sms", []):
            code = self._extract_code(sms.get("text"))
            if code:
                return code

        return None
    
    def finish_number(self, tzid: str) -> bool:
        data = self._request(
            "setOperationOk.php",
            params={
                "apikey": self.api_key,
                "tzid": tzid,
            }
        )
        
        