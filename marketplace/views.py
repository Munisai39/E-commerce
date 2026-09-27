"""
Views for MarketNest classified marketplace.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import (
    Category,
    SubCategory,
    Listing,
    ListingImage,
    Favorite,
    Conversation,
    Message,
    Offer,
    Report,
    Profile
)
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    ListingForm,
    OfferForm,
    MessageForm,
    ReportForm
)


# ==============================================================================
# HOME & BROWSING VIEWS
# ==============================================================================

def home_view(request):
    """
    Homepage displaying hero banner, search bar, category shortcuts,
    featured products, and latest marketplace listings.
    """
    categories = Category.objects.annotate(
        active_count=Count('listings', filter=Q(listings__status='active'))
    ).order_by('order', 'name')

    featured_listings = Listing.objects.filter(
        status='active',
        is_featured=True
    ).select_related('category', 'seller').prefetch_related('images')[:8]

    # If few or no explicitly featured listings, fall back to top viewed/active
    if not featured_listings.exists():
        featured_listings = Listing.objects.filter(
            status='active'
        ).select_related('category', 'seller').prefetch_related('images').order_by('-views_count', '-created_at')[:8]

    latest_listings = Listing.objects.filter(
        status='active'
    ).select_related('category', 'seller').prefetch_related('images').order_by('-created_at')[:12]

    # Popular locations for quick filter chips
    popular_locations = Listing.objects.filter(status='active').values_list('location', flat=True).distinct()[:8]

    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(user=request.user).values_list('listing_id', flat=True)
        )

    context = {
        'categories': categories,
        'featured_listings': featured_listings,
        'latest_listings': latest_listings,
        'popular_locations': popular_locations,
        'user_favorites': user_favorites,
        'total_active_listings': Listing.objects.filter(status='active').count(),
    }
    return render(request, 'home.html', context)


def browse_view(request):
    """
    Search, filter, sort, and paginate active marketplace listings.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    subcategory_id = request.GET.get('subcategory', '').strip()
    condition = request.GET.get('condition', '').strip()
    location = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    listings = Listing.objects.filter(status='active').select_related('category', 'subcategory', 'seller').prefetch_related('images')

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            listings = listings.filter(category=selected_category)

    if subcategory_id:
        listings = listings.filter(subcategory_id=subcategory_id)

    # Search keyword
    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        )

    if location:
        listings = listings.filter(location__icontains=location)

    if condition:
        listings = listings.filter(condition=condition)

    # Price filters
    if min_price:
        try:
            listings = listings.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    if sort_by == 'price_low':
        listings = listings.order_by('price')
    elif sort_by == 'price_high':
        listings = listings.order_by('-price')
    elif sort_by == 'popular':
        listings = listings.order_by('-views_count', '-created_at')
    else:
        listings = listings.order_by('-created_at')

    # Pagination: 12 listings per page
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    categories = Category.objects.annotate(
        active_count=Count('listings', filter=Q(listings__status='active'))
    ).order_by('order', 'name')

    subcategories = SubCategory.objects.none()
    if selected_category:
        subcategories = selected_category.subcategories.all()

    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(user=request.user).values_list('listing_id', flat=True)
        )

    context = {
        'page_obj': page_obj,
        'listings': page_obj.object_list,
        'total_results': paginator.count,
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category,
        'condition_choices': Listing.CONDITION_CHOICES,
        'query': query,
        'category_slug': category_slug,
        'subcategory_id': subcategory_id,
        'condition': condition,
        'location': location,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'user_favorites': user_favorites,
    }
    return render(request, 'product_list.html', context)


def category_view(request, slug):
    """
    Direct category route: /category/<slug>/
    Forwards into browse with category preselected.
    """
    category = get_object_or_404(Category, slug=slug)
    query_params = request.GET.copy()
    query_params['category'] = category.slug
    return redirect(f"/browse/?{query_params.urlencode()}")


# ==============================================================================
# PRODUCT DETAIL & INTERACTIONS
# ==============================================================================

