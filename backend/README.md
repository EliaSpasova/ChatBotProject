# ShopBot AI Backend

AI-powered customer support API for e-commerce stores.

## Quick Start

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
```

**Required:**
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

**Optional (for now):**
- `DATABASE_URL` - We'll add database later
- `REDIS_URL` - We'll add Redis later

### 3. Run the Server

```bash
# From the backend/ directory
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

### 4. Test It!

Open your browser and go to:
- http://localhost:8000 - Should show "ShopBot AI API is running"
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/health - Health check

## API Endpoints

### Chat Endpoints

**POST /api/chat/message**
```json
{
  "message": "What's your return policy?",
  "conversation_history": [],
  "store_context": null
}
```

**POST /api/chat/demo**
Same as above but uses demo store context automatically.

**POST /api/chat/detect-intent**
```
?message=Where is my order?
```

## Testing the Chat API

### Option 1: Using the Swagger UI
1. Go to http://localhost:8000/docs
2. Click on "POST /api/chat/demo"
3. Click "Try it out"
4. Enter a message like "What's your shipping policy?"
5. Click "Execute"

### Option 2: Using curl
```bash
curl -X POST "http://localhost:8000/api/chat/demo" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What sizes do you have?",
    "conversation_history": []
  }'
```

### Option 3: Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/demo",
    json={
        "message": "Do you ship internationally?",
        "conversation_history": []
    }
)

print(response.json())
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   └── routes/
│       ├── __init__.py
│       └── chat.py       # Chat endpoints
├── requirements.txt
├── .env.example
└── README.md
```

## Next Steps

- [ ] Add database (PostgreSQL)
- [ ] Add user authentication
- [ ] Add Shopify integration
- [ ] Add conversation persistence
- [ ] Add rate limiting
- [ ] Deploy to production

## Troubleshooting

**Import errors?**
Make sure you're in the virtual environment and all packages are installed.

**API key errors?**
Check that your `.env` file has the correct `ANTHROPIC_API_KEY`.

**Port already in use?**
Change the port in `main.py` or kill the process using port 8000.

## Development

```bash
# Run with auto-reload (for development)
uvicorn app.main:app --reload --port 8000

# Run tests (when we add them)
pytest

# Format code
black app/
```
