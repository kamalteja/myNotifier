import logging
import os

from flask import Flask, Response, render_template, request
from freerider.arguments import rider_arguments
from freerider.plugins.hertz import hertz_rides

from notifier import get_static_dir, get_template_dir
from notifier.lib.slack.client import SlackCommandException, SlackForm

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))

earth_app = Flask(
    __name__, template_folder=get_template_dir(), static_folder=get_static_dir()
)


@earth_app.route("/", methods=["GET"])
def hello():
    """Welcome message for the slack-bot app"""
    print(get_template_dir())
    return Response(render_template("earth.html"), 200)


@earth_app.route("/ride", methods=["POST"])
def ride():
    """
    Correlates to /ride slash command
    Looks up requested rides against the rider scrapper
    """

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


@earth_app.route("/notify-ride", methods=["POST"])
def notify_ride():
    """Performs recurring lookup for free ride availability"""
