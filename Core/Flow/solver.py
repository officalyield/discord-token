import time
import requests

from Core.NexusColors.color import NexusColor


class Solver:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

        self.api_base = "https://api.anysolver.com"
        self.api_key = self.config["solver"]["api_key"]

    def start_solve(self, rqdata: str, proxy: str = None, website_url: str = None) -> str:
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "PopularCaptchaEnterpriseToken",
                "websiteURL": website_url or "https://discord.com/register",
                "websiteKey": "a9b5fb07-92ff-493f-86fe-352a2803b3df",
                "proxy": proxy,
                "rqdata": rqdata
            },
            "provider": self.config["solver"]["subservice"],
        }

        r = requests.post(
            f"{self.api_base}/createTask",
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )

        data = r.json()

        if data.get("errorId") != 0:
            raise RuntimeError(
                f"{data.get('errorCode')}: "
                f"{data.get('errorDescription')}"
            )

        return data["taskId"]

    def wait_for_result(self, task_id: str, timeout: int = 120):
        if isinstance(self.config, dict):
            timeout = self.config.get("captcha_timeout", timeout)

        start = time.time()

        time.sleep(4)

        while True:
            r = requests.post(
                f"{self.api_base}/getTaskResult",
                json={
                    "clientKey": self.api_key,
                    "taskId": task_id
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )

            data = r.json()

            status = data.get("status")

            if status == "ready":
                elapsed = time.time() - start

                token = data["solution"]["token"]

                display_token = token[:32] + "..."

                self.logger.log(
                    f"Captcha Solved in "
                    f"{NexusColor.MAIN_COLOR}{elapsed:.1f}s "
                    f"{NexusColor.LIGHTBLACK}("
                    f"{NexusColor.MAIN_COLOR}{display_token}"
                    f"{NexusColor.LIGHTBLACK})"
                )

                return data

            if status == "failed":
                raise RuntimeError(
                    f"Captcha solve failed: "
                    f"{data.get('errorCode')} - "
                    f"{data.get('errorDescription')}"
                )

            if time.time() - start > timeout:
                raise TimeoutError("Captcha solve timed out")

            time.sleep(3)

    def solve(self, ctx, website_url: str = None):
        if not hasattr(ctx, "captcha_rqdata"):
            raise ValueError("Context missing captcha_rqdata")

        self.logger.log("Solving Captcha...")

        proxy = getattr(ctx, "proxy", None)

        task_id = self.start_solve(
            rqdata=ctx.captcha_rqdata,
            proxy=proxy,
            website_url=website_url
        )

        result = self.wait_for_result(task_id)

        if result:
            ctx.captcha_key = result["solution"]["token"]