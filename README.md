# MarketNest – A Local Buy & Sell Classified Marketplace

MarketNest is a full-stack classified marketplace web application built with **Python Django, HTML5, CSS3, and Vanilla JavaScript**, backed by an **SQLite** database and managed via **Django Admin**. It enables local communities to buy and sell pre-owned items, interact with sellers, submit price offers, save favorites, and manage their advertisements with zero external framework dependencies.

---

## 🌟 Key Features

### 1. User Authentication & Profile
- **Registration & Login**: Secure account creation with email uniqueness and password validation.
- **User Profiles**: Contact phone number, location, bio, custom avatar uploads, and member join date.
- **Security & Authorization**: Protected routes (`@login_required`), CSRF protection, and strict permission checks preventing unauthorized edits or deletions.

### 2. Homepage & Categories
- **Hero Showcase**: Prominent search bar with keyword query and neighborhood/city selector.
- **Interactive Categories**: Mobiles, Electronics, Vehicles, Property, Furniture, Fashion, Books, Services, and Others with dynamic active listing counters.
- **Featured & Fresh Recommendations**: Showcases verified local listings with badges, prices, and locations.

### 3. Product Listings & Search
- **Comprehensive Listings**: Title, description, price, condition (*New, Like New, Good, Fair, Used*), category & subcategory, location, contact phone, and multiple photo uploads.
- **Advanced Search & Multi-Filter**: Combine keyword searches with category, subcategory, price range (*Min & Max*), condition, location, and sorting (*Newest, Price: Low to High, Price: High to Low, Most Popular*).
- **Pagination**: Clean 12-item pagination preserving all active filter parameters.

### 4. Interactive Product Detail
- **Multi-Image Gallery**: Hero preview display with clickable interactive thumbnails.
- **Direct Seller Inquiries**: Built-in modal chat for contacting sellers.
- **Price Offers / Bargaining**: Buyers can submit custom price offers with personal notes; sellers can accept or reject them.
- **Phone Reveal**: Concealed contact phone number revealed upon user click.
- **Safety Tips & Reporting**: Report system with violation categories reviewed by administrators.
- **Related Products**: Auto-suggested similar listings within the same category.

### 5. Seller Management ("My Listings")
- **Status Filtering**: Filter user ads by *All, Active, Sold, Pending*.
- **Listing Actions**: Direct edit, delete with modal confirmation, and status toggle (*Mark as Sold* / *Mark Active*).

### 6. In-App Messaging System
- **Real-time Conversations**: Clean chat thread layout between buyers and sellers organized per advertisement.
- **Unread Indicators**: Unread badges in navigation header and conversation list; auto-marks messages as read upon viewing.

### 7. Saved Favorites (Wishlist)
- **One-Click AJAX Save**: Heart toggle with smooth animations, instant count updates in header, and fallback support.
- **Favorites Dashboard**: Dedicated view to track and manage saved items.

### 8. Robust Django Admin
- Pre-configured administration panel for Users, Categories, Subcategories, Listings, Images, Offers, Messages, and Reports with custom filters, search fields, editable statuses, and image previews.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+ / Django 5+ / Django 6+ |
| **Database** | SQLite3 |
| **Frontend** | HTML5, Modern Vanilla CSS3 (Custom Design System), Vanilla JavaScript |
| **Image Processing** | Pillow (PIL) |
| **Frameworks** | *No React, No Bootstrap, No Tailwind — 100% Pure Vanilla Web Standards* |

---

## 📁 Project Structure

