"""Root app file"""
from flask_migrate import Migrate
from notifier import create_app
from notifier.extensions import SQL_DB


earth_app = create_app()
migrate = Migrate(earth_app, SQL_DB)
