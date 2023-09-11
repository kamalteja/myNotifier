"""notifier app init"""

import logging
import os

from flask import Flask

from notifier.config import APP_DIR, get_config
from notifier.earth_bot import earth_app
from notifier.extensions import SQL_DB
from notifier.lib.ride.frider import RideThread
from notifier.models import FriderThread

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))


def get_template_dir() -> str:
    """Get template files directory location"""
    return os.path.join(APP_DIR, "template")


def get_static_dir() -> str:
    """Get static files directory location"""
    return os.path.join(APP_DIR, "static")


def create_app():
    """Flask application factory"""
    app = Flask(
        __name__, template_folder=get_template_dir(), static_folder=get_static_dir()
    )

    app.config.from_object(get_config())
    app.config.from_prefixed_env()

    # Registry blueprints
    app.register_blueprint(earth_app)

    SQL_DB.init_app(app)

    with app.app_context():
        # Creating tables on app start up.
        log.info("Initializing database: %s", app.config["SQLALCHEMY_DATABASE_URI"])
        SQL_DB.create_all()

        # Query frider_db table in database and launch rider threads
        for entry in FriderThread.query.all():
            RideThread.launch(args=entry.thread_arg)

    return app
