import sqlite3
import json
import os

from pathlib import Path
from flaskwebgui import FlaskUI
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

WORKING_DIR =  Path.home() / "Documents" / "Serendib Color Formular"
os.makedirs(WORKING_DIR, exist_ok=True)

DB_PATH = WORKING_DIR / "formulas.db"

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create a table for all formula data with a JSON field for table data
    c.execute('''
        CREATE TABLE IF NOT EXISTS formulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            code TEXT,
            color_name TEXT,
            product TEXT,
            base TEXT,
            can_size TEXT,
            table_data TEXT  -- JSON field to store table data
        )
    ''')
    conn.commit()
    conn.close()

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the "New" entry form
@app.route('/new')
def new_entry():
    # Provide an empty form with no pre-filled data
    table_data = []  # No data for new entries
    return render_template('edit_formula.html', table_data=table_data, customer='', code='', color_name='', 
                           product='', base='', can_size='', formula_id=None)


# Route for saving the formula (create new or update existing)
@app.route('/save', methods=['POST'])
def save_formula():
    formula_id = request.form.get('formula_id')  # Get the formula ID if editing

    # Get form data
    customer = request.form['customer']
    code = request.form['code']
    color_name = request.form['color-name']
    product = request.form['product']
    base = request.form['base']
    can_size = request.form['can-size']

    # Get table data (multiple rows)
    colors = ["TW", "LB", "BU", "MYX", "OY", "QR", "SPARE", "YOX", "QV", "UO", "PB", "PG", "ROX"]
    grs = request.form.getlist('gr[]')
    sgs = request.form.getlist('sg[]')
    mls = request.form.getlist('ml[]')
    dp_ozs = request.form.getlist('dp_oz[]')
    roundeds = request.form.getlist('rounded[]')

    # Create a list of dictionaries to store each row of table data
    table_data = []
    for i in range(len(colors)):
        if colors[i]:  # Only add rows that have a color value
            row = {
                'color': colors[i],
                'gr': grs[i],
                'sg': sgs[i],
                'ml': mls[i],
                'dp_oz': dp_ozs[i],
                'rounded': roundeds[i]
            }
            table_data.append(row)

    # Convert table data to JSON format
    table_data_json = json.dumps(table_data)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # If formula_id is provided, update the existing entry
    if formula_id != 'None':
        c.execute('''
            UPDATE formulas
            SET customer = ?, code = ?, color_name = ?, product = ?, base = ?, can_size = ?, table_data = ?
            WHERE id = ?
        ''', (customer, code, color_name, product, base, can_size, table_data_json, int(formula_id)))
    else:
        # Otherwise, insert a new entry
        c.execute('''
            INSERT INTO formulas (customer, code, color_name, product, base, can_size, table_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer, code, color_name, product, base, can_size, table_data_json))

    conn.commit()
    conn.close()

    # Return a JSON response to the client
    return jsonify({"status": "success", "message": "Formula saved successfully"})


# Route for handling search requests
@app.route('/search')
def search():
    query = request.args.get('q', '')  # Get the search query from the URL parameter

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # SQL query to search relevant fields
    c.execute('''
        SELECT id, customer, code, color_name, product, base, can_size 
        FROM formulas 
        WHERE customer LIKE ? OR code LIKE ? OR color_name LIKE ? 
        OR product LIKE ? OR base LIKE ? OR can_size LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))

    results = c.fetchall()
    conn.close()

    # Return the search results as JSON
    return jsonify(results)

# Route to handle the editing of a formula
# Route to handle the editing of a formula
@app.route('/edit_formula/<int:formula_id>')
def edit_formula(formula_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch the formula data based on the provided formula ID
    c.execute('SELECT * FROM formulas WHERE id = ?', (formula_id,))
    formula = c.fetchone()
    conn.close()

    if formula:
        # Extract data
        customer, code, color_name, product, base, can_size, table_data_json = formula[1:]
        table_data = json.loads(table_data_json)  # Convert JSON data back to Python dictionary
        
        # Render the edit formula page with the data
        return render_template('edit_formula.html', customer=customer, code=code, color_name=color_name, 
                               product=product, base=base, can_size=can_size, table_data=table_data, formula_id=formula_id)
    else:
        return "Formula not found", 404

# Initialize the database before the app starts
if __name__ == '__main__':
    init_db()
    ui = FlaskUI(app=app, width=1920, height=1024, server="flask")
    ui.run()  # Run the app in debug mode