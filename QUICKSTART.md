# ⚡ QUICKSTART - Get Running in 5 Minutes

## Step 1: Get Your API Key (2 min)

1. Go to https://console.anthropic.com
2. Sign up (free $5 credit)
3. Go to "API Keys"
4. Click "Create Key"
5. **Copy the key** (you'll need it in a moment)

## Step 2: Setup Backend (3 min)

Open terminal in VS Code:

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies (this takes ~1 minute)
pip install -r requirements.txt

# Create config file
cp .env.example .env
```

**Edit .env file:**
Open `backend/.env` in VS Code and change this line:
```
ANTHROPIC_API_KEY=your_claude_api_key_here
```

Paste your actual API key there.

Also generate a secret key:
```bash
# Run this in terminal:
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste it in .env as SECRET_KEY
```

## Step 3: Run It! (30 sec)

```bash
# Make sure you're in backend/ folder with venv activated
python -m app.main
```

You should see:
```
🚀 Starting ShopBot AI Backend...
INFO: Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test It!

Open your browser:

**http://localhost:8000/docs**

You'll see interactive API documentation.

### Try the Chatbot:

1. Click on `POST /api/chat/demo`
2. Click "Try it out"
3. Replace the example with:
```json
{
  "message": "What's your return policy?",
  "conversation_history": []
}
```
4. Click "Execute"
5. See the AI response! 🎉

### Try More Questions:

- "Do you ship internationally?"
- "What sizes do you have?"
- "How long does shipping take?"
- "Can I return an item?"

The AI knows all about the demo store and answers intelligently!

## 🎉 Success!

Your AI chatbot backend is running!

## What's Next?

### Option A: Deploy the Landing Page
1. Go to https://netlify.com
2. Drag the `website/` folder
3. Share the URL with potential customers

### Option B: Build the Frontend
Ask for help building the React chat widget and admin dashboard!

### Option C: Test More Features
Try the other endpoints in the API docs:
- `/api/chat/detect-intent` - See intent detection
- `/health` - Check system status

## Troubleshooting

**"Module not found" errors?**
→ Make sure venv is activated and you ran `pip install -r requirements.txt`

**"Invalid API key"?**
→ Check your `.env` file has the correct `ANTHROPIC_API_KEY`

**Port 8000 already in use?**
→ Kill the other process or change port in `app/main.py`

**Still stuck?**
→ Check `backend/README.md` for detailed troubleshooting

---

That's it! You now have a working AI customer support backend! 🚀
