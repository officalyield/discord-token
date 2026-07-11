import time
import requests

from Core.NexusColors.color import NexusColor


class Solver:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.api_key = self.config["solver"]["api_key"]

    def solve(self, ctx, website_url: str = None):
        if not hasattr(ctx, "captcha_rqdata"):
            raise ValueError("Context missing captcha_rqdata")

        self.logger.log("Solving Captcha via NopeCHA...")
        start = time.time()

        payload = {
            "key": self.api_key,
            "type": "hcaptcha",
            "sitekey": "a9b5fb07-92ff-493f-86fe-352a2803b3df",
            "url": website_url or "https://discord.com/register",
            "data": {
                "rqdata": ctx.captcha_rqdata
            }
        }

        try:
            # Step 1: Submit Task
            r = requests.post("https://api.nopecha.com/token/", json=payload, timeout=30)
            data = r.json()

            if "data" not in data:
                error_msg = data.get("message", "Unknown error")
                raise RuntimeError(f"NopeCHA task creation failed: {error_msg}")

            task_id = data["data"]

            # Step 2: Poll for Result
            timeout = self.config.get("solver", {}).get("captcha_timeout", 120)
            while time.time() - start < timeout:
                r = requests.get(
                    "https://api.nopecha.com/token/",
                    params={"key": self.api_key, "id": task_id},
                    timeout=30
                )
                res_data = r.json()

                if "data" in res_data:
                    token = res_data["data"]
                    elapsed = time.time() - start
                    display_token = token[:32] + "..."

                    self.logger.log(
                        f"Captcha Solved in "
                        f"{NexusColor.MAIN_COLOR}{elapsed:.1f}s "
                        f"{NexusColor.LIGHTBLACK}("
                        f"{NexusColor.MAIN_COLOR}{display_token}"
                        f"{NexusColor.LIGHTBLACK})"
                    )
                    ctx.captcha_key = token
                    return
                
                if res_data.get("error") == 14: # Incomplete job
                    time.sleep(3)
                    continue
                
                error_msg = res_data.get("message", "Unknown error during polling")
                raise RuntimeError(f"NopeCHA polling failed: {error_msg}")

            raise TimeoutError("NopeCHA solve timed out")

        except Exception as e:
            raise RuntimeError(f"NopeCHA process failed: {e}")