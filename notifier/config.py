""" This py file defines configuration for the flask app"""
import logging
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("SLACK_BOT_LOGLEVEL", "INFO"))


class Config:
    """Global config for flask app"""

    @staticmethod
    def db_path(db_name: str):
        """Returns path to database file"""
        _dir_path = "/tmp/db"
        if not os.path.isdir(_dir_path):
            os.mkdir(_dir_path)
        return os.path.join(_dir_path, db_name)

    DEBUG = False
    TESTING = False

    # Database config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path("earth.db")


class ProductionConfig(Config):
    """Production config for flask app"""


class DevelopmentConfig(Config):
    """Development Config for flask app"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + Config.db_path("dev-earth.db")


class TestingConfig(Config):
    """Testing Config for flask app"""

    TESTING = True


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "test": TestingConfig,
}


def get_config(
    env=os.getenv("FLASK_ENV"),
) -> ProductionConfig | DevelopmentConfig | TestingConfig:
    """
    Looks at ENV environment variable and returns environment specific config object

    Defaults to production config
    """
    _env = env or "production"
    if _env not in config:
        _env = "production"
        log.warning(
            "Invalid ENV environment supplied: '%s'. Defaulting to '%s'", env, _env
        )
    return config[_env]
