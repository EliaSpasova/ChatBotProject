from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from app.config import get_settings
from typing import List, Optional
import json

router = APIRouter()
settings = get_settings()

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=settings.anthropic_api_key)


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Message]] = []
    store_context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


# Simulated store context (in production, this comes from database)
DEFAULT_STORE_CONTEXT = {
    "store_name": "Demo T-Shirt Store",
    "return_policy": "30-day returns, free shipping on returns over $50",
    "shipping_info": "Standard shipping 5-7 days ($5.99), Express 2-3 days ($12.99), Next day ($24.99). Free shipping over $50.",
    "products": [
        {"name": "Classic White Tee", "price": 29.99, "sizes": ["S", "M", "L", "XL"]},
        {"name": "Vintage Band Shirt", "price": 34.99, "sizes": ["S", "M", "L", "XL", "XXL"]},
        {"name": "Premium Cotton Polo", "price": 44.99, "sizes": ["S", "M", "L", "XL"]},
    ]
}


def build_system_prompt(store_context: dict) -> str:
    """Build the system prompt with store context"""
    
    return f"""You are a helpful and friendly customer service AI assistant for {store_context['store_name']}.

Your goal is to help customers with their questions about products, orders, shipping, and returns.

STORE INFORMATION:
- Return Policy: {store_context['return_policy']}
- Shipping: {store_context['shipping_info']}

GUIDELINES:
1. Be helpful, friendly, and professional
2. Answer questions accurately based on the store information provided
3. If you don't know something, be honest and offer to connect them with a human support agent
4. Keep responses concise but complete
5. Use a warm, conversational tone
6. If asked about order tracking, ask for the order number
7. For product recommendations, ask about their preferences

Remember: You represent {store_context['store_name']} - maintain their brand voice and be helpful!"""


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and get AI response
    
    This endpoint:
    1. Takes user message + conversation history
    2. Adds store context
    3. Calls Claude API
    4. Returns AI response
    """
    
    try:
        # Use provided store context or default
        store_context = request.store_context or DEFAULT_STORE_CONTEXT
        
        # Build system prompt
        system_prompt = build_system_prompt(store_context)
        
        # Format conversation history for Claude
        messages = []
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model=settings.default_ai_model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=messages
        )
        
        # Extract response text
        assistant_message = response.content[0].text
        
        return ChatResponse(
            response=assistant_message,
            conversation_id=None  # We'll add conversation tracking later
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/demo", response_model=ChatResponse)
async def demo_chat(request: ChatRequest):
    """
    Demo endpoint that shows how the chatbot works
    Same as /message but with demo context
    """
    
    # Force demo context
    request.store_context = DEFAULT_STORE_CONTEXT
    
    return await send_message(request)


# Intent detection endpoint (for debugging/testing)
@router.post("/detect-intent")
async def detect_intent(message: str):
    """
    Detect the intent of a user message
    Useful for routing and analytics
    """
    
    try:
        response = anthropic_client.messages.create(
            model=settings.default_ai_model,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Analyze this customer message and categorize it into ONE of these intents:
                - order_tracking
                - product_question
                - shipping_question
                - return_question
                - complaint
                - general_inquiry
                
                Message: "{message}"
                
                Respond with ONLY the intent category, nothing else."""
            }]
        )
        
        intent = response.content[0].text.strip().lower()
        
        return {
            "message": message,
            "intent": intent
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting intent: {str(e)}"
        )


# Test endpoint
@router.get("/test")
async def test_chat():
    """Test that the chat API is working"""
    return {
        "status": "ok",
        "message": "Chat API is operational",
        "ai_model": settings.default_ai_model
    }
