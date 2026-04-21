from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Address, County, DeliveryZone,
    Category, Restaurant, MenuSection, MenuItem, MenuItemOption,
    Cart, CartItem, Order, OrderItem, Coupon
)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class AddressSerializer(serializers.ModelSerializer):
    county_name = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'label', 'street', 'town', 'county', 'county_name', 'is_default']


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ['id', 'name', 'slug', 'code', 'delivery_fee']


class DeliveryZoneSerializer(serializers.ModelSerializer):
    county_name = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'slug', 'county', 'county_name', 'delivery_fee', 'estimated_minutes']


class CategorySerializer(serializers.ModelSerializer):
    restaurant_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'image', 'restaurant_count']

    def get_restaurant_count(self, obj):
        return obj.restaurants.filter(is_active=True).count()


class MenuItemOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemOption
        fields = ['id', 'name', 'price', 'is_required']


class MenuItemSerializer(serializers.ModelSerializer):
    options = MenuItemOptionSerializer(many=True, read_only=True)
    discount_percent = serializers.ReadOnlyField()

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'price', 'compare_price',
            'discount_percent', 'is_available', 'is_popular', 'is_vegetarian', 'is_spicy',
            'calories', 'prep_time', 'options', 'section',
        ]


class MenuSectionSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuSection
        fields = ['id', 'name', 'description', 'items']


class RestaurantListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'logo', 'cover_image', 'category_name', 'zone_name',
            'delivery_fee', 'minimum_order', 'estimated_delivery_time',
            'rating', 'review_count', 'is_open', 'is_featured', 'is_free_delivery',
            'free_delivery_threshold',
        ]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    sections = MenuSectionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_free_delivery = serializers.ReadOnlyField()

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'cover_image',
            'category_name', 'address', 'county', 'zone',
            'delivery_fee', 'minimum_order', 'estimated_delivery_time',
            'free_delivery_threshold', 'is_free_delivery',
            'rating', 'review_count', 'is_open', 'opens_at', 'closes_at',
            'sections',
        ]


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'special_instructions', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    restaurant = RestaurantListSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'restaurant', 'items', 'total', 'item_count']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'item_name', 'item_description', 'quantity', 'unit_price', 'subtotal', 'special_instructions']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_logo = serializers.ImageField(source='restaurant.logo', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'restaurant_name', 'restaurant_logo',
            'delivery_street', 'delivery_town',
            'customer_name', 'customer_email', 'customer_phone',
            'subtotal', 'delivery_fee', 'discount', 'total',
            'payment_method', 'payment_method_display', 'payment_status',
            'estimated_delivery_time', 'notes', 'items', 'created_at',
        ]
        read_only_fields = ['id', 'order_number', 'status', 'subtotal', 'total', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    delivery_street = serializers.CharField()
    delivery_town = serializers.CharField()
    delivery_county_id = serializers.IntegerField()
    delivery_zone_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_instructions = serializers.CharField(required=False, allow_blank=True)
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHODS)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)