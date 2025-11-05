import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional

from ui.components.base_crud_view import BaseView
from ui.components.dialogs import FormDialog, DetailsDialog
from database.repositories.bolt_repo import BoltRepository
from models.bolt import Bolt
from utils.validators import validate_quantity, ValidationError
from config.translation import GREEK as t


class BoltsView(BaseView):
    @staticmethod
    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    
    def __init__(self, parent):
        repository = BoltRepository()
        super().__init__(parent, repository, Bolt)

    def get_columns(self):
        return ["name", "type", "stamp", "quantity"]
    
    def get_column_width(self, col):
        widths = {
            "id": 80,
            "name": 280,
            "type": 180,
            "stamp": 150,
            "quantity": 120
        }
        return widths.get(col, 150)
    
    def get_column_anchor(self, col):
        return CENTER 
    
    def get_table_name(self):
        return "bolts"
    
    def get_custom_buttons(self):
        """Add custom button for full details."""
        return [
            (t["full_details_button"], self.show_full_details)
        ]
    
    def fetch_data(self, search_term=""):
        """Fetch bolts data with optional search."""
        if search_term:
            return self.repository.find_by_name(search_term)
        return self.repository.get_all()
    
    def format_row(self, item):
        d = dict(item)                      
        qty = self._to_int(d.get('quantity'), 0) 
        return (
            d.get('name'),
            d.get('type'),
            d.get('stamp'),
            qty
        )
    
    def refresh(self):
        """Refresh table with low stock highlighting."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            search_term = self.search_var.get().strip()
            items = self.fetch_data(search_term)

            # Configure tags
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='#ffffff')

            for idx, item in enumerate(items):
                values = self.format_row(item)

                tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)

                self.tree.insert("", END, values=values, tags=tags)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")


    
    def get_form_fields(self, is_edit=False):
        """Define form fields for bolt."""
        return [
            {'name': 'name', 'label': t['bolt_name'], 'label_gr': t['bolt_name'], 'type': 'text', 'required': True},
            {'name': 'type', 'label': t['bolt_type'], 'label_gr': t['bolt_type'], 'type': 'combobox', 'required': True,
            'options': [t['single'], t['double']]},
            {'name': 'metal_strip', 'label': t['metal_strip'], 'label_gr': t['metal_strip'], 'type': 'text', 'required': False},
            {'name': 'screw', 'label': t['screw'], 'label_gr': t['screw'], 'type': 'text', 'required': False},
            {'name': 'rod', 'label': t['rod'], 'label_gr': t['rod'], 'type': 'text', 'required': False},
            #{'name': 'plate', 'label': t['plate'], 'label_gr': t['plate'], 'type': 'text', 'required': False},
            {'name': 'square_mechanism', 'label': t['square_mechanism'], 'label_gr': t['square_mechanism'], 'type': 'text', 'required': False},
            {'name': 'stamp', 'label': t['stamp'], 'label_gr': t['stamp'], 'type': 'text', 'required': True},
            {'name': 'quantity', 'label': t['quantity'], 'label_gr': t['quantity'], 'type': 'number', 'required': False},
        ]
    
    def validate_bolt_data(self, data):
        """Validate bolt data before saving."""
        try:
            if data.get('quantity') is not None:
                validate_quantity(data['quantity'])
            if data.get('min_stock_level') is not None:
                validate_quantity(data['min_stock_level'])
        except ValidationError as e:
            raise ValueError(str(e))
    
    def on_add(self):
        """Add new bolt."""
        def save_bolt(data):
            try:
                self.validate_bolt_data(data)
                bolt = Bolt(**data)
                self.repository.create(bolt)
                messagebox.showinfo(t["success"], t["bolt_added"])
                self.refresh()
            except Exception as e:
                messagebox.showerror(t["error"], f"{t['failed_to_add']}: {e}")
                raise
        
        FormDialog(self, "Add New Bolt", self.get_form_fields(), on_save=save_bolt)
    
    def on_update(self):
        """Update existing bolt."""
        bolt_id = self.get_selected_id()
        if not bolt_id:
            messagebox.showwarning(t["no_selection"], t["select_bolt_to_edit"])
            return
        
        try:
            row = self.repository.get_by_id(bolt_id)
            initial_data = dict(row)
            
            def save_bolt(data):
                try:
                    self.validate_bolt_data(data)
                    bolt = Bolt(id=bolt_id, **data)
                    self.repository.update(bolt)
                    messagebox.showinfo(t["success"], t["bolt_updated"])
                    self.refresh()
                except Exception as e:
                    messagebox.showerror(t["error"], f"{t['failed_to_update']}: {e}")
                    raise
            
            FormDialog(
                self,
                t["edit_bolt"],
                self.get_form_fields(True),
                initial_data=initial_data,
                on_save=save_bolt
            )
        except Exception as e:
            messagebox.showerror(t["error"], f"{t['failed_to_load']}: {e}")
    
    def on_read(self):
        """View bolt details."""
        bolt_id = self.get_selected_id()
        if not bolt_id:
            messagebox.showwarning(t["no_selection"], t["select_bolt_to_view"])
            return
        
        try:
            row = self.repository.get_by_id(bolt_id)
            DetailsDialog(self, f"{t['bolt_details']} #{bolt_id}", dict(row))
        except Exception as e:
            messagebox.showerror(t["error"], f"{t['failed_to_load']}: {e}")
   
    def show_full_details(self):
        """Show all bolt fields including optional ones."""
        bolt_id = self.get_selected_id()
        if not bolt_id:
            messagebox.showwarning(t["no_selection"], t["select_bolt_to_view"])
            return
        
        try:
            row = self.repository.get_by_id(bolt_id)
            data = dict(row)
            
            # Create detailed view with all fields
            DetailsDialog(self, f"{t['bolt_details']} #{bolt_id} - {t['full_details']}", data)
        except Exception as e:
            messagebox.showerror(t["error"], f"{t['failed_to_load']}: {e}")

    
    def refresh(self):
        """Refresh table data - override to store ID in item."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            search_term = self.search_var.get().strip()
            items = self.fetch_data(search_term)

            # Configure tags
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='#ffffff')

            for idx, item in enumerate(items):
                values = self.format_row(item)
                tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
                # Store the bolt ID as the tree item identifier
                self.tree.insert("", END, iid=str(item['id']), values=values, tags=tags)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def get_selected_id(self) -> Optional[int]:
        """Get ID of selected bolt from tree iid."""
        selection = self.tree.selection()
        if not selection:
            return None
        try:
            return int(selection[0])
        except (ValueError, IndexError):
            return None
