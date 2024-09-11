from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Sample product data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "image": "images/laptop.jpg", "description": "Powerful laptop for all your needs."},
    {"id": 2, "name": "Smartphone", "price": 499.99, "image": "images/smartphone.jpg", "description": "Latest smartphone with advanced features."},
    {"id": 3, "name": "Headphones", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones."},
    {"id": 4, "name": "Headphones1", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones1."},
    {"id": 5, "name": "Headphones2", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones2."},
    {"id": 6, "name": "Headphones3", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones3."},
    {"id": 7, "name": "Headphones4", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones4."},
    {"id": 8, "name": "Headphones5", "price": 99.99, "image": "images/headphones.jpg", "description": "High-quality wireless headphones5."},
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/cart', methods=['POST'])
def cart():
    cart_items = request.json
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return jsonify({"total": total})

@app.route('/transaction_request', methods=['POST'])
def transaction_request():
    transaction_data = request.json
    success = True
    message = "Transaction processed successfully"

    # Check if the transaction data is valid
    if not isinstance(transaction_data, list):
        success = False
        message = "Invalid transaction data format"

    for item in transaction_data:
        if not isinstance(item, dict) or 'id' not in item or 'quantity' not in item:
            success = False
            message += f";Invalid item format:{type(item)}"
        
        if not isinstance(item['id'], int) or not item['id'] > 0:
            success = False
            message += f";Invalid item ID:{item['id']}"
        
        if not isinstance(item['quantity'], int) or not item['quantity'] > 0:
            success = False
            message += f";Invalid item quantity for item ID {item['id']}:{item['quantity']}"
    
    if message.startswith(";"):
        message = message[1:]

    return jsonify({"success": success, "message": message})

if __name__ == '__main__':
    app.run(debug=True)