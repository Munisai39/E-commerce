"""
Context processors for MarketNest.
Injects categories and notification counts globally across all templates.
"""
from .models import Category, Favorite, Message, Offer


def marketplace_context(request):
    context = {
        'all_categories': Category.objects.all()[:10],
        'favorites_count': 0,
        'unread_messages_count': 0,
        'pending_offers_count': 0,
    }

    if request.user.is_authenticated:
        context['favorites_count'] = Favorite.objects.filter(user=request.user).count()
        context['unread_messages_count'] = Message.objects.filter(
            conversation__in=request.user.buyer_conversations.all() | request.user.seller_conversations.all(),
            is_read=False
        ).exclude(sender=request.user).count()
        context['pending_offers_count'] = Offer.objects.filter(
            seller=request.user,
            status='pending'
        ).count()

    return context
