import time

from Core.NexusColors.color import NexusColor


class PhoneVerification:
    def __init__(self, session, logger, stats, phone_api, solver) -> None:
        self.session = session
        self.logger = logger
        self.stats = stats
        self.phone_api = phone_api
        self.solver = solver

    def send_sms_code(self, ctx, phone_number: str) -> bool:
        try:
            response = self.session.post(
                "https://discord.com/api/v9/users/@me/phone",
                json={"phone": phone_number},
            )

            if response.ok:
                return True

            if "You need to update your app" not in response.text:
                return False

            data = response.json()
            ctx.captcha_rqdata = data.get("captcha_rqdata")
            ctx.captcha_rqtoken = data.get("captcha_rqtoken")
            ctx.captcha_session_id = data.get("captcha_session_id")


            self.solver.solve(ctx, website_url="https://discord.com/channels/@me")
            self.session.headers.update({
                "x-captcha-key": ctx.captcha_key,
                "x-captcha-rqtoken": ctx.captcha_rqtoken,
                "x-captcha-session-id": ctx.captcha_session_id,
            })
            
            response = self.session.post(
                "https://discord.com/api/v9/users/@me/phone",
                json={"phone": phone_number},
            )
            if not response.ok:
                raise RuntimeError(f"Failed to send SMS code: {response.text}")
            
            return response.ok

        except Exception as e:
            with open("error.txt", "a") as f:
                f.write(f"[send_sms_code] {e}\n")
            raise RuntimeError(f"Failed to send SMS code: {e}") from e

    def verify_sms_code(self, ctx, phone_number: str, code: str) -> bool:
        try:
            response = self.session.post(
                "https://discord.com/api/v9/phone-verifications/verify",
                json={"phone": phone_number, "code": code},
            )

            if not response.ok:
                return False

            phone_token = response.json().get("token")
            if not phone_token:
                raise RuntimeError("Phone verification response missing token")

            response = self.session.post(
                "https://discord.com/api/v9/users/@me/phone",
                json={"phone_token": phone_token, "password": ctx.password},
            )

            if not response.ok:
                raise RuntimeError(
                    f"Phone binding failed: HTTP {response.status_code} - {response.text[:200]}"
                )

            self.logger.log(
                f"Successfully Verified Phone -> {NexusColor.GREEN}{phone_number}"
            )
            self.stats.pv_tokens += 1
            return True

        except RuntimeError:
            raise
        except Exception as e:
            with open("error.txt", "a") as f:
                f.write(f"[verify_sms_code] {e}\n")
            raise RuntimeError(f"Failed to verify SMS code: {e}") from e

    def wait_for_sms_code(self, ctx, phone_number: str, timeout: int = 100) -> bool:
        self.logger.log(
            f"Waiting for SMS code -> {NexusColor.MAIN_COLOR}{phone_number}"
        )

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                code = self.phone_api.get_sms_code(ctx.tzid)

                if code:
                    elapsed = time.time() - start_time
                    self.logger.log(
                        f"Received SMS code in {NexusColor.MAIN_COLOR}{elapsed:.1f}s "
                        f"{NexusColor.LIGHTBLACK}({NexusColor.MAIN_COLOR}{code}{NexusColor.LIGHTBLACK})"
                    )
                    self.phone_api.finish_number(tzid=ctx.tzid)
                    return self.verify_sms_code(ctx, phone_number, code)

            except RuntimeError:
                raise
            except Exception as e:
                with open("error.txt", "a") as f:
                    f.write(f"[wait_for_sms_code] polling error: {e}\n")

            time.sleep(1)

        raise RuntimeError(
            f"SMS code timeout after {timeout}s for {phone_number}"
        )

    def verify_phone(self, ctx) -> bool:
        ctx.phone_number, ctx.tzid = self.phone_api.get_phone_number()

        self.logger.log(
            f"Acquired phone number {NexusColor.MAIN_COLOR}{ctx.phone_number}{NexusColor.RESET}"
        )

        self.session.headers.update({"referer": "https://discord.com/channels/@me"})
        self.session.headers = {
            k: v for k, v in self.session.headers.items()
            if k not in ("sec-fetch-user", "upgrade-insecure-requests")
        }

        if not self.send_sms_code(ctx=ctx, phone_number=ctx.phone_number):
            self.phone_api.finish_number(tzid=ctx.tzid)
            raise RuntimeError("Failed to initiate SMS code sending")

        if not self.wait_for_sms_code(ctx=ctx, phone_number=ctx.phone_number):
            self.phone_api.finish_number(tzid=ctx.tzid)
            raise RuntimeError("Failed to complete phone verification")

        return True