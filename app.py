from flask import Flask, render_template, request, redirect, g
import sqlite3

app = Flask(__name__)

DATABASE = 'store.db'

# --- DATABASE CONNECTION HELPERS ---

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- DATABASE SETUP (run once at startup) ---
with sqlite3.connect(DATABASE) as connection:
    cursor = connection.cursor()
    command1 = '''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )'''
    cursor.execute(command1)

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
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('products.html', products=products)

@app.route('/reports')
def reports():
    # Show sales reports/history
    # TODO: Query and display sales data, possibly with filters
    return render_template('reports.html')


@app.route('/sell', methods=['POST', 'GET'])
def sell():
    # Handle sale submission
    if request.method == 'GET':
        # Render form to select product and quantity
        db = get_db()
        products = db.execute('SELECT * FROM products').fetchall()
        return render_template('sell.html', products=products)
    
    # Validate and process the sale
    product_id = request.form.get('product_id')
    if not product_id:
        return "Product ID is required", 400
    
    quantity = request.form.get('quantity', type=int)
    if not quantity or quantity <= 0:
        return "Invalid quantity", 400
    
    db = get_db()
    stock = db.execute('SELECT stock FROM products WHERE id = ?', (product_id,)).fetchone()
    if not stock:
        return "Product not found", 404
    if stock['stock'] < quantity:
        return "Insufficient stock", 400
    
    # Update stock and history
    db.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
    db.execute('INSERT INTO history (product_id, quantity) VALUES (?, ?)', (product_id, quantity))
    db.commit()

    return redirect('/products')


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