from dataclasses import dataclass


"""
Sqlite Database Client
"""
@dataclass
class DatabaseClient:
    db_location: str

    