from flask import Flask, render_template, jsonify, request, send_from_directory, abort, url_for
import os
import json
import sqlite3
import uuid

import razorpay

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(APP_DIR, "pdfs")
PRODUCTS_FILE = os.path.join(APP_DIR, "products.json")
DB_FILE = os.path.join(APP_DIR, "payments.db")

app = Flask(__name__)

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print("WARNING: RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are not set. Set them as environment variables.")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID or "", RAZORPAY_KEY_SECRET or ""))

# Ensure pdfs dir exists
os.makedirs(PDF_DIR, exist_ok=True)

# Load products
if not os.path.exists(PRODUCTS_FILE):
    # Create a simple example products.json
    example = [
        {"id": "pdf1", "title": "Sample PDF", "filename": "sample.pdf", "amount": 1000}
    ]
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(example, f, indent=2)

with open(PRODUCTS_FILE, "r") as f:
    PRODUCTS = {p["id"]: p for p in json.load(f)}

# Simple sqlite for storing successful payments
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            product_id TEXT,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            razorpay_signature TEXT,
            amount INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    # Pass products and key id for checkout
    products = list(PRODUCTS.values())
    return render_template("index.html", products=products, razorpay_key_id=RAZORPAY_KEY_ID)

@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if not product_id or product_id not in PRODUCTS:
        return jsonify({"error": "Invalid product_id"}), 400

    product = PRODUCTS[product_id]
    amount = int(product.get("amount", 1000))

    # Create Razorpay order
    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": str(uuid.uuid4()),
        "payment_capture": 1,
    })

    return jsonify({
        "order_id": order.get("id"),
        "amount": amount,
        "currency": order.get("currency", "INR"),
        "product": {"id": product_id, "title": product.get("title")}
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json() or {}
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")
    product_id = data.get("product_id")

    if not (razorpay_payment_id and razorpay_order_id and razorpay_signature and product_id):
        return jsonify({"error": "Missing parameters"}), 400

    # Verify signature
    params = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params)
    except Exception as e:
        return jsonify({"error": "Signature verification failed", "message": str(e)}), 400

    # Record payment
    payment_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (id, product_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, amount) VALUES (?, ?, ?, ?, ?, ?)",
        (payment_id, product_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, PRODUCTS[product_id]["amount"]),
    )
    conn.commit()
    conn.close()

    download_url = url_for("download", product_id=product_id, payment_id=payment_id, _external=True)
    return jsonify({"success": True, "download_url": download_url})

@app.route("/download/<product_id>")
def download(product_id):
    payment_id = request.args.get("payment_id")
    if not payment_id:
        abort(403)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM payments WHERE id=? AND product_id=?", (payment_id, product_id))
    row = cur.fetchone()
    conn.close()

    if not row:
        abort(403)

    product = PRODUCTS.get(product_id)
    if not product:
        abort(404)

    filename = product.get("filename")
    return send_from_directory(PDF_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    # Development server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
