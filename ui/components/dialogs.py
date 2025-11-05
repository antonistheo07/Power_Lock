import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable, Optional
from config.translation import GREEK as t

class FormDialog(tk.Toplevel):
    def __init__(self, parent, title: str, fields: List[Dict], initial_data: Optional[Dict] = None,
                 on_save: Optional[Callable] = None):
        
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.fields_config = fields
        self.initial_data = initial_data or {}
        self.on_save_callback = on_save

        self.transient(parent)
        self.grab_set()

        self.setup_form()
        self.center_on_parent(parent)

    def setup_form(self):
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill="both", expand=True)

        self.widgets = {}
        for idx, field in enumerate(self.fields_config):
            #labels
            label_text = field['label']
            if field.get('required', False):
                label_text += f"*"
            ttk.Label(form_frame, text=label_text).grid(row=idx, column=0, sticky="", pady=5, padx=(0, 10))
            
            # Widget
            widget = self.create_widget(form_frame, field)
            widget.grid(row=idx, column=1, sticky="", pady=5)
            self.widgets[field['name']] = widget
            
            # Set initial value
            if field['name'] in self.initial_data:
                self.set_widget_value(widget, field, self.initial_data[field['name']])
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self, padding=(20, 0, 20, 20))
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text=t["cancel"], command=self.on_cancel).pack(side="right", padx=5)
        ttk.Button(btn_frame, text=t["save"], command=self.on_save).pack(side="right")

    def create_widget(self, parent, field):
        """Create appropriate widget based on field type."""
        field_type = field.get('type', 'text')
        
        if field_type == 'textarea':
            widget = tk.Text(parent, height=4, width=40)
        elif field_type == 'combobox':
            widget = ttk.Combobox(parent, values=field.get('options', []), state='readonly')
            if widget['values']:
                widget.current(0)
        else:
            widget = ttk.Entry(parent)
        
        return widget
    
    def set_widget_value(self, widget, field, value):
        """Set widget value."""
        if isinstance(widget, tk.Text):
            widget.delete("1.0", "end")
            widget.insert("1.0", str(value) if value else "")
        elif isinstance(widget, ttk.Combobox):
            widget.set(str(value) if value else "")
        else:
            widget.delete(0, "end")
            widget.insert(0, str(value) if value else "")
    
    def get_widget_value(self, widget, field):
        """Get widget value."""
        if isinstance(widget, tk.Text):
            value = widget.get("1.0", "end-1c").strip()
        elif isinstance(widget, ttk.Combobox):
            value = widget.get().strip()
        else:
            value = widget.get().strip()
        
        # Convert type
        field_type = field.get('type', 'text')
        if field_type == 'number' and value:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"{field['label']} must be a number")
        
        return value if value else None
    
    def validate_form(self) -> Dict:
        """Validate and return form data."""
        data = {}
        
        for field in self.fields_config:
            widget = self.widgets[field['name']]
            value = self.get_widget_value(widget, field)
            
            # Check required
            if field.get('required', False) and not value:
                field_label = field.get('label_gr', field['label'])  
                raise ValueError(f"{field['label']} is required")
            
            data[field['name']] = value
        
        return data
    
    def on_save(self):
        """Save form data."""
        try:
            self.result = self.validate_form()
            
            if self.on_save_callback:
                self.on_save_callback(self.result)
            
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
    
    def on_cancel(self):
        """Cancel and close."""
        self.result = None
        self.destroy()
    
    def center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")


class DetailsDialog(tk.Toplevel):
    """Generic dialog for displaying item details."""
    
    def __init__(self, parent, title: str, data: Dict,field_translations: Optional[Dict] = None):
        super().__init__(parent)
        self.title(title)
        self.field_translations = field_translations or {}
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui(data)
        self.center_on_parent(parent)
    
    def setup_ui(self, data: Dict):
        """Create detail view."""
        from config.translation import GREEK as t
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Create label-value pairs
        for idx, (key, value) in enumerate(data.items()):
            if key in self.field_translations:
                label = self.field_translations[key]
            elif key in t:
                label = t[key]
            else:
                label = key.replace("_", " ").title()
            
            ttk.Label(frame, text=f"{label}:", font=("", 9, "bold")).grid(
                row=idx, column=0, sticky="w", pady=3, padx=(0, 10)
            )
            ttk.Label(frame, text=str(value) if value is not None else "").grid(
                row=idx, column=1, sticky="w", pady=3
            )
        
        # Close button
        btn_frame = ttk.Frame(self, padding=(20, 0, 20, 20))
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="right")
    
    def center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")

