from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    preferred_county = models.ForeignKey(
        'core.County', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')
    street = models.CharField(max_length=255)
    town = models.CharField(max_length=100)
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.user.email} - {self.label}'


# ── Location models (moved from pickups into core) ──────────────────

class County(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    code = models.CharField(max_length=5, unique=True)
    is_active = models.BooleanField(default=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=200.00)

    class Meta:
        verbose_name_plural = 'Counties'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DeliveryZone(models.Model):
    """A zone within a county — e.g. Westlands, CBD, Karen"""
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=150.00)
    estimated_minutes = models.PositiveIntegerField(default=30, help_text='Estimated delivery time in minutes')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['county__name', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(f'{self.county.name}-{self.name}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.county.name})'


# ── Restaurant / Store models ─────────────────────────────────────────

class Category(models.Model):
    """Restaurant categories: Fast Food, Pizza, Sushi, Groceries, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class e.g. bi-egg-fried')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """A restaurant or store on the platform"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='restaurants')
    logo = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurants/covers/', blank=True, null=True)

    # Location
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='restaurants')
    zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurants')
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Delivery settings
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    minimum_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_delivery_time = models.PositiveIntegerField(default=30, help_text='Minutes')
    free_delivery_threshold = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    review_count = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    opens_at = models.TimeField(default='08:00')
    closes_at = models.TimeField(default='22:00')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-rating', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_free_delivery(self):
        return self.delivery_fee == 0


class MenuSection(models.Model):
    """Groups menu items: Burgers, Sides, Drinks, Desserts"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.restaurant.name} — {self.name}'


class MenuItem(models.Model):
    """A single item on a restaurant's menu"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    section = models.ForeignKey(MenuSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=300)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    calories = models.PositiveIntegerField(null=True, blank=True)
    prep_time = models.PositiveIntegerField(default=15, help_text='Prep time in minutes')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['section__order', 'order', 'name']
        unique_together = ['restaurant', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} — {self.restaurant.name}'

    @property
    def discount_percent(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0


class MenuItemOption(models.Model):
    """Extras/customisations: e.g. Add cheese, Extra sauce"""
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.item.name} — {self.name}'


# ── Cart ──────────────────────────────────────────────────────────────

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True, unique=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart #{self.id}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        from django.db.models import Sum
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_instructions = models.CharField(max_length=300, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'menu_item']

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.menu_item.name}'


# ── Orders ────────────────────────────────────────────────────────────

import uuid as _uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('on_the_way', 'On the Way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('cod', 'Cash on Delivery'),
    ]

    id = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, related_name='orders')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Delivery address
    delivery_street = models.CharField(max_length=255)
    delivery_town = models.CharField(max_length=100)
    delivery_county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='orders')
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_instructions = models.TextField(blank=True)

    # Customer snapshot
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    payment_status = models.CharField(max_length=20, default='unpaid')
    mpesa_transaction_id = models.CharField(max_length=50, blank=True)

    estimated_delivery_time = models.PositiveIntegerField(default=30)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by('-created_at').first()
            num = 1000
            if last and last.order_number:
                try:
                    num = int(last.order_number.replace('GV', '')) + 1
                except ValueError:
                    num = 1000
            self.order_number = f'GV{num}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.order_number}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=255)
    item_description = models.CharField(max_length=500, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f'{self.quantity}x {self.item_name}'


class Coupon(models.Model):
    DISCOUNT_TYPES = [('percent', 'Percentage'), ('fixed', 'Fixed Amount')]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return self.code