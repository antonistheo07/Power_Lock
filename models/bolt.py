from dataclasses import dataclass
from typing import Optional

@dataclass
class Bolt:
    id: Optional[int] = None
    name: str = ""
    type: str = ""
    metal_strip: Optional[str] = None
    screw: Optional[str] = None
    rod: Optional[str] = None
    plate: Optional[str] = None
    square_mechanism: Optional[str] = None
    stamp: str = ""
    quantity: int = 0
    last_updated: Optional[str] = None
    
    @classmethod
    def from_db_row(cls, row):
        """Create Bolt from database row."""
        return cls(**dict(row)) if row else None