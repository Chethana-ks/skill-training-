from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Order, OrderItem, Product


def seed_sample_products():
    """Add demo catalogue once, so a fresh store is not empty."""
    samples = [
        ("Classic White Sneakers", "Comfortable everyday sneakers with a clean, versatile look.", "2499.00", "3499.00", 29, "4.6", "BESTSELLER", "Fashion", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=900", 18),
        ("Wireless Headphones", "Enjoy your favourite music with a comfortable wireless design.", "1799.00", "2999.00", 40, "4.5", "HOT DEAL", "Electronics", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900", 20),
        ("Everyday Backpack", "A practical backpack for college, work and short trips.", "999.00", "1499.00", 33, "4.4", "POPULAR", "Fashion", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=900", 25),
        ("Smart Watch", "Track your day and stay connected with a stylish smartwatch.", "2299.00", "3999.00", 43, "4.3", "HOT DEAL", "Electronics", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900", 14),
        ("Skincare Essentials", "A simple skincare set for your everyday self-care routine.", "799.00", "1199.00", 33, "4.5", "VALUE PACK", "Beauty", "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=900", 30),
        ("Classic Sunglasses", "Lightweight sunglasses that complete your everyday style.", "599.00", "999.00", 40, "4.2", "TRENDING", "Accessories", "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=900", 22),
        ("Ceramic Coffee Mug", "A minimal ceramic mug for coffee, tea and cosy breaks.", "299.00", "449.00", 33, "4.7", "TOP RATED", "Home", "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=900", 40),
        ("Sports Water Bottle", "Reusable bottle to keep you hydrated throughout the day.", "399.00", "599.00", 33, "4.4", "POPULAR", "Sports", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=900", 35),
        ("Minimal Desk Lamp", "A modern desk lamp for your study table or workspace.", "899.00", "1299.00", 31, "4.3", "NEW", "Home", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900", 12),
        ("Leather Handbag", "A versatile handbag with a timeless everyday design.", "1499.00", "2199.00", 32, "4.6", "TRENDING", "Accessories", "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=900", 9),
        ("Running Shoes", "Lightweight shoes designed for daily walks and workouts.", "1899.00", "2799.00", 32, "4.5", "BESTSELLER", "Sports", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=900", 16),
        ("Bluetooth Speaker", "Compact speaker for music at home or on the go.", "1199.00", "1799.00", 33, "4.4", "HOT DEAL", "Electronics", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=900", 11),
    ]
    for name, description, price, old_price, discount, rating, badge, category, image, stock in samples:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "description": description, "price": Decimal(price),
                "original_price": Decimal(old_price), "discount_percent": discount,
                "rating": Decimal(rating), "badge": badge, "category": category,
                "image_url": image, "stock": stock,
            },
        )


def _cart_count(request):
    return sum(int(qty) for qty in request.session.get("cart", {}).values())


def _get_cart_items(request):
    cart_data = request.session.get("cart", {})
    items, total, cleaned_cart = [], Decimal("0.00"), {}
    for product_id, raw_quantity in cart_data.items():
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue
        product = Product.objects.filter(pk=product_id).first()
        if not product or quantity < 1:
            continue
        quantity = min(quantity, product.stock)
        if quantity < 1:
            continue
        cleaned_cart[str(product.pk)] = quantity
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    if cleaned_cart != cart_data:
        request.session["cart"] = cleaned_cart
    return items, total


def home(request):
    if not Product.objects.exists():
        seed_sample_products()
    products = Product.objects.all()
    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    if search:
        products = products.filter(name__icontains=search)
    if category:
        products = products.filter(category__iexact=category)
    categories = Product.objects.order_by("category").values_list("category", flat=True).distinct()
    return render(request, "home.html", {
        "products": products, "categories": categories, "search": search,
        "selected_category": category, "cart_count": _cart_count(request),
    })


def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("home")
    product = get_object_or_404(Product, pk=product_id)
    cart_data = request.session.get("cart", {})
    key = str(product.pk)
    current_quantity = int(cart_data.get(key, 0))
    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
    elif current_quantity >= product.stock:
        messages.warning(request, "You have already added all available stock.")
    else:
        cart_data[key] = current_quantity + 1
        request.session["cart"] = cart_data
        messages.success(request, f"{product.name} added to your cart.")
    return redirect("home")


def cart(request):
    items, total = _get_cart_items(request)
    return render(request, "cart.html", {"cart_items": items, "total": total, "cart_count": _cart_count(request)})


def update_cart(request, product_id):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, pk=product_id)
    cart_data = request.session.get("cart", {})
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        messages.error(request, "Enter a valid quantity.")
        return redirect("cart")
    if quantity <= 0:
        cart_data.pop(str(product_id), None)
        messages.success(request, "Product removed from your cart.")
    elif quantity > product.stock:
        messages.error(request, f"Only {product.stock} item(s) are available.")
    else:
        cart_data[str(product_id)] = quantity
        messages.success(request, "Cart quantity updated.")
    request.session["cart"] = cart_data
    return redirect("cart")


def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart_data = request.session.get("cart", {})
        cart_data.pop(str(product_id), None)
        request.session["cart"] = cart_data
        messages.success(request, "Product removed from your cart.")
    return redirect("cart")


def checkout(request):
    items, total = _get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        if not all([name, email, phone, address]):
            messages.error(request, "Please complete all delivery details.")
            return render(request, "checkout.html", {"cart_items": items, "total": total, "success": False})
        try:
            with transaction.atomic():
                locked_products = {}
                for item in items:
                    product = Product.objects.select_for_update().get(pk=item["product"].pk)
                    if product.stock < item["quantity"]:
                        raise ValueError(f"Not enough stock for {product.name}.")
                    locked_products[product.pk] = product
                order = Order.objects.create(customer_name=name, email=email, phone=phone, address=address, total_amount=total)
                for item in items:
                    product = locked_products[item["product"].pk]
                    quantity = item["quantity"]
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
                    product.stock -= quantity
                    product.save(update_fields=["stock"])
            request.session["cart"] = {}
            return render(request, "checkout.html", {"success": True, "order": order})
        except ValueError as error:
            messages.error(request, str(error))
            return redirect("cart")
    return render(request, "checkout.html", {"cart_items": items, "total": total, "success": False})
