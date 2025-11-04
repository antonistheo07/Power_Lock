import os
import sys
from pathlib import Path

def get_base_dir():
    """Get the correct base directory"""
    if getattr(sys, 'frozen', False):
        # Running as executable - use user directory
        return Path(os.path.expanduser('~')) / '.power_lock'
    else:
        # Running as script - use project directory
        return Path(__file__).parent.parent

def get_database_path():
    """Get the correct path for the database"""
    base_dir = get_base_dir()
    
    # Create directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = base_dir / "PLdatabase.db"
    
    # Create database if it doesn't exist (first run)
    if not db_path.exists():
        _create_initial_database(db_path)
    
    return db_path

def _create_initial_database(db_path):
    """Create the database with initial schema"""
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        )
    ''')

    # bolts table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bolts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            metal_strip TEXT,
            rod TEXT,
            screw TEXT,
            plate TEXT,
            square_mechanism TEXT,
            stamp TEXT,
            quantity TEXT,
            Last_updated TEXT DEFAULT (datetime('now'))
        )
    ''')

    # orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL DEFAULT (datetime('now')),
            status TEXT NOT NULL DEFAULT 'pending',
            notes TEXT,
            total_items INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
        )
    ''')

    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            bolt_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (bolt_id) REFERENCES bolts(id) ON DELETE RESTRICT
        )
    ''')
    
    # Order status history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            changed_at TEXT NOT NULL DEFAULT (datetime('now')),
            changed_by TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_bolt ON order_items(bolt_id)')
    
    conn.commit()
    conn.close()

BASE_DIR = get_base_dir()
DB_FILE = get_database_path()

APP_TITLE = "Power Lock"
APP_GEOMETRY = "1200x800"

ORDER_STATUSES = ["pending", "approved", "processing", "shipped", "delivered", "cancelled"]

LOG_FILE = BASE_DIR / "app.log"
LOG_LEVEL = "INFO"