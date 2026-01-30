# ShopBot AI - Technical Architecture & Implementation Plan

## Executive Summary

**Product:** AI-powered customer support chatbot for Shopify stores
**Target Market:** Small e-commerce businesses ($10k-100k/month revenue)
**Pricing:** $79/month subscription
**MVP Timeline:** 2-3 weeks

---

## 1. SYSTEM ARCHITECTURE

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S SHOPIFY STORE                    │
│                 (Embedded Chat Widget)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  - Chat Widget (embeds in customer site)                    │
│  - Admin Dashboard (for store owner)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (Python/FastAPI)                    │
│  - WebSocket for real-time chat                             │
│  - REST API for configuration                                │
│  - Authentication & authorization                            │
│  - Rate limiting                                             │
└─────┬──────────────┬──────────────┬─────────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌────────────────┐
│PostgreSQL│  │  Redis   │  │  AI Layer      │
│ Database │  │  Cache   │  │ (Claude API)   │
│          │  │          │  │                │
│- Users   │  │- Sessions│  │- Conversation  │
│- Stores  │  │- Messages│  │- Context       │
│- Chats   │  │          │  │- Generation    │
└──────────┘  └──────────┘  └────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│            SHOPIFY INTEGRATION                               │
│  - Shopify API for product data                             │
│  - Order tracking                                            │
│  - Customer information                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. TECHNOLOGY STACK

### Frontend
- **Framework:** React 18+ with TypeScript
- **State Management:** Zustand (lightweight)
- **UI Components:** Tailwind CSS + shadcn/ui
- **Real-time:** Socket.io-client
- **Build Tool:** Vite
- **Hosting:** Vercel (free tier initially, ~$20/month for production)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **Caching:** Redis
- **WebSockets:** Socket.io for Python
- **Task Queue:** Celery (for background jobs)
- **Hosting:** Railway or Render (~$20-40/month)

### AI & APIs
- **LLM:** Claude API (Anthropic) - $10-50/month depending on usage
- **Alternative:** OpenAI GPT-4 as backup
- **E-commerce:** Shopify API (free to integrate)

### Infrastructure
- **DNS/CDN:** Cloudflare (free)
- **Monitoring:** Sentry (free tier)
- **Analytics:** PostHog (open-source, self-hosted)
- **Email:** SendGrid or Resend (free tier)

**Total Infrastructure Cost:** $50-100/month to start

---

## 3. DATABASE SCHEMA

```sql
-- Core Tables

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    shopify_store_url VARCHAR(255) NOT NULL,
    shopify_access_token TEXT NOT NULL, -- encrypted
    store_name VARCHAR(255),
    business_info JSONB, -- return policy, shipping info, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id),
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, escalated
    metadata JSONB -- customer IP, browser, etc.
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- context used, order info referenced, etc.
);

CREATE TABLE products_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id),
    shopify_product_id BIGINT,
    title VARCHAR(500),
    description TEXT,
    variants JSONB,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(store_id, shopify_product_id)
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50), -- active, canceled, past_due
    plan VARCHAR(50) DEFAULT 'basic',
    monthly_message_limit INTEGER DEFAULT 10000,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP
);
```

---

## 4. API ENDPOINTS

### Authentication
```
POST   /api/auth/register          - Create new user account
POST   /api/auth/login             - Login (returns JWT)
POST   /api/auth/logout            - Logout
GET    /api/auth/me                - Get current user
```

### Stores
```
POST   /api/stores                 - Connect new Shopify store
GET    /api/stores/:id             - Get store details
PUT    /api/stores/:id/config      - Update store configuration
DELETE /api/stores/:id             - Disconnect store
POST   /api/stores/:id/sync        - Sync products from Shopify
```

### Chat (for embedded widget)
```
WS     /ws/chat/:storeId           - WebSocket for real-time chat
POST   /api/chat/init              - Initialize new conversation
GET    /api/chat/history/:convId   - Get conversation history
```

### Dashboard
```
GET    /api/dashboard/stats        - Get conversation stats
GET    /api/dashboard/conversations - List recent conversations
GET    /api/dashboard/analytics    - Usage analytics
```

