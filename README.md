# Razorpay ₹10 payment integration (simple)

This adds a minimal Flask backend and frontend to sell PDFs using Razorpay checkout.

Quick start:

1. Install dependencies

   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Set Razorpay credentials (you will get these from Razorpay dashboard)

   export RAZORPAY_KEY_ID="your_key_id"
   export RAZORPAY_KEY_SECRET="your_key_secret"

3. Add your PDFs into the `pdfs/` folder and update `products.json` with entries like:

   {
     "id": "pdf1",
     "title": "My Notes",
     "filename": "mynotes.pdf",
     "amount": 1000
   }

   Amount is in paise (1000 = ₹10).

4. Run the app

   python app.py

5. Open http://localhost:5000 and click Buy. After a successful payment you'll be redirected to the download.

Notes:
- This is a simple example for development and demonstration. For production:
  - Run behind a proper WSGI server (gunicorn)
  - Use HTTPS
  - Securely store your Razorpay keys (do not commit them to the repo)
  - Consider expiring download links or using signed URLs
