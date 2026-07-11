from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from Core.NexusColors.color import NexusColor

class MailVerify:
    def __init__(self, session, logger, stats) -> None:
        self.session = session
        self.logger = logger
        self.stats = stats

    def get_verify_token(self, upn: str) -> Optional[str]:
        try:
            response = self.session.get(
                'https://click.discord.com/ls/click',
                params={'upn': upn},
                allow_redirects=False
            )
            location = response.headers.get("Location")
            if location:
                fragment = urlparse(location).fragment
                if fragment and "token=" in fragment:
                    return fragment.split("token=")[-1]
        except Exception as e:
            print(f"Error getting verify token: {e}")
            with open("error.txt", "a") as f:
                f.write(str(e) + "\n")
        return None

    def verify_token(self, ctx) -> None:
        verify_token = self.get_verify_token(ctx.upn)
        if not verify_token:
            return None, False

        try:
            self.session.headers.update({"referer": "https://discord.com/verify"})
            response = self.session.post(
                'https://discord.com/api/v9/auth/verify',
                json={'token': verify_token}
            )
            if 200 <= response.status_code < 300:
                token = response.json().get("token")
                self.stats.ev_tokens += 1
                self.logger.log_token(f"Succsefully verified Mail -> {NexusColor.MAIN_COLOR}", token)
                ctx.token = token
                return
            
        except Exception as e:
            print(f"Error verifying token: {e}")
            with open("error.txt", "a") as f:
                f.write(str(e) + "\n")

        return None, False