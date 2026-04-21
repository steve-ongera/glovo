from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils import timezone

from .models import (
    User, Address,
    County, DeliveryZone,
    Category, Restaurant, MenuSection, MenuItem, MenuItemOption,
    Cart, CartItem,
    Order, OrderItem,
    Coupon,
)


# ─────────────────────────────────────────────────────────────
#  Site header
# ─────────────────────────────────────────────────────────────

admin.site.site_header  = '🛵 Glovoke Admin'
admin.site.site_title   = 'Glovoke'
admin.site.index_title  = 'Dashboard'


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def thumb(image_field, size=48):
    """Render a small thumbnail for an ImageField."""
    if image_field:
        return format_html(
            '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;'
            'border-radius:6px;border:1px solid #e5e7eb;" />',
            image_field.url, size, size,
        )
    return '—'


def status_badge(text, colour):
    """Render a coloured pill badge."""
    return format_html(
        '<span style="background:{};color:#fff;padding:3px 10px;border-radius:50px;'
        'font-size:11px;font-weight:700;">{}</span>',
        colour, text,
    )


ORDER_STATUS_COLOURS = {
    'pending':    '#f59e0b',
    'confirmed':  '#3b82f6',
    'preparing':  '#8b5cf6',
    'ready':      '#06b6d4',
    'on_the_way': '#f97316',
    'delivered':  '#22c55e',
    'cancelled':  '#ef4444',
}


# ─────────────────────────────────────────────────────────────
#  User
# ─────────────────────────────────────────────────────────────

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('label', 'street', 'town', 'county', 'is_default')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-date_joined',)
    list_display  = ('email', 'full_name', 'phone', 'avatar_thumb', 'preferred_county', 'is_active', 'is_staff', 'date_joined')
    list_filter   = ('is_active', 'is_staff', 'is_superuser', 'preferred_county')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('date_joined', 'last_login', 'avatar_thumb')
    inlines = [AddressInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'avatar_thumb', 'preferred_county')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates'), {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Avatar')
    def avatar_thumb(self, obj):
        return thumb(obj.avatar, 40)

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.get_full_name()


# ─────────────────────────────────────────────────────────────
#  Location
# ─────────────────────────────────────────────────────────────

class DeliveryZoneInline(admin.TabularInline):
    model = DeliveryZone
    extra = 0
    fields = ('name', 'delivery_fee', 'estimated_minutes', 'is_active')


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'slug', 'delivery_fee', 'zone_count', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DeliveryZoneInline]

    @admin.display(description='Zones')
    def zone_count(self, obj):
        return obj.zones.count()


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display  = ('name', 'county', 'delivery_fee', 'estimated_minutes', 'is_active')
    list_filter   = ('is_active', 'county')
    search_fields = ('name', 'county__name')
    prepopulated_fields = {'slug': ('name',)}


# ─────────────────────────────────────────────────────────────
#  Category
# ─────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('image_thumb', 'name', 'slug', 'icon', 'restaurant_count', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Image')
    def image_thumb(self, obj):
        return thumb(obj.image, 40)

    @admin.display(description='Restaurants')
    def restaurant_count(self, obj):
        return obj.restaurants.filter(is_active=True).count()


# ─────────────────────────────────────────────────────────────
#  Restaurant
# ─────────────────────────────────────────────────────────────