class CustomerSelectDialog(tk.Toplevel):
    """Dialog for selecting a customer."""
    
    def __init__(self, parent, customers: list):
        super().__init__(parent)
        self.title("Select Customer")
        self.result = None
        self.customers = customers
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Choose a customer:", font=("", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Create listbox with customer names
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        for customer in self.customers:
            display_text = f"{customer['name']} - {customer['phone']}"
            self.listbox.insert("end", display_text)
        
        self.listbox.bind("<Double-1>", lambda e: self.on_ok())
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Select", command=self.on_ok).pack(side="right")
        
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())
    
    def on_ok(self):
        """Confirm selection."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer.")
            return
        
        idx = selection[0]
        customer = self.customers[idx]
        self.result = (customer['id'], customer['name'])
        self.destroy()
    
    def on_cancel(self):
        """Cancel selection."""
        self.result = None
        self.destroy()
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")


class StatusUpdateDialog(tk.Toplevel):
    """Dialog for updating order status."""
    
    def __init__(self, parent, current_status: str, available_statuses: list):
        super().__init__(parent)
        self.title("Update Order Status")
        self.result = None
        self.current_status = current_status
        self.available_statuses = available_statuses
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Current status
        ttk.Label(frame, text=f"Current Status: {self.current_status}", 
                 font=("", 10, "bold")).pack(anchor="w", pady=(0, 15))
        
        # New status
        ttk.Label(frame, text="New Status:").pack(anchor="w", pady=(0, 5))
        self.status_var = tk.StringVar(value=self.current_status)
        status_combo = ttk.Combobox(frame, textvariable=self.status_var, 
                                    values=self.available_statuses, state="readonly", width=30)
        status_combo.pack(fill="x", pady=(0, 15))
        
        # Optional notes
        ttk.Label(frame, text="Notes (optional):").pack(anchor="w", pady=(0, 5))
        self.notes_text = tk.Text(frame, height=4, width=40)
        self.notes_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Update", command=self.on_ok).pack(side="right")
    
    def on_ok(self):
        """Confirm update."""
        new_status = self.status_var.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        if new_status == self.current_status and not notes:
            messagebox.showinfo("No Changes", "No changes to apply.")
            return
        
        self.result = {
            'status': new_status,
            'notes': notes
        }
        self.destroy()
    
    def on_cancel(self):
        """Cancel update."""
        self.result = None
        self.destroy()
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")


class OrderSearchDialog(tk.Toplevel):
    """Dialog for advanced order search."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Advanced Order Search")
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Search By:", font=("", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Search type
        self.search_type = tk.StringVar(value="customer")
        
        ttk.Radiobutton(frame, text="Customer Name", variable=self.search_type, 
                       value="customer").pack(anchor="w", pady=2)
        ttk.Radiobutton(frame, text="Order Status", variable=self.search_type, 
                       value="status").pack(anchor="w", pady=2)
        ttk.Radiobutton(frame, text="Bolt/Product Name", variable=self.search_type, 
                       value="bolt").pack(anchor="w", pady=2)
        
        # Search value
        ttk.Label(frame, text="Search Value:", font=("", 10)).pack(anchor="w", pady=(15, 5))
        self.search_entry = ttk.Entry(frame, width=40)
        self.search_entry.pack(fill="x", pady=(0, 15))
        self.search_entry.focus_set()
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Search", command=self.on_search).pack(side="right")
        
        self.bind("<Return>", lambda e: self.on_search())
        self.bind("<Escape>", lambda e: self.on_cancel())
    
    def on_search(self):
        """Perform search."""
        search_value = self.search_entry.get().strip()
        if not search_value:
            messagebox.showwarning("Empty Search", "Please enter a search value.")
            return
        
        self.result = {
            'type': self.search_type.get(),
            'value': search_value
        }
        self.destroy()
    
    def on_cancel(self):
        """Cancel search."""
        self.result = None
        self.destroy()
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")


