from abc import ABC, abstractmethod
from database.connection import db

class BaseRepository(ABC):
    """Base repository with common CRUD operations."""

    def __init__(self):
        self.db = db
    
    @abstractmethod
    def get_table_name(self) -> str:
        pass

    def get_by_id(self, item_id: int):
        query = f"SELECT * FROM {self.get_table_name()} WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (item_id,))
            return cursor.fetchone()
        
    def get_all(self, order_by="id DESC"):
        query = f"SELECT * FROM {self.get_table_name()} ORDER BY {order_by}"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        
    def delete(self, item_id: int):
        query = f"DELETE FROM {self.get_table_name()} WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (item_id,))
            return cursor.rowcount > 0