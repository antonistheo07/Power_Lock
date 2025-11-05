import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional

from ui.components.base_crud_view import BaseView
from ui.components.dialogs import FormDialog, DetailsDialog
from database.repositories.customer_repo import CustomerRepository
from models.customer import Customer
from utils.validators import validate_phone, ValidationError


class CustomerView(BaseView):
    """customer management view"""
    
    def __init__(self, parent):
        repository = CustomerRepository()
        super().__init__(parent, repository, Customer)

    def get_columns(self):
        return ["name", "phone"]
    
    def get_column_width(self, col):
        widths = {"id": 80, "name": 300, "phone": 200}
        return widths.get(col, 150)
    
    def get_table_name(self):
        return "customers"
    
    def fetch_data(self, search_term=""):
        if search_term:
            return self.repository.find_by_name(search_term)
        return self.repository.get_all()
    
    def format_row(self, item):
        return (item['name'], item['phone'])
    
    def get_column_anchor(self, col: str) -> str:
        """Return anchor alignment for columns."""
        if col in ["id", "name", "phone"]:
            return CENTER
        return W  
    
    def get_form_fields(self, is_edit=False):
        """Define form fields for customer."""
        return [
            {'name': 'name', 'label': 'Customer Name', 'type': 'text', 'required': True},
            {'name': 'phone', 'label': 'Phone Number', 'type': 'text', 'required': False},
        ]
    
    def validate_customer_data(self, data):
        """Validate customer data before saving."""
        phone = data.get('phone')  
        try:
            validate_phone(phone)
        except ValidationError as e:
            raise ValueError(str(e))
    
    def on_add(self):
        """Handle add customer action."""
        def save_customer(data):
            try:
                self.validate_customer_data(data)
                customer = Customer(**data)
                self.repository.create(customer)
                messagebox.showinfo("Success", "Customer added successfully!")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")
                raise
        
        FormDialog(self, "Add New Customer", self.get_form_fields(), on_save=save_customer)

    def on_update(self):
        """Handle edit customer action."""
        customer_id = self.get_selected_id()
        if not customer_id:
            messagebox.showwarning("No Selection", "Please select a customer to edit.")
            return
        
        try:
            row = self.repository.get_by_id(customer_id)
            initial_data = dict(row)
            
            def save_customer(data):
                try:
                    self.validate_customer_data(data)
                    customer = Customer(id=customer_id, **data)
                    self.repository.update(customer)
                    messagebox.showinfo("Success", "Customer updated successfully!")
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update customer: {e}")
                    raise
            
            FormDialog(
                self,
                "Edit Customer",
                self.get_form_fields(True),
                initial_data=initial_data,
                on_save=save_customer
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer: {e}")
    
    def on_read(self):
        """View customer details."""
        customer_id = self.get_selected_id()
        if not customer_id:
            messagebox.showwarning("No Selection", "Please select a customer to view.")
            return
        
        try:
            row = self.repository.get_by_id(customer_id)
            DetailsDialog(self, f"Customer #{customer_id}", dict(row))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer: {e}")

    def refresh(self):
        """Refresh the table data - override to store ID in item."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            search_term = self.search_var.get().strip() if hasattr(self, 'search_var') else ""
            items = self.fetch_data(search_term)

            for idx, item in enumerate(items):
                values = self.format_row(item)
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", END, iid=str(item['id']), values=values, tags=(tag,))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def get_selected_id(self) -> Optional[int]:
        """Get ID of selected customer from tree iid."""
        selection = self.tree.selection()
        if not selection:
            return None
        try:
            return int(selection[0])
        except (ValueError, IndexError):
            return None