### Webhooks (from Shopify)
```
POST   /api/webhooks/shopify/orders     - Order updates
POST   /api/webhooks/shopify/products   - Product changes
```

---

## 5. AI CONVERSATION FLOW

```python
# Simplified conversation logic

async def handle_customer_message(message: str, store_context: dict):
    """
    Main conversation handler
    """
    
    # 1. Detect intent
    intent = await detect_intent(message)
    
    # 2. Fetch relevant context
    if intent == "order_tracking":
        context = await fetch_order_info(store_context)
    elif intent == "product_question":
        context = await search_products(message, store_context)
    elif intent == "policy_question":
        context = get_store_policies(store_context)
    
    # 3. Build prompt for Claude
    prompt = f"""
    You are a helpful customer service agent for {store_context['store_name']}.
    
    Store Information:
    - Return Policy: {store_context['return_policy']}
    - Shipping Info: {store_context['shipping_info']}
    
    Relevant Context:
    {context}
    
    Customer Question:
    {message}
    
    Provide a helpful, friendly response. If you need more info, ask clarifying questions.
    If you can't help, suggest contacting support@{store_context['domain']}.
    """
    
    # 4. Call Claude API
    response = await anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 5. Return response
    return response.content[0].text
```

---

## 6. SHOPIFY INTEGRATION

### Required Shopify API Scopes
```
read_products
read_orders
read_customers
write_customers (optional - for capturing emails)
```

### Key Integration Points

1. **OAuth Flow:** User clicks "Connect Shopify" → redirected to Shopify → approve → get access token
2. **Product Sync:** Periodic job (every 6 hours) to sync product catalog
3. **Order Lookup:** Real-time API calls when customer asks about order
4. **Webhooks:** Receive updates about orders/products automatically

### Sample Shopify API Calls

```python
import shopify

# Initialize Shopify session
shopify.ShopifyResource.set_site(f"https://{shop_name}.myshopify.com/admin")
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, api_version, access_token))

# Get products
products = shopify.Product.find()

# Get order by order number
order = shopify.Order.find(order_id)

# Search customer orders by email
orders = shopify.Order.find(email="customer@example.com")
```

---

## 7. FRONTEND WIDGET EMBED

Store owners add ONE line of code to their site:

```html
<script src="https://cdn.shopbotai.com/widget.js" data-store-id="abc123"></script>
```