class MenuSectionInline(admin.TabularInline):
    model = MenuSection
    extra = 0
    fields = ('name', 'description', 'order', 'is_active')
    show_change_link = True


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display  = (
        'logo_thumb', 'name', 'category', 'county', 'zone',
        'delivery_fee', 'minimum_order', 'rating', 'review_count',
        'is_open', 'is_featured', 'is_active',
    )
    list_filter   = ('is_active', 'is_open', 'is_featured', 'category', 'county')
    list_editable = ('is_open', 'is_featured', 'is_active')
    search_fields = ('name', 'address')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields  = ('logo_thumb', 'cover_thumb', 'created_at')
    inlines = [MenuSectionInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'category'),
        }),
        ('Images', {
            'fields': ('logo', 'logo_thumb', 'cover_image', 'cover_thumb'),
        }),
        ('Location', {
            'fields': ('county', 'zone', 'address', 'latitude', 'longitude'),
        }),
        ('Delivery Settings', {
            'fields': (
                'delivery_fee', 'minimum_order',
                'estimated_delivery_time', 'free_delivery_threshold',
            ),
        }),
        ('Ratings & Status', {
            'fields': (
                'rating', 'review_count',
                'is_active', 'is_featured', 'is_open',
                'opens_at', 'closes_at',
            ),
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Logo')
    def logo_thumb(self, obj):
        return thumb(obj.logo, 44)

    @admin.display(description='Cover')
    def cover_thumb(self, obj):
        return thumb(obj.cover_image, 120)


# ─────────────────────────────────────────────────────────────
#  Menu Section & Items
# ─────────────────────────────────────────────────────────────

class MenuItemOptionInline(admin.TabularInline):
    model = MenuItemOption
    extra = 1
    fields = ('name', 'price', 'is_required')


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('name', 'price', 'compare_price', 'is_available', 'is_popular', 'order')
    show_change_link = True


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'restaurant', 'item_count', 'order', 'is_active')
    list_filter   = ('is_active', 'restaurant')
    search_fields = ('name', 'restaurant__name')
    list_editable = ('order', 'is_active')
    inlines = [MenuItemInline]

    @admin.display(description='Items')
    def item_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = (
        'image_thumb', 'name', 'restaurant', 'section',
        'price', 'compare_price', 'discount_badge',
        'is_popular', 'is_vegetarian', 'is_spicy', 'is_available',
    )
    list_filter   = ('is_available', 'is_popular', 'is_vegetarian', 'is_spicy', 'restaurant', 'section')
    list_editable = ('price', 'is_available', 'is_popular')
    search_fields = ('name', 'restaurant__name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_thumb', 'discount_badge')
    inlines = [MenuItemOptionInline]

    fieldsets = (
        ('Item Info', {
            'fields': ('restaurant', 'section', 'name', 'slug', 'description', 'image', 'image_thumb'),
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'discount_badge'),
        }),
        ('Attributes', {
            'fields': ('is_available', 'is_popular', 'is_vegetarian', 'is_spicy', 'calories', 'prep_time', 'order'),
        }),
    )

    @admin.display(description='Image')
    def image_thumb(self, obj):
        return thumb(obj.image, 44)

    @admin.display(description='Discount')
    def discount_badge(self, obj):
        pct = obj.discount_percent
        if pct:
            return format_html(
                '<span style="background:#ef4444;color:#fff;padding:2px 8px;'
                'border-radius:50px;font-size:11px;font-weight:700;">-{}%</span>', pct
            )
        return '—'


