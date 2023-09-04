"""Earth bot for slack commands"""

from datetime import datetime
import hashlib
import hmac

import logging
import os

from flask import Flask, Response, render_template, request

from notifier import get_static_dir, get_template_dir
from notifier.lib.slack.client import SlackCommandException, SlackForm
from notifier.ride.frider import get_ride_details

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))

earth_app = Flask(
    __name__, template_folder=get_template_dir(), static_folder=get_static_dir()
)


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


@earth_app.route("/notify-ride", methods=["POST"])
def notify_ride():
    """Performs recurring lookup for free ride availability"""
