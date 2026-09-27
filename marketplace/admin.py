"""
Django Admin configuration for MarketNest models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category,
    SubCategory,
    Profile,
    Listing,
    ListingImage,
    Favorite,
    Conversation,
    Message,
    Offer,
    Report,
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'subcategories_count', 'listings_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    inlines = [SubCategoryInline]

    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'Subcategories'

    def listings_count(self, obj):
        return obj.listings.count()
    listings_count.short_description = 'Total Listings'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'listings_count')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'name')

    def listings_count(self, obj):
        return obj.listings.count()
    listings_count.short_description = 'Listings'


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;" />', obj.image.url)
        return "No Image"


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail', 'seller', 'category', 'price', 'condition', 'status', 'is_featured', 'views_count', 'created_at')
    list_filter = ('status', 'is_featured', 'condition', 'category', 'created_at')
    search_fields = ('title', 'description', 'location', 'seller__username', 'seller__email')
    ordering = ('-created_at',)
    list_editable = ('status', 'is_featured')
    inlines = [ListingImageInline]
    date_hierarchy = 'created_at'

    def thumbnail(self, obj):
        img_url = obj.primary_image_url
        if img_url:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', img_url)
        return "-"
    thumbnail.short_description = 'Thumb'


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'is_primary', 'created_at', 'preview')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('listing__title',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px;" />', obj.image.url)
        return "-"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'location')
    ordering = ('-created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title')
    ordering = ('-created_at',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'is_read', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'seller', 'messages_count', 'updated_at', 'created_at')
    list_filter = ('updated_at', 'created_at')
    search_fields = ('listing__title', 'buyer__username', 'seller__username')
    ordering = ('-updated_at',)
    inlines = [MessageInline]

    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'content_snippet', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'content', 'conversation__listing__title')
    ordering = ('-created_at',)

    def content_snippet(self, obj):
        return obj.content[:60] + ('...' if len(obj.content) > 60 else '')
    content_snippet.short_description = 'Snippet'


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('listing', 'buyer', 'seller', 'offered_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('listing__title', 'buyer__username', 'seller__username')
    list_editable = ('status',)
    ordering = ('-created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('listing', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('listing__title', 'reporter__username', 'description')
    list_editable = ('status',)
    ordering = ('-created_at',)
