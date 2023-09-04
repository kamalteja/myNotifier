""" Freerider library file for earth bot """

import logging
import os

from freerider.arguments import rider_arguments
from freerider.plugins.hertz import hertz_rides

from notifier.lib.slack.client import SlackCommandException

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))


def get_rider_args(ride_arg: str):
    """Parses arguments supplied in /ride slash command"""
    stations = ride_arg.split(":")
    if len(stations) > 2:
        raise SlackCommandException(f"Invalid argument supplied: {ride_arg}")

    if ride_arg.startswith(":"):
        return ["--to", ride_arg[1:]]

    if ride_arg.endswith(":"):
        return ["--from", ride_arg[:-1]]

    if ":" not in ride_arg:
        return ["-s", ride_arg]

    return ["--from", stations[0], "--to", stations[1]]


def get_ride_details(ride_args: str):
    ride_details = []
    args = get_rider_args(ride_args)
    log.debug("Arguments to rider: %s", args)

    for free_ride in hertz_rides(rider_arguments(args)):
        ride_details.append(str(free_ride))

    if not ride_details:
        ride_details = [f"No matching rides found for '{ride_args}'"]

    log.debug("Ride details: %s", ride_details)
    return "\n".join(ride_details)
