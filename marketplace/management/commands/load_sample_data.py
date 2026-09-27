"""
Management command to populate MarketNest with rich categories, subcategories,
realistic demo users, sample listings with generated images, messages, and offers.
Run via: python manage.py load_sample_data
"""
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from marketplace.models import (
    Category,
    SubCategory,
    Profile,
    Listing,
    ListingImage,
    Favorite,
    Conversation,
    Message,
    Offer,
)


def create_sample_image(title, subtitle, category_color=(37, 99, 235), width=800, height=600):
    """
    Generate an attractive, lightweight image using Pillow with modern typography and gradients.
    """
    image = Image.new('RGB', (width, height), color=category_color)
    draw = ImageDraw.Draw(image)

    # Draw gradient or overlay effect
    for y in range(height):
        alpha = int(30 * (y / height))
        draw.line([(0, y), (width, y)], fill=(category_color[0] + alpha, category_color[1] + alpha, min(255, category_color[2] + alpha)))

    # Draw a card container inside
    margin = 40
    card_shape = [margin, margin, width - margin, height - margin]
    draw.rounded_rectangle(card_shape, radius=24, fill=(255, 255, 255, 250), outline=(226, 232, 240), width=3)

    # Simple icon / decorative badge in the center
    badge_box = [width // 2 - 40, height // 2 - 120, width // 2 + 40, height // 2 - 40]
    draw.rounded_rectangle(badge_box, radius=20, fill=category_color)

    # Decorative MarketNest badge
    draw.text((margin + 30, margin + 25), "MarketNest Verified Item", fill=(100, 116, 139))

    # Title text
    words = title.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:8]) if len(words) > 4 else ""

    draw.text((width // 2, height // 2 + 10), line1, fill=(15, 23, 42), anchor="mm")
    if line2:
        draw.text((width // 2, height // 2 + 50), line2, fill=(15, 23, 42), anchor="mm")

    # Subtitle / price / spec text
    draw.text((width // 2, height // 2 + 100), subtitle, fill=(37, 99, 235), anchor="mm")

    # Footer banner
    draw.text((width // 2, height - margin - 35), "Local Buy & Sell Marketplace", fill=(148, 163, 184), anchor="mm")

    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=90)
    return ContentFile(buffer.getvalue(), name=f"{title[:15].lower().replace(' ', '_')}.jpg")


class Command(BaseCommand):
    help = 'Populates the database with realistic sample categories, users, listings, images, offers and chats.'

    def handle(self, *args, **options):
        self.stdout.write("Setting up MarketNest sample data...")

        # 1. Create Superuser 'admin'
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@marketnest.local', 'admin123')
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin123"))
        else:
            admin_user = User.objects.get(username='admin')

        # 2. Create Demo Users
        demo_users_data = [
            {'username': 'rahul_sharma', 'email': 'rahul@example.com', 'name': 'Rahul Sharma', 'location': 'Bandra West, Mumbai', 'phone': '+91 98200 12345', 'bio': 'Tech enthusiast, upgrading gadgets frequently. All items well maintained.'},
            {'username': 'sarah_connor', 'email': 'sarah@example.com', 'name': 'Sarah Connor', 'location': 'Indiranagar, Bangalore', 'phone': '+91 98450 67890', 'bio': 'Interior designer moving to a new home. Selling high quality furniture and decor.'},
            {'username': 'alex_miller', 'email': 'alex@example.com', 'name': 'Alex Miller', 'location': 'Connaught Place, New Delhi', 'phone': '+91 98110 54321', 'bio': 'Student & bibliophile. Selling engineering reference textbooks and cameras.'},
            {'username': 'priya_patel', 'email': 'priya@example.com', 'name': 'Priya Patel', 'location': 'Satellite, Ahmedabad', 'phone': '+91 97230 98765', 'bio': 'Automobile enthusiast and certified electronics technician.'},
        ]

        users = {}
        for udata in demo_users_data:
            user, created = User.objects.get_or_create(
                username=udata['username'],
                defaults={'email': udata['email'], 'first_name': udata['name'].split()[0], 'last_name': udata['name'].split()[-1]}
            )
            if created:
                user.set_password('demo1234')
                user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = udata['phone']
            profile.location = udata['location']
            profile.bio = udata['bio']
            profile.save()
            users[udata['username']] = user

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(users)} demo user accounts (password: demo1234)."))

        # 3. Create Categories & Subcategories
        categories_data = [
            {
                'name': 'Mobiles',
                'slug': 'mobiles',
                'icon': 'smartphone',
                'color': (37, 99, 235),
                'subs': ['Smartphones', 'Tablets', 'Accessories', 'Smart Watches']
            },
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'icon': 'laptop',
                'color': (14, 165, 233),
                'subs': ['Laptops', 'TVs', 'Cameras', 'Computer Accessories', 'Audio & Headphones']
            },
            {
                'name': 'Vehicles',
                'slug': 'vehicles',
                'icon': 'car',
                'color': (249, 115, 22),
                'subs': ['Cars', 'Bikes', 'Scooters', 'Commercial Vehicles', 'Spare Parts']
            },
            {
                'name': 'Property',
                'slug': 'property',
                'icon': 'home',
                'color': (16, 185, 129),
                'subs': ['Houses', 'Apartments', 'Land', 'Commercial Property']
            },
            {
                'name': 'Furniture',
                'slug': 'furniture',
                'icon': 'armchair',
                'color': (139, 92, 246),
                'subs': ['Sofa', 'Beds', 'Tables & Desks', 'Chairs', 'Wardrobes']
            },
            {
                'name': 'Fashion',
                'slug': 'fashion',
                'icon': 'shirt',
                'color': (236, 72, 153),
                'subs': ['Men Clothing', 'Women Clothing', 'Kids Wear', 'Watches & Jewelry']
            },
            {
                'name': 'Books',
                'slug': 'books',
                'icon': 'book',
                'color': (245, 158, 11),
                'subs': ['Academic', 'Competitive Exams', 'Novels', 'Children Books']
            },
            {
                'name': 'Services',
                'slug': 'services',
                'icon': 'wrench',
                'color': (100, 116, 139),
                'subs': ['Electronics Repair', 'Home Services', 'Tuition & Coaching', 'Movers & Packers']
            },
            {
                'name': 'Others',
                'slug': 'others',
                'icon': 'box',
                'color': (71, 85, 105),
                'subs': ['Musical Instruments', 'Sports & Fitness', 'Hobbies & Toys']
            },
        ]

        cat_objs = {}
        sub_objs = {}
        for order_idx, cdata in enumerate(categories_data):
            cat, _ = Category.objects.get_or_create(
                slug=cdata['slug'],
                defaults={'name': cdata['name'], 'icon': cdata['icon'], 'order': order_idx}
            )
            cat_objs[cat.slug] = (cat, cdata['color'])

            for sub_name in cdata['subs']:
                from django.utils.text import slugify
                sub_slug = slugify(sub_name)
                sub, _ = SubCategory.objects.get_or_create(
                    category=cat,
                    slug=sub_slug,
                    defaults={'name': sub_name}
                )
                sub_objs[f"{cat.slug}_{sub_slug}"] = sub

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cat_objs)} categories and their subcategories."))

        # 4. Create Sample Listings
        sample_listings = [
            {
                'title': 'Samsung Galaxy S24 Ultra (512GB Titanium Gray)',
                'cat_slug': 'mobiles',
                'sub_slug': 'smartphones',
                'price': Decimal('899.00'),
                'condition': 'like_new',
                'seller': 'rahul_sharma',
                'location': 'Bandra West, Mumbai',
                'phone': '+91 98200 12345',
                'featured': True,
                'desc': 'Samsung Galaxy S24 Ultra 512GB in pristine Titanium Gray finish.\nUsed for just 3 months with screen protector and case from day one.\nIncludes original box, fast charging cable, S-Pen, and purchase invoice with remaining brand warranty.\nNo scratches or dents whatsoever. Battery health is 100%.\nReason for selling: upgraded to company phone.'
            },
            {
                'title': 'HP Pavilion 15.6 Laptop (Intel Core i7, 16GB, 1TB SSD)',
                'cat_slug': 'electronics',
                'sub_slug': 'laptops',
                'price': Decimal('649.00'),
                'condition': 'good',
                'seller': 'alex_miller',
                'location': 'Connaught Place, New Delhi',
                'phone': '+91 98110 54321',
                'featured': True,
                'desc': 'HP Pavilion 15.6-inch Full HD Laptop.\nSpecs: Intel Core i7 12th Gen, 16GB DDR4 RAM, 1TB NVMe Fast SSD, Backlit Keyboard, Bang & Olufsen Audio.\nPerfect for software development, graphic work, college, and casual gaming.\nComes with original 65W charger and laptop backpack.'
            },
            {
                'title': 'Royal Enfield Classic 350 (Matte Stealth Black)',
                'cat_slug': 'vehicles',
                'sub_slug': 'bikes',
                'price': Decimal('2250.00'),
                'condition': 'like_new',
                'seller': 'priya_patel',
                'location': 'Satellite, Ahmedabad',
                'phone': '+91 97230 98765',
                'featured': True,
                'desc': '2023 Royal Enfield Classic 350 Dual Channel ABS in Matte Stealth Black.\nOnly 8,200 km driven. All regular services done on schedule at authorized service center.\nSingle owner, zero insurance claims, valid comprehensive insurance up to 2027.\nIncludes crash guard, touring seat, and sump guard.'
            },
            {
                'title': 'Solid Sheesham Wooden Study Table & Ergonomic Mesh Chair',
                'cat_slug': 'furniture',
                'sub_slug': 'tables-desks',
                'price': Decimal('195.00'),
                'condition': 'good',
                'seller': 'sarah_connor',
                'location': 'Indiranagar, Bangalore',
                'phone': '+91 98450 67890',
                'featured': True,
                'desc': 'High quality solid Sheesham wood desk with 3 pull-out drawers and cable organizer hole.\nDimensions: 48 inches wide, 24 inches deep, 30 inches high.\nIncludes an ergonomic high-back mesh chair with adjustable lumbar support.\nSelling due to house relocation. Both items are spotless and sturdy.'
            },
            {
                'title': 'Apple iPhone 14 (128GB Starlight White, 94% Battery)',
                'cat_slug': 'mobiles',
                'sub_slug': 'smartphones',
                'price': Decimal('520.00'),
                'condition': 'good',
                'seller': 'rahul_sharma',
                'location': 'Andheri East, Mumbai',
                'phone': '+91 98200 12345',
                'featured': False,
                'desc': 'Apple iPhone 14 128GB in Starlight White color.\nNever repaired, all original parts including display and FaceID working perfectly.\nBattery health 94%. Comes with original box, USB-C to Lightning cable, and 2 Spigen cases.\nClean IMEI and iCloud removed.'
            },
            {
                'title': 'Engineering Mathematics & Computer Science Reference Books',
                'cat_slug': 'books',
                'sub_slug': 'academic',
                'price': Decimal('45.00'),
                'condition': 'like_new',
                'seller': 'alex_miller',
                'location': 'North Campus, New Delhi',
                'phone': '+91 98110 54321',
                'featured': False,
                'desc': 'Complete bundle of top recommended engineering books:\n1. Higher Engineering Mathematics by B.S. Grewal\n2. Introduction to Algorithms (CLRS 3rd Edition)\n3. Operating System Concepts by Silberschatz\n4. Computer Networks by Tanenbaum\nAll books are like new with clean pages, no pen marks or missing leaves.'
            },
            {
                'title': 'Sony Bravia 55-inch 4K Ultra HD Smart Google TV',
                'cat_slug': 'electronics',
                'sub_slug': 'tvs',
                'price': Decimal('499.00'),
                'condition': 'like_new',
                'seller': 'sarah_connor',
                'location': 'Koramangala, Bangalore',
                'phone': '+91 98450 67890',
                'featured': False,
                'desc': 'Sony Bravia 55-inch 4K HDR Smart Google TV (X74K Series).\nFeatures Dolby Audio, Google Assistant voice remote, Apple AirPlay 2, Chromecast built-in.\nRazor sharp 4K picture quality, wall mount bracket and table stands included.'
            },
            {
                'title': 'Canon EOS 1500D DSLR Camera with 18-55mm IS II Lens',
                'cat_slug': 'electronics',
                'sub_slug': 'cameras',
                'price': Decimal('310.00'),
                'condition': 'good',
                'seller': 'alex_miller',
                'location': 'Hauz Khas, New Delhi',
                'phone': '+91 98110 54321',
                'featured': False,
                'desc': 'Canon EOS 1500D 24.1 Megapixel DSLR camera.\nEquipped with DIGIC 4+ processor, Full HD video recording, built-in Wi-Fi and NFC.\nIncludes 18-55mm lens, 32GB high-speed memory card, battery, charger, and Canon camera bag.'
            },
            {
                'title': 'Spacious 2BHK Furnished Apartment for Rent (1150 sq.ft)',
                'cat_slug': 'property',
                'sub_slug': 'apartments',
                'price': Decimal('450.00'),
                'condition': 'new',
                'seller': 'sarah_connor',
                'location': 'Whitefield, Bangalore',
                'phone': '+91 98450 67890',
                'featured': True,
                'desc': 'Beautiful 2 BHK luxury apartment in a gated society with 24/7 security and power backup.\nFeatures 2 bedrooms, 2 bathrooms, 2 balconies with scenic greenery views.\nFurnished with modular kitchen, wardrobes, sofa, dining table, and covered parking slot.'
            },
            {
                'title': 'L-Shape Modern Fabric 5-Seater Living Room Sofa',
                'cat_slug': 'furniture',
                'sub_slug': 'sofa',
                'price': Decimal('280.00'),
                'condition': 'good',
                'seller': 'sarah_connor',
                'location': 'Indiranagar, Bangalore',
                'phone': '+91 98450 67890',
                'featured': False,
                'desc': 'Grey textured fabric L-shaped sectional sofa with high density foam cushions.\nVery comfortable and stain-resistant fabric. Includes 4 decorative cushions.\nOnly 1 year old, selling because we are redesigning the living room.'
            },
            {
                'title': 'Professional Laptop & Smartphone Doorstep Repair Service',
                'cat_slug': 'services',
                'sub_slug': 'electronics-repair',
                'price': Decimal('25.00'),
                'condition': 'new',
                'seller': 'priya_patel',
                'location': 'Vastrapur, Ahmedabad',
                'phone': '+91 97230 98765',
                'featured': False,
                'desc': 'Certified technicians available for doorstep laptop and mobile repair.\nServices include: screen replacement, battery swap, SSD upgrade, thermal paste replacement, OS reinstallation, and liquid spill cleaning.\n30 days service warranty provided on all repairs.'
            },
            {
                'title': 'Yamaha F310 Acoustic Guitar with Padded Gig Bag & Stand',
                'cat_slug': 'others',
                'sub_slug': 'musical-instruments',
                'price': Decimal('115.00'),
                'condition': 'like_new',
                'seller': 'rahul_sharma',
                'location': 'Bandra West, Mumbai',
                'phone': '+91 98200 12345',
                'featured': False,
                'desc': 'Yamaha F310 Natural finish full-size dreadnought acoustic guitar.\nWarm, resonant tone with low action suitable for beginners and seasoned players alike.\nIncludes D\'Addario strings installed, guitar capo, guitar tuner, and heavy-duty padded gig bag.'
            },
        ]

        created_listings = []
        for ldata in sample_listings:
            cat_obj, color = cat_objs[ldata['cat_slug']]
            sub_key = f"{ldata['cat_slug']}_{ldata['sub_slug']}"
            sub_obj = sub_objs.get(sub_key)
            seller_user = users[ldata['seller']]

            listing, created = Listing.objects.get_or_create(
                title=ldata['title'],
                defaults={
                    'category': cat_obj,
                    'subcategory': sub_obj,
                    'seller': seller_user,
                    'price': ldata['price'],
                    'condition': ldata['condition'],
                    'location': ldata['location'],
                    'contact_phone': ldata['phone'],
                    'description': ldata['desc'],
                    'is_featured': ldata['featured'],
                    'status': 'active',
                    'views_count': 32 + (len(ldata['title']) % 40)
                }
            )

            # Generate sample image if none exists
            if created or not listing.images.exists():
                img_file = create_sample_image(
                    title=listing.title,
                    subtitle=f"{listing.formatted_price} • {listing.get_condition_display()} • {listing.location}",
                    category_color=color
                )
                ListingImage.objects.create(
                    listing=listing,
                    image=img_file,
                    is_primary=True
                )

                # Add a second angle image
                img_file_2 = create_sample_image(
                    title=f"{listing.title} - View 2",
                    subtitle="Detailed Condition & Accessories",
                    category_color=color
                )
                ListingImage.objects.create(
                    listing=listing,
                    image=img_file_2,
                    is_primary=False
                )

            created_listings.append(listing)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_listings)} rich sample listings with images."))

        # 5. Create Sample Favorites
        fav_listings = created_listings[:4]
        for item in fav_listings:
            Favorite.objects.get_or_create(user=users['rahul_sharma'], listing=item)
            Favorite.objects.get_or_create(user=admin_user, listing=item)

        # 6. Create Sample Offers
        if len(created_listings) >= 3:
            s24_item = created_listings[0]
            Offer.objects.get_or_create(
                listing=s24_item,
                buyer=users['alex_miller'],
                defaults={
                    'seller': s24_item.seller,
                    'offered_price': Decimal('840.00'),
                    'message': 'Hi Rahul, I can pick it up tomorrow afternoon with instant cash if $840 works for you.',
                    'status': 'pending'
                }
            )

            laptop_item = created_listings[1]
            Offer.objects.get_or_create(
                listing=laptop_item,
                buyer=users['rahul_sharma'],
                defaults={
                    'seller': laptop_item.seller,
                    'offered_price': Decimal('600.00'),
                    'message': 'Can you do $600 for the HP laptop without the bag?',
                    'status': 'accepted'
                }
            )

        # 7. Create Sample Conversations & Messages
        if len(created_listings) >= 2:
            bike_item = created_listings[2]
            convo, _ = Conversation.objects.get_or_create(
                listing=bike_item,
                buyer=users['alex_miller'],
                defaults={'seller': bike_item.seller}
            )
            Message.objects.get_or_create(
                conversation=convo,
                sender=users['alex_miller'],
                defaults={'content': 'Hello Priya! Is the Royal Enfield Classic 350 still available for a test ride?', 'is_read': True}
            )
            Message.objects.get_or_create(
                conversation=convo,
                sender=bike_item.seller,
                defaults={'content': 'Hi Alex, yes! You can visit Satellite, Ahmedabad this weekend between 11 AM and 4 PM.', 'is_read': False}
            )

        self.stdout.write(self.style.SUCCESS("MarketNest sample data initialized successfully!"))
