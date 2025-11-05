import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class MainContainer(ttk.Frame):
    """Main application container with sidebar navigation"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=YES)
        
        # Track current view
        self.current_view = None
        self.current_view_widget = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main UI structure"""
        # Left sidebar for navigation
        self._create_sidebar()
        
        # Right content area
        self._create_content_area()
        
    def _create_sidebar(self):
        """Create left navigation sidebar"""
        self.sidebar = ttk.Frame(self, bootstyle="secondary", width=220)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)  
        
        # App title/logo area
        title_frame = ttk.Frame(self.sidebar, bootstyle="secondary")
        title_frame.pack(fill=X, padx=20, pady=20)
        
        ttk.Label(
            title_frame,
            text="⚡ Power Lock",
            font=("Segoe UI", 15, "bold"),
            bootstyle="inverse-secondary"
        ).pack(anchor=NW)
        
        ttk.Label(
            title_frame,
            text="Order Management",
            font=("Segoe UI", 9),
            bootstyle="inverse-secondary"
        ).pack(anchor=W)
        
        # Separator
        ttk.Separator(self.sidebar, bootstyle="secondary").pack(fill=X, padx=10, pady=10)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.sidebar, bootstyle="secondary")
        nav_frame.pack(fill=X, padx=10, pady=10)
        
        self.nav_buttons = {}
        
        nav_items = [
            ("👥  Customers", "customers"),
            ("🔩  Bolts Inventory", "bolts"),
            ("📦  Orders", "orders"),
        ]
        
        for label, view_name in nav_items:
            btn = ttk.Button(
                nav_frame,
                text=label,
                command=lambda v=view_name: self._on_nav_click(v),
                bootstyle="secondary",
                width=18
            )
            btn.pack(fill=X, pady=3)
            self.nav_buttons[view_name] = btn
            
        # Spacer to push bottom items down
        spacer = ttk.Frame(self.sidebar, bootstyle="secondary")
        spacer.pack(fill=BOTH, expand=YES)
        
        # Separator before bottom section
        ttk.Separator(self.sidebar, bootstyle="secondary").pack(fill=X, padx=10, pady=10)
        
        # Bottom section - Settings/Help
        bottom_frame = ttk.Frame(self.sidebar, bootstyle="secondary")
        bottom_frame.pack(fill=X, padx=10, pady=(0, 20))
        
        ttk.Button(
            bottom_frame,
            text="⚙️  Settings",
            bootstyle="secondary-link",
            command=self._show_settings
        ).pack(fill=X, pady=2)
        
        ttk.Button(
            bottom_frame,
            text="❓  Help",
            bootstyle="secondary-link",
            command=self._show_help
        ).pack(fill=X, pady=2)
        
    def _create_content_area(self):
        """Create main content area where views will be loaded"""
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
    def _on_nav_click(self, view_name):
        """Handle navigation button click"""
        # Update button states
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="secondary")
        
        # Store current view
        self.current_view = view_name
        
        # Notify parent window to switch view
        if hasattr(self.master, 'on_view_change'):
            self.master.on_view_change(view_name)
        
    def load_view(self, view_widget):
        """Load a view widget into the content area"""
        # Clear existing view
        if self.current_view_widget:
            self.current_view_widget.destroy()
        
        # Load new view
        self.current_view_widget = view_widget
        self.current_view_widget.pack(fill=BOTH, expand=YES)
        
    def get_content_frame(self):
        """Get the content frame for loading views"""
        return self.content_frame
        
    def _show_settings(self):
        """Show settings dialog"""
        if hasattr(self.master, 'update_status'):
            self.master.update_status("Settings - Coming soon")
        
    def _show_help(self):
        """Show help dialog"""
        if hasattr(self.master, 'update_status'):
            self.master.update_status("Help - Coming soon")
