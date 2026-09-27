"""
Unit and integration tests for MarketNest classified marketplace.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, SubCategory, Listing, Favorite, Offer, Conversation, Message, Report, Profile


class MarketNestTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test users
        self.user1 = User.objects.create_user(username='buyer_user', email='buyer@example.com', password='password123')
        self.user2 = User.objects.create_user(username='seller_user', email='seller@example.com', password='password123')

        # Create Category & Subcategory
        self.cat = Category.objects.create(name='Mobiles', slug='mobiles', icon='smartphone')
        self.subcat = SubCategory.objects.create(category=self.cat, name='Smartphones', slug='smartphones')

        # Create Listing
        self.listing = Listing.objects.create(
            seller=self.user2,
            title='iPhone 13 128GB Midnight',
            description='Good condition iPhone 13 with charger and cover.',
            price=Decimal('450.00'),
            category=self.cat,
            subcategory=self.subcat,
            condition='good',
            location='Downtown, Chicago',
            contact_phone='+1 312 555 0199',
            status='active'
        )

    def test_home_page_status(self):
        """Test homepage loads with 200 OK and contains brand name"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MarketNest')
        self.assertContains(response, 'Buy and Sell')

    def test_browse_page_and_search(self):
        """Test browsing, search keyword filtering, and category filtering"""
        response = self.client.get(reverse('browse'), {'q': 'iPhone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 13 128GB Midnight')

        # Search for non-existent item
        response_empty = self.client.get(reverse('browse'), {'q': 'NonExistentItem999'})
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, 'No Listings Found')

    def test_product_detail_page(self):
        """Test detail page increments view count and displays specs"""
        initial_views = self.listing.views_count
        response = self.client.get(reverse('product_detail', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.views_count, initial_views + 1)

    def test_user_registration_and_login(self):
        """Test user can register, receive profile, and log in"""
        reg_response = self.client.post(reverse('register'), {
            'username': 'new_buyer',
            'email': 'newbuyer@example.com',
            'password': 'safePassword123',
            'confirm_password': 'safePassword123'
        })
        self.assertEqual(reg_response.status_code, 302)
        new_user = User.objects.filter(username='new_buyer').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_create_listing_authenticated(self):
        """Test authenticated user can create a listing"""
        self.client.login(username='seller_user', password='password123')
        response = self.client.post(reverse('create_listing'), {
            'title': 'Sony Wireless Headphones WH-1000XM4',
            'category': self.cat.id,
            'condition': 'like_new',
            'price': '180.00',
            'location': 'New York, NY',
            'contact_phone': '+1 212 555 1234',
            'description': 'Noise cancelling headphones in mint condition with carry case.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Listing.objects.filter(title='Sony Wireless Headphones WH-1000XM4').exists())

    def test_edit_listing_permission(self):
        """Ensure non-owner cannot edit another user's listing"""
        self.client.login(username='buyer_user', password='password123')
        response = self.client.get(reverse('edit_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Redirects with permission error

    def test_favorites_toggle(self):
        """Test authenticated user adding and removing a favorite"""
        self.client.login(username='buyer_user', password='password123')
        # Add to favorites
        response = self.client.post(reverse('toggle_favorite', args=[self.listing.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Favorite.objects.filter(user=self.user1, listing=self.listing).exists())

        # Toggle again to remove
        response_remove = self.client.post(reverse('toggle_favorite', args=[self.listing.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_remove.status_code, 200)
        self.assertFalse(Favorite.objects.filter(user=self.user1, listing=self.listing).exists())

    def test_make_offer(self):
        """Test buyer submitting a price offer on a listing"""
        self.client.login(username='buyer_user', password='password123')
        response = self.client.post(reverse('make_offer', args=[self.listing.id]), {
            'offered_price': '400.00',
            'message': 'Can pick up today with cash.'
        })
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.filter(listing=self.listing, buyer=self.user1).first()
        self.assertIsNotNone(offer)
        self.assertEqual(offer.offered_price, Decimal('400.00'))
        self.assertEqual(offer.status, 'pending')

        # Seller accepts offer
        self.client.login(username='seller_user', password='password123')
        accept_resp = self.client.post(reverse('offer_action', args=[offer.id, 'accept']))
        self.assertEqual(accept_resp.status_code, 302)
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'accepted')

    def test_conversation_and_messaging(self):
        """Test initiating a chat between buyer and seller"""
        self.client.login(username='buyer_user', password='password123')
        response = self.client.post(reverse('start_conversation', args=[self.listing.id]), {
            'content': 'Hi seller, is this still available?'
        })
        self.assertEqual(response.status_code, 302)
        convo = Conversation.objects.filter(listing=self.listing, buyer=self.user1).first()
        self.assertIsNotNone(convo)
        self.assertEqual(convo.messages.count(), 1)
        self.assertEqual(convo.messages.first().content, 'Hi seller, is this still available?')

    def test_report_listing(self):
        """Test reporting an inappropriate advertisement"""
        self.client.login(username='buyer_user', password='password123')
        response = self.client.post(reverse('report_listing', args=[self.listing.id]), {
            'reason': 'spam',
            'description': 'Suspicious external links in description.'
        })
        self.assertEqual(response.status_code, 302)
        report = Report.objects.filter(listing=self.listing, reporter=self.user1).first()
        self.assertIsNotNone(report)
        self.assertEqual(report.reason, 'spam')
