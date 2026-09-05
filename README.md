# Deploying to Heroku

Quick steps to deploy this Flask app to Heroku (easy):

1. Install the Heroku CLI and login:

   https://devcenter.heroku.com/articles/heroku-cli

   heroku login

2. From the repo root, create a Heroku app (or use the dashboard):

   heroku create your-app-name

   This will create an app at https://your-app-name.herokuapp.com

3. Set environment variables (Config Vars) on Heroku (either via CLI or the dashboard):

   heroku config:set RAZORPAY_KEY_ID="<your_key_id>" RAZORPAY_KEY_SECRET="<your_key_secret>" RAZORPAY_WEBHOOK_SECRET="<your_webhook_secret>"

   - If you are only using razorpay.me links and webhooks, you only need RAZORPAY_WEBHOOK_SECRET. RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are only needed for automated Checkout flows.

4. Push the branch to Heroku / Deploy:

   # If your local git remote is set to Heroku
   git push heroku add-razorpay-payment:main

   Or connect the GitHub repo to Heroku via dashboard and choose the add-razorpay-payment branch to deploy.

5. Configure the Razorpay webhook URL:

   In Razorpay dashboard -> Webhooks, set the webhook URL to:

     https://your-app-name.herokuapp.com/webhook/razorpay

   Content type: application/json
   Webhook Secret: use the same secret you set in RAZORPAY_WEBHOOK_SECRET

6. (Optional) Upload PDFs and products.json updates:

   - Add your PDF files to the `pdfs/` folder and add entries to `products.json` with the `filename`, `id`, `title`, `amount` and optional `payment_link` fields.
   - Commit & push changes to the branch and redeploy.

Notes
- Heroku's filesystem is ephemeral. Files added to /pdfs in the repo at build time will be present, but any runtime uploads will be lost on dyno restart. For production, store PDFs in S3 and update the download flow to serve from S3.
- Heroku free tier may sleep your dyno; use a paid dyno for consistent uptime.

Alternative (quick testing): Use ngrok locally for webhook testing (see README).