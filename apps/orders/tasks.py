"""
Celery tasks for the orders app.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_order_confirmation_email(order_id: int):
    """
    Send order confirmation email.
    """
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    items_list = "\n".join(
        f"- {item.quantity}x {item.product_name}: R$ {item.total_price}"
        for item in order.items.all()
    )

    send_mail(
        subject=f"Order Confirmation - {order.number}",
        message=f"""
        Hi {order.user.first_name or 'there'},

        Thank you for your order!

        Order Number: {order.number}

        Items:
        {items_list}

        Subtotal: R$ {order.subtotal}
        Shipping: R$ {order.shipping_cost}
        Discount: R$ {order.discount}
        Total: R$ {order.total}

        We'll notify you when your order ships.

        Best regards,
        E-commerce Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )


@shared_task
def send_order_shipped_email(order_id: int):
    """
    Send order shipped email with tracking code.
    """
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    send_mail(
        subject=f"Your Order {order.number} Has Shipped!",
        message=f"""
        Hi {order.user.first_name or 'there'},

        Great news! Your order has shipped.

        Order Number: {order.number}
        Tracking Code: {order.tracking_code}

        Track your package at: https://www.correios.com.br/rastreamento/{order.tracking_code}

        Estimated delivery: {order.estimated_delivery or 'N/A'}

        Best regards,
        E-commerce Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )
