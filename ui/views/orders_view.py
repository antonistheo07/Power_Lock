import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
from typing import Optional, Dict, List

from ui.components.base_crud_view import BaseView
from ui.components.dialogs import (
    FormDialog, DetailsDialog, CustomerSelectDialog,
    StatusUpdateDialog, OrderSearchDialog, OrderDetailsDialog, OrderListDialog, OrderItemsDialog
)
from database.repositories.order_repo import OrderRepository
from database.repositories.customer_repo import CustomerRepository
from database.repositories.bolt_repo import BoltRepository
from models.order import Order, OrderItem
from config.settings import ORDER_STATUSES



class OrdersView(BaseView):
    """Modern order management view with simplified architecture"""
    
    def __init__(self, parent):
        self.customer_repo = CustomerRepository()
        self.bolt_repo = BoltRepository()
        repository = OrderRepository()
        super().__init__(parent, repository, Order)
    
    def get_columns(self):
        return ["id", "customer", "status", "order_date", "items", "total_items"]
    
    def get_column_width(self, col):
        widths = {
            "id": 80,
            "customer": 220,
            "status": 130,
            "order_date": 170,
            "items": 300,
            "total_items": 100
        }
        return widths.get(col, 150)
    
    def get_column_anchor(self, col):
        return CENTER 
    
    def get_table_name(self):
        return "orders"
    
    def get_custom_buttons(self):
        """Add custom buttons for order-specific actions."""
        return [
            ("🔍 View Details", self.on_view_details),
            ("✏️ Update Status", self.on_update_status),
            ("🔎 Advanced Search", self.on_advanced_search),
        ]
    
    def fetch_data(self, search_term=""):
        """Fetch orders with customer names and item summary."""
        if search_term:
            # Search by customer name
            return self.repository.search_by_customer_name(search_term)
        return self.repository.get_all_with_summary()
    
    def format_row(self, item):
        """Format order for display."""
        items_summary = self._get_items_summary(item.get('id'))
        
        return (
            item['id'],
            item.get('customer_name', 'Unknown'),
            item.get('status', 'pending'),
            item.get('order_date', '')[:16],  
            items_summary,
            item.get('total_items', 0)
        )
    
    def refresh(self):
        """Refresh table with status-based highlighting."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            search_term = self.search_var.get().strip()
            items = self.fetch_data(search_term)

            # Configure status tags
            self.tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
            self.tree.tag_configure('approved', background='#d1ecf1', foreground='#0c5460')
            self.tree.tag_configure('shipped', background='#d4edda', foreground='#155724')
            self.tree.tag_configure('delivered', background='#d4edda', foreground='#155724')
            self.tree.tag_configure('cancelled', background='#f8d7da', foreground='#721c24')
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='#ffffff')

            # Insert items with appropriate tags
            for idx, item in enumerate(items):
                values = self.format_row(item)
                
                status = item.get('status', 'pending').lower()
                if status in ['pending', 'approved', 'shipped', 'delivered', 'cancelled']:
                    tags = [status]
                else:
                    tags = ['evenrow' if idx % 2 == 0 else 'oddrow']
                
                self.tree.insert("", END, values=values, tags=tuple(tags))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def _get_items_summary(self, order_id: int) -> str:
        """Get brief summary of order items."""
        try:
            order_details = self.repository.get_with_details(order_id)
            if not order_details or not order_details.get('items'):
                return "No items"
            
            items = order_details['items']
            if len(items) == 1:
                return f"{items[0]['bolt_name']} x{items[0]['quantity']}"
            elif len(items) == 2:
                return f"{items[0]['bolt_name']} x{items[0]['quantity']}, {items[1]['bolt_name']} x{items[1]['quantity']}"
            else:
                return f"{items[0]['bolt_name']} x{items[0]['quantity']}, {items[1]['bolt_name']} x{items[1]['quantity']}, +{len(items)-2} more"
        except:
            return "Error loading items"
    
    def on_add(self):
        """Create new order with customer selection and item entry."""
        customer_id, customer_name = self._select_customer()
        if not customer_id:
            return
        
        items_dict = self._select_order_items_dialog()
        if not items_dict:
            return
        
        notes = simpledialog.askstring(
            "Order Notes",
            "Add notes for this order (optional):"
        )
        
        try:
            order_items = self._convert_items_to_order_items(items_dict)
            if not order_items:
                return
            
            # Create order
            order = Order(
                customer_id=customer_id,
                status="pending",
                notes=notes,
                total_items=sum(item.quantity for item in order_items)
            )
            
            order_id = self.repository.create(order, order_items)
            
            items_summary = ", ".join([f"{name} x{qty}" for name, qty in items_dict.items()])
            messagebox.showinfo(
                "Success",
                f"Order #{order_id} created for {customer_name}\n\nItems:\n{items_summary}"
            )
            
            self.refresh()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create order:\n{e}")

    def _select_order_items_dialog(self) -> Optional[Dict[str, int]]:
        """Show dialog to select order items."""
        try:
            bolts = list(self.bolt_repo.get_all())
            if not bolts:
                messagebox.showerror("No Bolts", "Please add bolts to inventory first!")
                return None
        

            dialog = OrderItemsDialog(self, bolts)
            self.wait_window(dialog)
            return dialog.result
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bolts:\n{e}")
            return None
    
    def _select_customer(self) -> tuple[Optional[int], Optional[str]]:
        """Show customer selection dialog."""
        try:
            customers = self.customer_repo.get_all()
            if not customers:
                messagebox.showerror("No Customers", "Please add customers first!")
                return None, None
            
            dialog = CustomerSelectDialog(self, customers)
            self.wait_window(dialog)
            return dialog.result if dialog.result else (None, None)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{e}")
            return None, None
    
    def _enter_order_items(self) -> Optional[Dict[str, int]]:
        """Get order items from user input."""
        items_text = simpledialog.askstring(
            "Order Items",
            "Enter items as 'BoltName:Quantity' pairs, separated by commas.\n\n"
            "Example:\n"
            "  Hex Bolt:10, Carriage Bolt:5, Machine Bolt:3\n\n"
            "Tips:\n"
            "- Names are case-insensitive\n"
            "- Duplicate items will be combined"
        )
        
        if not items_text:
            return None
        
        try:
            return self._parse_items_input(items_text)
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
    
    def _parse_items_input(self, text: str) -> Dict[str, int]:
        """Parse items input string into dict."""
        if not text or not text.strip():
            raise ValueError("Please provide at least one item.")
        
        aggregated = {}
        pairs = [p.strip() for p in text.split(",") if p.strip()]
        
        if not pairs:
            raise ValueError("No valid items provided.")
        
        for pair in pairs:
            if ":" not in pair:
                raise ValueError(f"Invalid format: '{pair}'. Use 'BoltName:Quantity'")
            
            name_part, qty_part = pair.split(":", 1)
            name = name_part.strip()
            qty_str = qty_part.strip()
            
            if not name:
                raise ValueError("Bolt name cannot be empty.")
            
            try:
                qty = int(qty_str)
            except ValueError:
                raise ValueError(f"Quantity for '{name}' must be a whole number.")
            
            if qty <= 0:
                raise ValueError(f"Quantity for '{name}' must be positive.")
            
            key = name.lower()
            aggregated[key] = aggregated.get(key, 0) + qty
        
        result = {}
        seen = set()
        for pair in pairs:
            name = pair.split(":", 1)[0].strip()
            key = name.lower()
            if key not in seen:
                result[name] = aggregated[key]
                seen.add(key)
        
        return result
    
    def _convert_items_to_order_items(self, items_dict: Dict[str, int]) -> List[OrderItem]:
        """Convert item names to OrderItem objects with bolt IDs."""
        order_items = []
        
        for bolt_name, quantity in items_dict.items():
            bolts = self.bolt_repo.find_by_name(bolt_name)
            
            if not bolts:
                messagebox.showerror(
                    "Bolt Not Found",
                    f"Bolt '{bolt_name}' not found in inventory.\n"
                    "Please add it to inventory first."
                )
                return []
        
            bolt = None
            for b in bolts:
                if b['name'].lower() == bolt_name.lower():
                    bolt = b
                    break
            if not bolt:
                bolt = bolts[0]
            
            order_items.append(OrderItem(
                bolt_id=bolt['id'],
                bolt_name=bolt['name'],
                quantity=quantity
            ))
        
        return order_items
    
    def on_update(self):
        """Update order (redirect to status update)."""
        self.on_update_status()
    
    def on_update_status(self):
        """Update order status."""
        order_id = self.get_selected_id()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order to update.")
            return
        
        try:
            order = self.repository.get_with_details(order_id)
            if not order:
                messagebox.showerror("Error", "Order not found.")
                return
            
            current_status = order['status']
            
            dialog = StatusUpdateDialog(self, current_status, ORDER_STATUSES)
            self.wait_window(dialog)
            
            if dialog.result:
                new_status = dialog.result['status']
                notes = dialog.result.get('notes', '')
                
                self.repository.update_status(order_id, new_status, "User")
                
                if notes:
                    self.repository.update_notes(order_id, notes)
                
                messagebox.showinfo(
                    "Success",
                    f"Order #{order_id} status updated:\n"
                    f"{current_status} → {new_status}"
                )
                
                self.refresh()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order:\n{e}")
    
    def on_read(self):
        """Show basic order info (use View Details for full info)."""
        order_id = self.get_selected_id()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order to view.")
            return
        
        self.on_view_details()
    
    def on_view_details(self):
        """Show detailed order information."""
        order_id = self.get_selected_id()
        if not order_id:
            messagebox.showwarning("No Selection", "Please select an order to view details.")
            return
        
        try:
            order = self.repository.get_with_details(order_id)
            if not order:
                messagebox.showerror("Error", "Order not found.")
                return
            
            OrderDetailsDialog(self, order)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order details:\n{e}")
    
    def on_advanced_search(self):
        """Show advanced search dialog."""
        dialog = OrderSearchDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            search_type = dialog.result['type']
            search_value = dialog.result['value']
            
            try:
                if search_type == "customer":
                    results = self.repository.search_by_customer_name(search_value)
                elif search_type == "status":
                    results = self.repository.find_by_status(search_value)
                elif search_type == "bolt":
                    results = self.repository.search_by_bolt_name(search_value)
                else:
                    return
                
                if not results:
                    messagebox.showinfo("No Results", "No orders found matching your search.")
                    return
                
                OrderListDialog(self, results, on_open=self._open_order_from_search)
                
            except Exception as e:
                messagebox.showerror("Error", f"Search failed:\n{e}")
    
    def _open_order_from_search(self, order_id: int):
        """Open order details from search results."""
        try:
            order = self.repository.get_with_details(order_id)
            OrderDetailsDialog(self, order)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order:\n{e}")
