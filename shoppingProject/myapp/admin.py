from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "original_price", "category", "rating", "stock", "created_at")
    list_filter = ("category", "badge")
    search_fields = ("name", "description")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "email", "total_amount", "created_at")
    search_fields = ("customer_name", "email", "phone")
    readonly_fields = ("customer_name", "email", "phone", "address", "total_amount", "created_at")
    inlines = [OrderItemInline]