def product_detail_view(request, pk):
    """
    Detailed product listing page with image gallery, seller info,
    offer modal, contact seller modal, report modal, and related items.
    """
    listing = get_object_or_404(
        Listing.objects.select_related('category', 'subcategory', 'seller', 'seller__profile').prefetch_related('images'),
        pk=pk
    )

    # Increment view count safely
    Listing.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    listing.refresh_from_db(fields=['views_count'])

    is_owner = request.user.is_authenticated and request.user == listing.seller
    is_favorited = False
    existing_offer = None
    existing_conversation = None

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, listing=listing).exists()
        existing_offer = Offer.objects.filter(listing=listing, buyer=request.user).first()
        existing_conversation = Conversation.objects.filter(listing=listing, buyer=request.user).first()

    related_listings = Listing.objects.filter(
        category=listing.category,
        status='active'
    ).exclude(pk=listing.pk).select_related('category', 'seller').prefetch_related('images')[:4]

    offer_form = OfferForm()
    message_form = MessageForm()
    report_form = ReportForm()

    context = {
        'listing': listing,
        'images': listing.images.all(),
        'is_owner': is_owner,
        'is_favorited': is_favorited,
        'existing_offer': existing_offer,
        'existing_conversation': existing_conversation,
        'related_listings': related_listings,
        'offer_form': offer_form,
        'message_form': message_form,
        'report_form': report_form,
    }
    return render(request, 'product_detail.html', context)


@login_required
def create_listing_view(request):
    """
    Create a new product listing with multiple image uploads.
    """
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        uploaded_images = request.FILES.getlist('images')

        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.status = 'active'
            listing.save()

            # Handle multiple images
            first = True
            for img in uploaded_images:
                # Basic validation for image file extension
                ext = img.name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ListingImage.objects.create(
                        listing=listing,
                        image=img,
                        is_primary=first
                    )
                    first = False

            messages.success(request, f"Your listing '{listing.title}' has been posted successfully!")
            return redirect('product_detail', pk=listing.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        # Prepopulate contact phone from profile if available
        initial_data = {}
        if hasattr(request.user, 'profile') and request.user.profile.phone:
            initial_data['contact_phone'] = request.user.profile.phone
            initial_data['location'] = request.user.profile.location
        form = ListingForm(initial=initial_data)

    categories = Category.objects.all().order_by('order', 'name')
    return render(request, 'create_listing.html', {'form': form, 'categories': categories})


@login_required
def edit_listing_view(request, pk):
    """
    Edit an existing listing and manage its images.
    Protected to only allow listing owner.
    """
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller != request.user:
        messages.error(request, "You are not authorized to edit this listing.")
        return redirect('product_detail', pk=listing.pk)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        uploaded_images = request.FILES.getlist('images')
        delete_image_ids = request.POST.getlist('delete_images')

        if form.is_valid():
            listing = form.save()

            # Delete selected images
            if delete_image_ids:
                listing.images.filter(id__in=delete_image_ids).delete()

            # Add new uploaded images
            has_primary = listing.images.filter(is_primary=True).exists()
            for img in uploaded_images:
                ext = img.name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ListingImage.objects.create(
                        listing=listing,
                        image=img,
                        is_primary=not has_primary
                    )
                    has_primary = True

            # Ensure at least one image is primary if images exist
            if not listing.images.filter(is_primary=True).exists() and listing.images.exists():
                first_img = listing.images.first()
                first_img.is_primary = True
                first_img.save()

            messages.success(request, f"Listing '{listing.title}' updated successfully.")
            return redirect('product_detail', pk=listing.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ListingForm(instance=listing)

    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'form': form,
        'listing': listing,
        'existing_images': listing.images.all(),
        'categories': categories,
    }
    return render(request, 'edit_listing.html', context)


@login_required
@require_POST
def delete_listing_view(request, pk):
    """
    Delete a listing owned by the authenticated user.
    """
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller != request.user:
        messages.error(request, "You cannot delete a listing you do not own.")
        return redirect('product_detail', pk=listing.pk)

    title = listing.title
    listing.delete()
    messages.success(request, f"Listing '{title}' was permanently deleted.")
    return redirect('my_listings')


@login_required
@require_POST
def mark_sold_view(request, pk):
    """
    Toggle listing status between active and sold.
    """
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller != request.user:
        messages.error(request, "Unauthorized action.")
        return redirect('product_detail', pk=listing.pk)

    if listing.status == 'sold':
        listing.status = 'active'
        messages.success(request, f"Listing '{listing.title}' is now marked as Active!")
    else:
        listing.status = 'sold'
        messages.success(request, f"Listing '{listing.title}' has been marked as Sold.")

    listing.save()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'my_listings'
    return redirect(next_url)


# ==============================================================================
# FAVORITES / WISHLIST
# ==============================================================================

@login_required
def toggle_favorite_view(request, pk):
    """
    Add or remove listing from user favorites.
    Supports both AJAX and standard POST/GET redirects.
    """
    listing = get_object_or_404(Listing, pk=pk)
    fav = Favorite.objects.filter(user=request.user, listing=listing).first()

    if fav:
        fav.delete()
        is_favorited = False
        msg = f"Removed '{listing.title}' from your saved favorites."
    else:
        Favorite.objects.create(user=request.user, listing=listing)
        is_favorited = True
        msg = f"Saved '{listing.title}' to your favorites!"

    total_favs = Favorite.objects.filter(user=request.user).count()

    # If AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'status': 'ok',
            'is_favorited': is_favorited,
            'message': msg,
            'favorites_count': total_favs,
        })

    messages.info(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'product_detail'))


