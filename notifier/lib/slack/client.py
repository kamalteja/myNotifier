import os
from dataclasses import dataclass

import slack

slack_client = slack.WebClient(os.environ["SLACK_BOT_TOKEN"])


class SlackCommandException(ValueError):
    """Exception caused during slash command execution"""


@dataclass
class SlackForm:
    """Represents slack post data (over webhook)"""

    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    api_app_id: str
    is_enterprise_install: str
    response_url: str
    trigger_id: str
