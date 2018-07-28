import os
import re
import sqlite3
from abc import ABC

import config


class DAO(ABC):
    """Base class for DAO objects. It defines a 'regex' function to use in SQL queries."""
    _DEFAULT = ":memory:"
    _INSTANCES = {}

    # Singleton implementation
    def __new__(cls, database=_DEFAULT):
        key = cls, database
        if key not in cls._INSTANCES:
            cls._INSTANCES[key] = super().__new__(cls)
        return cls._INSTANCES[key]

    def __init__(self, database=_DEFAULT):
        """
        Initializes this DAO using the given database. If nothing is specified, special ':memory:' database will be
        used.

        :param database: The database to connect to.
        """
        file_exists = os.path.exists(database) and database != self._DEFAULT
        self._connection = sqlite3.connect(database)
        # Disable autocommit when BEGIN has been called.
        self._connection.isolation_level = None
        if not file_exists:
            with open(config.DB_SETUP_FILE) as db_script_file:
                self._connection.executescript(db_script_file.read())

        self._connection.create_function("regexp", 2, lambda x, y: re.search(x, y) is not None)

    def close(self):
        """Closes database connection."""
        self._connection.close()