# ─────────────────────────────────────────────────────────────
#  Cart
# ─────────────────────────────────────────────────────────────

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('menu_item', 'quantity', 'subtotal', 'special_instructions', 'added_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'session_key', 'restaurant', 'item_count_display', 'total_display', 'updated_at')
    list_filter   = ('restaurant',)
    search_fields = ('user__email', 'session_key')
    readonly_fields = ('total_display', 'item_count_display', 'created_at', 'updated_at')
    inlines = [CartItemInline]

    @admin.display(description='Items')
    def item_count_display(self, obj):
        return obj.item_count

    @admin.display(description='Total')
    def total_display(self, obj):
        return f'Ksh {obj.total:,.2f}'


# ─────────────────────────────────────────────────────────────
#  Orders
# ─────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('item_name', 'quantity', 'unit_price', 'subtotal', 'special_instructions')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = (
        'order_number', 'customer_name', 'customer_phone',
        'restaurant', 'status_badge_display', 'payment_method',
        'payment_status_display', 'total_display', 'created_at',
    )
    list_filter   = ('status', 'payment_method', 'payment_status', 'restaurant', 'delivery_county')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'mpesa_transaction_id')
    readonly_fields = (
        'id', 'order_number', 'subtotal', 'total', 'created_at', 'updated_at',
        'confirmed_at', 'delivered_at',
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('id', 'order_number', 'user', 'restaurant', 'status', 'notes'),
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
        }),
        ('Delivery Address', {
            'fields': ('delivery_street', 'delivery_town', 'delivery_county', 'delivery_zone', 'delivery_instructions'),
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'discount', 'total'),
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'mpesa_transaction_id'),
        }),
        ('Timing', {
            'fields': ('estimated_delivery_time', 'created_at', 'updated_at', 'confirmed_at', 'delivered_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_confirmed', 'mark_preparing', 'mark_on_the_way', 'mark_delivered', 'mark_cancelled']

    @admin.display(description='Status')
    def status_badge_display(self, obj):
        colour = ORDER_STATUS_COLOURS.get(obj.status, '#6b7280')
        return status_badge(obj.get_status_display(), colour)

    @admin.display(description='Payment')
    def payment_status_display(self, obj):
        colour = '#22c55e' if obj.payment_status == 'paid' else '#f59e0b'
        return status_badge(obj.payment_status.upper(), colour)

    @admin.display(description='Total')
    def total_display(self, obj):
        return f'Ksh {obj.total:,.2f}'

    # ── Bulk actions ──────────────────────────────────────────
    def _bulk_status(self, request, queryset, new_status, label):
        extra = {}
        if new_status == 'confirmed':
            extra['confirmed_at'] = timezone.now()
        if new_status == 'delivered':
            extra['delivered_at'] = timezone.now()
        updated = queryset.update(status=new_status, **extra)
        self.message_user(request, f'{updated} order(s) marked as {label}.')

    @admin.action(description='✅ Mark as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._bulk_status(request, queryset, 'confirmed', 'Confirmed')

    @admin.action(description='🍳 Mark as Preparing')
    def mark_preparing(self, request, queryset):
        self._bulk_status(request, queryset, 'preparing', 'Preparing')

    @admin.action(description='🛵 Mark as On the Way')
    def mark_on_the_way(self, request, queryset):
        self._bulk_status(request, queryset, 'on_the_way', 'On the Way')

    @admin.action(description='📦 Mark as Delivered')
    def mark_delivered(self, request, queryset):
        self._bulk_status(request, queryset, 'delivered', 'Delivered')

    @admin.action(description='❌ Mark as Cancelled')
    def mark_cancelled(self, request, queryset):
        self._bulk_status(request, queryset, 'cancelled', 'Cancelled')


# ─────────────────────────────────────────────────────────────
#  Coupon
# ─────────────────────────────────────────────────────────────

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display  = (
        'code', 'discount_type', 'discount_value', 'minimum_order',
        'times_used', 'usage_limit', 'usage_bar', 'is_active',
        'valid_from', 'valid_until', 'is_expired',
    )
    list_filter   = ('is_active', 'discount_type')
    search_fields = ('code',)
    list_editable = ('is_active',)
    readonly_fields = ('times_used',)

    @admin.display(description='Usage')
    def usage_bar(self, obj):
        if not obj.usage_limit:
            return f'{obj.times_used} / ∞'
        pct = int((obj.times_used / obj.usage_limit) * 100)
        colour = '#22c55e' if pct < 70 else '#f59e0b' if pct < 90 else '#ef4444'
        return format_html(
            '<div style="display:flex;align-items:center;gap:6px;">'
            '<div style="width:80px;height:8px;background:#e5e7eb;border-radius:99px;overflow:hidden;">'
            '<div style="width:{}%;height:100%;background:{};border-radius:99px;"></div>'
            '</div>'
            '<span style="font-size:11px;color:#6b7280;">{}/{}</span>'
            '</div>',
            min(pct, 100), colour, obj.times_used, obj.usage_limit,
        )

    @admin.display(description='Expired', boolean=True)
    def is_expired(self, obj):
        return timezone.now() > obj.valid_until