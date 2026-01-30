from app.database import SessionLocal
from app.models import PromoCode, User, Subscription

db = SessionLocal()

# Show all promo codes
print("\n🎟️  PROMO CODES:")
print("=" * 60)
for promo in db.query(PromoCode).all():
    print(f"Code: {promo.code}")
    print(f"  Discount: {promo.discount_value}% off")
    print(f"  Used: {promo.times_used}/{promo.max_uses or 'unlimited'}")
    print(f"  Valid until: {promo.valid_until}")
    print(f"  Description: {promo.description}")
    print()

# Show all users
print("\n👥 USERS:")
print("=" * 60)
for user in db.query(User).all():
    print(f"Email: {user.email}")
    print(f"  Name: {user.full_name}")
    print(f"  Company: {user.company_name}")
    print(f"  Store: {user.shopify_store_url}")
    print(f"  Created: {user.created_at}")
    print()

# Show subscriptions
print("\n💳 SUBSCRIPTIONS:")
print("=" * 60)
for sub in db.query(Subscription).all():
    user = db.query(User).filter(User.id == sub.user_id).first()
    print(f"User: {user.email if user else 'Unknown'}")
    print(f"  Status: {sub.status}")
    print(f"  Plan: {sub.plan_name} - ${sub.monthly_price}/month")
    print(f"  Discount: {sub.discount_percent}%")
    print()

db.close()
print("\n✅ Done!\n")