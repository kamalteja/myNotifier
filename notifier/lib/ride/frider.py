""" Freerider library file for earth bot """

import logging
import os
import threading

from freerider.arguments import rider_arguments
from freerider.plugins.hertz import hertz_rides

from notifier.lib.exceptions import SlackCommandException
from notifier.lib.slack.client import slack_client

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))


class RideThread(threading.Thread):
    """Runs freerider checks in thread(s)"""

    thread_name = "Freerider"

    def __init__(self, *args, sleep_interval=60 * 5, kill=False, **kwargs):
        super().__init__(*args, name=f"{self.thread_name}->{kwargs['args']}", **kwargs)

        self._kill = threading.Event()
        self.sleep_interval = sleep_interval
        self.value = ""
        self.thread_args = self._args
        if kill:
            self.kill()

    def run(self):
        while True:
            log.info("Running Thread: '%s'", self.name)
            self.value = get_ride_details(self.thread_args)
            log.debug(self.value)

            # Posting message to slack channel
            result = slack_client.chat_postMessage(channel="freerider", text=self.value)
            if result["ok"] is not True:
                log.warning("Falied to send rider details to #freerider channel")
                log.warning("Killing thread %s", self.name)
                self.kill()

            is_killed = self._kill.wait(timeout=self.sleep_interval)
            if is_killed:
                break
        log.info("killing thread: %s", self)

    def kill(self):
        """Set _kill Event to true to kill the thread"""
        self._kill.set()

    @classmethod
    def list_threads(cls):
        """Returns a list of runnging freerider threads"""
        return [
            thread for thread in threading.enumerate() if cls.thread_name in thread.name
        ]

    @classmethod
    def launch(cls, *args, **kwargs):
        """Launches rider threads"""
        ride_thread = cls(*args, **kwargs)
        ride_thread.start()
        return ride_thread


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
        ride_details = [f"No rides available for '{ride_args}'"]

    log.debug("Ride details: %s", ride_details)
    return "\n".join(ride_details)
