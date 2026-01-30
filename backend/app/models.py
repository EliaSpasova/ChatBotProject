from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    shopify_store_url = Column(String)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    stores = relationship("Store", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Stripe info
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String, unique=True)
    stripe_price_id = Column(String)
    
    # Subscription details
    status = Column(String, default="trialing")  # trialing, active, canceled, past_due
    plan_name = Column(String, default="basic")  # basic, pro, enterprise
    monthly_price = Column(Float, default=79.00)
    
    # Promo code tracking
    promo_code_id = Column(String, ForeignKey("promo_codes.id"))
    discount_percent = Column(Float, default=0.0)
    
    # Usage limits
    monthly_message_limit = Column(Integer, default=999999)  # unlimited for now
    messages_used_this_month = Column(Integer, default=0)
    
    # Dates
    trial_ends_at = Column(DateTime)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    canceled_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    promo_code = relationship("PromoCode")


class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, unique=True, nullable=False, index=True)  # e.g., "LAUNCH50"
    
    # Discount details
    discount_type = Column(String, default="percent")  # percent or fixed
    discount_value = Column(Float, nullable=False)  # 50 for 50% off, or $20 for $20 off
    
    # Usage limits
    max_uses = Column(Integer)  # None = unlimited
    times_used = Column(Integer, default=0)
    
    # Validity
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    # Restrictions
    first_month_only = Column(Boolean, default=False)
    duration_months = Column(Integer)  # How many months the discount applies
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    description = Column(String)  # e.g., "50% off for first 10 customers"


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Shopify details
    shopify_store_url = Column(String, nullable=False)
    shopify_access_token = Column(String)  # Encrypted in production
    shopify_shop_id = Column(String)
    
    # Store info
    store_name = Column(String)
    store_domain = Column(String)
    
    # Chatbot configuration
    business_info = Column(Text)  # JSON: return policy, shipping info, etc.
    widget_settings = Column(Text)  # JSON: colors, position, greeting message
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="stores")
    conversations = relationship("Conversation", back_populates="store")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    
    # Customer info
    customer_email = Column(String)
    customer_name = Column(String)
    customer_ip = Column(String)
    
    # Conversation details
    status = Column(String, default="active")  # active, resolved, escalated
    rating = Column(Integer)  # 1-5 stars
    
    # Metadata
    extra_data = Column(Text)  # JSON: browser, location, etc.

    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    store = relationship("Store", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    
    # AI metadata
    model_used = Column(String)  # claude-sonnet-4-20250514
    tokens_used = Column(Integer)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
