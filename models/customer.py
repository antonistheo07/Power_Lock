from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""

    @classmethod
    def from_db_row(cls, row):
        return cls(**dict(row)) if row else None