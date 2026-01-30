# ShopBot AI - Complete Project

🤖 AI-powered 24/7 customer support for Shopify stores

## 📁 Project Structure

```
shopbot-ai-complete/
│
├── backend/              ← Python FastAPI server (READY TO RUN!)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── routes/
│   │       └── chat.py  ← AI chatbot logic
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md        ← Backend setup instructions
│
├── frontend/             ← React app (COMING SOON)
│   └── README.md
│
├── website/              ← Marketing pages (READY!)
│   ├── landing-page.html
│   └── chatbot-demo.html
│
├── docs/
│   └── technical-architecture.md
│
└── README.md            ← You are here!
```

## 🚀 Quick Start

### Option 1: Test the Marketing Pages (Instant)

1. Open `website/landing-page.html` in your browser
2. Open `website/chatbot-demo.html` in your browser

These work immediately - just double-click!

### Option 2: Run the Backend (5 minutes)

**Requirements:**
- Python 3.11+
- Claude API key (get free $5 credit at https://console.anthropic.com)

**Steps:**

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 6. Run!
python -m app.main
```

Then open: **http://localhost:8000/docs**

Try the chatbot API in the interactive docs!

### Option 3: Deploy Marketing Site (5 minutes)

1. Go to https://netlify.com
2. Drag the `website/` folder
3. Get a live URL!

Share it with potential customers.

## 📖 Documentation

- **Backend Setup:** See `backend/README.md`
- **Technical Architecture:** See `docs/technical-architecture.md`
- **Frontend:** Coming soon (we'll build React app next)

## 🎯 What Works Right Now

✅ **Backend API**
- AI chatbot powered by Claude
- Conversation history
- Intent detection
- Health checks
- API documentation

✅ **Marketing Website**
- Professional landing page
- Working chatbot demo
- Ready to deploy

❌ **Not Yet Built**
- Frontend React app (admin dashboard + chat widget)
- Database persistence
- User authentication
- Shopify integration
- Payment processing

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- Claude API (Anthropic)
- PostgreSQL (coming)
- Redis (coming)

**Frontend:** (coming)
- React + TypeScript
- Tailwind CSS
- Socket.io

**Deployment:**
- Backend: Railway/Render
- Frontend: Vercel
- Marketing: Netlify

## 📊 Business Model

- **Price:** $79/month per store
- **Target:** Small Shopify stores ($10k-100k/month revenue)
- **Infrastructure Cost:** ~$50-100/month
- **Break-even:** 2-3 customers

## 🔜 Next Steps

1. **Get API key** from Anthropic
2. **Run the backend** and test the chatbot
3. **Deploy landing page** to Netlify
4. **Share with 5-10 Shopify stores** for feedback
5. **Build React frontend** (we'll do this together)
6. **Add database + auth**
7. **Integrate with Shopify**
8. **Launch!**

## 💡 Development Roadmap

### Week 1-2: MVP
- [x] Backend API structure
- [x] AI chatbot logic
- [x] Marketing pages
- [ ] React frontend
- [ ] Database setup
- [ ] Basic auth

### Week 3: Beta
- [ ] Shopify integration
- [ ] Payment (Stripe)
- [ ] Deploy to production
- [ ] 3-5 beta users

### Month 2: Growth
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] Multi-language
- [ ] 25+ paying customers

## 🤝 Support

Questions? Issues? Want help building the next part?

Just ask! We're building this together step-by-step.

## 📝 License

Your project - build it, sell it, make money! 💰
