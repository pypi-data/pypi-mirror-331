import sqlite3
from typing import Union, List, Iterable, Any
from pathlib import Path
from dataclasses import dataclass, asdict, is_dataclass


class DB:
    def __init__(
        self,
        db_path: Union[str, Path],
        migrations: dict = None,
        migrate_on_connect=False,
        server_mode: bool = True,
        query_only: bool = False,
    ):
        self.query_only = query_only
        self.migrate_on_connect = migrate_on_connect
        self.db_path = db_path
        self.server_mode = server_mode
        if migrations:
            self.migrations = migrations
        else:
            self.migrations = {}
        self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            # data structure for rows that supports casting to dict
            self._connection.row_factory = sqlite3.Row
            cursor = self._connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute('PRAGMA encoding = "UTF-8";')
            if self.query_only:
                cursor.execute("PRAGMA query_only=ON;")
            if self.migrate_on_connect and not self.query_only:
                self.migrate()
                self.commit()
            # this is a set of configuration directives
            # to make SQLite a little more fit for
            # concurrent usage (see https://kerkour.com/sqlite-for-servers)
            if self.server_mode:
                cursor.execute("PRAGMA journal_mode = WAL;")
                cursor.execute("PRAGMA busy_timeout = 5000;")
                cursor.execute("PRAGMA synchronous = NORMAL;")
                cursor.execute("PRAGMA cache_size = 1000000000;")
                cursor.execute("PRAGMA temp_store = memory;")
        return self._connection

    def migrate(self, migrations: dict = None):
        if migrations:
            self.migrations = migrations
        cursor = self.cursor()
        cursor.execute(  # mandatory table to keep track of migrations
            "CREATE TABLE IF NOT EXISTS _migrations(identifier TEXT UNIQUE, script TEXT);"
        )
        needs_commit = False
        for identifier, script in self.migrations.items():
            cursor.execute(
                "SELECT COUNT(*) from _migrations where identifier = ?", (identifier,)
            )
            result = cursor.fetchone()
            if result["COUNT(*)"] == 0:
                cursor.executescript(script)
                cursor.execute(
                    "INSERT INTO _migrations(identifier, script) VALUES(?,?)",
                    (identifier, script),
                )
                needs_commit = True
        if needs_commit:
            self.commit()
        return self

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def insert(
        self, table: str, values: Union[dict, dataclass]
    ) -> Union[sqlite3.Row, None]:
        """
        No escaping of any kind is done on the 'table' param and 'values' keys.
        Do not trust user input with these.
        """
        if is_dataclass(values):
            values = asdict(values)
        if not isinstance(values, dict):
            raise ValueError("values must be either a dict or a dataclass")
        if len(values) == 0:
            raise ValueError("no values to insert")
        sql = f"INSERT INTO {table}({', '.join(values.keys())}) VALUES({', '.join(['?' for x in values.keys()])}) RETURNING *;"
        cur = self.cursor()
        cur.execute(sql, list(values.values()))
        return cur.fetchone()

    def update(
        self,
        table: str,
        values: Union[dict, dataclass],
        where: str = None,
        params: Any = None,
    ) -> sqlite3.Cursor:
        """
        No escaping of any kind is done on the 'table', 'where' params and 'values' keys.
        Do not trust user input with these.
        """
        if is_dataclass(values):
            values = asdict(values)
        if not isinstance(values, dict):
            raise ValueError("values must be either a dict or a dataclass")
        if len(values) == 0:
            raise ValueError("no values to update")
        if params is not None:
            if type(params) not in [tuple, list]:
                params = [params]
        sql = f"UPDATE {table} SET {', '.join([f'{x}=?' for x in values.keys()])}{f' WHERE {where}' if where is not None else ''} RETURNING *;"
        all_params = list(values.values()) + (params if params is not None else [])
        cur = self.cursor()
        cur.execute(sql, all_params)
        return cur

    def save(self, dataclass_instance: Any) -> Any:
        """
        Will save a dataclass instance to the db.
        The dataclass must have an integer id field.
        The DB instance is attached as dataclass_instance._db
        """
        if not is_dataclass(dataclass_instance):
            raise ValueError("must be a dataclass")
        if not hasattr(dataclass_instance, "id"):
            raise ValueError("dataclass instance must have an id field")
        table = type(dataclass_instance).__name__.lower()
        if dataclass_instance.id is not None:
            self.update(table, dataclass_instance, "id=?", dataclass_instance.id)
        else:
            row = dict(self.insert(table, dataclass_instance))
            dataclass_instance.id = row["id"]
        dataclass_instance._db = self
        return dataclass_instance

    def delete(
        self, table: str, where: str = None, params: List = None
    ) -> sqlite3.Cursor:
        """
        No escaping of any kind is done on the 'table' and 'where' params.
        Do not trust user input with these.
        """
        if params is not None:
            if type(params) not in [tuple, list]:
                params = [params]
        sql = f"DELETE fROM {table}{f' WHERE {where}' if where is not None else ''} RETURNING *;"
        cur = self.cursor()
        cur.execute(sql, params if params is not None else [])
        return cur

    def execute(self, sql: str, parameters: Iterable[Any] = None) -> sqlite3.Cursor:
        if parameters is not None:
            if type(parameters) not in [tuple, list]:
                parameters = [parameters]
            return self.cursor().execute(sql, parameters)
        return self.cursor().execute(sql)

    def commit(self):
        self.connection.commit()

    def cursor(self) -> sqlite3.Cursor:
        return self.connection.cursor()

    def __del__(self):
        self.close()

    def schema(self) -> str:
        cur = self.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL;")
        return ";\n".join([dict(row)["sql"] for row in cur])

    def hydrate(self, dataclass_class, row: sqlite3.Row):
        """
        Converts row to dataclass instance and attach itself as instance._db
        """
        instance = dataclass_class(**dict(row))
        instance._db = self
        return instance
