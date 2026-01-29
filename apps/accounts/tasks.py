"""
Celery tasks for the accounts app.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_verification_email(user_id: int):
    """
    Send email verification link to user.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    # TODO: Generate verification token
    verification_link = f"https://example.com/verify?token=xxx"

    send_mail(
        subject="Verify your email - E-commerce",
        message=f"""
        Hi {user.first_name or 'there'},
        
        Please verify your email by clicking the link below:
        {verification_link}
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        E-commerce Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def send_password_reset_email(user_id: int):
    """
    Send password reset link to user.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    # TODO: Generate password reset token
    reset_link = f"https://example.com/reset-password?token=xxx"

    send_mail(
        subject="Password Reset - E-commerce",
        message=f"""
        Hi {user.first_name or 'there'},
        
        You requested a password reset. Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        E-commerce Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def send_welcome_email(user_id: int):
    """
    Send welcome email to new user.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    send_mail(
        subject="Welcome to E-commerce!",
        message=f"""
        Hi {user.first_name or 'there'},
        
        Welcome to our e-commerce platform!
        
        We're excited to have you on board. Start exploring our products and find great deals.
        
        If you have any questions, feel free to contact our support team.
        
        Best regards,
        E-commerce Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
