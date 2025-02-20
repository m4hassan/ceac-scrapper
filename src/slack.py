import logging
import config

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

channel = "C08DWMHED0T"

class Slack:

    def __init__(self) -> None:
        self.client = WebClient(token=config.SLACK_AUTH_TOKEN)

    def send_message_to_channel(self, payload):
        try:
            resp = self.client.chat_postMessage(channel=channel,
                                                text="Visa Case Number Error",
                                                blocks=payload)
            if not resp.status_code == 200:
                return False
            logger.info(f"Slack message sent: {resp}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack API error \n {e}")
            return False
        except Exception as e:
            logger.error(f"Something went wrong in sending slack message.\n {e}")
            return False

    def create_slack_payload(self, visa_case_number, visa_type):
        slack_payload = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:* Invalid Visa Case Number\n"
                            f"*Visa Case Number:* {visa_case_number}\n"
                            f"*Visa Type:* {visa_type}"
                }
            }
        ]
        return slack_payload