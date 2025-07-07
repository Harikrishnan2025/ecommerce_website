from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_price', 'created_at','get_phone_number']
    inlines = [OrderItemInline]
    list_filter = ['status']
    # search_fields = ['order_number', 'user__username']
    @admin.display(description='Phone Number')
    def get_phone_number(self, obj):
        return obj.user.phone_number if hasattr(obj.user, 'phone_number') else 'N/A'
