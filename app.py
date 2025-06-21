from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 1. Connect to SQLite database
connection = sqlite3.connect('store.db')
cursor = connection.cursor()

# Create tables if they don't exist
command1 = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)'''
cursor.execute(command1)

command2 = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)'''
cursor.execute(command2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    app.run(debug=True)