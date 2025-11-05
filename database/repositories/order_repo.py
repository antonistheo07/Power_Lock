from database.repositories.base_repo import BaseRepository
from models.order import Order, OrderItem
from typing import List, Dict, Optional


class OrderRepository(BaseRepository):
    """Repository for order management with full CRUD and search capabilities."""
    
    def get_table_name(self):
        return "orders"
    
    # CREATE OPERATIONS 
    
    def create(self, order: Order, items: List[OrderItem]) -> int:
        """
        Create new order with items.
        
        Args:
            order: Order object with customer_id, status, notes
            items: List of OrderItem objects
            
        Returns:
            order_id: ID of created order
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert order
            cursor.execute("""
                INSERT INTO orders (customer_id, status, notes, total_items)
                VALUES (?, ?, ?, ?)
            """, (order.customer_id, order.status, order.notes, len(items)))
            
            order_id = cursor.lastrowid
            
            # Insert order items
            for item in items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, bolt_id, quantity)
                    VALUES (?, ?, ?)
                """, (order_id, item.bolt_id, item.quantity))
                
                # Optional: Decrease bolt inventory
                # cursor.execute("""
                #     UPDATE bolts 
                #     SET quantity = quantity - ?,
                #         last_updated = datetime('now')
                #     WHERE id = ?
                # """, (item.quantity, item.bolt_id))
            
            # Add initial status history
            cursor.execute("""
                INSERT INTO order_status_history (order_id, new_status, changed_by)
                VALUES (?, ?, ?)
            """, (order_id, order.status, "System"))
            
            return order_id
    
    #  READ OPERATIONS 
    
    def get_all_with_summary(self):
        """Get all orders with customer names and item counts."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.order_date DESC
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
    
    def get_with_details(self, order_id: int) -> Optional[Dict]:
        """
        Get complete order details including items and status history.
        
        Returns:
            Dictionary with order data, items list, and status_history list
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get order with customer info
            cursor.execute("""
                SELECT o.*, c.name as customer_name
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.id = ?
            """, (order_id,))
            
            order_row = cursor.fetchone()
            if not order_row:
                return None
            
            order_dict = dict(order_row)
            
            # Get order items with bolt names
            cursor.execute("""
                SELECT oi.*, b.name as bolt_name
                FROM order_items oi
                JOIN bolts b ON oi.bolt_id = b.id
                WHERE oi.order_id = ?
                ORDER BY oi.id
            """, (order_id,))
            
            order_dict['items'] = [dict(row) for row in cursor.fetchall()]
            
            # Get status history
            cursor.execute("""
                SELECT * FROM order_status_history
                WHERE order_id = ?
                ORDER BY changed_at DESC
            """, (order_id,))
            
            order_dict['status_history'] = [dict(row) for row in cursor.fetchall()]
            
            return order_dict
    
    # UPDATE OPERATIONS 
    
    def update_status(self, order_id: int, new_status: str, changed_by: str = "System"):
        """
        Update order status and log history.
        
        Args:
            order_id: ID of order to update
            new_status: New status value
            changed_by: Who made the change
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current status
            cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Order {order_id} not found")
            
            old_status = row['status']
    
            if old_status == new_status:
                return
            
            # Update status
            cursor.execute("""
                UPDATE orders 
                SET status = ?, last_updated = datetime('now')
                WHERE id = ?
            """, (new_status, order_id))
            
            # Log history
            cursor.execute("""
                INSERT INTO order_status_history 
                (order_id, old_status, new_status, changed_by)
                VALUES (?, ?, ?, ?)
            """, (order_id, old_status, new_status, changed_by))
    
    def update_notes(self, order_id: int, notes: str):
        """Update order notes."""
        query = """
            UPDATE orders 
            SET notes = ?, last_updated = datetime('now')
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (notes, order_id))
            return cursor.rowcount > 0
    
    def update_customer(self, order_id: int, customer_id: int):
        """Update order customer."""
        query = """
            UPDATE orders 
            SET customer_id = ?, last_updated = datetime('now')
            WHERE id = ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (customer_id, order_id))
            return cursor.rowcount > 0
    
    # DELETE OPERATIONS 
    
    def delete(self, order_id: int):
        """
        Delete order and all related items.
        Status history is also deleted due to CASCADE.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Optional: Restore inventory before deleting
            # cursor.execute("""
            #     UPDATE bolts
            #     SET quantity = quantity + (
            #         SELECT quantity FROM order_items 
            #         WHERE order_id = ? AND bolt_id = bolts.id
            #     )
            #     WHERE id IN (SELECT bolt_id FROM order_items WHERE order_id = ?)
            # """, (order_id, order_id))
            
            # Delete order (items are cascade deleted)
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            return cursor.rowcount > 0
    
    #  SEARCH OPERATIONS 
    
    def search_by_customer_name(self, name: str):
        """Search orders by customer name (partial match)."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE c.name LIKE ?
            GROUP BY o.id
            ORDER BY o.order_date DESC
            LIMIT 100
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{name}%",))
            return cursor.fetchall()
    
    def find_by_customer(self, customer_id: int):
        """Find all orders for a specific customer."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.customer_id = ?
            GROUP BY o.id
            ORDER BY o.order_date DESC
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (customer_id,))
            return cursor.fetchall()
    
    def find_by_status(self, status: str):
        """Find orders by status."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = ?
            GROUP BY o.id
            ORDER BY o.order_date DESC
            LIMIT 100
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (status,))
            return cursor.fetchall()
    
    def search_by_bolt_name(self, bolt_name: str):
        """Search orders containing a specific bolt (partial match)."""
        query = """
            SELECT DISTINCT o.*, c.name as customer_name,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN bolts b ON oi.bolt_id = b.id
            WHERE b.name LIKE ?
            ORDER BY o.order_date DESC
            LIMIT 100
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{bolt_name}%",))
            return cursor.fetchall()
    
    # STATISTICS & REPORTING 
    
    def get_statistics(self) -> Dict:
        """Get comprehensive order statistics."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total orders
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = cursor.fetchone()['count']
            
            # Orders by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM orders
                GROUP BY status
            """)
            stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Recent orders (last 30 days)
            cursor.execute("""
                SELECT COUNT(*) as count FROM orders
                WHERE order_date >= datetime('now', '-30 days')
            """)
            stats['recent_orders'] = cursor.fetchone()['count']
            
            # Total items ordered
            cursor.execute("""
                SELECT SUM(quantity) as total FROM order_items
            """)
            result = cursor.fetchone()
            stats['total_items_ordered'] = result['total'] if result['total'] else 0
            
            # Average items per order
            cursor.execute("""
                SELECT AVG(total_items) as avg FROM orders
            """)
            result = cursor.fetchone()
            stats['avg_items_per_order'] = round(result['avg'], 2) if result['avg'] else 0
            
            # Most ordered bolts
            cursor.execute("""
                SELECT b.name, SUM(oi.quantity) as total_quantity
                FROM order_items oi
                JOIN bolts b ON oi.bolt_id = b.id
                GROUP BY oi.bolt_id
                ORDER BY total_quantity DESC
                LIMIT 5
            """)
            stats['top_ordered_bolts'] = [
                {'name': row['name'], 'quantity': row['total_quantity']}
                for row in cursor.fetchall()
            ]
            
            # Top customers (by order count)
            cursor.execute("""
                SELECT c.name, COUNT(o.id) as order_count
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY o.customer_id
                ORDER BY order_count DESC
                LIMIT 5
            """)
            stats['top_customers'] = [
                {'name': row['name'], 'orders': row['order_count']}
                for row in cursor.fetchall()
            ]
            
            return stats
    
    def get_recent_orders(self, limit: int = 10):
        """Get most recent orders."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.order_date DESC
            LIMIT ?
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            return cursor.fetchall()
    
    def get_orders_by_date_range(self, start_date: str, end_date: str):
        """Get orders within a date range."""
        query = """
            SELECT o.*, c.name as customer_name,
                   COUNT(oi.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.order_date BETWEEN ? AND ?
            GROUP BY o.id
            ORDER BY o.order_date DESC
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_date, end_date))
            return cursor.fetchall()
    
    # VALIDATION & HELPERS 
    
    def can_delete_order(self, order_id: int) -> tuple[bool, str]:
        """
        Check if order can be deleted.
        
        Returns:
            (can_delete: bool, reason: str)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Order not found"
            
            status = row['status']
            
            if status in ['shipped', 'delivered']:
                return False, f"Cannot delete {status} orders"
            
            return True, "OK"
    
    def get_order_summary(self, order_id: int) -> Optional[str]:
        """Get a brief text summary of an order."""
        order = self.get_with_details(order_id)
        if not order:
            return None
        
        items_list = [f"{item['bolt_name']} x{item['quantity']}" 
                     for item in order.get('items', [])]
        items_text = ", ".join(items_list)
        
        return (f"Order #{order['id']} - {order['customer_name']}\n"
                f"Status: {order['status']}\n"
                f"Date: {order['order_date']}\n"
                f"Items: {items_text}")


