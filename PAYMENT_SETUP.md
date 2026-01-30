# Payment & Subscription Setup Guide

This guide shows you how to set up Stripe payments, create promo codes, and handle subscriptions.

## 🎯 What's Included

Your backend now has:
- ✅ User registration
- ✅ Stripe checkout integration
- ✅ Promo code system
- ✅ Subscription management
- ✅ Webhook handling
- ✅ 14-day free trial
- ✅ SQLite database (easy for development)

---

## Step 1: Get Your Stripe Keys (10 minutes)

### 1.1 Create Stripe Account
1. Go to https://stripe.com
2. Click "Start now" (free)
3. Sign up with your email
4. Complete verification (they'll ask for business info later, but you can use test mode now)

### 1.2 Get API Keys
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Copy your **Secret key** (starts with `sk_test_`) - click "Reveal test key"

### 1.3 Create a Product & Price
1. Go to https://dashboard.stripe.com/test/products
2. Click "+ Add product"
3. **Name:** ShopBot AI - Basic Plan
4. **Description:** AI-powered 24/7 customer support
5. **Pricing:** 
   - Type: Recurring
   - Price: $79.00
   - Billing period: Monthly
6. Click "Save product"
7. **Copy the Price ID** (starts with `price_`) - you'll need this!

### 1.4 Set Up Webhook (for production later)
1. Go to https://dashboard.stripe.com/test/webhooks
2. Click "+ Add endpoint"
3. URL: `https://your-api.com/api/payment/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. **Copy the Webhook secret** (starts with `whsec_`)

---

## Step 2: Configure Your Backend

### 2.1 Update .env File

Open `backend/.env` and add your Stripe keys:

```bash
# Stripe Keys
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_PRICE_ID_BASIC=price_YOUR_PRICE_ID_HERE

# Make sure you also have these:
ANTHROPIC_API_KEY=your_claude_key
SECRET_KEY=your_generated_secret_key_here
DATABASE_URL=sqlite:///./shopbot.db
```

### 2.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2.3 Run the Server

```bash
python -m app.main
```

You should see:
```
🚀 Starting ShopBot AI Backend...
✅ Database initialized!
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Step 3: Create Promo Codes for Your First Customers

### Option A: Using the API (Recommended)

Go to http://localhost:8000/docs and find `POST /api/payment/admin/create-promo`

**Example promo codes to create:**

**1. LAUNCH50 - 50% off for first 10 customers**
```json
{
  "code": "LAUNCH50",
  "discount_value": 50,
  "description": "50% off for first 10 early adopters",
  "max_uses": 10,
  "duration_months": 3,
  "valid_days": 90
}
```

**2. EARLYBIRD - 30% off for first month**
```json
{
  "code": "EARLYBIRD",
  "discount_value": 30,
  "description": "30% off first month",
  "max_uses": 50,
  "duration_months": 1,
  "valid_days": 60
}
```

**3. FOUNDER100 - 100% off (free) for founding customers**
```json
{
  "code": "FOUNDER100",
  "discount_value": 100,
  "description": "Free for founding customers",
  "max_uses": 5,
  "duration_months": 6,
  "valid_days": 30
}
```

### Option B: Using Python Script

Create a file `create_promos.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

promos = [
    {
        "code": "LAUNCH50",
        "discount_value": 50,
        "description": "50% off for early adopters",
        "max_uses": 10,
        "duration_months": 3,
        "valid_days": 90
    },
    {
        "code": "EARLYBIRD",
        "discount_value": 30,
        "description": "30% off first month",
        "max_uses": 50,
        "duration_months": 1,
        "valid_days": 60
    }
]

for promo in promos:
    response = requests.post(f"{BASE_URL}/api/payment/admin/create-promo", params=promo)
    print(response.json())
```

Run it:
```bash
python create_promos.py
```

---

## Step 4: Test the Complete Flow

### 4.1 Test Registration with Promo Code

```bash
curl -X POST "http://localhost:8000/api/payment/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "full_name": "Test User",
    "company_name": "Test Store",
    "shopify_store_url": "teststore.myshopify.com",
    "promo_code": "LAUNCH50"
  }'
```

### 4.2 Test Promo Code Validation

```bash
curl -X POST "http://localhost:8000/api/payment/validate-promo" \
  -H "Content-Type: application/json" \
  -d '{"code": "LAUNCH50"}'
```

### 4.3 Test Checkout Flow

1. Register a user (step 4.1)
2. Get the checkout URL:
```bash
curl -X POST "http://localhost:8000/api/payment/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{
    "promo_code": "LAUNCH50"
  }'
```
3. Open the returned `checkout_url` in your browser
4. Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
   - Any ZIP code

---

## Step 5: Share Promo Codes with Early Customers

### Email Template:

```
Subject: You're invited! 50% off ShopBot AI 🤖

Hey [Name],

Thanks for your interest in ShopBot AI!

As one of our first customers, I'm offering you 50% off for the first 3 months.

👉 Use code: LAUNCH50

Here's what you get:
• 24/7 AI customer support for your Shopify store
• Instant answers to customer questions
• Order tracking automation
• 14-day free trial
• Only $39.50/month (normally $79) for 3 months

Sign up here: [your-site-url]

This offer is limited to the first 10 customers!

Questions? Just reply to this email.

Thanks,
[Your Name]
```

---

## Step 6: Monitor Everything

### Check Promo Code Usage

```python
# In Python shell or script
from app.database import SessionLocal
from app.models import PromoCode

db = SessionLocal()
promos = db.query(PromoCode).all()

for promo in promos:
    print(f"{promo.code}: {promo.times_used}/{promo.max_uses or 'unlimited'} uses")
```

### Check Subscriptions

Go to https://dashboard.stripe.com/test/subscriptions

You'll see:
- All subscriptions
- Trial status
- Payment history
- Customer details

---

## Production Deployment (When Ready)

### Switch to Live Mode

1. In Stripe dashboard, toggle from "Test mode" to "Live mode"
2. Get new API keys (live keys start with `pk_live_` and `sk_live_`)
3. Create products again in live mode
4. Update `.env` with live keys
5. Set up webhook endpoint with your production URL

### Security Checklist

- [ ] Use environment variables (never commit keys to Git)
- [ ] Enable HTTPS on your domain
- [ ] Set up proper database (PostgreSQL, not SQLite)
- [ ] Add admin authentication to promo code creation
- [ ] Enable Stripe fraud detection
- [ ] Set up email notifications
- [ ] Add logging and monitoring

---

## Troubleshooting

**Database errors?**
```bash
# Delete and recreate database
rm shopbot.db
python -m app.main
```

**Stripe test card not working?**
- Make sure you're in test mode
- Use card: 4242 4242 4242 4242
- Check https://stripe.com/docs/testing for more test cards

**Promo code not applying?**
- Check if it's expired (valid_until date)
- Check if max_uses reached
- Make sure code is uppercase

**Webhook not receiving events?**
- Use `stripe listen --forward-to localhost:8000/api/payment/webhook` for local testing
- Check webhook secret matches your .env

---

## What's Next?

Now that payments work, you can:

1. **Build the frontend signup form** (React)
2. **Connect the frontend to these endpoints**
3. **Launch and get your first customers!**
4. **Scale and iterate based on feedback**

The hard parts are done - payments, subscriptions, promos all work! 🎉