class OrderDetailsDialog(tk.Toplevel):
    """Dialog for displaying complete order details."""
    
    def __init__(self, parent, order: dict):
        super().__init__(parent)
        self.title(f"Order #{order['id']} Details")
        self.order = order
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header = ttk.Label(main_frame, text=f"Order #{self.order['id']}", 
                          font=("Arial", 14, "bold"))
        header.pack(pady=(0, 15))
        
        # Order info
        info_frame = ttk.LabelFrame(main_frame, text="Order Information", padding=15)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info = [
            ("Customer", f"{self.order.get('customer_name', 'Unknown')} (ID: {self.order['customer_id']})"),
            ("Status", self.order['status'].upper()),
            ("Order Date", self.order.get('order_date', 'N/A')),
            ("Last Updated", self.order.get('last_updated', 'N/A')),
            ("Total Items", self.order.get('total_items', 0)),
        ]
        
        if self.order.get('notes'):
            info.append(("Notes", self.order['notes']))
        
        for label, value in info:
            row = ttk.Frame(info_frame)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=f"{label}:", font=("", 9, "bold"), width=15).pack(side="left")
            ttk.Label(row, text=str(value), font=("", 9)).pack(side="left")
        
        # Items
        items_frame = ttk.LabelFrame(main_frame, text="Order Items", padding=15)
        items_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        cols = ("bolt", "quantity")
        items_tree = ttk.Treeview(items_frame, columns=cols, show="headings", height=6)
        items_tree.heading("bolt", text="Bolt/Product")
        items_tree.heading("quantity", text="Quantity")
        items_tree.column("bolt", width=300)
        items_tree.column("quantity", width=100, anchor="e")
        
        for item in self.order.get('items', []):
            items_tree.insert("", "end", values=(
                item.get('bolt_name', 'Unknown'),
                item.get('quantity', 0)
            ))
        
        items_tree.pack(fill="both", expand=True)
        
        # Status history
        if self.order.get('status_history'):
            history_frame = ttk.LabelFrame(main_frame, text="Status History", padding=15)
            history_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            cols = ("changed_at", "old_status", "new_status", "changed_by")
            history_tree = ttk.Treeview(history_frame, columns=cols, show="headings", height=4)
            history_tree.heading("changed_at", text="When")
            history_tree.heading("old_status", text="From")
            history_tree.heading("new_status", text="To")
            history_tree.heading("changed_by", text="By")
            history_tree.column("changed_at", width=160)
            history_tree.column("old_status", width=100)
            history_tree.column("new_status", width=100)
            history_tree.column("changed_by", width=120)
            
            for h in self.order['status_history']:
                history_tree.insert("", "end", values=(
                    h.get('changed_at', '')[:19],  
                    h.get('old_status', 'N/A'),
                    h.get('new_status', ''),
                    h.get('changed_by', 'System')
                ))
            
            history_tree.pack(fill="both", expand=True)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.destroy).pack(pady=(10, 0))
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")


