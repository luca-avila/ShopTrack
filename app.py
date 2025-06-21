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
        type TEXT NOT NULL CHECK(type IN('BUY', 'SELL')),
        price REAL NOT NULL,
        sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )'''
    cursor.execute(command2)

# --- ROUTES ---

@app.route('/')
def index():
    return redirect('/products')

@app.route('/products', methods=['GET'])
def products():
    # Fetch products from the database and send to template
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('products.html', products=products)

@app.route('/sell', methods=['POST', 'GET'])
def sell():
    if request.method == 'GET':
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
    stock = db.execute('SELECT stock, price FROM products WHERE id = ?', (product_id,)).fetchone()
    if not stock:
        return "Product not found", 404
    if stock['stock'] < quantity:
        return "Insufficient stock", 400

    current_price = stock['price']
    
    # Update stock and history
    db.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
    db.execute(
        'INSERT INTO history (product_id, quantity, type, price) VALUES (?, ?, ?, ?)',
        (product_id, quantity, 'SELL', current_price)
    )
    db.commit()

    return redirect('/products')

@app.route('/restock', methods=['POST', 'GET'])
def restock():
    if request.method == 'GET':
        db = get_db()
        products = db.execute('SELECT * FROM products').fetchall()
        return render_template('restock.html', products=products)
    
    product_id = request.form.get('product_id')
    if not product_id:
        return "Product ID is required", 400
    
    quantity = request.form.get('quantity', type=int)
    if not quantity or quantity <= 0:
        return "Invalid quantity", 400
    
    db = get_db()
    product = db.execute('SELECT price FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        return "Product not found", 404
    current_price = product['price']

    db.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (quantity, product_id))
    db.execute(
        'INSERT INTO history (product_id, quantity, type, price) VALUES (?, ?, ?, ?)',
        (product_id, quantity, 'BUY', current_price)
    )
    db.commit()

    return redirect('/products')

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    if request.method == 'GET':
        return render_template("add_product.html")
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price', type=float)
    stock = request.form.get('stock', type=int)
    if not name or price is None or stock is None:
        return "All fields are required", 400
    if price < 0 or stock < 0:
        return "Price and stock must be non-negative", 400
    db = get_db()
    db.execute(
        'INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)',
        (name, description, price, stock)
    )
    db.commit()
    new_product = db.execute('SELECT id FROM products WHERE name = ?', (name,)).fetchone()
    if not new_product:
        return "Product not found", 404
    product_id = new_product['id']
    if stock > 0:
        db.execute(
            'INSERT INTO history (product_id, quantity, type, price) VALUES (?, ?, ?, ?)',
            (product_id, stock, 'BUY', price)
        )
        db.commit()
    return redirect('/products')

@app.route('/delete_product', methods=['GET', 'POST'])
def delete_product():

    # Get products and send them to the html
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()

    if request.method == 'GET':
        return render_template('delete_product.html', products = products)

    product_id = request.form.get('product_id')
    if not product_id:
        return "Please select a product", 404
    
    db.execute('DELETE FROM products WHERE id = ?', (product_id))
    db.commit()

    return redirect('/products')

@app.route('/reports', methods=['GET'])
def reports():
    db = get_db()
    sales = db.execute('''
        SELECT products.name, history.price, history.quantity, history.sale_date
        FROM history
        JOIN products ON history.product_id = products.id
        WHERE history.type = ?
        ORDER BY history.sale_date DESC
    ''', ('SELL',)).fetchall()

    restocks = db.execute('''
        SELECT products.name, history.price, history.quantity, history.sale_date
        FROM history
        JOIN products ON history.product_id = products.id
        WHERE history.type = ?
        ORDER BY history.sale_date DESC
    ''', ('BUY',)).fetchall()

    return render_template('reports.html', sales=sales, restocks=restocks)

@app.route('/edit_price', methods=['GET', 'POST'])
def edit_price():
    if request.method == 'GET':
        db = get_db()
        products = db.execute('SELECT * FROM products').fetchall()
        return render_template('edit_price.html', products=products)

    product_id = request.form.get('product_id')
    new_price = request.form.get('new_price', type=float)
    
    if not product_id or new_price is None:
        return "Product ID and new price are required", 400
    if new_price < 0:
        return "Price must be non-negative", 400

    db = get_db()
    db.execute('UPDATE products SET price = ? WHERE id = ?', (new_price, product_id))
    db.commit()

    return redirect('/products')

# --- ADDITIONAL FUNCTIONALITY TO IMPLEMENT ---
# - Improve input validation and error handling
# - Add OOP structure for better organization
# - Generate reports: sales per product, date range, etc.
# - Flash messages for user feedback
# - Implement user authentication for admin features
# - Add javascript for dynamic UI updates 

if __name__ == '__main__':
    # Run the Flask development server
    app.run(debug=True)
