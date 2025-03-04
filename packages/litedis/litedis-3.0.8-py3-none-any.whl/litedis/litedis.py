from pathlib import Path
from typing import Any, Union

from litedis.client.commands import (
    BasicCommands,
    HashCommands,
    ListCommands,
    SetCommands,
    ZSetCommands
)
from litedis.core.dbmanager import DBManager
from litedis.typing import CommandProcessor, DBCommandPair


class Litedis(
    BasicCommands,
    HashCommands,
    ListCommands,
    SetCommands,
    ZSetCommands
):
    """
    Litedis class is a unified interface for interacting with the database,
    inheriting from multiple command classes to support various database operations.
    """
    def __init__(self,
                 dbname: str = "db",
                 persistence_on: bool = True,
                 data_path: Union[str, Path] = "ldbdata",
                 aof_rewrite_cycle: int = 666):
        """
        Initialize the Litedis instance.

        Args:
            dbname (str): The name of the database, default is "db".
            persistence_on (bool): Whether to enable data persistence, default is True.
            data_path (Union[str, Path]): The path to store data, default is "ldbdata".
            aof_rewrite_cycle (int): The cycle for AOF rewrite, default is 666(seconds).
        """
        self.dbname = dbname

        dbmanager = DBManager(data_path,
                              persistence_on=persistence_on,
                              aof_rewrite_cycle=aof_rewrite_cycle)

        self.executor: CommandProcessor = dbmanager

    def execute(self, *args) -> Any:
        result = self.executor.process_command(DBCommandPair(self.dbname, list(args)))
        return result
