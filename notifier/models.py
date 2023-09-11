"""notifier models definitions"""
from datetime import datetime

from notifier.extensions import SQL_DB


class FriderThread(SQL_DB.Model):
    """Database model for freerider threads"""

    id = SQL_DB.Column(SQL_DB.Integer, primary_key=True)
    thread_arg = SQL_DB.Column(SQL_DB.String(100), nullable=False)
    created_at = SQL_DB.Column(
        SQL_DB.DateTime(timezone=True), server_default=str(datetime.now())
    )

    def __repr__(self):
        return f"{self.__class__} {self.thread_arg}"
