from database.repositories.base_repo import BaseRepository
from models.customer import Customer

class CustomerRepository(BaseRepository):
    def get_table_name(self):
        return "customers"
    
    def create(self, customer: Customer) -> int:
        query = """
            INSERT INTO customers (name, phone)
            VALUES (?, ?)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (customer.name, customer.phone))
            return cursor.lastrowid
        
    def update(self, customer: Customer):
        query = """
            UPDATE customers
            SET name = ?, phone = ?
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (customer.name, customer.phone, customer.id))
            return cursor.rowcount > 0
        
    def find_by_name(self, name: str):
        query = "SELECT * FROM customers WHERE name LIKE ? ORDER BY name"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{name}%",))
            return cursor.fetchall()
        