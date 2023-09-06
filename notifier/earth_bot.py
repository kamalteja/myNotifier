"""Earth bot for slack commands"""

import hashlib
import hmac
import logging
import os
from datetime import datetime

from flask import Blueprint, Response, render_template, request

from notifier.extensions import SQL_DB
from notifier.lib.exceptions import SlackCommandException
from notifier.lib.ride.frider import RideThread, get_ride_details
from notifier.lib.slack.client import SlackForm
from notifier.lib.slack.rich_text import AccessoryBlock, Checkbox, CheckboxesAccessory
from notifier.models import FriderThread

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))

earth_app = Blueprint("earth_app", __name__)


@earth_app.before_request
def validate_request():
    """Validate requests from SLACK"""
    if request.method == "GET":
        return

    log.info(
        "Verifying reqeust -> method: %s, url: %s, path: %s",
        request.method,
        request.url,
        request.path,
    )

    # Validating timestamp of request to be less than 5minutes.
    timestamp = request.headers["X-Slack-Request-Timestamp"]
    if (
        datetime.now() - datetime.fromtimestamp(int(timestamp))
    ).total_seconds() > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        raise SlackCommandException("request timestamp is more than five minutes")

    # Verifying the POST request against signing key
    raw_body = request.get_data().decode()
    if not raw_body:
        raise SlackCommandException("Received Emply POST body")

    base_string = str.encode(f"v0:{timestamp}:{raw_body}")
    my_signature_digest = hmac.new(
        key=os.environ["SLACK_APP_SIGNING_KEY"].encode("UTF-8"),
        msg=base_string,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        f"v0={my_signature_digest}", request.headers["X_SLACK_SIGNATURE"]
    ):
        raise SlackCommandException(f"Invalid Signature for path: '{request.url}'")


@earth_app.route("/", methods=["GET"])
def hello():
    """Welcome message for the slack-bot app"""
    return Response(render_template("earth.html"), 200)


@earth_app.route("/ride", methods=["POST"])
def ride():
    """
    Correlates to /ride slash command
    Looks up requested rides against the rider scrapper
    """
    slack_form = SlackForm(**request.form.to_dict())
    return Response(get_ride_details(slack_form.text), 200)


@earth_app.route("/ride-notify", methods=["POST"])
def notify_ride():
    """Performs recurring lookup for free ride availability"""
    slack_form = SlackForm(**request.form.to_dict())

    _text = slack_form.text.strip()

    # Recoding this thread in database to survive application restart
    frider_entry = FriderThread(thread_arg=_text)
    SQL_DB.session.add(frider_entry)
    SQL_DB.session.commit()

    # Start rider thread
    ride_thread = RideThread.launch(args=_text)

    return Response(
        f"Successfully started a notify thread {ride_thread.name}", status=200
    )


@earth_app.route("/list", methods=["POST"])
def list_notify_threads():
    """Lists currently running rider threads"""
    checkbox_options = []
    for i, ride_thread in enumerate(RideThread.list_threads()):
        checkbox_options.append(
            Checkbox(text=ride_thread.name, value=f"{ride_thread.name}-{i}")
        )

    threads = "Currently there are no rider threads running"
    if checkbox_options:
        threads = AccessoryBlock(
            text="List of running threads",
            accessory=CheckboxesAccessory(options=checkbox_options),
        ).get_slack_payload()

    log.debug(threads)
    return Response(threads, status=200, content_type="application/json")


@earth_app.route("/stop", methods=["POST"])
def stop_rider_thread():
    """Stops requested background thread"""
    slack_form = SlackForm(**request.form.to_dict())

    for thread in RideThread.list_threads():
        if slack_form.text not in thread.name:
            continue

        frider_entries = FriderThread.query.filter_by(
            thread_arg=thread.thread_args
        ).all()
        log.debug(frider_entries)
        if not frider_entries:
            log.warning("Database entry not found: '%s'", thread.thread_args)
            return Response("Skipping ride kill request", status=200)

        thread.kill()
        thread.join()

        if thread.is_alive():
            _text = f"Falied to stop '{thread}'"
            log.warning(_text)
            return Response(_text, status=500)

        # Removing entry from database
        for entry in frider_entries:
            log.debug("Dropping row: %s", entry)
            SQL_DB.session.delete(entry)
            SQL_DB.session.commit()

        return Response(f"Successfully stopped '{thread.name}'", 200)
    return Response(f"Requested thread '{slack_form.text}' is not running", status=200)