@login_required
def favorites_view(request):
    """
    Display all listings favorited by the logged in user.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'listing', 'listing__category', 'listing__seller'
    ).prefetch_related('listing__images')

    return render(request, 'favorites.html', {'favorites': favorites})


# ==============================================================================
# SELLER MY LISTINGS
# ==============================================================================

@login_required
def my_listings_view(request):
    """
    Manage user's own listings: view, edit, mark sold, delete.
    Filterable by status: all, active, sold, pending.
    """
    status_filter = request.GET.get('status', 'all')
    user_listings = Listing.objects.filter(seller=request.user).select_related('category').prefetch_related('images')

    counts = {
        'all': user_listings.count(),
        'active': user_listings.filter(status='active').count(),
        'sold': user_listings.filter(status='sold').count(),
        'pending': user_listings.filter(status='pending').count(),
    }

    if status_filter in ['active', 'sold', 'pending', 'expired']:
        user_listings = user_listings.filter(status=status_filter)

    user_listings = user_listings.order_by('-created_at')

    context = {
        'listings': user_listings,
        'current_status': status_filter,
        'counts': counts,
    }
    return render(request, 'my_listings.html', context)


# ==============================================================================
# MESSAGING SYSTEM
# ==============================================================================

@login_required
def messages_inbox_view(request):
    """
    Inbox showing all conversations the user is participating in.
    """
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('listing', 'buyer', 'seller', 'buyer__profile', 'seller__profile').prefetch_related('messages')

    # Attach metadata helper for template
    for convo in conversations:
        convo.other_user = convo.seller if convo.buyer == request.user else convo.buyer
        convo.unread_count = convo.unread_count_for_user(request.user)

    context = {
        'conversations': conversations,
        'active_conversation': None,
    }
    return render(request, 'messages.html', context)


@login_required
def conversation_detail_view(request, pk):
    """
    Chat thread for a specific conversation.
    """
    conversation = get_object_or_404(
        Conversation.objects.select_related('listing', 'buyer', 'seller', 'buyer__profile', 'seller__profile'),
        pk=pk
    )

    # Permission check: must be either buyer or seller
    if request.user != conversation.buyer and request.user != conversation.seller:
        messages.error(request, "Access denied to this conversation.")
        return redirect('messages_inbox')

    # Mark unread messages sent by other user as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.save()
            # Update conversation timestamp
            conversation.save()
            messages.success(request, "Message sent!")
            return redirect('conversation_detail', pk=conversation.pk)
    else:
        form = MessageForm()

    all_conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('listing', 'buyer', 'seller').prefetch_related('messages')

    for convo in all_conversations:
        convo.other_user = convo.seller if convo.buyer == request.user else convo.buyer
        convo.unread_count = convo.unread_count_for_user(request.user)

    other_user = conversation.seller if conversation.buyer == request.user else conversation.buyer

    context = {
        'conversations': all_conversations,
        'active_conversation': conversation,
        'messages_list': conversation.messages.all().select_related('sender'),
        'other_user': other_user,
        'message_form': form,
    }
    return render(request, 'messages.html', context)


@login_required
@require_POST
def start_conversation_view(request, pk):
    """
    Initiate a message or contact seller for a listing.
    """
    listing = get_object_or_404(Listing, pk=pk)

    if request.user == listing.seller:
        messages.warning(request, "You cannot message yourself about your own listing.")
        return redirect('product_detail', pk=listing.pk)

    content = request.POST.get('content', '').strip()
    if not content:
        messages.error(request, "Message cannot be empty.")
        return redirect('product_detail', pk=listing.pk)

    conversation, created = Conversation.objects.get_or_create(
        listing=listing,
        buyer=request.user,
        defaults={'seller': listing.seller}
    )

    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    conversation.save()

    messages.success(request, "Your message has been sent to the seller!")
    return redirect('conversation_detail', pk=conversation.pk)


# ==============================================================================
# MAKE AN OFFER SYSTEM
# ==============================================================================

@login_required
@require_POST
def make_offer_view(request, pk):
    """
    Submit a price offer to the seller of a listing.
    """
    listing = get_object_or_404(Listing, pk=pk)

    if request.user == listing.seller:
        messages.warning(request, "You cannot make an offer on your own listing.")
        return redirect('product_detail', pk=listing.pk)

    form = OfferForm(request.POST)
    if form.is_valid():
        offer, created = Offer.objects.update_or_create(
            listing=listing,
            buyer=request.user,
            defaults={
                'seller': listing.seller,
                'offered_price': form.cleaned_data['offered_price'],
                'message': form.cleaned_data.get('message', ''),
                'status': 'pending'
            }
        )
        if created:
            messages.success(request, f"Offer of ${offer.offered_price:,.2f} submitted to {listing.seller.username}!")
        else:
            messages.success(request, f"Your offer on '{listing.title}' was updated to ${offer.offered_price:,.2f}.")
    else:
        for error in form.errors.values():
            messages.error(request, error.as_text())

    return redirect('product_detail', pk=listing.pk)


@login_required
def offers_list_view(request):
    """
    Display offers received by the user (as seller) and offers made (as buyer).
    """
    received_offers = Offer.objects.filter(seller=request.user).select_related(
        'listing', 'buyer', 'buyer__profile'
    ).prefetch_related('listing__images')

    sent_offers = Offer.objects.filter(buyer=request.user).select_related(
        'listing', 'seller', 'seller__profile'
    ).prefetch_related('listing__images')

    context = {
        'received_offers': received_offers,
        'sent_offers': sent_offers,
    }
    return render(request, 'offers.html', context)


@login_required
@require_POST
def offer_action_view(request, pk, action):
    """
    Seller accepts or rejects a buyer's offer.
    """
    offer = get_object_or_404(Offer, pk=pk)

    if request.user != offer.seller:
        messages.error(request, "You can only manage offers for your own listings.")
        return redirect('offers_list')

    if action == 'accept':
        offer.status = 'accepted'
        offer.save()
        messages.success(request, f"You accepted {offer.buyer.username}'s offer of ${offer.offered_price:,.2f}!")
    elif action == 'reject':
        offer.status = 'rejected'
        offer.save()
        messages.info(request, f"Offer from {offer.buyer.username} was rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('offers_list')


# ==============================================================================
# REPORT LISTING
# ==============================================================================

@login_required
@require_POST
def report_listing_view(request, pk):
    """
    Report an inappropriate listing to the administrator.
    """
    listing = get_object_or_404(Listing, pk=pk)
    form = ReportForm(request.POST)

    if form.is_valid():
        report = form.save(commit=False)
        report.listing = listing
        report.reporter = request.user
        report.status = 'pending'
        report.save()
        messages.success(request, "Thank you! Your report has been submitted and will be reviewed by our team.")
    else:
        messages.error(request, "Please choose a reason for reporting.")

    return redirect('product_detail', pk=listing.pk)


# ==============================================================================
# USER AUTHENTICATION & PROFILE
# ==============================================================================

def register_view(request):
    """
    User registration with username, email, password validation.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Log in immediately
            login(request, user)
            messages.success(request, f"Welcome to MarketNest, {user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the requirements below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def user_login_view(request):
    """
    User login supporting username or email.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Allow login by email or username
            user = None
            if '@' in ident:
                found_user = User.objects.filter(email__iexact=ident).first()
                if found_user:
                    user = authenticate(request, username=found_user.username, password=password)
            else:
                user = authenticate(request, username=ident, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next') or request.POST.get('next') or 'home'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def user_logout_view(request):
    """
    Log out the user with confirmation message.
    """
    logout(request)
    messages.info(request, "You have been logged out. See you again soon!")
    return redirect('home')


@login_required
def profile_view(request):
    """
    View and edit current user's profile information.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors in your profile form.")
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    user_listings = Listing.objects.filter(seller=request.user)
    stats = {
        'total_listings': user_listings.count(),
        'active_listings': user_listings.filter(status='active').count(),
        'sold_listings': user_listings.filter(status='sold').count(),
        'favorites_count': Favorite.objects.filter(user=request.user).count(),
        'offers_made': Offer.objects.filter(buyer=request.user).count(),
    }

    context = {
        'form': form,
        'profile': profile,
        'stats': stats,
    }
    return render(request, 'profile.html', context)


def public_profile_view(request, username):
    """
    Public seller profile displaying member info and their active listings.
    """
    seller = get_object_or_404(User.objects.select_related('profile'), username=username)
    seller_listings = Listing.objects.filter(seller=seller, status='active').prefetch_related('images')

    context = {
        'seller': seller,
        'seller_listings': seller_listings,
        'total_active': seller_listings.count(),
    }
    return render(request, 'public_profile.html', context)


# ==============================================================================
# AJAX / API HELPERS
# ==============================================================================

def get_subcategories_api(request, category_id):
    """
    JSON API returning subcategories for a selected category.
    Used by JavaScript in create/edit listing forms.
    """
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

def error_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def error_403_view(request, exception=None):
    return render(request, '403.html', status=403)


def error_500_view(request):
    return render(request, '500.html', status=500)
