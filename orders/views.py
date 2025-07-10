from django.shortcuts import render
from rest_framework import generics,permissions,status
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.response import Response
from cart.models import Cart,CartItem
from .models import Order,OrderItem
from .serializers import CreateOrderSerializer,UserOrderListSerializer,UpdatrOrderStatusSerializer,AdminUserOrderListSerializer
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.exceptions import ValidationError
from reportlab.pdfgen import canvas
import os

class IsOrderOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            request.user.is_staff or
            request.user.role == 'admin'
        )
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin')

class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateOrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            raise ValidationError("Cart is empty or does not exist.")

        phone_number = getattr(user, 'phone_number', None)

        with transaction.atomic():
            for item in cart.items.select_related('product'):
                product = item.product
                if item.quantity > product.quantity:
                    raise ValidationError(
                        f"Not enough stock for '{product.name}'. Available: {product.quantity}, requested: {item.quantity}"
                    )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(user=user)


            total = 0
            for item in cart.items.select_related('product'):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                item.product.quantity -= item.quantity
                item.product.save()
                total += item.quantity * item.product.price

            order.total_price = total
            order.save()

            pdf_filename = f'invoice_{order.order_number}.pdf'
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

            c = canvas.Canvas(pdf_path)
            c.drawString(100, 800, f"Invoice for Order {order.order_number}")
            c.drawString(100, 780, f"Name: {order.full_name}")
            c.drawString(100, 760, f"Address: {order.address}")
            c.drawString(100, 740, f"Phone: {phone_number}")
            c.drawString(100, 720, f"Payment Method: {order.payment_method}")
            c.drawString(100, 700, "Items:")
            y = 680
            for item in order.items.all():
                c.drawString(100, y, f"{item.product.name} x {item.quantity} @ ₹{item.price}")
                y -= 20
            c.drawString(100, y - 10, f"Total: ₹{order.total_price}")
            c.save()

            relative_path = f'invoices/{pdf_filename}'
            order.invoice_pdf.name = relative_path
            order.save()

            cart.items.all().delete()
    
        subject = f'Order Confirmation - {order.order_number}'
        message = (
            f"Hi {order.full_name},\n\n"
            f"Your order {order.order_number} has been placed successfully!\n"
            f"Total: ₹{order.total_price}\n"
            f"Shipping Address: {order.address}\n\n"
            f"Phone: {phone_number or 'N/A'}\n\n"
            f"Payment Method: {order.payment_method}\n\n"
            "Thank you for shopping with us!"
        )
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            
        )
        if os.path.exists(pdf_path):
            email.attach_file(pdf_path)

        email.send()

        return Response(self.get_serializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

class UserOrderListView(generics.ListAPIView):
    serializer_class = UserOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
class UserOrderDetailView(generics.RetrieveAPIView):
    serializer_class = UserOrderListSerializer
    permission_classes = [permissions.IsAuthenticated,IsOrderOwnerOrAdmin]
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
class UserOrderCancelView(APIView):
    permission_classes =[permissions.IsAuthenticated,IsOrderOwnerOrAdmin]

    def post(self,request,order_number):
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'Pending':
            return Response({"error": "Only pending orders can be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        for item in order.items.all():
            product = item.product
            product.quantity += item.quantity
            product.save()
        order.status = "Cancelled"
        order.save() 
        return Response({"message": f"Order {order_number} was cancelled. Stock restored."}, status=status.HTTP_200_OK)


class AdminOrderListView(generics.ListAPIView):
    permission_classes =[IsAdminUser]
    serializer_class = AdminUserOrderListSerializer
    queryset = Order.objects.all().order_by('-created_at')
    search_fields = ['user__username','user__email','order_number','status']
     
class UpdatrOrderStatusView(generics.UpdateAPIView):
    serializer_class = UpdatrOrderStatusSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    lookup_field = 'order_number'
    http_method_names = ['patch', 'put', 'head', 'options']

    def perform_update(self, serializer):
        order =  self.get_object()
        previous_status = order.status
        new_status = serializer.validated_data['status']
        serializer.save()
        if previous_status != 'Cancelled' and new_status == 'Cancelled':
            for item in order.items.all():
                item.product.quantity += item.quantity
                item.product.save()

        elif previous_status == 'Cancelled' and new_status != 'Cancelled':
            for item in order.items.all():
                if item.product.quantity < item.quantity:
                    raise ValidationError({
                     "detail": f"Cannot change status from Cancelled to {new_status}. "
                          f"Not enough stock for '{item.product.name}'. "
                          f"Available: {item.product.quantity}, Needed: {item.quantity}"
            })
            for item in order.items.all():
                item.product.quantity -= item.quantity
                item.product.save()
   

        



