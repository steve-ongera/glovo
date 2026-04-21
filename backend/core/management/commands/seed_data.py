"""
python manage.py seed_data

Populates the database with:
  - 8 Counties (Kenyan)
  - 24 Delivery zones
  - 10 Categories
  - 12 Restaurants
  - 60+ Menu items across sections
  - 5 Coupons
  - 2 Demo users

Images are fetched from Unsplash (no API key required).
To use your local Jumia images instead, replace the image-download
helper at the bottom with one that copies from your local path, e.g.:
    shutil.copy(r'D:\\gadaf\\Documents\\images\\jumia\\burger.jpg', dest)
"""

import os
import io
import random
import shutil
import urllib.request
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


# ─────────────────────────────────────────────
#  Unsplash "source" URLs — direct image CDN
#  Format: https://source.unsplash.com/{width}x{height}/?{keyword}
#  Each URL streams a random relevant image (no key needed).
# ─────────────────────────────────────────────

def unsplash(keyword, w=800, h=600, seed=None):
    """Return an Unsplash source URL for a keyword."""
    q = f"{keyword},{seed}" if seed else keyword
    return f"https://source.unsplash.com/{w}x{h}/?{q}"


def fetch_image(url, filename):
    """Download an image from `url` and return (filename, ContentFile)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        return filename, ContentFile(data)
    except Exception as e:
        print(f"    ⚠  Could not fetch {url}: {e}")
        return None, None


# ─────────────────────────────────────────────
#  Seed data definitions
# ─────────────────────────────────────────────

COUNTIES = [
    {"name": "Nairobi",      "code": "NBI",  "delivery_fee": "150.00"},
    {"name": "Mombasa",      "code": "MBA",  "delivery_fee": "180.00"},
    {"name": "Kisumu",       "code": "KSM",  "delivery_fee": "200.00"},
    {"name": "Nakuru",       "code": "NKR",  "delivery_fee": "200.00"},
    {"name": "Eldoret",      "code": "ELD",  "delivery_fee": "220.00"},
    {"name": "Thika",        "code": "THK",  "delivery_fee": "180.00"},
    {"name": "Machakos",     "code": "MCH",  "delivery_fee": "200.00"},
    {"name": "Kiambu",       "code": "KBU",  "delivery_fee": "170.00"},
]

ZONES = {
    "Nairobi": [
        ("Westlands",   "120.00", 25),
        ("CBD",         "100.00", 20),
        ("Karen",       "180.00", 40),
        ("Kilimani",    "130.00", 25),
        ("Eastlands",   "150.00", 35),
        ("Langata",     "160.00", 35),
        ("Kasarani",    "170.00", 40),
        ("Gigiri",      "140.00", 30),
    ],
    "Mombasa": [
        ("Nyali",       "140.00", 30),
        ("Bamburi",     "160.00", 35),
        ("Likoni",      "180.00", 45),
        ("Mtwapa",      "200.00", 50),
    ],
    "Kisumu": [
        ("Milimani",    "150.00", 30),
        ("Kondele",     "160.00", 35),
        ("Mamboleo",    "180.00", 40),
    ],
    "Nakuru": [
        ("Section 58",  "160.00", 35),
        ("Milimani",    "150.00", 30),
        ("Pipeline",    "170.00", 40),
    ],
    "Eldoret": [
        ("Town Centre", "150.00", 30),
        ("Langas",      "180.00", 40),
    ],
    "Thika": [
        ("Town Centre", "150.00", 30),
        ("Thika Road",  "160.00", 35),
    ],
    "Kiambu": [
        ("Ruiru",       "160.00", 35),
        ("Juja",        "170.00", 40),
    ],
}

CATEGORIES = [
    {"name": "Fast Food",      "icon": "bi-egg-fried",          "kw": "fast food burger"},
    {"name": "Pizza",          "icon": "bi-pizza",              "kw": "pizza"},
    {"name": "Sushi & Asian",  "icon": "bi-cup-hot",            "kw": "sushi japanese food"},
    {"name": "Groceries",      "icon": "bi-basket2-fill",       "kw": "grocery supermarket"},
    {"name": "Chicken",        "icon": "bi-fire",               "kw": "fried chicken"},
    {"name": "Burgers",        "icon": "bi-bag-fill",           "kw": "gourmet burger"},
    {"name": "Healthy",        "icon": "bi-heart-pulse-fill",   "kw": "healthy salad bowl"},
    {"name": "Desserts",       "icon": "bi-cake2-fill",         "kw": "dessert cake pastry"},
    {"name": "Drinks",         "icon": "bi-cup-straw",          "kw": "drinks smoothie juice"},
    {"name": "Local Cuisine",  "icon": "bi-flower1",            "kw": "kenyan ugali nyama choma"},
]

RESTAURANTS = [
    {
        "name": "Burger Palace",
        "category": "Burgers",
        "county": "Nairobi",
        "zone": "Westlands",
        "address": "Westlands Avenue, Nairobi",
        "delivery_fee": "100.00",
        "minimum_order": "500.00",
        "estimated_delivery_time": 30,
        "free_delivery_threshold": "2000.00",
        "rating": "4.7",
        "review_count": 342,
        "is_featured": True,
        "cover_kw": "burger restaurant",
        "logo_kw": "burger logo food",
        "sections": [
            {
                "name": "Signature Burgers",
                "items": [
                    {"name": "Classic Smash Burger",      "price": "650",  "compare": "800",  "desc": "Double smash patty, American cheese, special sauce, brioche bun", "popular": True,  "kw": "smash burger"},
                    {"name": "BBQ Bacon Burger",          "price": "750",  "compare": None,   "desc": "Smoky BBQ sauce, crispy bacon, cheddar, caramelised onions",       "popular": True,  "kw": "bbq bacon burger"},
                    {"name": "Mushroom Swiss Burger",     "price": "700",  "compare": None,   "desc": "Sautéed mushrooms, Swiss cheese, garlic aioli",                    "popular": False, "kw": "mushroom burger"},
                    {"name": "Spicy Jalapeño Burger",     "price": "680",  "compare": "750",  "desc": "Fresh jalapeños, pepper jack cheese, chipotle mayo",               "popular": False, "kw": "spicy burger jalapeno", "spicy": True},
                    {"name": "Veggie Black Bean Burger",  "price": "600",  "compare": None,   "desc": "House-made black bean patty, avocado, fresh salsa",                "popular": False, "kw": "veggie burger", "veg": True},
                ]
            },
            {
                "name": "Sides & Fries",
                "items": [
                    {"name": "Loaded Cheese Fries",   "price": "350", "compare": None,  "desc": "Crispy fries, nacho cheese sauce, jalapeños, sour cream", "popular": True,  "kw": "cheese fries loaded"},
                    {"name": "Onion Rings",            "price": "280", "compare": None,  "desc": "Beer-battered golden onion rings with dipping sauce",     "popular": False, "kw": "onion rings"},
                    {"name": "Coleslaw",               "price": "180", "compare": None,  "desc": "Creamy homemade coleslaw",                                "popular": False, "kw": "coleslaw side dish"},
                    {"name": "Sweet Potato Fries",     "price": "300", "compare": None,  "desc": "Oven-baked sweet potato fries with sriracha dip",         "popular": False, "kw": "sweet potato fries"},
                ]
            },
            {
                "name": "Drinks",
                "items": [
                    {"name": "Chocolate Milkshake",  "price": "350", "compare": None, "desc": "Thick creamy chocolate milkshake with whipped cream", "popular": True,  "kw": "chocolate milkshake"},
                    {"name": "Strawberry Lemonade",  "price": "280", "compare": None, "desc": "Fresh strawberries, lemon juice, sparkling water",     "popular": False, "kw": "strawberry lemonade"},
                    {"name": "Iced Coffee",          "price": "300", "compare": None, "desc": "Cold brew iced coffee with oat milk",                  "popular": False, "kw": "iced coffee cold brew"},
                ]
            },
        ]
    },
    {
        "name": "Pizza Roma",
        "category": "Pizza",
        "county": "Nairobi",
        "zone": "Kilimani",
        "address": "Ngong Road, Kilimani, Nairobi",
        "delivery_fee": "120.00",
        "minimum_order": "600.00",
        "estimated_delivery_time": 40,
        "free_delivery_threshold": "2500.00",
        "rating": "4.5",
        "review_count": 218,
        "is_featured": True,
        "cover_kw": "pizza restaurant italy",
        "logo_kw": "pizza logo",
        "sections": [
            {
                "name": "Classic Pizzas",
                "items": [
                    {"name": "Margherita",          "price": "850",  "compare": None,   "desc": "San Marzano tomato, fresh mozzarella, basil, EVOO", "popular": True,  "kw": "margherita pizza", "veg": True},
                    {"name": "Pepperoni Supreme",   "price": "1050", "compare": "1200", "desc": "Double pepperoni, mozzarella, oregano",             "popular": True,  "kw": "pepperoni pizza"},
                    {"name": "BBQ Chicken",         "price": "1100", "compare": None,   "desc": "Smoky BBQ sauce, grilled chicken, red onion, corn", "popular": False, "kw": "bbq chicken pizza"},
                    {"name": "Four Cheese",         "price": "1000", "compare": None,   "desc": "Mozzarella, cheddar, parmesan, gorgonzola blend",   "popular": False, "kw": "four cheese pizza", "veg": True},
                    {"name": "Veggie Delight",      "price": "900",  "compare": None,   "desc": "Roasted peppers, mushrooms, olives, spinach",       "popular": False, "kw": "veggie pizza", "veg": True},
                ]
            },
            {
                "name": "Pasta",
                "items": [
                    {"name": "Spaghetti Bolognese",  "price": "750", "compare": None,  "desc": "Slow-cooked beef ragù, parmesan, fresh pasta",    "popular": True,  "kw": "spaghetti bolognese"},
                    {"name": "Penne Arrabbiata",     "price": "700", "compare": None,  "desc": "Spicy tomato sauce, garlic, fresh chilli",        "popular": False, "kw": "penne arrabbiata", "veg": True, "spicy": True},
                    {"name": "Creamy Chicken Pasta", "price": "850", "compare": None,  "desc": "Grilled chicken, cream sauce, mushrooms, spinach", "popular": True,  "kw": "creamy chicken pasta"},
                ]
            },
            {
                "name": "Starters & Sides",
                "items": [
                    {"name": "Garlic Bread",        "price": "350", "compare": None, "desc": "Toasted ciabatta with garlic butter and herbs",  "popular": True,  "kw": "garlic bread"},
                    {"name": "Caesar Salad",        "price": "550", "compare": None, "desc": "Romaine, croutons, parmesan, house Caesar dressing", "popular": False, "kw": "caesar salad"},
                    {"name": "Bruschetta",          "price": "400", "compare": None, "desc": "Tomato, basil, garlic on grilled bread",         "popular": False, "kw": "bruschetta appetizer", "veg": True},
                ]
            },
        ]
    },
    {
        "name": "KFC Westlands",
        "category": "Chicken",
        "county": "Nairobi",
        "zone": "Westlands",
        "address": "Ring Road Westlands, Nairobi",
        "delivery_fee": "80.00",
        "minimum_order": "400.00",
        "estimated_delivery_time": 25,
        "free_delivery_threshold": "1500.00",
        "rating": "4.3",
        "review_count": 521,
        "is_featured": False,
        "cover_kw": "fried chicken restaurant",
        "logo_kw": "fried chicken logo",
        "sections": [
            {
                "name": "Chicken",
                "items": [
                    {"name": "Original Recipe 2pc",  "price": "580", "compare": None,  "desc": "2 pieces of KFC original recipe chicken",             "popular": True,  "kw": "original fried chicken"},
                    {"name": "Crispy Strips (5pc)",  "price": "650", "compare": "720", "desc": "Tender crispy chicken strips with dipping sauce",      "popular": True,  "kw": "chicken strips crispy"},
                    {"name": "Hot & Spicy 2pc",      "price": "600", "compare": None,  "desc": "Hot & spicy coating on classic recipe chicken",        "popular": False, "kw": "spicy fried chicken", "spicy": True},
                    {"name": "Zinger Burger",        "price": "550", "compare": "620", "desc": "Crispy chicken fillet, lettuce, spicy mayo in a bun",  "popular": True,  "kw": "zinger chicken burger"},
                ]
            },
            {
                "name": "Sides & Combos",
                "items": [
                    {"name": "Large Fries",         "price": "250", "compare": None, "desc": "Crispy golden fries, lightly salted",             "popular": False, "kw": "french fries"},
                    {"name": "Coleslaw",            "price": "180", "compare": None, "desc": "KFC's signature creamy coleslaw",                 "popular": False, "kw": "coleslaw"},
                    {"name": "Mashed Potato",       "price": "200", "compare": None, "desc": "Creamy mashed potato with gravy",                 "popular": True,  "kw": "mashed potato gravy"},
                    {"name": "Streetwise 2 Combo",  "price": "680", "compare": "750","desc": "2pc chicken + fries + drink",                     "popular": True,  "kw": "chicken combo meal"},
                ]
            },
        ]
    },
    {
        "name": "Sushi Garden",
        "category": "Sushi & Asian",
        "county": "Nairobi",
        "zone": "CBD",
        "address": "Kenyatta Avenue, Nairobi CBD",
        "delivery_fee": "150.00",
        "minimum_order": "1000.00",
        "estimated_delivery_time": 45,
        "free_delivery_threshold": "3000.00",
        "rating": "4.8",
        "review_count": 189,
        "is_featured": True,
        "cover_kw": "sushi restaurant japanese",
        "logo_kw": "sushi logo",
        "sections": [
            {
                "name": "Rolls",
                "items": [
                    {"name": "California Roll (8pc)",  "price": "850",  "compare": None,   "desc": "Crab, avocado, cucumber, sesame seeds",           "popular": True,  "kw": "california roll sushi"},
                    {"name": "Spicy Tuna Roll (8pc)",  "price": "950",  "compare": "1100", "desc": "Spicy tuna, sriracha mayo, cucumber",             "popular": True,  "kw": "spicy tuna roll", "spicy": True},
                    {"name": "Dragon Roll (8pc)",      "price": "1200", "compare": None,   "desc": "Shrimp tempura inside, avocado on top",           "popular": True,  "kw": "dragon roll sushi"},
                    {"name": "Vegetable Roll (8pc)",   "price": "700",  "compare": None,   "desc": "Cucumber, avocado, carrot, pickled radish",       "popular": False, "kw": "vegetable sushi roll", "veg": True},
                ]
            },
            {
                "name": "Nigiri & Sashimi",
                "items": [
                    {"name": "Salmon Nigiri (2pc)",   "price": "600", "compare": None, "desc": "Fresh Atlantic salmon over seasoned sushi rice",  "popular": True,  "kw": "salmon nigiri"},
                    {"name": "Tuna Sashimi (5pc)",    "price": "900", "compare": None, "desc": "Premium bluefin tuna, thinly sliced",             "popular": False, "kw": "tuna sashimi"},
                    {"name": "Ebi Prawn Nigiri (2pc)","price": "550", "compare": None, "desc": "Tiger prawn over hand-pressed sushi rice",        "popular": False, "kw": "prawn shrimp sushi"},
                ]
            },
            {
                "name": "Starters",
                "items": [
                    {"name": "Edamame",           "price": "300", "compare": None, "desc": "Steamed salted edamame beans",                 "popular": False, "kw": "edamame", "veg": True},
                    {"name": "Miso Soup",         "price": "250", "compare": None, "desc": "Traditional Japanese miso with tofu and nori", "popular": True,  "kw": "miso soup", "veg": True},
                    {"name": "Gyoza (6pc)",       "price": "550", "compare": None, "desc": "Pan-fried pork & cabbage dumplings",           "popular": True,  "kw": "gyoza dumplings"},
                ]
            },
        ]
    },
    {
        "name": "Mama's Kitchen",
        "category": "Local Cuisine",
        "county": "Nairobi",
        "zone": "Eastlands",
        "address": "Jogoo Road, Eastlands, Nairobi",
        "delivery_fee": "80.00",
        "minimum_order": "300.00",
        "estimated_delivery_time": 30,
        "free_delivery_threshold": "1200.00",
        "rating": "4.6",
        "review_count": 634,
        "is_featured": True,
        "cover_kw": "kenyan food restaurant nyama",
        "logo_kw": "kenyan food logo",
        "sections": [
            {
                "name": "Main Course",
                "items": [
                    {"name": "Nyama Choma (500g)",     "price": "950",  "compare": None,  "desc": "Roasted goat ribs, served with kachumbari and ugali",              "popular": True,  "kw": "nyama choma goat"},
                    {"name": "Ugali & Beef Stew",      "price": "380",  "compare": None,  "desc": "Kenyan staple — white ugali with rich slow-cooked beef stew",     "popular": True,  "kw": "ugali beef stew"},
                    {"name": "Chicken Stew & Rice",    "price": "420",  "compare": "480", "desc": "Tender chicken in tomato-onion stew, served with pilau rice",    "popular": True,  "kw": "chicken stew rice"},
                    {"name": "Matoke",                 "price": "320",  "compare": None,  "desc": "Steamed green bananas in coconut curry — homestyle",             "popular": False, "kw": "matoke plantain", "veg": True},
                    {"name": "Fish Fry (Tilapia)",     "price": "700",  "compare": None,  "desc": "Whole fried Nile tilapia with ugali, sukuma and kachumbari",      "popular": True,  "kw": "fried tilapia fish"},
                    {"name": "Githeri Special",        "price": "280",  "compare": None,  "desc": "Mixed beans and maize, cooked with spices and vegetables",        "popular": False, "kw": "githeri beans corn", "veg": True},
                ]
            },
            {
                "name": "Sides & Extras",
                "items": [
                    {"name": "Chapati (2pc)",       "price": "80",  "compare": None, "desc": "Soft hand-rolled Kenyan chapati",               "popular": True,  "kw": "chapati flatbread"},
                    {"name": "Kachumbari",          "price": "100", "compare": None, "desc": "Fresh tomato, onion, coriander salad",          "popular": False, "kw": "kachumbari salad", "veg": True},
                    {"name": "Sukuma Wiki",         "price": "120", "compare": None, "desc": "Sautéed collard greens with onion and tomato",  "popular": False, "kw": "sukuma wiki greens", "veg": True},
                ]
            },
            {
                "name": "Drinks",
                "items": [
                    {"name": "Dawa Cocktail",    "price": "350", "compare": None, "desc": "Vodka, lime, honey — the classic Kenyan dawa", "popular": True,  "kw": "dawa cocktail lime"},
                    {"name": "Tangawizi Juice",  "price": "200", "compare": None, "desc": "Freshly pressed ginger-lemon juice",            "popular": False, "kw": "ginger juice drink", "veg": True},
                    {"name": "Mango Madafu",     "price": "250", "compare": None, "desc": "Coconut water blended with fresh mango",        "popular": True,  "kw": "coconut mango drink", "veg": True},
                ]
            },
        ]
    },
    {
        "name": "Green Bowl",
        "category": "Healthy",
        "county": "Nairobi",
        "zone": "Gigiri",
        "address": "UN Crescent, Gigiri, Nairobi",
        "delivery_fee": "130.00",
        "minimum_order": "700.00",
        "estimated_delivery_time": 30,
        "free_delivery_threshold": "2500.00",
        "rating": "4.4",
        "review_count": 156,
        "is_featured": False,
        "cover_kw": "healthy food restaurant salad",
        "logo_kw": "healthy food logo green",
        "sections": [
            {
                "name": "Power Bowls",
                "items": [
                    {"name": "Acai Superfood Bowl",      "price": "850",  "compare": None,   "desc": "Acai base, granola, banana, berries, honey drizzle",    "popular": True,  "kw": "acai bowl superfood", "veg": True},
                    {"name": "Quinoa Protein Bowl",      "price": "900",  "compare": "1050", "desc": "Quinoa, grilled chicken, roasted veg, tahini dressing", "popular": True,  "kw": "quinoa bowl protein"},
                    {"name": "Buddha Bowl",              "price": "850",  "compare": None,   "desc": "Brown rice, chickpeas, avocado, roasted sweet potato",  "popular": False, "kw": "buddha bowl vegan", "veg": True},
                    {"name": "Chicken & Kale Caesar",    "price": "800",  "compare": None,   "desc": "Grilled chicken, kale, parmesan, Caesar dressing",      "popular": False, "kw": "chicken kale salad"},
                ]
            },
            {
                "name": "Cold Press Juices",
                "items": [
                    {"name": "Green Detox Juice",   "price": "400", "compare": None, "desc": "Spinach, cucumber, green apple, ginger, lemon",  "popular": True,  "kw": "green detox juice", "veg": True},
                    {"name": "Sunrise Blend",       "price": "380", "compare": None, "desc": "Carrot, orange, turmeric, pineapple",             "popular": False, "kw": "orange carrot juice", "veg": True},
                    {"name": "Beet & Berry Boost",  "price": "420", "compare": None, "desc": "Beetroot, blueberry, ginger, lemon juice",       "popular": False, "kw": "beet juice smoothie", "veg": True},
                ]
            },
        ]
    },
    {
        "name": "Sweet Tooth Bakery",
        "category": "Desserts",
        "county": "Nairobi",
        "zone": "Karen",
        "address": "Karen Road, Karen, Nairobi",
        "delivery_fee": "150.00",
        "minimum_order": "500.00",
        "estimated_delivery_time": 35,
        "free_delivery_threshold": "2000.00",
        "rating": "4.9",
        "review_count": 287,
        "is_featured": True,
        "cover_kw": "bakery pastry dessert",
        "logo_kw": "bakery logo cake",
        "sections": [
            {
                "name": "Cakes & Slices",
                "items": [
                    {"name": "Red Velvet Slice",         "price": "450", "compare": None,  "desc": "Moist red velvet cake with cream cheese frosting",      "popular": True,  "kw": "red velvet cake slice", "veg": True},
                    {"name": "Belgian Choc Lava Cake",   "price": "550", "compare": "650", "desc": "Warm chocolate lava cake, vanilla ice cream, berries",  "popular": True,  "kw": "chocolate lava cake", "veg": True},
                    {"name": "Cheesecake Slice",         "price": "480", "compare": None,  "desc": "Classic New York cheesecake with strawberry compote",   "popular": True,  "kw": "new york cheesecake", "veg": True},
                    {"name": "Carrot Walnut Cake",       "price": "420", "compare": None,  "desc": "Spiced carrot cake with cream cheese and walnuts",      "popular": False, "kw": "carrot walnut cake", "veg": True},
                ]
            },
            {
                "name": "Pastries & Cookies",
                "items": [
                    {"name": "Croissant (Butter)",     "price": "280", "compare": None, "desc": "Classic flaky French butter croissant",         "popular": True,  "kw": "butter croissant pastry", "veg": True},
                    {"name": "Cinnamon Roll",          "price": "320", "compare": None, "desc": "Warm cinnamon roll with cream cheese glaze",    "popular": True,  "kw": "cinnamon roll bun", "veg": True},
                    {"name": "Chocolate Chip Cookie",  "price": "180", "compare": None, "desc": "Soft-baked, chunky chocolate chip cookies",     "popular": False, "kw": "chocolate chip cookie", "veg": True},
                ]
            },
        ]
    },
    {
        "name": "Nairobi Grill House",
        "category": "Fast Food",
        "county": "Nairobi",
        "zone": "Langata",
        "address": "Langata Road, Nairobi",
        "delivery_fee": "100.00",
        "minimum_order": "500.00",
        "estimated_delivery_time": 35,
        "free_delivery_threshold": "2000.00",
        "rating": "4.2",
        "review_count": 198,
        "is_featured": False,
        "cover_kw": "grill house barbecue restaurant",
        "logo_kw": "grill bbq logo",
        "sections": [
            {
                "name": "Grills",
                "items": [
                    {"name": "Mixed Grill Platter",   "price": "1500", "compare": None,   "desc": "Beef, chicken & lamb kebabs, served with salad and chips",  "popular": True,  "kw": "mixed grill platter"},
                    {"name": "Ribeye Steak (200g)",   "price": "1800", "compare": "2000", "desc": "Angus ribeye, chimichurri, roasted garlic butter",          "popular": True,  "kw": "ribeye steak grill"},
                    {"name": "Lamb Chops (3pc)",      "price": "1400", "compare": None,   "desc": "Marinated lamb chops, harissa, mint sauce",                 "popular": False, "kw": "lamb chops grill"},
                    {"name": "Grilled Whole Fish",    "price": "1200", "compare": None,   "desc": "Whole tilapia, lemon herb butter, grilled plantain",        "popular": False, "kw": "grilled whole fish"},
                ]
            },
            {
                "name": "Wraps & Burgers",
                "items": [
                    {"name": "Chicken Shawarma Wrap", "price": "580", "compare": "650", "desc": "Grilled chicken, garlic sauce, pickles, chips in lavash",  "popular": True,  "kw": "chicken shawarma wrap"},
                    {"name": "Beef Shawarma",         "price": "620", "compare": None,  "desc": "Marinated beef strips, tahini, fresh veg",                "popular": True,  "kw": "beef shawarma"},
                    {"name": "Club Sandwich",         "price": "550", "compare": None,  "desc": "Triple-decker chicken, bacon, egg, lettuce, tomato",      "popular": False, "kw": "club sandwich"},
                ]
            },
        ]
    },
    {
        "name": "Mombasa Biryani House",
        "category": "Local Cuisine",
        "county": "Mombasa",
        "zone": "Nyali",
        "address": "Nyali Bridge Road, Mombasa",
        "delivery_fee": "120.00",
        "minimum_order": "400.00",
        "estimated_delivery_time": 40,
        "free_delivery_threshold": None,
        "rating": "4.7",
        "review_count": 412,
        "is_featured": True,
        "cover_kw": "biryani rice indian food",
        "logo_kw": "biryani logo spice",
        "sections": [
            {
                "name": "Biryani",
                "items": [
                    {"name": "Chicken Biryani",    "price": "650",  "compare": None,   "desc": "Fragrant basmati, whole spices, raita, fried onions",       "popular": True,  "kw": "chicken biryani"},
                    {"name": "Beef Biryani",       "price": "750",  "compare": "850",  "desc": "Slow-cooked beef, saffron basmati, boiled egg",            "popular": True,  "kw": "beef biryani"},
                    {"name": "Vegetable Biryani",  "price": "550",  "compare": None,   "desc": "Mixed vegetable biryani with mint raita",                  "popular": False, "kw": "vegetable biryani", "veg": True},
                    {"name": "Prawn Biryani",      "price": "900",  "compare": "1000", "desc": "Tiger prawns, coastal spices, coconut basmati",            "popular": True,  "kw": "prawn biryani seafood"},
                ]
            },
            {
                "name": "Coastal Dishes",
                "items": [
                    {"name": "Pilau Mbuzi",       "price": "850", "compare": None, "desc": "Goat pilau rice with whole spices and kachumbari",    "popular": True,  "kw": "pilau rice kenyan"},
                    {"name": "Coconut Fish Curry", "price": "750", "compare": None, "desc": "Fresh catch in coconut-tamarind curry, chapati",      "popular": True,  "kw": "fish coconut curry"},
                    {"name": "Urojo Mix",          "price": "350", "compare": None, "desc": "Mombasa mix — coconut broth, bhajia, coconut chutney","popular": False, "kw": "urojo mix soup"},
                ]
            },
        ]
    },
    {
        "name": "Nakuru Fast Bites",
        "category": "Fast Food",
        "county": "Nakuru",
        "zone": "Section 58",
        "address": "Section 58, Nakuru Town",
        "delivery_fee": "100.00",
        "minimum_order": "300.00",
        "estimated_delivery_time": 25,
        "free_delivery_threshold": "1500.00",
        "rating": "4.0",
        "review_count": 88,
        "is_featured": False,
        "cover_kw": "fast food restaurant counter",
        "logo_kw": "fast food logo icon",
        "sections": [
            {
                "name": "Snacks",
                "items": [
                    {"name": "Chicken Samosa (3pc)",    "price": "180", "compare": None,  "desc": "Crispy samosas stuffed with spiced chicken",          "popular": True,  "kw": "chicken samosa"},
                    {"name": "Beef Mandazi (4pc)",      "price": "120", "compare": None,  "desc": "Fluffy East African fried dough with beef filling",   "popular": False, "kw": "mandazi african pastry"},
                    {"name": "Chips Masala",            "price": "200", "compare": None,  "desc": "Crispy chips tossed in masala spices",               "popular": True,  "kw": "masala chips fries", "spicy": True},
                    {"name": "Smokies & Kachumbari",    "price": "150", "compare": None,  "desc": "Grilled beef smokies, fresh kachumbari, chilli sauce","popular": True,  "kw": "smokies sausage kenyan"},
                ]
            },
        ]
    },
    {
        "name": "Kisumu Lakeside Grill",
        "category": "Local Cuisine",
        "county": "Kisumu",
        "zone": "Milimani",
        "address": "Oginga Odinga Street, Kisumu",
        "delivery_fee": "150.00",
        "minimum_order": "500.00",
        "estimated_delivery_time": 35,
        "free_delivery_threshold": None,
        "rating": "4.5",
        "review_count": 203,
        "is_featured": False,
        "cover_kw": "lake victoria fish grill",
        "logo_kw": "fish grill logo lakeside",
        "sections": [
            {
                "name": "Lake Victoria Specials",
                "items": [
                    {"name": "Fried Whole Tilapia",   "price": "750",  "compare": None,   "desc": "Lake Victoria tilapia, ugali, sukuma, kachumbari",        "popular": True,  "kw": "fried tilapia whole"},
                    {"name": "Grilled Omena",         "price": "350",  "compare": None,   "desc": "Sun-dried silver cyprinid, pan-fried with tomato sauce",  "popular": False, "kw": "omena silver fish"},
                    {"name": "Catfish Stew",          "price": "680",  "compare": "750",  "desc": "Slow-cooked catfish in rich tomato-coconut stew",         "popular": True,  "kw": "catfish stew african"},
                    {"name": "Grilled Nile Perch",    "price": "900",  "compare": None,   "desc": "Giant Nile perch, lemon herb marinade, pilau rice",       "popular": True,  "kw": "nile perch grilled"},
                ]
            },
        ]
    },
    {
        "name": "QuickMart Express",
        "category": "Groceries",
        "county": "Kiambu",
        "zone": "Ruiru",
        "address": "Thika Road, Ruiru",
        "delivery_fee": "100.00",
        "minimum_order": "500.00",
        "estimated_delivery_time": 60,
        "free_delivery_threshold": "3000.00",
        "rating": "3.9",
        "review_count": 144,
        "is_featured": False,
        "cover_kw": "grocery supermarket store",
        "logo_kw": "grocery store logo",
        "sections": [
            {
                "name": "Fresh Produce",
                "items": [
                    {"name": "Tomatoes (1kg)",      "price": "80",  "compare": None,  "desc": "Fresh ripe tomatoes, farm to door",          "popular": True,  "kw": "fresh tomatoes", "veg": True},
                    {"name": "Avocados (3pc)",      "price": "120", "compare": None,  "desc": "Ripe Kenyan Hass avocados",                  "popular": True,  "kw": "avocado fresh", "veg": True},
                    {"name": "Sukuma Wiki (bunch)",  "price": "50",  "compare": None,  "desc": "Fresh collard greens, ready to cook",        "popular": False, "kw": "collard greens vegetable", "veg": True},
                    {"name": "Spinach (bunch)",      "price": "50",  "compare": None,  "desc": "Fresh baby spinach",                         "popular": False, "kw": "spinach green", "veg": True},
                ]
            },
            {
                "name": "Dairy & Eggs",
                "items": [
                    {"name": "Brookside Milk (1L)",  "price": "85",  "compare": None, "desc": "Fresh full-cream Brookside milk",          "popular": True,  "kw": "milk carton dairy"},
                    {"name": "Eggs Tray (30pc)",     "price": "480", "compare": "520","desc": "Free-range eggs, 30-piece tray",           "popular": True,  "kw": "eggs tray free range"},
                    {"name": "KCC Butter (250g)",    "price": "250", "compare": None, "desc": "KCC salted butter block",                  "popular": False, "kw": "butter dairy"},
                ]
            },
            {
                "name": "Pantry Essentials",
                "items": [
                    {"name": "Unga Duma (2kg)",     "price": "180", "compare": None,  "desc": "Unga Duma maize meal, 2kg pack",          "popular": True,  "kw": "maize flour ugali"},
                    {"name": "Cooking Oil (1L)",    "price": "320", "compare": "360", "desc": "Elianto vegetable cooking oil, 1 litre",  "popular": True,  "kw": "cooking oil bottle"},
                    {"name": "Sugar (2kg)",         "price": "260", "compare": None,  "desc": "Mumias white refined sugar, 2kg pack",    "popular": False, "kw": "sugar packet white"},
                ]
            },
        ]
    },
]

COUPONS = [
    {
        "code": "WELCOME20",
        "discount_type": "percent",
        "discount_value": "20.00",
        "minimum_order": "500.00",
        "usage_limit": 1000,
        "valid_from": timezone.now(),
        "valid_until": timezone.now() + datetime.timedelta(days=365),
    },
    {
        "code": "FIRSTORDER",
        "discount_type": "fixed",
        "discount_value": "200.00",
        "minimum_order": "800.00",
        "usage_limit": 500,
        "valid_from": timezone.now(),
        "valid_until": timezone.now() + datetime.timedelta(days=180),
    },
    {
        "code": "FREEDEL",
        "discount_type": "fixed",
        "discount_value": "150.00",
        "minimum_order": "600.00",
        "usage_limit": 200,
        "valid_from": timezone.now(),
        "valid_until": timezone.now() + datetime.timedelta(days=90),
    },
    {
        "code": "FRIDAY50",
        "discount_type": "percent",
        "discount_value": "50.00",
        "minimum_order": "1500.00",
        "usage_limit": 100,
        "valid_from": timezone.now(),
        "valid_until": timezone.now() + datetime.timedelta(days=30),
    },
    {
        "code": "FESTIVE",
        "discount_type": "fixed",
        "discount_value": "500.00",
        "minimum_order": "2000.00",
        "usage_limit": 50,
        "valid_from": timezone.now(),
        "valid_until": timezone.now() + datetime.timedelta(days=60),
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo data for Glovoke'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-images',
            action='store_true',
            help='Skip downloading images (faster, for CI/testing)',
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before seeding (careful!)',
        )

    def handle(self, *args, **options):
        from core.models import (
            County, DeliveryZone, Category, Restaurant,
            MenuSection, MenuItem, Coupon,
        )

        no_images = options['no_images']

        if options['flush']:
            self.stdout.write(self.style.WARNING('⚠  Flushing existing data...'))
            MenuItem.objects.all().delete()
            MenuSection.objects.all().delete()
            Restaurant.objects.all().delete()
            Category.objects.all().delete()
            DeliveryZone.objects.all().delete()
            County.objects.all().delete()
            Coupon.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓  Flushed'))

        # ── 1. Counties ───────────────────────────────────────
        self.stdout.write('\n📍 Seeding Counties...')
        county_map = {}
        for c in COUNTIES:
            obj, created = County.objects.get_or_create(
                code=c['code'],
                defaults={
                    'name': c['name'],
                    'slug': slugify(c['name']),
                    'delivery_fee': Decimal(c['delivery_fee']),
                    'is_active': True,
                }
            )
            county_map[c['name']] = obj
            self.stdout.write(f"  {'✓' if created else '·'} {obj.name}")

        # ── 2. Delivery Zones ─────────────────────────────────
        self.stdout.write('\n🗺  Seeding Delivery Zones...')
        zone_map = {}  # (county_name, zone_name) -> obj
        for county_name, zones in ZONES.items():
            county = county_map.get(county_name)
            if not county:
                continue
            for zone_name, fee, minutes in zones:
                slug = slugify(f'{county_name}-{zone_name}')
                obj, created = DeliveryZone.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'county': county,
                        'name': zone_name,
                        'delivery_fee': Decimal(fee),
                        'estimated_minutes': minutes,
                        'is_active': True,
                    }
                )
                zone_map[(county_name, zone_name)] = obj
                self.stdout.write(f"  {'✓' if created else '·'} {county_name} › {zone_name}")

        # ── 3. Categories ─────────────────────────────────────
        self.stdout.write('\n🏷  Seeding Categories...')
        category_map = {}
        for i, cat in enumerate(CATEGORIES):
            obj, created = Category.objects.get_or_create(
                slug=slugify(cat['name']),
                defaults={
                    'name': cat['name'],
                    'icon': cat['icon'],
                    'order': i,
                    'is_active': True,
                }
            )
            if created and not no_images:
                self.stdout.write(f"    📸 Fetching category image for {cat['name']}...")
                fname, content = fetch_image(
                    unsplash(cat['kw'], 400, 300, seed=i),
                    f"cat_{slugify(cat['name'])}.jpg"
                )
                if content:
                    obj.image.save(fname, content, save=True)

            category_map[cat['name']] = obj
            self.stdout.write(f"  {'✓' if created else '·'} {obj.name}")

        # ── 4. Restaurants ────────────────────────────────────
        self.stdout.write('\n🍽  Seeding Restaurants & Menus...')
        for r_data in RESTAURANTS:
            county = county_map.get(r_data['county'])
            zone = zone_map.get((r_data['county'], r_data['zone']))
            category = category_map.get(r_data['category'])

            slug = slugify(r_data['name'])
            rest, r_created = Restaurant.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': r_data['name'],
                    'description': f"Welcome to {r_data['name']} — {r_data['category']} at its finest.",
                    'category': category,
                    'county': county,
                    'zone': zone,
                    'address': r_data['address'],
                    'delivery_fee': Decimal(r_data['delivery_fee']),
                    'minimum_order': Decimal(r_data['minimum_order']),
                    'estimated_delivery_time': r_data['estimated_delivery_time'],
                    'free_delivery_threshold': Decimal(r_data['free_delivery_threshold']) if r_data.get('free_delivery_threshold') else None,
                    'rating': Decimal(r_data['rating']),
                    'review_count': r_data['review_count'],
                    'is_featured': r_data.get('is_featured', False),
                    'is_active': True,
                    'is_open': True,
                    'opens_at': datetime.time(8, 0),
                    'closes_at': datetime.time(22, 0),
                }
            )

            if r_created and not no_images:
                self.stdout.write(f"    📸 Fetching restaurant images for {rest.name}...")
                # Cover image
                fname, content = fetch_image(
                    unsplash(r_data['cover_kw'], 1200, 600, seed=slug),
                    f"cover_{slug}.jpg"
                )
                if content:
                    rest.cover_image.save(fname, content, save=False)
                # Logo
                fname2, content2 = fetch_image(
                    unsplash(r_data['logo_kw'], 300, 300, seed=f"{slug}_logo"),
                    f"logo_{slug}.jpg"
                )
                if content2:
                    rest.logo.save(fname2, content2, save=False)
                rest.save()

            self.stdout.write(f"  {'✓' if r_created else '·'} {rest.name}")

            # Sections & Items
            for s_idx, section_data in enumerate(r_data.get('sections', [])):
                section, _ = MenuSection.objects.get_or_create(
                    restaurant=rest,
                    name=section_data['name'],
                    defaults={'order': s_idx, 'is_active': True}
                )

                for i_idx, item_data in enumerate(section_data.get('items', [])):
                    item_slug = slugify(item_data['name'])
                    item, i_created = MenuItem.objects.get_or_create(
                        restaurant=rest,
                        slug=item_slug,
                        defaults={
                            'section': section,
                            'name': item_data['name'],
                            'description': item_data.get('desc', ''),
                            'price': Decimal(item_data['price']),
                            'compare_price': Decimal(item_data['compare']) if item_data.get('compare') else None,
                            'is_available': True,
                            'is_popular': item_data.get('popular', False),
                            'is_vegetarian': item_data.get('veg', False),
                            'is_spicy': item_data.get('spicy', False),
                            'order': i_idx,
                            'prep_time': random.randint(10, 25),
                            'calories': random.randint(200, 900) if random.random() > 0.4 else None,
                        }
                    )

                    if i_created and not no_images:
                        kw = item_data.get('kw', item_data['name'])
                        fname, content = fetch_image(
                            unsplash(kw, 600, 400, seed=f"{slug}_{item_slug}"),
                            f"menu_{slug}_{item_slug}.jpg"
                        )
                        if content:
                            item.image.save(fname, content, save=True)

                    self.stdout.write(f"      {'·' if not i_created else '+'} {item.name}")

        # ── 5. Coupons ────────────────────────────────────────
        self.stdout.write('\n🎟  Seeding Coupons...')
        from core.models import Coupon
        for c in COUPONS:
            obj, created = Coupon.objects.get_or_create(
                code=c['code'],
                defaults=c,
            )
            self.stdout.write(f"  {'✓' if created else '·'} {obj.code}")

        # ── 6. Demo users ─────────────────────────────────────
        self.stdout.write('\n👤 Seeding Demo Users...')
        if not User.objects.filter(email='admin@glovoke.com').exists():
            User.objects.create_superuser(
                email='admin@glovoke.com',
                password='admin1234',
                first_name='Admin',
                last_name='Glovoke',
            )
            self.stdout.write('  ✓ admin@glovoke.com  (password: admin1234)')

        if not User.objects.filter(email='demo@glovoke.com').exists():
            User.objects.create_user(
                email='demo@glovoke.com',
                password='demo1234',
                first_name='Demo',
                last_name='User',
                phone='+254712345678',
                preferred_county=county_map.get('Nairobi'),
            )
            self.stdout.write('  ✓ demo@glovoke.com   (password: demo1234)')

        # ── Done ──────────────────────────────────────────────
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(
            '🎉  Seed complete!\n'
            f'    Counties   : {County.objects.count()}\n'
            f'    Zones      : {DeliveryZone.objects.count()}\n'
            f'    Categories : {Category.objects.count()}\n'
            f'    Restaurants: {Restaurant.objects.count()}\n'
            f'    Menu items : {MenuItem.objects.count()}\n'
            f'    Coupons    : {Coupon.objects.count()}\n'
            f'    Users      : {User.objects.count()}\n'
        ))

        if no_images:
            self.stdout.write(self.style.WARNING(
                '    ⚠  Images were skipped (--no-images flag). '
                'Run without the flag to download them.'
            ))

        self.stdout.write(self.style.HTTP_INFO(
            '\n💡 To use your local Jumia images instead of Unsplash:\n'
            '   Replace the fetch_image() call in the items loop with:\n'
            '     src = r"D:\\gadaf\\Documents\\images\\jumia\\<filename>.jpg"\n'
            '     with open(src, "rb") as f:\n'
            '         item.image.save(os.path.basename(src), ContentFile(f.read()), save=True)\n'
        ))