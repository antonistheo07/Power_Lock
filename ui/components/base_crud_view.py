import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseView(ttk.Frame, ABC):
    """base class for all CRUD views"""

    def __init__(self, parent, repository, model_class):
        super().__init__(parent)
        self.repository = repository
        self.model_class = model_class
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """Setup the modern UI layout."""
        # Header section
        self._create_header()
        
        # Search and action bar
        self._create_toolbar()
        
        # Table frame
        self._create_table()
        
        # Bottom action buttons
        self._create_action_buttons()

    def _create_header(self):
        """Create header with view title."""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=(10, 0))
        
        # Get title from table name
        title = self.get_table_name().replace("_", " ").title()
        
        ttk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

    def _create_toolbar(self):
        """Create toolbar with search and actions."""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=X, padx=20, pady=15)
        
        # Search section (left side)
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=LEFT, fill=X, expand=YES)
        
        ttk.Label(
            search_frame,
            text="🔍 Search:",
            font=("Segoe UI", 10)
        ).pack(side=LEFT, padx=(0, 8))
        
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search())
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35,
            font=("Segoe UI", 10)
        )
        search_entry.pack(side=LEFT, padx=(0, 15))
        
        # Action buttons (right side)
        ttk.Button(
            search_frame,
            text="🔄 Refresh",
            command=self.refresh,
            bootstyle="secondary-outline",
            width=12
        ).pack(side=LEFT, padx=3)
        
        ttk.Button(
            search_frame,
            text="📤 Export",
            command=self.on_export,
            bootstyle="info-outline",
            width=12
        ).pack(side=LEFT, padx=3)

    def _create_table(self):
        """Create modern data table."""
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 15))
        
        # Create Treeview with modern styling
        columns = self.get_columns()
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            bootstyle="primary"
        )
        
        # Configure columns
        for col in columns:
            display_name = col.replace("_", " ").title()
            self.tree.heading(col, text=display_name)
            self.tree.column(
                col,
                width=self.get_column_width(col),
                anchor=self.get_column_anchor(col)
            )
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Double-click to view details
        self.tree.bind("<Double-1>", lambda e: self.on_read())
        
        # Alternating row colors
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='#ffffff')

    def _create_action_buttons(self):
        """Create bottom action buttons with modern styling."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        # Left side - primary actions
        left_frame = ttk.Frame(btn_frame)
        left_frame.pack(side=LEFT)
        
        ttk.Button(
            left_frame,
            text="➕ Add",
            command=self.on_add,
            bootstyle="success",
            width=15
        ).pack(side=LEFT, padx=3)
        
        ttk.Button(
            left_frame,
            text="✏️ Edit",
            command=self.on_update,
            bootstyle="primary",
            width=15
        ).pack(side=LEFT, padx=3)
        
        ttk.Button(
            left_frame,
            text="🗑️ Delete",
            command=self.on_delete,
            bootstyle="danger",
            width=15
        ).pack(side=LEFT, padx=3)
        
        ttk.Button(
            left_frame,
            text="👁️ View Details",
            command=self.on_read,
            bootstyle="info",
            width=15
        ).pack(side=LEFT, padx=3)
        
        # Custom buttons if defined
        custom_buttons = self.get_custom_buttons()
        for btn_text, btn_command in custom_buttons:
            ttk.Button(
                left_frame,
                text=btn_text,
                command=btn_command,
                bootstyle="secondary",
                width=15
            ).pack(side=LEFT, padx=3)

    @abstractmethod
    def get_columns(self) -> List[str]:
        """Return list of column names."""
        pass

    def get_column_width(self, col: str) -> int:
        """Return width for a column."""
        return 150
    
    def get_column_anchor(self, col: str) -> str:
        """Return anchor alignment for a column."""
        return CENTER if col in ["id", "quantity"] else W
    
    def get_custom_buttons(self) -> List[tuple]:
        """Return list of custom buttons as (text, command) tuples."""
        return []
    
    def refresh(self):
        """Refresh the table data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            search_term = self.search_var.get().strip()
            items = self.fetch_data(search_term)

            # Insert items with alternating row colors
            for idx, item in enumerate(items):
                values = self.format_row(item)
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", END, values=values, tags=(tag,))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    @abstractmethod
    def fetch_data(self, search_term: str = ""):
        """Fetch data from repository."""
        pass

    @abstractmethod
    def format_row(self, item) -> tuple:
        """Format item as row tuple."""
        pass

    def get_selected_id(self) -> Optional[int]:
        """Get ID of selected item."""
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0])["values"]
        return values[0] if values else None
    
    def on_search(self):
        """Handle search input."""
        self.refresh()

    @abstractmethod
    def on_add(self):
        """Handle add action."""
        pass

    @abstractmethod
    def on_update(self):
        """Handle update action."""
        pass

    def on_delete(self):
        """Handle delete action."""
        item_id = self.get_selected_id()
        if not item_id:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            return
        
        try:
            self.repository.delete(item_id)
            messagebox.showinfo("Success", "Item deleted successfully!")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    @abstractmethod
    def on_read(self):
        """Handle view/read action."""
        pass
    
    def on_export(self):
        """Handle export action."""
        from utils.exports import export_to_csv
        try:
            items = self.fetch_data()
            filename = f"{self.get_table_name()}_export.csv"
            export_to_csv(items, self.get_columns(), filename)
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    @abstractmethod
    def get_table_name(self) -> str:
        """Return table name for export."""
        pass
