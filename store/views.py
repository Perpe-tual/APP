import re
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.db.models import Q
from .models import Product
from .forms import CheckoutForm, SearchForm

# ─────────────────────────────────────────────
# HOME PAGE
# Shows welcome message + featured products
# ─────────────────────────────────────────────
def _is_newborn_age(age_text):
    if 'newborn' in age_text or 'new born' in age_text:
        return True
    month_range = re.search(r'(\d+)\s*-\s*(\d+)\s*months?', age_text)
    if month_range:
        return int(month_range.group(2)) <= 10
    single_month = re.search(r'(\d+)\s*months?', age_text)
    if single_month:
        return int(single_month.group(1)) <= 10
    return False


def _is_toddler_age(age_text):
    if 'toddler' in age_text:
        return True
    year_range = re.search(r'(\d+)\s*-\s*(\d+)\s*years?', age_text)
    if year_range:
        low, high = int(year_range.group(1)), int(year_range.group(2))
        return low >= 6 and high <= 10
    return False


def home(request):
    featured_products = Product.objects.filter(is_featured=True)
    search_form = SearchForm()
    
    newborn_products = []
    toddler_products = []
    
    for product in featured_products:
        age_lower = product.age_range.lower()
        if _is_newborn_age(age_lower):
            newborn_products.append(product)
        elif _is_toddler_age(age_lower):
            toddler_products.append(product)
    
    context = {
        'newborn_products': newborn_products,
        'toddler_products': toddler_products,
        'search_form': search_form,
        'page_title': 'Welcome to TinySteps Children\'s Wear'
    }
    return render(request, 'store/home.html', context)


# ─────────────────────────────────────────────
# PRODUCT LISTING PAGE
# Shows all products, can filter by category
# ─────────────────────────────────────────────
def product_list(request):
    category = request.GET.get('category')  # reads ?category=shoes from URL
    search_query = request.GET.get('search', '')  # reads ?search=query from URL
    search_form = SearchForm(request.GET if search_query else None)
    
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    elif category:
        products = products.filter(category=category)

    context = {
        'products': products,
        'selected_category': category,
        'search_form': search_form,
        'search_query': search_query,
        'page_title': 'All Products'
    }
    return render(request, 'store/product.html', context)


# ─────────────────────────────────────────────
# PRODUCT DETAIL PAGE
# Shows product details and additional gallery images
# ─────────────────────────────────────────────

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get similar products by name similarity and category
    # Extract keywords from product name to find truly similar items
    product_name_words = set(product.name.lower().split())
    similar_products = []
    
    candidates = Product.objects.filter(category=product.category).exclude(id=product_id)
    for candidate in candidates:
        candidate_words = set(candidate.name.lower().split())
        # Check if they share meaningful keywords (filter out common words)
        common_words = product_name_words & candidate_words
        common_words = {w for w in common_words if len(w) > 2}  # Filter short words
        if common_words:
            similar_products.append(candidate)
        if len(similar_products) >= 4:
            break
    
    similar_products = similar_products[:4]

    context = {
        'product': product,
        'similar_products': similar_products,
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