from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import stripe

from app.config import get_settings
from app.database import get_db
from app.models import User, Subscription, PromoCode
from app.auth import hash_password, create_access_token

settings = get_settings()
router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str | None = None
    shopify_store_url: str | None = None
    promo_code: str | None = None


class CheckoutRequest(BaseModel):
    promo_code: str | None = None


class PromoCodeValidation(BaseModel):
    code: str


@router.post("/register")
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    Creates user account but doesn't start subscription yet
    """
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate promo code if provided
    promo_discount = 0.0
    promo_code_id = None
    
    if request.promo_code:
        promo = db.query(PromoCode).filter(
            PromoCode.code == request.promo_code.upper(),
            PromoCode.is_active == True
        ).first()
        
        if not promo:
            raise HTTPException(status_code=400, detail="Invalid promo code")
        
        # Check if promo code is still valid
        now = datetime.utcnow()
        if promo.valid_until and promo.valid_until < now:
            raise HTTPException(status_code=400, detail="Promo code has expired")
        
        if promo.max_uses and promo.times_used >= promo.max_uses:
            raise HTTPException(status_code=400, detail="Promo code usage limit reached")
        
        promo_discount = promo.discount_value
        promo_code_id = promo.id
    
    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        company_name=request.company_name,
        shopify_store_url=request.shopify_store_url
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
        "access_token": access_token,
        "promo_applied": bool(request.promo_code),
        "discount": promo_discount
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user_email: str,
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription
    """
    
    # Get user
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for existing subscription
    existing_sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if existing_sub and existing_sub.status == "active":
        raise HTTPException(status_code=400, detail="User already has active subscription")
    
    # Apply promo code if provided
    promo_discount = None
    if request.promo_code:
        promo = db.query(PromoCode).filter(
            PromoCode.code == request.promo_code.upper(),
            PromoCode.is_active == True
        ).first()
        
        if promo:
            # Update usage count
            promo.times_used += 1
            db.commit()
            
            # Create Stripe coupon
            if promo.discount_type == "percent":
                promo_discount = stripe.Coupon.create(
                    percent_off=promo.discount_value,
                    duration="repeating" if promo.duration_months else "once",
                    duration_in_months=promo.duration_months if promo.duration_months else 1,
                    name=f"{promo.code} - {promo.discount_value}% off"
                )
    
    # Create or get Stripe customer
    if not user.subscription or not user.subscription.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={
                "user_id": user.id,
                "company": user.company_name or ""
            }
        )
        customer_id = customer.id
    else:
        customer_id = user.subscription.stripe_customer_id
    
    # Create checkout session
    checkout_params = {
        "customer": customer_id,
        "payment_method_types": ["card"],
        "line_items": [{
            "price": settings.stripe_price_id_basic,
            "quantity": 1,
        }],
        "mode": "subscription",
        "success_url": "https://shopifybotai.netlify.app/success.html",
        "cancel_url": "https://shopifybotai.netlify.app/index.html",
        "subscription_data": {
            "trial_period_days": 14,  # 14-day free trial
            "metadata": {
                "user_id": user.id,
                "promo_code": request.promo_code or ""
            }
        }
    }
    
    # Add coupon if promo code was valid
    if promo_discount:
        checkout_params["discounts"] = [{"coupon": promo_discount.id}]
    
    session = stripe.checkout.Session.create(**checkout_params)
    
    return {
        "checkout_url": session.url,
        "session_id": session.id
    }


@router.post("/validate-promo")
async def validate_promo_code(request: PromoCodeValidation, db: Session = Depends(get_db)):
    """
    Validate a promo code without applying it
    """
    
    promo = db.query(PromoCode).filter(
        PromoCode.code == request.code.upper(),
        PromoCode.is_active == True
    ).first()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Check validity
    now = datetime.utcnow()
    if promo.valid_until and promo.valid_until < now:
        raise HTTPException(status_code=400, detail="Promo code has expired")
    
    if promo.max_uses and promo.times_used >= promo.max_uses:
        raise HTTPException(status_code=400, detail="Promo code usage limit reached")
    
    return {
        "valid": True,
        "code": promo.code,
        "discount_type": promo.discount_type,
        "discount_value": promo.discount_value,
        "description": promo.description,
        "first_month_only": promo.first_month_only,
        "duration_months": promo.duration_months
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks
    Updates subscription status based on Stripe events
    """
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Get user
        user_id = session["subscription_data"]["metadata"]["user_id"]
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            # Create or update subscription
            subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
            if not subscription:
                subscription = Subscription(user_id=user_id)
                db.add(subscription)
            
            subscription.stripe_customer_id = session["customer"]
            subscription.stripe_subscription_id = session["subscription"]
            subscription.status = "trialing"
            subscription.trial_ends_at = datetime.utcnow() + timedelta(days=14)
            
            db.commit()
    
    elif event["type"] == "customer.subscription.updated":
        subscription_data = event["data"]["object"]
        
        # Update subscription in database
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data["id"]
        ).first()
        
        if subscription:
            subscription.status = subscription_data["status"]
            subscription.current_period_start = datetime.fromtimestamp(subscription_data["current_period_start"])
            subscription.current_period_end = datetime.fromtimestamp(subscription_data["current_period_end"])
            db.commit()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"]
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data["id"]
        ).first()
        
        if subscription:
            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()
            db.commit()
    
    return {"status": "success"}


# Admin endpoint to create promo codes
@router.post("/admin/create-promo")
async def create_promo_code(
    code: str,
    discount_value: float,
    description: str | None = None,
    max_uses: int | None = None,
    duration_months: int | None = None,
    valid_days: int = 90,
    db: Session = Depends(get_db)
):
    """
    Create a new promo code (admin only - add auth later)
    """
    
    # Check if code already exists
    existing = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Promo code already exists")
    
    promo = PromoCode(
        code=code.upper(),
        discount_type="percent",
        discount_value=discount_value,
        max_uses=max_uses,
        duration_months=duration_months,
        valid_until=datetime.utcnow() + timedelta(days=valid_days),
        description=description
    )
    
    db.add(promo)
    db.commit()
    db.refresh(promo)
    
    return {
        "message": "Promo code created successfully",
        "code": promo.code,
        "discount": f"{promo.discount_value}% off",
        "max_uses": promo.max_uses or "unlimited",
        "valid_until": promo.valid_until
    }
