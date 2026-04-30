from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from .models import Product
from .forms import CheckoutForm

# ─────────────────────────────────────────────
# HOME PAGE
# Shows welcome message + featured products
# ─────────────────────────────────────────────
def home(request):
    featured_products = Product.objects.filter(is_featured=True)
    context = {
        'featured_products': featured_products,
        'page_title': 'Welcome to TinySteps Baby Store'
    }
    return render(request, 'store/home.html', context)


# ─────────────────────────────────────────────
# PRODUCT LISTING PAGE
# Shows all products, can filter by category
# ─────────────────────────────────────────────
def product_list(request):
    category = request.GET.get('category')  # reads ?category=shoes from URL
    if category:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'selected_category': category,
        'page_title': 'All Products'
    }
    return render(request, 'store/product.html', context)


# ─────────────────────────────────────────────
# PRODUCT DETAIL PAGE
# Shows product details and additional gallery images
# ─────────────────────────────────────────────

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    gallery_images = []

    if product.image_url:
        gallery_images.append(product.image_url)

    gallery_images.extend([
        static('store/images/boy.jpg'),
        static('store/images/girl.jpg'),
        static('store/images/boy 2 piece.jpg')
    ])

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'page_title': product.name
    }
    return render(request, 'store/product_detail.html', context)


# ─────────────────────────────────────────────
# ADD TO CART
# Saves product ID in the session (like a cookie)
# ─────────────────────────────────────────────
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})  # get cart from session or empty dict

    product_id_str = str(product_id)  # session keys must be strings

    if product_id_str in cart:
        cart[product_id_str] += 1      # if already in cart, increase quantity
    else:
        cart[product_id_str] = 1       # otherwise add it with quantity 1

    request.session['cart'] = cart     # save back to session
    request.session.modified = True    # tell Django the session changed

    return redirect('cart')


# ─────────────────────────────────────────────
# REMOVE FROM CART
# Removes one product from the session cart
# ─────────────────────────────────────────────
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')


# ─────────────────────────────────────────────
# CART PAGE
# Reads product IDs from session, fetches products
# ─────────────────────────────────────────────
def cart(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id_str, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'total': total,
        'page_title': 'Your Cart'
    }
    return render(request, 'store/cart.html', context)


# ─────────────────────────────────────────────
# CHECKOUT PAGE
# Shows form, handles form submission
# ─────────────────────────────────────────────
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # In a real app you'd save the order here
            # For now, we just clear the cart and show a thank you
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_success')
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'page_title': 'Checkout'
    }
    return render(request, 'store/checkout.html', context)


# ─────────────────────────────────────────────
# ORDER SUCCESS PAGE
# Simple thank you page after checkout
# ─────────────────────────────────────────────
def order_success(request):
    return render(request, 'store/order_success.html', {
        'page_title': 'Order Placed!'
    })