# Razorpay ₹10 payment integration (simple)

This adds a minimal Flask backend and frontend to sell PDFs using Razorpay checkout or razorpay.me links.

Two payment modes are supported:

- Automated Checkout (recommended): uses Razorpay API keys to create orders and verify signatures. Configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET as environment variables and create products in products.json without a payment_link.

- Payment Link mode (no API keys required): use a razorpay.me link (like https://razorpay.me/@zubyanlearningcircle) and set the `payment_link` field on a product. The frontend will open the link in a new tab. After completing payment, the buyer should click "I have paid" and paste their Razorpay payment id (e.g., pay_XXXX) to get the download. This is a simple user-driven flow and does not automatically verify the payment with Razorpay.

Quick start:

1. Install dependencies

   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. If using Automated Checkout, set Razorpay credentials (you will get these from Razorpay dashboard):

   export RAZORPAY_KEY_ID="your_key_id"
   export RAZORPAY_KEY_SECRET="your_key_secret"

3. Add your PDFs into the `pdfs/` folder and update `products.json` with entries like:

   {
     "id": "pdf1",
     "title": "My Notes",
     "filename": "mynotes.pdf",
     "amount": 1000,
     "payment_link": "https://razorpay.me/@zubyanlearningcircle"
   }

   Amount is in paise (1000 = ₹10). If `payment_link` is present the UI will use the payment link mode for that product.

4. Run the app

   python app.py

5. Open http://localhost:5000 and click Pay. For payment link products: the payment page opens in a new tab and then use "I have paid" to paste the payment id and download.

Notes:
- This is a simple example for development and demonstration. For production:
  - Run behind a proper WSGI server (gunicorn)
  - Use HTTPS
  - Securely store your Razorpay keys (do not commit them to the repo)
  - Consider expiring download links or using signed URLs
  - If you want automatic verification with payment links, provide API keys and use Razorpay webhooks / Order APIs to verify server-side.
