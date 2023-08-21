"""Slack Bot"""

import logging
import os
from dataclasses import dataclass

import slack
from flask import Flask, Response, request
from freerider.arguments import rider_arguments
from freerider.plugins.hertz import hertz_rides

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))

app = Flask(__name__)
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


@app.route("/", methods=["GET"])
def hello():
    """Welcome message for the slack-bot app"""
    return "Earth is up and running!!", 200


@app.route("/ride", methods=["POST"])
def ride():
    """Correlates to /ride slash command"""

    def get_rider_args(data: str):
        stations = data.split(":")
        if len(stations) > 2:
            raise SlackCommandException(f"Invalid argument supplied: {data}")

        if data.startswith(":"):
            return ["--to", data[1:]]

        if data.endswith(":"):
            return ["--from", data[:-1]]

        if ":" not in data:
            return ["-s", data]

        return ["--from", stations[0], "--to", stations[1]]

    slack_form = SlackForm(**request.form.to_dict())
    if slack_form.command != "/ride":
        raise SlackCommandException(f"Unknown slash command : {slack_form.command}")

    ride_details = []
    args = get_rider_args(slack_form.text)
    log.debug("Arguments to rider: %s", args)

    for free_ride in hertz_rides(rider_arguments(args)):
        ride_details.append(str(free_ride))

    if not ride_details:
        ride_details = [f"No matching rides found for '{slack_form.text}'"]

    log.debug("Ride details: %s", ride_details)
    return Response("\n".join(ride_details), 200)


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