class OrderListDialog(tk.Toplevel):
    """Dialog for displaying a list of orders from search results."""
    
    def __init__(self, parent, orders: list, on_open=None):
        super().__init__(parent)
        self.title("Search Results")
        self.orders = orders
        self.on_open = on_open
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text=f"Found {len(self.orders)} order(s)", 
                 font=("", 10, "bold")).pack(pady=(0, 10))
        
        # Create treeview
        cols = ("id", "customer", "status", "date", "items")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="Order #")
        self.tree.heading("customer", text="Customer")
        self.tree.heading("status", text="Status")
        self.tree.heading("date", text="Date")
        self.tree.heading("items", text="Total Items")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("customer", width=200)
        self.tree.column("status", width=100)
        self.tree.column("date", width=140)
        self.tree.column("items", width=80, anchor="e")
        
        for order in self.orders:
            self.tree.insert("", "end", values=(
                order.get('id'),
                order.get('customer_name', 'Unknown'),
                order.get('status', ''),
                order.get('order_date', '')[:16],
                order.get('total_items', 0)
            ))
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._open_selected())
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=(5, 0))
        if self.on_open:
            ttk.Button(btn_frame, text="View Details", command=self._open_selected).pack(side="right")
    
    def _open_selected(self):
        """Open selected order."""
        if not self.on_open:
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an order.")
            return
        
        try:
            order_id = int(self.tree.item(selection[0])["values"][0])
            self.on_open(order_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open order:\n{e}")
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
    
class OrderItemsDialog(tk.Toplevel):
    """Dialog for selecting order items with dropdown and quantity."""
    
    def __init__(self, parent, bolts: list):
        super().__init__(parent)
        self.title("Add Order Items")
        self.result = None
        self.bolts = bolts
        self.items = {}  
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_on_parent(parent)
    
    def setup_ui(self):
        """Create UI."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Instructions
        ttk.Label(
            main_frame,
            text="Select bolts and quantities for this order:",
            font=("", 10, "bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Add Item", padding=15)
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Bolt selection
        ttk.Label(input_frame, text="Bolt:").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.bolt_var = tk.StringVar()
        bolt_names = [f"{b['name']} (Stock: {b['quantity']})" for b in self.bolts]
        self.bolt_combo = ttk.Combobox(
            input_frame,
            textvariable=self.bolt_var,
            values=bolt_names,
            state="readonly",
            width=40
        )
        self.bolt_combo.grid(row=0, column=1, sticky="ew", pady=5)
        if bolt_names:
            self.bolt_combo.current(0)
        
        # Quantity
        ttk.Label(input_frame, text="Quantity:").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=15)
        quantity_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Add button
        ttk.Button(
            input_frame,
            text="➕ Add Item",
            command=self.add_item,
            bootstyle="success"
        ).grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Items list frame
        list_frame = ttk.LabelFrame(main_frame, text="Order Items", padding=15)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview for items
        cols = ("bolt", "quantity")
        self.items_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8)
        self.items_tree.heading("bolt", text="Bolt Name")
        self.items_tree.heading("quantity", text="Quantity")
        self.items_tree.column("bolt", width=300)
        self.items_tree.column("quantity", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Remove button
        ttk.Button(
            list_frame,
            text="🗑️ Remove Selected",
            command=self.remove_item,
            bootstyle="danger"
        ).pack(pady=(10, 0))
        
        # Summary
        self.summary_label = ttk.Label(
            main_frame,
            text="Total Items: 0",
            font=("", 10, "bold")
        )
        self.summary_label.pack(anchor="w", pady=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Create Order", command=self.on_create, bootstyle="success").pack(side="right")
        
        # Bind Enter key
        quantity_entry.bind("<Return>", lambda e: self.add_item())
    
    def add_item(self):
        """Add selected item to the list."""
        try:
            selected = self.bolt_combo.get()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a bolt.")
                return
            
            bolt_name = selected.split(" (Stock:")[0]
            
            quantity_str = self.quantity_var.get().strip()
            if not quantity_str:
                messagebox.showwarning("Invalid Quantity", "Please enter a quantity.")
                return
            
            try:
                quantity = int(quantity_str)
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Quantity must be a number.")
                return
            
            if quantity <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be positive.")
                return
            
            # Add or update item
            if bolt_name in self.items:
                self.items[bolt_name] += quantity
            else:
                self.items[bolt_name] = quantity
            
            self.refresh_items_list()
            self.quantity_var.set("1")  
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item:\n{e}")
    
    def remove_item(self):
        """Remove selected item from list."""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
        
        item = self.items_tree.item(selection[0])
        bolt_name = item['values'][0]
        
        if bolt_name in self.items:
            del self.items[bolt_name]
            self.refresh_items_list()
    
    def refresh_items_list(self):
        """Refresh the items treeview."""
        # Clear tree
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items
        total_items = 0
        for bolt_name, quantity in self.items.items():
            self.items_tree.insert("", "end", values=(bolt_name, quantity))
            total_items += quantity
        
        # Update summary
        self.summary_label.configure(text=f"Total Items: {total_items}")
    
    def on_create(self):
        """Create order with selected items."""
        if not self.items:
            messagebox.showwarning("No Items", "Please add at least one item to the order.")
            return
        
        self.result = self.items
        self.destroy()
    
    def on_cancel(self):
        """Cancel and close."""
        self.result = None
        self.destroy()
    
    def center_on_parent(self, parent):
        """Center dialog on parent."""
        self.update_idletasks()
        if parent.winfo_ismapped():
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
