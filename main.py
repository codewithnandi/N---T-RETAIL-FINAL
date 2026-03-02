# Retail Shopping Management System (Admin Only)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# Database name
DB_NAME = "retail.db"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

# Elegant Olive, Beige & White Color Palette
OLIVE_DARK = "#4A5D23"      # Deep olive (primary)
OLIVE_MEDIUM = "#6B8E23"    # Medium olive (secondary)
OLIVE_LIGHT = "#8A9A5B"     # Light olive (accents)
BEIGE_DARK = "#E8DCC4"      # Dark beige (cards)
BEIGE_LIGHT = "#F5F0E6"     # Light beige (background)
WHITE = "#FFFFFF"           # Pure white (foregrounds, entries)
OFF_WHITE = "#FAF7F0"       # Off-white (alternate)
ACCENT = "#C0A080"          # Warm accent (hover)

# ================= DATABASE =================
class Database:
    def __init__(self):
        """Initialize database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.create_tables()
        self.ensure_sale_time_column()

    def create_tables(self):
        """Create necessary tables for the retail management system."""
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            sale_date DATE NOT NULL,
            sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """)
        
        self.cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)
        """)
        
        self.conn.commit()

    def ensure_sale_time_column(self):
        """Ensure sale_time column exists (for older databases)."""
        try:
            self.cur.execute("SELECT sale_time FROM sales LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it without DEFAULT (SQLite limitation)
            self.cur.execute("ALTER TABLE sales ADD COLUMN sale_time TIMESTAMP")
            self.conn.commit()
            print("Added sale_time column to sales table.")

    def execute(self, query, params=()):
        """Execute a query with parameters and commit."""
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur.lastrowid

    def fetchall(self, query, params=()):
        """Fetch all results from a query."""
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def fetchone(self, query, params=()):
        """Fetch single result from a query."""
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def __del__(self):
        """Close database connection when object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()


