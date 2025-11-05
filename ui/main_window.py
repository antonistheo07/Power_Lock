import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Menu, messagebox, filedialog, Text
from datetime import datetime
from shutil import copy2

from config.settings import APP_TITLE, APP_GEOMETRY, DB_FILE
from database.schema import initialize_database
from database.connection import db
from ui.components.main_container import MainContainer
from ui.views.customer_view import CustomerView
from ui.views.bolts_view import BoltsView
from ui.views.orders_view import OrdersView
from utils.logger import setup_logger

# Setup logger
logger = setup_logger()


class MainWindow(ttk.Window):
    """Main application window - Part 3: Complete"""
    
    def __init__(self):
        # Initialize with modern theme
        super().__init__(themename="litera")
        
        # Window configuration
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(900, 600)
        
        # Initialize database
        self._initialize_database()
        
        # Setup UI components
        self._create_status_bar()
        self._create_menu_bar()
        self._create_main_container()
        
        # Center window
        self._center_window()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("Application started successfully - Part 3")
    
    def _initialize_database(self):
        """Initialize the database and handle errors."""
        try:
            initialize_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            messagebox.showerror(
                "Database Error",
                f"Failed to initialize database:\n{e}\n\n"
                "The application may not work correctly."
            )
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        status_bar = ttk.Frame(self, bootstyle="secondary", height=30)
        status_bar.pack(side=BOTTOM, fill=X)
        
        self.status_label = ttk.Label(
            status_bar,
            text="Ready",
            bootstyle="inverse-secondary",
            padding=5
        )
        self.status_label.pack(side=LEFT)
        
        # Version info
        ttk.Label(
            status_bar,
            text="v2.0",
            bootstyle="inverse-secondary",
            padding=5
        ).pack(side=RIGHT)
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Current View...", command=self._export_current_view)
        file_menu.add_command(label="Generate Report...", command=self._generate_report)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database...", command=self._backup_database)
        file_menu.add_command(label="Restore Database...", command=self._restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Current View", 
                             command=self._refresh_current_view,
                             accelerator="F5")
        view_menu.add_command(label="Dashboard", command=self._show_dashboard)
        view_menu.add_separator()
        view_menu.add_command(label="Customers", command=lambda: self.on_view_change("customers"))
        view_menu.add_command(label="Bolts Inventory", command=lambda: self.on_view_change("bolts"))
        view_menu.add_command(label="Orders", command=lambda: self.on_view_change("orders"))
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Pending Orders", command=self._show_pending_orders)
        tools_menu.add_command(label="Order Statistics", command=self._show_order_statistics)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings...", command=self._show_settings)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        
        # Bind keyboard shortcuts
        self.bind("<F5>", lambda e: self._refresh_current_view())
        self.bind("<Control-q>", lambda e: self._on_closing())
    
    def _create_main_container(self):
        """Create the main container with sidebar."""
        try:
            # Create the main container (sidebar + content area)
            self.container = MainContainer(self)
            
            # Track current view widget
            self.current_view_widget = None
            
            # Load initial view (customers)
            self.on_view_change("customers")
            
            logger.info("Main container created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create main container: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to create container:\n{e}"
            )
    
    # VIEW MANAGEMENT 
    
    def on_view_change(self, view_name):
        """Handle navigation clicks - load real views"""
        try:
            # Get content frame
            content_frame = self.container.get_content_frame()
            
            # Create the appropriate view
            if view_name == "customers":
                view_widget = CustomerView(content_frame)
                display_name = "Customers"
                
            elif view_name == "bolts":
                view_widget = BoltsView(content_frame)
                display_name = "Bolts Inventory"
                
            elif view_name == "orders":
                view_widget = OrdersView(content_frame)
                display_name = "Orders"
            else:
                return
            
            # Store reference to current view
            self.current_view_widget = view_widget
            
            # Load the view
            self.container.load_view(view_widget)
            self.update_status(f"Viewing {display_name}")
            logger.info(f"Loaded view: {display_name}")
            
        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}")
            messagebox.showerror("Error", f"Failed to load view:\n{e}")
    
    def _get_current_view(self):
        """Get the currently active view widget."""
        return self.current_view_widget
    
    def _refresh_current_view(self):
        """Refresh the currently active view."""
        try:
            current_view = self._get_current_view()
            if current_view and hasattr(current_view, 'refresh'):
                current_view.refresh()
                self.update_status("Refreshed")
                logger.info("Current view refreshed")
            else:
                self.update_status("Nothing to refresh")
        except Exception as e:
            logger.error(f"Failed to refresh view: {e}")
            messagebox.showerror("Error", f"Failed to refresh:\n{e}")
    
    def _export_current_view(self):
        """Export data from current view."""
        try:
            current_view = self._get_current_view()
            view_name = self.container.current_view
            
            if not current_view:
                messagebox.showwarning("Export", "No view selected")
                return
            
            if hasattr(current_view, 'on_export'):
                current_view.on_export()
                self.update_status(f"Export initiated")
                logger.info(f"Data export initiated for {view_name}")
            else:
                messagebox.showinfo("Export", "Export not available for this view.")
                    
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}")
    
    # FILE MENU ACTIONS 
    
    #def _generate_report(self):
       # """Generate comprehensive report."""
       # try:
           # from utils.exports import generate_report
            
            # Gather statistics
            #stats = self._get_statistics()
            
           # report_data = {
               #    "Generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 #   "Application": APP_TITLE,
                #    "Database": str(DB_FILE)
              #  },
             #   "System Statistics": stats
           # }
            
           # filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
          #  generate_report(report_data, filename)
            
           # messagebox.showinfo(
             #   "Success",
              #  f"Report generated successfully!\n\nSaved as: {filename}"
           # )
           # logger.info(f"Report generated: {filename}")
            
       # except Exception as e:
           # logger.error(f"Report generation failed: {e}")
            #messagebox.showerror("Error", f"Failed to generate report:\n{e}")
    
    def _backup_database(self):
        """Backup database to file."""
        default_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            initialfile=default_name,
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                copy2(DB_FILE, filename)
                messagebox.showinfo(
                    "Success",
                    f"Database backed up successfully!\n\nLocation:\n{filename}"
                )
                logger.info(f"Database backed up to {filename}")
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                messagebox.showerror("Backup Error", f"Failed to backup database:\n{e}")
    
    def _restore_database(self):
        """Restore database from backup file."""
        if not messagebox.askyesno(
            "Confirm Restore",
            "WARNING: Restoring will overwrite the current database.\n"
            "All current data will be lost!\n\n"
            "Make sure you have a backup of the current database.\n\n"
            "Do you want to continue?"
        ):
            return
        
        filename = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                copy2(filename, DB_FILE)
                messagebox.showinfo(
                    "Success",
                    "Database restored successfully!\n\n"
                    "Please restart the application for changes to take effect."
                )
                logger.info(f"Database restored from {filename}")
                self._on_closing()
            except Exception as e:
                logger.error(f"Restore failed: {e}")
                messagebox.showerror("Restore Error", f"Failed to restore database:\n{e}")
    
    # VIEW MENU ACTIONS 
    
    def _show_dashboard(self):
        """Show dashboard with statistics."""
        stats = self._get_statistics()
        
        # Create dashboard window
        dashboard = ttk.Toplevel(self)
        dashboard.title("Dashboard")
        dashboard.geometry("650x700")
        dashboard.transient(self)
        dashboard.grab_set()
        
        # Header
        header_frame = ttk.Frame(dashboard)
        header_frame.pack(fill=X, pady=20, padx=20)
        
        ttk.Label(
            header_frame,
            text="📊 Dashboard",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        ).pack(anchor=W)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(
            dashboard,
            text="System Statistics",
            padding=20,
            bootstyle="primary"
        )
        stats_frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        # Add statistics
        for key, value in stats.items():
            row_frame = ttk.Frame(stats_frame)
            row_frame.pack(fill=X, pady=8)
            
            ttk.Label(
                row_frame,
                text=f"{key}:",
                font=("Segoe UI", 10, "bold"),
                width=22
            ).pack(side=LEFT)
            
            ttk.Label(
                row_frame,
                text=str(value),
                font=("Segoe UI", 10),
                bootstyle="info"
            ).pack(side=LEFT)
        
        # Close button
        ttk.Button(
            dashboard,
            text="Close",
            command=dashboard.destroy,
            bootstyle="secondary",
            width=15
        ).pack(pady=20)
        
        self._center_dialog(dashboard)
    
    #  TOOLS MENU ACTIONS   
    def _show_pending_orders(self):
        """Show pending orders."""
        try:
            from database.repositories.order_repo import OrderRepository
            repo = OrderRepository()
            pending = repo.find_by_status("pending")
            
            if not pending:
                messagebox.showinfo("Pending Orders", "✅ No pending orders!")
                return
            
            # Switch to orders view
            self.on_view_change("orders")
            
            messagebox.showinfo(
                "Pending Orders",
                f"Found {len(pending)} pending order(s).\n\n"
                "Switched to Orders view."
            )
            
        except Exception as e:
            logger.error(f"Failed to show pending orders: {e}")
            messagebox.showerror("Error", f"Failed to load pending orders:\n{e}")
    
    def _show_order_statistics(self):
        """Show detailed order statistics."""
        try:
            from database.repositories.order_repo import OrderRepository
            repo = OrderRepository()
            stats = repo.get_statistics()
            
            # Create statistics window
            stats_window = ttk.Toplevel(self)
            stats_window.title("Order Statistics")
            stats_window.geometry("650x600")
            stats_window.transient(self)
            stats_window.grab_set()
            
            # Header
            header_frame = ttk.Frame(stats_window)
            header_frame.pack(fill=X, pady=20, padx=20)
            
            ttk.Label(
                header_frame,
                text="📊 Order Statistics",
                font=("Segoe UI", 16, "bold"),
                bootstyle="primary"
            ).pack(anchor=W)
            
            # Basic stats
            basic_frame = ttk.LabelFrame(
                stats_window,
                text="Overview",
                padding=20,
                bootstyle="info"
            )
            basic_frame.pack(fill=X, padx=20, pady=10)
            
            basic_stats = [
                ("Total Orders", stats.get('total_orders', 0)),
                ("Recent Orders (30 days)", stats.get('recent_orders', 0)),
                ("Total Items Ordered", stats.get('total_items_ordered', 0)),
                ("Avg Items per Order", stats.get('avg_items_per_order', 0))
            ]
            
            for label, value in basic_stats:
                row = ttk.Frame(basic_frame)
                row.pack(fill=X, pady=5)
                ttk.Label(
                    row,
                    text=f"{label}:",
                    font=("Segoe UI", 10, "bold"),
                    width=28
                ).pack(side=LEFT)
                ttk.Label(
                    row,
                    text=str(value),
                    bootstyle="info"
                ).pack(side=LEFT)
            
            # Orders by status
            status_frame = ttk.LabelFrame(
                stats_window,
                text="Orders by Status",
                padding=20,
                bootstyle="info"
            )
            status_frame.pack(fill=X, padx=20, pady=10)
            
            for status, count in stats.get('by_status', {}).items():
                row = ttk.Frame(status_frame)
                row.pack(fill=X, pady=5)
                ttk.Label(
                    row,
                    text=f"{status.title()}:",
                    font=("Segoe UI", 10),
                    width=20
                ).pack(side=LEFT)
                ttk.Label(
                    row,
                    text=str(count),
                    bootstyle="info"
                ).pack(side=LEFT)
            
            ttk.Button(
                stats_window,
                text="Close",
                command=stats_window.destroy,
                bootstyle="secondary",
                width=15
            ).pack(pady=20)
            
            self._center_dialog(stats_window)
            
        except Exception as e:
            logger.error(f"Failed to show order statistics: {e}")
            messagebox.showerror("Error", f"Failed to load statistics:\n{e}")
    
    def _show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo(
            "Settings",
            "Settings configuration coming soon!\n\n"
            "For now, you can edit config/settings.py directly."
        )
    
    #  HELP MENU ACTIONS 
    
    def _show_help(self):
        """Show user guide."""
        help_text = """ORDER MANAGEMENT SYSTEM - USER GUIDE

CUSTOMERS VIEW:
• Add new customers with contact information
• Edit existing customer details  
• Search customers by name (real-time)
• View complete customer details
• Delete customers (if no orders exist)
• Export customer list to CSV

BOLTS INVENTORY VIEW:
• Manage bolt inventory
• Track stock levels with quantities
• Search by bolt name
• Export inventory to CSV

ORDERS VIEW:
• Create new orders for customers
• Select customer from list
• Add multiple items (format: "BoltName:Qty, BoltName:Qty")
• Track order status (pending/approved/shipped/etc.)
• View complete order details with history
• Update order status with notes
• Advanced search by customer/status/bolt
• Export orders to CSV

KEYBOARD SHORTCUTS:
• F5 - Refresh current view
• Ctrl+Q - Quit application
• Double-click - View details
• Enter - Confirm/Search

MENU FEATURES:
• File → Export/Report/Backup/Restore
• View → Dashboard/Refresh
• Tools → Low Stock/Pending Orders/Statistics
• Help → User Guide/About

TIPS:
• Use search bars for quick filtering
• Export data regularly for backup
• Monitor low stock alerts
• Track order status changes in history
        """
        
        help_window = ttk.Toplevel(self)
        help_window.title("User Guide")
        help_window.geometry("700x650")
        help_window.transient(self)
        help_window.grab_set()
        
        # Header
        header_frame = ttk.Frame(help_window)
        header_frame.pack(fill=X, pady=15, padx=20)
        
        ttk.Label(
            header_frame,
            text="📖 User Guide",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(anchor=W)
        
        # Text widget with scrollbar
        frame = ttk.Frame(help_window)
        frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        text_widget = Text(
            frame,
            wrap="word",
            padx=15,
            pady=15,
            font=("Consolas", 9)
        )
        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")
        
        ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            bootstyle="secondary",
            width=15
        ).pack(pady=15)
        
        self._center_dialog(help_window)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts = """KEYBOARD SHORTCUTS

F5                  Refresh current view
Ctrl+Q              Quit application
Double-click        View item details
Enter               Confirm action / Search
Escape              Cancel dialog

IN TABLES:
↑↓                  Navigate items
Home/End            First/Last item
        """
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = f"""{APP_TITLE}

Version: 2.0 (Modern UI)

A comprehensive order management system for 
tracking customers, inventory, and orders.

✨ Features:
• Customer Management
• Inventory Tracking
• Order Processing with Status History
• Database Backup/Restore
• Dashboard 
• UI with ttkbootstrap

Developed with Python & ttkbootstrap

© 2024 - Open Source
        """
        
        messagebox.showinfo("About", about_text)
    
    # HELPER METHODS 
    
    def _get_statistics(self):
        """Get application statistics."""
        stats = {}
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Customer count
                cursor.execute("SELECT COUNT(*) as count FROM customers")
                stats["Total Customers"] = cursor.fetchone()['count']
                
                # Bolt count and low stock
                cursor.execute("SELECT COUNT(*) as count FROM bolts")
                stats["Total Bolt Types"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT SUM(quantity) as total FROM bolts")
                result = cursor.fetchone()
                stats["Total Bolt Quantity"] = result['total'] if result['total'] else 0
                
                cursor.execute("SELECT COUNT(*) as count FROM bolts WHERE quantity < min_stock_level")
                stats["Low Stock Items"] = cursor.fetchone()['count']
                
                # Order statistics
                cursor.execute("SELECT COUNT(*) as count FROM orders")
                stats["Total Orders"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
                stats["Pending Orders"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'shipped'")
                stats["Shipped Orders"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'delivered'")
                stats["Delivered Orders"] = cursor.fetchone()['count']
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            stats["Error"] = str(e)
        
        return stats
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)
        self.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def _center_dialog(self, dialog):
        """Center dialog on parent window."""
        dialog.update_idletasks()
        if self.winfo_ismapped():
            x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            logger.info("Application closed by user")
            self.destroy()
