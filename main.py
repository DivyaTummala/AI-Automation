import tkinter as tk
from tkinter import ttk, messagebox

class ETLConfigUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ETL - Validation testing")
        self.root.geometry("1200x600")
        self.root.configure(bg='#e8f5e9')

        # Create main container
        self.create_header()
        self.create_main_panels()
        self.create_footer()

    def create_header(self):
        """Create the header with gradient effect"""
        header_frame = tk.Frame(self.root, bg='#4ecdc4', height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

    def create_main_panels(self):
        """Create the two main panels for source and target configuration"""
        # Main container for both panels
        main_container = tk.Frame(self.root, bg='#e8f5e9')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Left Panel - Source Configuration
        left_panel = self.create_source_panel(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Right Panel - Target Configuration
        right_panel = self.create_target_panel(main_container)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

    def create_source_panel(self, parent):
        """Create the source configuration panel"""
        panel = tk.Frame(parent, bg='white', relief='raised', bd=1)

        # Header with gradient-like effect
        header = tk.Frame(panel, bg='#ff9a9e', height=40)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text="📊  Configure your data source connection",
                              bg='#ff9a9e', fg='white', font=('Arial', 11, 'bold'),
                              anchor='w', padx=10)
        title_label.pack(fill='both', expand=True)

        # Content area
        content = tk.Frame(panel, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Source Type
        self.create_field_with_icon(content, "📦", "Source Type", 0)
        self.source_type = ttk.Combobox(content, values=['RDBMS'], state='readonly')
        self.source_type.set('RDBMS')
        self.source_type.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        # Source Database Type
        self.create_field_with_icon(content, "📦", "Source Database Type", 2)
        self.source_db_type = ttk.Combobox(content, values=['SQL Server', 'MySQL', 'PostgreSQL', 'Oracle'],
                                          state='readonly')
        self.source_db_type.set('SQL Server')
        self.source_db_type.grid(row=3, column=0, sticky='ew', pady=(0, 15))

        # Database Connection Settings
        settings_label = tk.Label(content, text="⚙ Database Connection Settings",
                                 bg='white', font=('Arial', 10, 'bold'), anchor='w')
        settings_label.grid(row=4, column=0, sticky='w', pady=(10, 10))

        # Server / Host
        self.create_field_with_icon(content, "🖥️", "Server / Host", 5)
        self.server_host = tk.Entry(content, bg='#e1f5fe')
        self.server_host.grid(row=6, column=0, sticky='ew', pady=(0, 15))

        # Database Name
        self.create_field_with_icon(content, "📦", "Database Name", 7)
        self.db_name = tk.Entry(content, bg='#e1f5fe')
        self.db_name.grid(row=8, column=0, sticky='ew', pady=(0, 15))

        # Port
        self.create_field_with_icon(content, "🔌", "Port", 9)
        port_hint = tk.Label(content, text="1433 for SQL Server, 3306 for MySQL, 5432 for PostgreSQL",
                           bg='white', font=('Arial', 8), fg='#666', anchor='w')
        port_hint.grid(row=10, column=0, sticky='w', pady=(0, 15))

        # Authentication Type
        self.create_field_with_icon(content, "🔐", "Authentication Type", 11)
        self.auth_type = ttk.Combobox(content, values=['SQL Server Authentication', 'Windows Authentication'],
                                     state='readonly')
        self.auth_type.set('SQL Server Authentication')
        self.auth_type.grid(row=12, column=0, sticky='ew', pady=(0, 15))

        content.columnconfigure(0, weight=1)

        return panel

    def create_target_panel(self, parent):
        """Create the target configuration panel"""
        panel = tk.Frame(parent, bg='white', relief='raised', bd=1)

        # Header with gradient-like effect
        header = tk.Frame(panel, bg='#a1c4fd', height=40)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text="📊  Configure your target data destination",
                              bg='#a1c4fd', fg='white', font=('Arial', 11, 'bold'),
                              anchor='w', padx=10)
        title_label.pack(fill='both', expand=True)

        # Content area
        content = tk.Frame(panel, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Target Type
        self.create_field_with_icon(content, "📦", "Target Type", 0)
        self.target_type = ttk.Combobox(content, values=['Flat File', 'RDBMS', 'Data Platform / Lakehouse'],
                                       state='readonly')
        self.target_type.set('RDBMS')
        self.target_type.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        # Target Database Type
        self.create_field_with_icon(content, "📦", "Target Database Type", 2)
        self.target_db_type = ttk.Combobox(content, values=['SQL Server', 'MySQL', 'PostgreSQL', 'Oracle'],
                                          state='readonly')
        self.target_db_type.set('SQL Server')
        self.target_db_type.grid(row=3, column=0, sticky='ew', pady=(0, 15))

        # Database Connection Settings
        settings_label = tk.Label(content, text="⚙ Database Connection Settings",
                                 bg='white', font=('Arial', 10, 'bold'), anchor='w')
        settings_label.grid(row=4, column=0, sticky='w', pady=(10, 10))

        # Server / Host
        self.create_field_with_icon(content, "🖥️", "Server / Host", 5)
        self.target_server_host = tk.Entry(content, bg='#e1f5fe')
        self.target_server_host.grid(row=6, column=0, sticky='ew', pady=(0, 15))

        # Database Name
        self.create_field_with_icon(content, "📦", "Database Name", 7)
        self.target_db_name = tk.Entry(content, bg='#e1f5fe')
        self.target_db_name.grid(row=8, column=0, sticky='ew', pady=(0, 15))

        # Port
        self.create_field_with_icon(content, "🔌", "Port", 9)
        target_port_hint = tk.Label(content, text="1433 for SQL Server, 3306 for MySQL, 5432 for PostgreSQL",
                           bg='white', font=('Arial', 8), fg='#666', anchor='w')
        target_port_hint.grid(row=10, column=0, sticky='w', pady=(0, 15))

        # Authentication Type
        self.create_field_with_icon(content, "🔐", "Authentication Type", 11)
        self.target_auth_type = ttk.Combobox(content, values=['SQL Server Authentication', 'Windows Authentication'],
                                     state='readonly')
        self.target_auth_type.set('SQL Server Authentication')
        self.target_auth_type.grid(row=12, column=0, sticky='ew', pady=(0, 15))

        content.columnconfigure(0, weight=1)

        return panel

    def create_field_with_icon(self, parent, icon, label_text, row):
        """Helper to create field labels with icons"""
        label = tk.Label(parent, text=f"{icon}  {label_text}",
                        bg='white', font=('Arial', 9, 'bold'), anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=(5, 2))

    def create_footer(self):
        """Create footer with buttons and info"""
        footer = tk.Frame(self.root, bg='#e8f5e9', height=60)
        footer.pack(fill='x', padx=10, pady=(0, 10))
        footer.pack_propagate(False)

        # Button frame
        button_frame = tk.Frame(footer, bg='#e8f5e9')
        button_frame.pack(side='right', padx=10, pady=10)

        # Warning button
        warning_btn = tk.Button(button_frame, text="⚠️ Warning", bg='#ffd93d',
                               font=('Arial', 9, 'bold'), padx=15, pady=5,
                               relief='raised', cursor='hand2')
        warning_btn.pack(side='left', padx=5)

        # Private & Confidential button
        private_btn = tk.Button(button_frame, text="🔒 Private & Confidential",
                               bg='#ff6b9d', fg='white',
                               font=('Arial', 9, 'bold'), padx=15, pady=5,
                               relief='raised', cursor='hand2')
        private_btn.pack(side='left', padx=5)

        # Footer info
        info_label = tk.Label(footer,
                            text="ETL - Validation testing © 2026 | Powered by Python & Flask",
                            bg='#e8f5e9', font=('Arial', 8), fg='#666')
        info_label.pack(side='bottom', pady=5)

def main():
    root = tk.Tk()
    app = ETLConfigUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