```
marketnest/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Project dependencies (Django, Pillow)
├── db.sqlite3                         # SQLite database with sample data
├── README.md                          # Documentation
│
├── marketnest/                        # Project configuration
│   ├── __init__.py
│   ├── settings.py                   # App config, media/static, context processors
│   ├── urls.py                       # Root URL routing & media serving
│   ├── wsgi.py
│   └── asgi.py
│
├── marketplace/                       # Core marketplace app
│   ├── migrations/                   # Database migrations
│   │   └── 0001_initial.py
│   ├── templates/                    # Semantic HTML5 templates
│   │   ├── base.html                 # Master layout & navbar
│   │   ├── home.html                 # Homepage with hero & categories
│   │   ├── product_list.html         # Browse, search, filter & pagination
│   │   ├── product_detail.html       # Gallery, seller card, offer & report modals
│   │   ├── create_listing.html       # Multi-image ad posting
│   │   ├── edit_listing.html         # Ad editing & image management
│   │   ├── my_listings.html          # Seller dashboard
│   │   ├── favorites.html            # Saved wishlist
│   │   ├── messages.html             # Buyer-seller chat messenger
│   │   ├── offers.html               # Price offer management
│   │   ├── profile.html              # Account & profile settings
│   │   ├── public_profile.html       # Public seller page
│   │   ├── login.html                # User login
│   │   ├── register.html             # User registration
│   │   ├── 404.html                  # Not found error page
│   │   ├── 403.html                  # Access denied error page
│   │   └── 500.html                  # Server error page
│   │
│   ├── static/                       # Static assets
│   │   ├── css/
│   │   │   └── style.css             # Vanilla CSS design tokens & components
│   │   └── js/
│   │       └── script.js             # Vanilla JS: modals, favorites, image preview
│   │
│   ├── management/
│   │   └── commands/
│   │       └── load_sample_data.py   # Seeder for demo users, categories & listings
│   │
│   ├── models.py                     # Category, Listing, Image, Offer, Message, etc.
│   ├── views.py                      # Full view logic and API handlers
│   ├── urls.py                       # Marketplace clean URLs
│   ├── forms.py                      # ModelForms and input validation
│   ├── admin.py                      # Django Admin registration
│   ├── context_processors.py         # Global navbar badges and category tree
│   ├── tests.py                      # Automated test suite (10 test cases)
│   └── apps.py
│
└── media/                            # User uploads & generated listing images
    └── listings/
```

---

## 🚀 Installation & Setup Guide

### 1. Clone or Open the Project
Open terminal in the project directory:
```bash
cd Antigravity_DEMO
```

### 2. Create and Activate Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load Rich Sample Data (Includes Categories, Users, Ads & Images)
Populate the marketplace with sample data:
```bash
python manage.py load_sample_data
```
This automatically sets up:
- Superuser: `admin` (Password: `admin123`)
- Demo Sellers: `rahul_sharma`, `sarah_connor`, `alex_miller`, `priya_patel` (Password: `demo1234`)
- 9 Primary Categories with Subcategories
- 12 Realistic Listings with generated sample photos, price offers, and chats

### 6. (Optional) Create Custom Superuser Manually
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Default Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| **Superuser / Admin** | `admin` | `admin123` | `admin@marketnest.local` |
| **Seller 1** | `rahul_sharma` | `demo1234` | `rahul@example.com` |
| **Seller 2** | `sarah_connor` | `demo1234` | `sarah@example.com` |
| **Seller 3** | `alex_miller` | `demo1234` | `alex@example.com` |
| **Seller 4** | `priya_patel` | `demo1234` | `priya@example.com` |

- **Django Admin Panel URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Testing Checklist

Run the automated test suite anytime using:
```bash
python manage.py test
```

### Manual Verification Checklist:
- [x] **Homepage**: Hero search with keyword & location autocomplete, categories grid, featured cards, latest recommendations.
- [x] **Search & Multi-Filter**: Search by keyword "Samsung", filter by category "Mobiles", sort by "Price: High to Low".
- [x] **Product Detail**: Thumbnail switching gallery, view counter increment, condition badge, phone number reveal toggle.
- [x] **Buyer Actions**: Modal contact seller dialog, make price offer modal, report listing dialog.
- [x] **Seller Actions**: Post an ad with multiple photos and live previews, edit existing ad, delete ad with modal confirmation, mark ad as sold.
- [x] **Chat Messenger**: View message threads, send reply, automatic unread message badge count.
- [x] **Price Offers**: Tabular view of received & sent offers, instant Accept/Reject actions for sellers.
- [x] **Wishlist**: Click heart on any card to save/unsave; verify counter updates in header.
- [x] **Profile**: Edit phone number, location, bio, and avatar.

---

## 🔮 Future Enhancements
- Integration of map pins (Leaflet / OpenStreetMap) for visual radius search.
- In-browser push notifications or email alerts for new offers and messages.
- Rating and review system for verified buyers and sellers.
- Listing bump/boost premium featured promotions.
