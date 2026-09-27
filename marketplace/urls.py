"""
URL configuration for marketplace app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home & Browsing
    path('', views.home_view, name='home'),
    path('browse/', views.browse_view, name='browse'),
    path('category/<slug:slug>/', views.category_view, name='category_listings'),

    # Listings CRUD & Actions
    path('listing/create/', views.create_listing_view, name='create_listing'),
    path('listing/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('listing/<int:pk>/edit/', views.edit_listing_view, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing_view, name='delete_listing'),
    path('listing/<int:pk>/mark-sold/', views.mark_sold_view, name='mark_sold'),
    path('listing/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('listing/<int:pk>/offer/', views.make_offer_view, name='make_offer'),
    path('listing/<int:pk>/message/', views.start_conversation_view, name='start_conversation'),
    path('listing/<int:pk>/report/', views.report_listing_view, name='report_listing'),

    # User Seller Center & Favorites
    path('my-listings/', views.my_listings_view, name='my_listings'),
    path('favorites/', views.favorites_view, name='favorites'),

    # Messaging System
    path('messages/', views.messages_inbox_view, name='messages_inbox'),
    path('messages/<int:pk>/', views.conversation_detail_view, name='conversation_detail'),

    # Offers System
    path('offers/', views.offers_list_view, name='offers_list'),
    path('offers/<int:pk>/<str:action>/', views.offer_action_view, name='offer_action'),

    # Authentication & User Profile
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('seller/<str:username>/', views.public_profile_view, name='public_profile'),

    # API Endpoints
    path('api/subcategories/<int:category_id>/', views.get_subcategories_api, name='api_subcategories'),
]
