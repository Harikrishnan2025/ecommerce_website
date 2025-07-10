import random
from datetime import timedelta
from django.utils import timezone

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def otp_is_valid(user, expiry_minutes=10):
    if not user.email_otp or not user.otp_created_at:
        return False
    return timezone.now() <= user.otp_created_at + timedelta(minutes=expiry_minutes)