The widget:
- Loads asynchronously (doesn't slow down site)
- Appears as a chat bubble in bottom-right
- Opens chat interface on click
- Maintains conversation state
- Mobile-responsive

---

## 8. MVP FEATURE PRIORITIES

### Phase 1 (Week 1-2): Core MVP
- [ ] User registration & authentication
- [ ] Shopify OAuth connection
- [ ] Basic chatbot (with Claude API)
- [ ] Product catalog sync
- [ ] Simple order lookup
- [ ] Embeddable chat widget
- [ ] Admin dashboard (basic stats)

### Phase 2 (Week 3): Polish & Launch
- [ ] Stripe payment integration
- [ ] Email notifications for escalations
- [ ] Conversation history in dashboard
- [ ] Basic analytics
- [ ] Landing page & documentation
- [ ] Beta testing with 3-5 stores

### Phase 3 (Post-Launch): Enhancements
- [ ] Multi-language support
- [ ] Custom branding options
- [ ] Advanced analytics
- [ ] Integration with email support tools
- [ ] AI training on specific store data
- [ ] Mobile app for store owners

---

## 9. SECURITY CONSIDERATIONS

1. **API Keys:** All Shopify tokens encrypted at rest (using Fernet)
2. **Rate Limiting:** 100 requests/min per store to prevent abuse
3. **Input Validation:** Sanitize all user inputs
4. **CORS:** Strict origin policies for widget
5. **DDoS Protection:** Cloudflare in front
6. **Data Privacy:** GDPR-compliant (customer data retention policies)

---

## 10. COST ANALYSIS

### Infrastructure (Monthly)
- Railway/Render hosting: $30
- PostgreSQL database: $10 (included in hosting)
- Redis cache: $10 (included in hosting)
- Claude API usage: $20-100 (depends on volume)
- CDN/Domain: $5
- **Total: $50-150/month**

### Revenue Model
- Subscription: $79/month per store
- **Break-even:** 2-3 customers
- **Sustainable:** 10+ customers = $790/month revenue

---

## 11. DEVELOPMENT ROADMAP

### Week 1
**Days 1-2:** Backend foundation
- Set up FastAPI project
- Database schema & migrations
- User authentication

**Days 3-4:** Shopify integration
- OAuth flow
- Product sync
- Order lookup API

**Days 5-7:** AI integration
- Claude API setup
- Basic conversation logic
- Context management

### Week 2
**Days 8-10:** Frontend
- React chat widget
- Admin dashboard
- Embedding script

**Days 11-12:** Testing & Polish
- Test with sample store
- Bug fixes
- Performance optimization

**Days 13-14:** Deployment
- Deploy to production
- Domain setup
- Launch prep

### Week 3
**Days 15-17:** Payment & Launch
- Stripe integration
- Beta user onboarding
- Documentation

**Days 18-21:** Marketing & Iteration
- Get first paying customers
- Collect feedback
- Iterate on features

---

## 12. SUCCESS METRICS

### Week 1-2 (MVP)
- [ ] Successfully connects to Shopify store
- [ ] Answers 80%+ of common questions correctly
- [ ] Widget loads in <2 seconds
- [ ] Zero critical bugs

### Week 3-4 (Beta)
- [ ] 5 beta users signed up
- [ ] 3+ positive testimonials
- [ ] <5% churn rate
- [ ] Average response time <2 seconds

### Month 2-3 (Growth)
- [ ] 25 paying customers
- [ ] $2,000/month MRR
- [ ] 90%+ customer satisfaction
- [ ] <10% monthly churn

---

## 13. NEXT IMMEDIATE STEPS

1. **Set up development environment**
   - Install Python 3.11+, Node.js 18+
   - Create GitHub repo
   - Set up local PostgreSQL & Redis

2. **Get API keys**
   - Anthropic Claude API key ($5 credit to start)
   - Create Shopify Partner account (free)
   - Stripe account (for later)

3. **Start coding**
   - Backend first (FastAPI skeleton)
   - Then Shopify integration
   - Then AI layer
   - Finally frontend

4. **Find beta testers**
   - Reach out to 10 small Shopify stores
   - Offer free trial in exchange for feedback

---

## 14. POTENTIAL CHALLENGES & SOLUTIONS

### Challenge 1: AI accuracy
**Solution:** 
- Use RAG (Retrieval Augmented Generation) to ground responses in store data
- Add confidence scores - if low confidence, escalate to human
- Continuously improve prompts based on feedback

### Challenge 2: Shopify API rate limits
**Solution:**
- Cache product data (refresh every 6 hours)
- Use Redis for frequently accessed data
- Implement exponential backoff for API calls

### Challenge 3: Customer trust
**Solution:**
- Clearly label as AI assistant
- Make it easy to reach human support
- Show "powered by Claude" badge
- Provide conversation transcripts

### Challenge 4: Multi-store scalability
**Solution:**
- Design for multi-tenancy from day 1
- Use store_id in all database queries
- Separate Redis namespaces per store
- Monitor per-store resource usage

---

## 15. GO-TO-MARKET STRATEGY

1. **Landing Page** (Done ✓)
2. **Product Hunt Launch** (Week 3)
3. **Shopify App Store** (Month 2)
4. **Content Marketing**
   - "How to provide 24/7 support without hiring"
   - "AI customer service for small e-commerce"
5. **Direct Outreach**
   - Find Shopify stores on Reddit, Facebook groups
   - Offer free setup in exchange for testimonial

---

## SUMMARY

This is a **totally feasible MVP** that you can build in 2-3 weeks with your Python skills. The tech stack is proven, the market need is real, and the business model is sustainable.

**Your immediate action items:**
1. Review this architecture
2. Set up your dev environment
3. Start with backend - I'll help you code every step
4. Build, test, launch

Let's build this! 🚀
