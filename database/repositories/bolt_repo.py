from database.repositories.base_repo import BaseRepository
from models.bolt import Bolt

class BoltRepository(BaseRepository):

    def get_table_name(self):
        return "bolts"
    
    def create(self, bolt: Bolt) -> int:
        query = """
            INSERT INTO bolts (name, type, metal_strip, screw, rod, plate, 
                          square_mechanism, stamp, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_connection()as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                bolt.name, bolt.type, bolt.metal_strip, bolt.screw, bolt.rod,
                bolt.plate, bolt.square_mechanism, bolt.stamp, bolt.quantity
            ))
            return cursor.lastrowid
        
    def update(self, bolt: Bolt):
        query = """
            UPDATE bolts 
            SET name = ?, type = ?, metal_strip = ?, screw = ?, rod = ?,
                plate = ?, square_mechanism = ?, stamp = ?, quantity = ?,
                last_updated = datetime('now')
            WHERE id = ?
        """
        with self.db.get_connection() as conn :
            cursor = conn.cursor()
            cursor.execute(query, (
            bolt.name, bolt.type, bolt.metal_strip, bolt.screw, bolt.rod,
            bolt.plate, bolt.square_mechanism, bolt.stamp, bolt.quantity,
            bolt.id
        ))
            return cursor.rowcount > 0
        
    def find_by_name(self, name: str):
        query = "SELECT * FROM bolts WHERE name LIKE ? ORDER BY name"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{name}%",))
            return cursor.fetchall()
        
    def adjust_quantity(self, bolt_id: int, adjustment: int):
        query = """
            UPDATE bolts
            SET quantity = quantity + ?, last_updated = datetime('now')
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (adjustment, bolt_id))
            return cursor.rowcount > 0