# ================= MAIN APPLICATION =================
class RetailApp:
    def __init__(self, root):
        """Initialize the main application."""
        self.root = root
        self.root.title("N & T RETAIL SHOP - Administration")
        self.root.geometry("1200x700")
        self.root.configure(bg=BEIGE_LIGHT)
        
        # Center window on screen
        self.center_window()
        
        # Initialize database
        self.db = Database()
        
        # Shopping cart for multi-item billing
        self.cart = []  # List of dicts: {'product_id': id, 'name': name, 'price': price, 'quantity': qty, 'total': total}
        
        # Configure styles
        self.setup_styles()
        
        # Main container
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.pack(fill="both", expand=True)
        
        # Show login screen
        self.show_login()

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_styles(self):
        """Configure ttk styles for elegant olive, beige and white theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Main background
        style.configure('Main.TFrame', background=BEIGE_LIGHT)
        style.configure('Card.TFrame', background=BEIGE_DARK, relief='raised', borderwidth=1)

        # Labels
        style.configure('Title.TLabel', 
                       background=BEIGE_LIGHT, 
                       foreground=OLIVE_DARK,
                       font=('Helvetica', 24, 'bold'))
        
        style.configure('Heading.TLabel', 
                       background=BEIGE_LIGHT, 
                       foreground=OLIVE_MEDIUM,
                       font=('Helvetica', 14, 'bold'))
        
        style.configure('CardTitle.TLabel', 
                       background=BEIGE_DARK, 
                       foreground=OLIVE_DARK,
                       font=('Helvetica', 12, 'bold'))
        
        style.configure('CardValue.TLabel', 
                       background=BEIGE_DARK, 
                       foreground=OLIVE_MEDIUM,
                       font=('Helvetica', 20, 'bold'))

        # Buttons
        style.configure('Primary.TButton',
                       background=OLIVE_DARK,
                       foreground=WHITE,
                       borderwidth=0,
                       focusthickness=2,
                       focuscolor=OLIVE_LIGHT,
                       font=('Helvetica', 10, 'bold'),
                       padding=(20, 10))
        style.map('Primary.TButton',
                 background=[('active', OLIVE_MEDIUM), ('pressed', OLIVE_LIGHT)],
                 foreground=[('active', WHITE)])

        style.configure('Secondary.TButton',
                       background=OLIVE_MEDIUM,
                       foreground=WHITE,
                       borderwidth=0,
                       focusthickness=2,
                       focuscolor=OLIVE_LIGHT,
                       font=('Helvetica', 10, 'bold'),
                       padding=(20, 10))
        style.map('Secondary.TButton',
                 background=[('active', OLIVE_DARK), ('pressed', OLIVE_LIGHT)],
                 foreground=[('active', WHITE)])

        # Entry fields
        style.configure('TEntry',
                       fieldbackground=WHITE,
                       foreground=OLIVE_DARK,
                       borderwidth=1,
                       relief='solid',
                       padding=5)
        
        style.configure('TCombobox',
                       fieldbackground=WHITE,
                       foreground=OLIVE_DARK,
                       borderwidth=1,
                       padding=5)

        # Treeview
        style.configure('Treeview',
                       background=WHITE,
                       foreground=OLIVE_DARK,
                       fieldbackground=WHITE,
                       borderwidth=0,
                       font=('Helvetica', 10))
        style.map('Treeview',
                 background=[('selected', OLIVE_LIGHT)],
                 foreground=[('selected', WHITE)])
        
        style.configure('Treeview.Heading',
                       background=BEIGE_DARK,
                       foreground=OLIVE_DARK,
                       font=('Helvetica', 10, 'bold'),
                       borderwidth=1,
                       relief='solid')

        # Scrollbar
        style.configure('TScrollbar',
                       background=BEIGE_DARK,
                       troughcolor=BEIGE_LIGHT,
                       arrowcolor=OLIVE_DARK)

    def clear_frame(self):
        """Clear all widgets from the main container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ================= LOGIN SCREEN =================
    def show_login(self):
        """Display the login screen."""
        self.clear_frame()

        # Create centered card
        login_card = ttk.Frame(self.main_container, style='Card.TFrame')
        login_card.place(relx=0.5, rely=0.5, anchor='center', width=400, height=400)

        # Store logo/title
        title_label = ttk.Label(login_card, 
                               text="N & T RETAIL", 
                               style='Title.TLabel',
                               background=BEIGE_DARK)
        title_label.pack(pady=(40, 10))

        subtitle_label = tk.Label(login_card,
                                 text="Administration Portal",
                                 bg=BEIGE_DARK,
                                 fg=OLIVE_MEDIUM,
                                 font=('Helvetica', 12, 'italic'))
        subtitle_label.pack(pady=(0, 20))

        # Login form
        form_frame = ttk.Frame(login_card, style='Card.TFrame')
        form_frame.pack(pady=10, padx=40, fill='x')

        # Username
        ttk.Label(form_frame, text=" Username:", 
                 style='CardTitle.TLabel').pack(anchor='w', pady=(10, 5))
        username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=username_var, width=30)
        username_entry.pack(fill='x', pady=(0, 10))
        username_entry.focus()

        # Password
        ttk.Label(form_frame, text=" Password:", 
                 style='CardTitle.TLabel').pack(anchor='w', pady=(10, 5))
        password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=password_var, 
                                  show="•", width=30)
        password_entry.pack(fill='x', pady=(0, 20))

        def attempt_login():
            """Validate login credentials."""
            if username_var.get() == ADMIN_USER and password_var.get() == ADMIN_PASS:
                self.show_dashboard()
            else:
                messagebox.showerror("Access Denied", 
                                   "Invalid username or password.\nPlease try again.",
                                   parent=login_card)
                password_var.set("")

        # Login button
        login_btn = ttk.Button(form_frame, text="LOGIN", 
                              style='Primary.TButton',
                              command=attempt_login)
        login_btn.pack(pady=10)

        # Bind Enter key
        password_entry.bind('<Return>', lambda e: attempt_login())

        # Footer
        footer = tk.Label(login_card,
                         text="© 2026 N & T Retail Solutions",
                         bg=BEIGE_DARK,
                         fg=OLIVE_LIGHT,
                         font=('Helvetica', 8))
        footer.pack(side='bottom', pady=10)

    # ================= DASHBOARD =================
    def show_dashboard(self):
        """Display the main dashboard with statistics."""
        self.clear_frame()

        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', padx=30, pady=(20, 10))
        
        ttk.Label(header_frame, text="Dashboard", 
                 style='Title.TLabel').pack(side='left')
        
        # Date display
        current_date = datetime.now().strftime("%B %d, %Y")
        date_label = tk.Label(header_frame,
                            text=current_date,
                            bg=BEIGE_LIGHT,
                            fg=OLIVE_MEDIUM,
                            font=('Helvetica', 12))
        date_label.pack(side='right')

        # Statistics cards
        self.display_statistics()

        # Navigation buttons
        self.display_navigation_buttons()

    def display_statistics(self):
        """Display statistics cards on dashboard."""
        # Fetch statistics
        total_products = self.db.fetchone("SELECT COUNT(*) FROM products")[0] or 0
        total_sales = self.db.fetchone("SELECT COUNT(*) FROM sales")[0] or 0
        total_revenue = self.db.fetchone("SELECT IFNULL(SUM(total), 0) FROM sales")[0] or 0
        low_stock = self.db.fetchone("SELECT COUNT(*) FROM products WHERE stock < 10")[0] or 0

        # Create cards frame
        cards_frame = ttk.Frame(self.main_container)
        cards_frame.pack(pady=30)

        # Statistics cards
        stats = [
            ("Total Products", total_products, "📦"),
            ("Total Sales", total_sales, "💰"),
            ("Total Revenue", f"₹ {total_revenue:,.2f}", "📊"),
            ("Low Stock Items", low_stock, "⚠️")
        ]

        for i, (title, value, icon) in enumerate(stats):
            card = ttk.Frame(cards_frame, style='Card.TFrame', padding=20)
            card.grid(row=0, column=i, padx=15, pady=10, sticky='nsew')
            
            # Icon and title
            tk.Label(card, text=icon, bg=BEIGE_DARK, 
                    fg=OLIVE_DARK, font=('Helvetica', 24)).pack()
            
            ttk.Label(card, text=title, 
                     style='CardTitle.TLabel').pack(pady=(5, 10))
            
            # Value
            value_label = tk.Label(card, text=value,
                                  bg=BEIGE_DARK,
                                  fg=OLIVE_DARK if i < 3 else '#C04040',
                                  font=('Helvetica', 18, 'bold'))
            value_label.pack()

    def display_navigation_buttons(self):
        """Display navigation buttons on dashboard."""
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(pady=40)

        buttons = [
            ("📋 Manage Products", self.manage_products),
            ("💰 Sales Management", self.sales_management),
            ("📈 Sales Analysis", self.sales_analysis),
            ("🚪 Logout", self.show_login)
        ]

        for i, (text, command) in enumerate(buttons):
            style = 'Secondary.TButton' if i < 3 else 'Primary.TButton'
            btn = ttk.Button(nav_frame, text=text, 
                           style=style, width=25,
                           command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)

    # ================= PRODUCT MANAGEMENT =================
    def manage_products(self):
        """Display product management interface."""
        self.clear_frame()

        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', padx=30, pady=(20, 10))
        
        ttk.Label(header_frame, text="Product Management", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="← Back to Dashboard",
                  style='Secondary.TButton',
                  command=self.show_dashboard).pack(side='right')

        # Product entry form
        self.create_product_form()

        # Products list
        self.display_products_list()

    def create_product_form(self):
        """Create product entry form."""
        form_frame = ttk.Frame(self.main_container, style='Card.TFrame', padding=20)
        form_frame.pack(fill='x', padx=30, pady=20)

        ttk.Label(form_frame, text="Add New Product", 
                 style='Heading.TLabel',
                 background=BEIGE_DARK).pack(anchor='w', pady=(0, 15))

        # Input fields
        fields_frame = ttk.Frame(form_frame, style='Card.TFrame')
        fields_frame.pack(fill='x')

        # Product fields
        labels = ["Product Name:", "Category:", "Price (₹):", "Stock:"]
        self.product_name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.price_var = tk.DoubleVar()
        self.stock_var = tk.IntVar()
        
        vars_list = [self.product_name_var, self.category_var, self.price_var, self.stock_var]

        for i, (label, var) in enumerate(zip(labels, vars_list)):
            # Label
            ttk.Label(fields_frame, text=label, 
                     style='CardTitle.TLabel',
                     background=BEIGE_DARK).grid(row=i//2, column=(i%2)*2, 
                                                padx=(20 if i%2==0 else 10, 5), 
                                                pady=10, sticky='w')
            
            # Entry
            entry = ttk.Entry(fields_frame, textvariable=var, width=25)
            entry.grid(row=i//2, column=(i%2)*2 + 1, 
                      padx=(0, 20), pady=10, sticky='w')

        # Add button
        ttk.Button(fields_frame, text="➕ Add Product",
                  style='Primary.TButton',
                  command=self.add_product).grid(row=2, column=0, columnspan=4, 
                                                pady=(20, 10))

    def add_product(self):
        """Add a new product to database."""
        try:
            # Validate inputs
            name = self.product_name_var.get().strip()
            category = self.category_var.get().strip()
            price = self.price_var.get()
            stock = self.stock_var.get()

            if not all([name, category]):
                messagebox.showwarning("Validation Error", 
                                     "Please fill in all fields.")
                return

            if price <= 0:
                messagebox.showwarning("Validation Error", 
                                     "Price must be greater than 0.")
                return

            if stock < 0:
                messagebox.showwarning("Validation Error", 
                                     "Stock cannot be negative.")
                return

            # Insert into database
            self.db.execute("""
                INSERT INTO products (name, category, price, stock) 
                VALUES (?, ?, ?, ?)
            """, (name, category, price, stock))

            messagebox.showinfo("Success", 
                              f"Product '{name}' added successfully!")
            
            # Clear form
            self.product_name_var.set("")
            self.category_var.set("")
            self.price_var.set(0)
            self.stock_var.set(0)
            
            # Refresh products list
            self.display_products_list()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", 
                               "Product with this name already exists.")
        except ValueError:
            messagebox.showerror("Error", 
                               "Please enter valid numeric values for price and stock.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_products_list(self):
        """Display products in a treeview."""
        # Clear previous list if exists
        for widget in self.main_container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.main_container.winfo_children()[0]:
                if len(widget.winfo_children()) > 0 and isinstance(widget.winfo_children()[0], ttk.Treeview):
                    widget.destroy()

        # Products list frame
        list_frame = ttk.Frame(self.main_container)
        list_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        # Header with title and restock button
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="Current Products", 
                 style='Heading.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="🔄 Restock Selected Product", style='Secondary.TButton',
                   command=self.restock_product).pack(side='right', padx=5)

        # Treeview with scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        columns = ("ID", "Product Name", "Category", "Price (₹)", "Stock", "Status")
        self.products_tree = ttk.Treeview(tree_frame, columns=columns, 
                                          show="headings", height=12,
                                          yscrollcommand=vsb.set,
                                          xscrollcommand=hsb.set)

        # Configure columns
        column_widths = [50, 250, 150, 120, 100, 100]
        for col, width in zip(columns, column_widths):
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=width, anchor='center' if col != "Product Name" else 'w')

        # Configure scrollbars
        vsb.config(command=self.products_tree.yview)
        hsb.config(command=self.products_tree.xview)

        # Grid layout
        self.products_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Fetch and display products
        products = self.db.fetchall("SELECT * FROM products ORDER BY name")
        
        for product in products:
            # Determine stock status
            stock = product[4]
            if stock <= 0:
                status = "Out of Stock"
                tag = 'outofstock'
            elif stock < 10:
                status = "Low Stock"
                tag = 'lowstock'
            else:
                status = "In Stock"
                tag = 'instock'

            # Insert with tags for color coding
            self.products_tree.insert("", "end", values=(
                product[0], product[1], product[2], 
                f"₹ {product[3]:,.2f}", product[4], status
            ), tags=(tag,))

        # Configure tag colors
        self.products_tree.tag_configure('outofstock', foreground='#C04040')
        self.products_tree.tag_configure('lowstock', foreground='#DAA520')
        self.products_tree.tag_configure('instock', foreground=OLIVE_DARK)

        # Summary
        total_products = len(products)
        total_stock = sum(p[4] for p in products)
        
        summary_frame = ttk.Frame(list_frame)
        summary_frame.pack(fill='x', pady=10)
        
        ttk.Label(summary_frame, 
                 text=f"Total Products: {total_products} | Total Stock Units: {total_stock}",
                 style='Heading.TLabel').pack(side='left')

    def restock_product(self):
        """Increase stock for the selected product."""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to restock.")
            return

        # Get product ID from the selected row
        item = self.products_tree.item(selected[0])
        product_id = item['values'][0]  # ID is first column
        current_stock = item['values'][4]  # Stock is fifth column (0-indexed)
        product_name = item['values'][1]

        # Ask for quantity to add
        qty = simpledialog.askinteger("Restock Product", 
                                       f"Enter additional quantity for '{product_name}':\nCurrent stock: {current_stock}",
                                       parent=self.root, minvalue=1, maxvalue=10000)
        if qty is None or qty <= 0:
            return

        try:
            # Update stock in database
            self.db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, product_id))
            messagebox.showinfo("Success", f"Added {qty} units to '{product_name}'.\nNew stock: {current_stock + qty}")
            # Refresh the product list
            self.display_products_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restock: {str(e)}")

    # ================= SALES MANAGEMENT WITH CART =================
    def sales_management(self):
        """Display sales management interface with multi-item cart."""
        self.clear_frame()
        self.cart = []  # Reset cart when entering sales

        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', padx=30, pady=(20, 10))
        
        ttk.Label(header_frame, text="Sales Management", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="← Back to Dashboard",
                  style='Secondary.TButton',
                  command=self.show_dashboard).pack(side='right')

        # Main content: two columns - left for adding items, right for cart
        main_content = ttk.Frame(self.main_container)
        main_content.pack(fill='both', expand=True, padx=30, pady=10)

        # Left column - Add to cart form
        left_frame = ttk.Frame(main_content, style='Card.TFrame', padding=20)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        ttk.Label(left_frame, text="Add Item to Cart", 
                 style='Heading.TLabel',
                 background=BEIGE_DARK).pack(anchor='w', pady=(0, 15))

        # Product selection
        products = self.db.fetchall("SELECT id, name, price, stock FROM products WHERE stock > 0 ORDER BY name")
        if not products:
            tk.Label(left_frame, text="No products available.", bg=BEIGE_DARK, fg=OLIVE_DARK).pack()
        else:
            ttk.Label(left_frame, text="Select Product:", style='CardTitle.TLabel',
                     background=BEIGE_DARK).pack(anchor='w', pady=5)
            product_list = [f"{p[1]} (Stock: {p[3]} | ₹ {p[2]:,.2f})" for p in products]
            self.cart_product_var = tk.StringVar()
            product_cb = ttk.Combobox(left_frame, textvariable=self.cart_product_var,
                                       values=product_list, width=50, state='readonly')
            product_cb.pack(fill='x', pady=5)

            ttk.Label(left_frame, text="Quantity:", style='CardTitle.TLabel',
                     background=BEIGE_DARK).pack(anchor='w', pady=5)
            self.cart_qty_var = tk.IntVar(value=1)
            qty_spin = ttk.Spinbox(left_frame, from_=1, to=999, textvariable=self.cart_qty_var, width=20)
            qty_spin.pack(anchor='w', pady=5)

            # Add to cart button
            ttk.Button(left_frame, text="➕ Add to Cart", style='Secondary.TButton',
                       command=self.add_to_cart).pack(pady=15)

        # Right column - Cart contents
        right_frame = ttk.Frame(main_content, style='Card.TFrame', padding=20)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))

        ttk.Label(right_frame, text="Shopping Cart", 
                 style='Heading.TLabel',
                 background=BEIGE_DARK).pack(anchor='w', pady=(0, 15))

        # Cart treeview
        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill='both', expand=True)

        columns = ("Product", "Price (₹)", "Quantity", "Total (₹)")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120 if col == "Product" else 100, anchor='center')
        self.cart_tree.pack(side='left', fill='both', expand=True)

        cart_scroll = ttk.Scrollbar(cart_frame, orient='vertical', command=self.cart_tree.yview)
        cart_scroll.pack(side='right', fill='y')
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)

        # Cart total label
        self.cart_total_label = tk.Label(right_frame, text="Cart Total: ₹ 0.00",
                                         bg=BEIGE_DARK, fg=OLIVE_DARK,
                                         font=('Helvetica', 14, 'bold'))
        self.cart_total_label.pack(pady=10)

        # Cart action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="🗑️ Remove Selected", style='Secondary.TButton',
                   command=self.remove_from_cart).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧾 Generate Bill", style='Primary.TButton',
                   command=self.generate_bill).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Clear Cart", style='Secondary.TButton',
                   command=self.clear_cart).pack(side='left', padx=5)

        # Today's sales summary (below the two columns)
        self.display_todays_sales()

    def add_to_cart(self):
        """Add selected product and quantity to cart."""
        if not self.cart_product_var.get():
            messagebox.showwarning("Warning", "Please select a product.")
            return

        qty = self.cart_qty_var.get()
        if qty < 1:
            messagebox.showwarning("Warning", "Quantity must be at least 1.")
            return

        # Find selected product
        products = self.db.fetchall("SELECT * FROM products WHERE stock > 0")
        selected_text = self.cart_product_var.get()
        selected_product = None
        for p in products:
            if p[1] in selected_text:  # product name is in the string
                selected_product = p
                break

        if not selected_product:
            return

        # Check stock
        if qty > selected_product[4]:
            messagebox.showerror("Error", f"Insufficient stock! Available: {selected_product[4]}")
            return

        # Check if product already in cart
        for item in self.cart:
            if item['product_id'] == selected_product[0]:
                # Update quantity
                new_qty = item['quantity'] + qty
                if new_qty > selected_product[4]:
                    messagebox.showerror("Error", f"Total quantity in cart exceeds stock! Available: {selected_product[4]}")
                    return
                item['quantity'] = new_qty
                item['total'] = item['price'] * new_qty
                self.update_cart_display()
                return

        # New item
        total = selected_product[3] * qty
        self.cart.append({
            'product_id': selected_product[0],
            'name': selected_product[1],
            'price': selected_product[3],
            'quantity': qty,
            'total': total
        })
        self.update_cart_display()

    def update_cart_display(self):
        """Refresh the cart treeview and total."""
        # Clear tree
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        cart_total = 0
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item['name'],
                f"₹ {item['price']:,.2f}",
                item['quantity'],
                f"₹ {item['total']:,.2f}"
            ))
            cart_total += item['total']

        self.cart_total_label.config(text=f"Cart Total: ₹ {cart_total:,.2f}")

    def remove_from_cart(self):
        """Remove selected item from cart."""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return

        # Get the product_id of the selected item by matching name and price
        # (since name is unique, we can use it)
        item_values = self.cart_tree.item(selected[0], 'values')
        item_name = item_values[0]
        item_price = float(item_values[1].replace('₹', '').replace(',', '').strip())

        # Find matching item in cart
        for i, item in enumerate(self.cart):
            if item['name'] == item_name and item['price'] == item_price:
                del self.cart[i]
                break

        self.update_cart_display()

    def clear_cart(self):
        """Empty the cart."""
        self.cart = []
        self.update_cart_display()

    def generate_bill(self):
        """Process all items in cart, record sales, update stock, and show receipt."""
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return

        try:
            # Start a transaction
            self.db.conn.execute("BEGIN TRANSACTION")

            today = date.today().isoformat()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bill_items = []

            for item in self.cart:
                # Insert sale record
                self.db.execute("""
                    INSERT INTO sales (product_id, quantity, total, sale_date, sale_time) 
                    VALUES (?, ?, ?, ?, ?)
                """, (item['product_id'], item['quantity'], item['total'], today, now))

                # Update stock
                self.db.execute("""
                    UPDATE products SET stock = stock - ? WHERE id = ?
                """, (item['quantity'], item['product_id']))

                bill_items.append(item)

            # Commit transaction
            self.db.conn.commit()

            # Show receipt
            self.show_multi_item_receipt(bill_items)

            # Clear cart and refresh
            self.cart = []
            self.update_cart_display()
            self.display_todays_sales()  # Refresh today's sales

        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to process bill: {str(e)}")

    def show_multi_item_receipt(self, items):
        """Display a formatted receipt for multiple items."""
        receipt_lines = []
        receipt_lines.append("╔════════════════════════════════════════╗")
        receipt_lines.append("║         N & T RETAIL SHOP             ║")
        receipt_lines.append("║           SALES RECEIPT               ║")
        receipt_lines.append("╠════════════════════════════════════════╣")
        receipt_lines.append(f"║ Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        receipt_lines.append("╠════════════════════════════════════════╣")
        receipt_lines.append("║ Items:                                 ║")

        total_amount = 0
        for item in items:
            receipt_lines.append(f"║ {item['name'][:20]:20} x{item['quantity']:3}  ₹ {item['total']:8,.2f} ║")
            total_amount += item['total']

        receipt_lines.append("╠════════════════════════════════════════╣")
        receipt_lines.append(f"║ TOTAL:                      ₹ {total_amount:10,.2f} ║")
        receipt_lines.append("╚════════════════════════════════════════╝")
        receipt_lines.append("")
        receipt_lines.append("Thank you for your business!")

        receipt = "\n".join(receipt_lines)
        messagebox.showinfo("Bill Generated", receipt)

    def display_todays_sales(self):
        """Display today's sales summary with fallback for missing sale_time."""
        today = date.today().isoformat()
        
        # Remove old today's sales frame if exists
        for widget in self.main_container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_name() == "todays_sales_frame":
                widget.destroy()

        # Try to fetch with sale_time, fallback to id order if column missing
        try:
            sales = self.db.fetchall("""
                SELECT s.sale_time, p.name, s.quantity, s.total
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE s.sale_date = ?
                ORDER BY s.sale_time DESC
            """, (today,))
            use_sale_time = True
        except sqlite3.OperationalError:
            # sale_time column missing, fallback to id order
            sales = self.db.fetchall("""
                SELECT p.name, s.quantity, s.total
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE s.sale_date = ?
                ORDER BY s.id DESC
            """, (today,))
            use_sale_time = False

        if not sales:
            return

        # Summary frame
        summary_frame = ttk.Frame(self.main_container, style='Card.TFrame', padding=20, name="todays_sales_frame")
        summary_frame.pack(fill='both', expand=True, padx=30, pady=20)

        ttk.Label(summary_frame, text="Today's Sales", 
                 style='Heading.TLabel',
                 background=BEIGE_DARK).pack(anchor='w', pady=(0, 10))

        # Treeview for today's sales
        tree_frame = ttk.Frame(summary_frame)
        tree_frame.pack(fill='both', expand=True)

        columns = ("Time", "Product", "Quantity", "Total (₹)")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col == "Product" else 100, anchor='center')

        for sale in sales:
            if use_sale_time:
                sale_time = sale[0]
                if sale_time and len(sale_time) >= 16:
                    time_str = sale_time[11:16]  # Extract HH:MM
                else:
                    time_str = "--:--"
                product_name = sale[1]
                quantity = sale[2]
                total = sale[3]
            else:
                time_str = "--:--"
                product_name = sale[0]
                quantity = sale[1]
                total = sale[2]
                
            tree.insert("", "end", values=(
                time_str,
                product_name,
                quantity,
                f"₹ {total:,.2f}"
            ))

        tree.pack(side='left', fill='both', expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)

        # Daily total
        daily_total = sum(sale[3] if use_sale_time else sale[2] for sale in sales)
        total_label = tk.Label(summary_frame,
                              text=f"Today's Total Sales: ₹ {daily_total:,.2f}",
                              bg=BEIGE_DARK,
                              fg=OLIVE_DARK,
                              font=('Helvetica', 12, 'bold'))
        total_label.pack(pady=10)

    # ================= SALES ANALYSIS =================
    def sales_analysis(self):
        """Display sales analysis charts."""
        self.clear_frame()

        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', padx=30, pady=(20, 10))
        
        ttk.Label(header_frame, text="Sales Analysis", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="← Back to Dashboard",
                  style='Secondary.TButton',
                  command=self.show_dashboard).pack(side='right')

        # Check if sales data exists
        sales_count = self.db.fetchone("SELECT COUNT(*) FROM sales")[0]
        
        if sales_count == 0:
            # No data message
            no_data_frame = ttk.Frame(self.main_container, style='Card.TFrame', padding=50)
            no_data_frame.pack(expand=True, padx=30, pady=50)
            
            tk.Label(no_data_frame, 
                    text="📊 No Sales Data Available",
                    bg=BEIGE_DARK,
                    fg=OLIVE_DARK,
                    font=('Helvetica', 18, 'bold')).pack()
            
            tk.Label(no_data_frame,
                    text="Start making sales to see analytics!",
                    bg=BEIGE_DARK,
                    fg=OLIVE_MEDIUM,
                    font=('Helvetica', 12)).pack(pady=10)
            return

        # Create notebook for tabs
        notebook = ttk.Notebook(self.main_container)
        notebook.pack(fill='both', expand=True, padx=30, pady=20)

        # Daily sales tab
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="Daily Sales")
        self.create_daily_sales_chart(daily_frame)

        # Product performance tab
        product_frame = ttk.Frame(notebook)
        notebook.add(product_frame, text="Product Performance")
        self.create_product_performance_chart(product_frame)

        # Summary statistics
        self.display_sales_summary()

    def create_daily_sales_chart(self, parent):
        """Create daily sales chart."""
        # Fetch daily sales data
        data = self.db.fetchall("""
            SELECT sale_date, COUNT(*), SUM(total) 
            FROM sales 
            GROUP BY sale_date 
            ORDER BY sale_date DESC
            LIMIT 30
        """)

        if not data:
            ttk.Label(parent, text="No daily data available",
                     style='Heading.TLabel').pack(pady=50)
            return

        # Reverse for chronological order
        data = list(reversed(data))
        
        dates = [d[0][5:] for d in data]  # Show MM-DD only
        counts = [d[1] for d in data]
        revenues = [d[2] for d in data]

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor(BEIGE_LIGHT)

        # Revenue chart
        ax1.plot(dates, revenues, marker='o', color=OLIVE_DARK, linewidth=2, markersize=6)
        ax1.set_title('Daily Revenue', fontsize=14, color=OLIVE_DARK, fontweight='bold')
        ax1.set_xlabel('Date', color=OLIVE_MEDIUM)
        ax1.set_ylabel('Revenue (₹)', color=OLIVE_MEDIUM)
        ax1.tick_params(colors=OLIVE_MEDIUM)
        ax1.grid(True, linestyle='--', alpha=0.3, color=OLIVE_LIGHT)
        ax1.set_facecolor(BEIGE_DARK)

        # Transaction count chart
        ax2.bar(dates, counts, color=OLIVE_MEDIUM, alpha=0.8)
        ax2.set_title('Daily Transaction Count', fontsize=14, color=OLIVE_DARK, fontweight='bold')
        ax2.set_xlabel('Date', color=OLIVE_MEDIUM)
        ax2.set_ylabel('Number of Transactions', color=OLIVE_MEDIUM)
        ax2.tick_params(colors=OLIVE_MEDIUM)
        ax2.grid(True, linestyle='--', alpha=0.3, color=OLIVE_LIGHT, axis='y')
        ax2.set_facecolor(BEIGE_DARK)

        plt.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def create_product_performance_chart(self, parent):
        """Create product performance chart."""
        # Fetch product sales data
        data = self.db.fetchall("""
            SELECT p.name, SUM(s.quantity), SUM(s.total)
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY SUM(s.total) DESC
            LIMIT 10
        """)

        if not data:
            ttk.Label(parent, text="No product data available",
                     style='Heading.TLabel').pack(pady=50)
            return

        products = [d[0][:15] + "..." if len(d[0]) > 15 else d[0] for d in data]
        quantities = [d[1] for d in data]
        revenues = [d[2] for d in data]

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        fig.patch.set_facecolor(BEIGE_LIGHT)

        # Quantity bar chart
        bars1 = ax1.barh(products, quantities, color=OLIVE_DARK, alpha=0.8)
        ax1.set_title('Top Products by Quantity Sold', fontsize=14, color=OLIVE_DARK, fontweight='bold')
        ax1.set_xlabel('Quantity Sold', color=OLIVE_MEDIUM)
        ax1.tick_params(colors=OLIVE_MEDIUM)
        ax1.grid(True, linestyle='--', alpha=0.3, color=OLIVE_LIGHT, axis='x')
        ax1.set_facecolor(BEIGE_DARK)

        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}', ha='left', va='center', fontweight='bold')

        # Revenue pie chart
        colors = [OLIVE_DARK, OLIVE_MEDIUM, OLIVE_LIGHT, BEIGE_DARK, ACCENT]
        wedges, texts, autotexts = ax2.pie(revenues, labels=products, 
                                           autopct='%1.1f%%',
                                           colors=colors[:len(products)],
                                           textprops={'color': OLIVE_DARK, 'fontweight': 'bold'})
        
        # Style percentage labels
        for autotext in autotexts:
            autotext.set_color(WHITE)
            autotext.set_fontweight('bold')

        ax2.set_title('Revenue Distribution by Product', fontsize=14, color=OLIVE_DARK, fontweight='bold')

        plt.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def display_sales_summary(self):
        """Display summary statistics."""
        # Fetch summary statistics
        stats = self.db.fetchone("""
            SELECT 
                COUNT(DISTINCT sale_date) as days,
                COUNT(*) as transactions,
                SUM(quantity) as items_sold,
                SUM(total) as total_revenue,
                AVG(total) as avg_transaction,
                MAX(total) as max_transaction
            FROM sales
        """)

        if not stats or stats[0] == 0:
            return

        # Summary frame
        summary_frame = ttk.Frame(self.main_container, style='Card.TFrame', padding=20)
        summary_frame.pack(fill='x', padx=30, pady=(0, 20))

        ttk.Label(summary_frame, text="Sales Summary", 
                 style='Heading.TLabel',
                 background=BEIGE_DARK).pack(anchor='w', pady=(0, 15))

        # Create metrics grid
        metrics = [
            ("📅 Active Days", stats[0]),
            ("💰 Total Transactions", stats[1]),
            ("📦 Items Sold", stats[2]),
            ("💵 Total Revenue", f"₹ {stats[3]:,.2f}"),
            ("📊 Avg Transaction", f"₹ {stats[4]:,.2f}" if stats[4] else "₹ 0.00"),
            ("🏆 Max Transaction", f"₹ {stats[5]:,.2f}" if stats[5] else "₹ 0.00")
        ]

        metrics_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        metrics_frame.pack(fill='x')

        for i, (label, value) in enumerate(metrics):
            metric_card = tk.Frame(metrics_frame, bg=WHITE, relief='raised', bd=1)
            metric_card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            tk.Label(metric_card, text=label, bg=WHITE, 
                    fg=OLIVE_MEDIUM, font=('Helvetica', 10)).pack(pady=(10, 5))
            
            tk.Label(metric_card, text=value, bg=WHITE,
                    fg=OLIVE_DARK, font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))

            metrics_frame.grid_columnconfigure(i%3, weight=1)


# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    root = tk.Tk()
    app = RetailApp(root)
    
    # Make window resizable with minimum size
    root.minsize(1000, 600)
    
    # Start the application
    root.mainloop()