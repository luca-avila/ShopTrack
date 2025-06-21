from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# --- DATABASE SETUP ---
# Connect to SQLite database (creates file if it doesn't exist)
connection = sqlite3.connect('store.db')
cursor = connection.cursor()

# Create 'products' table: stores product info
command1 = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)'''
cursor.execute(command1)

# Create 'history' table: stores sales history
command2 = '''
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
)'''
cursor.execute(command2)

# --- ROUTES ---

@app.route('/')
def index():
    # Home page: summary/dashboard (e.g., stats, quick links)
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def products():
    # Fetch products from the database and send to template
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('products.html', products=products)

@app.route('/sales')
def sales():
    # Register a new sale
    # TODO: Show form to select product and quantity, update stock/history
    return render_template('sales.html')

@app.route('/reports')
def reports():
    # Show sales reports/history
    # TODO: Query and display sales data, possibly with filters
    return render_template('reports.html')

# --- ADDITIONAL FUNCTIONALITY TO IMPLEMENT ---
# - Add product: form to add new products (POST)
# - Edit product: form to update product info (GET/POST)
# - Delete product: remove product from DB
# - Register sale: decrease stock, add entry to history
# - View sales history: list/filter sales
# - Generate reports: sales per product, date range, etc.
# - Input validation and error handling
# - Use Flask's g and context for DB connections (for production apps)
# - Flash messages for user feedback

if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)