from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class OrderItem:
    bolt_id: int
    bolt_name: str
    quantity: int
    id: Optional[int] = None
    created_at: Optional[str] = None

@dataclass
class Order:
    id: Optional[int] = None
    customer_id: int = 0
    customer_name: str = ""
    order_date: Optional[str] = None
    status: str = "pending"
    notes: Optional[str] = None
    total_items: int = 0
    last_updated: Optional[str] = None
    items: List[OrderItem] = field(default_factory=list)
    status_history: List[Dict] = field(default_factory=list)
    
    @classmethod
    def from_db_row(cls, row):
        """Create Order from database row."""
        return cls(**dict(row)) if row else None