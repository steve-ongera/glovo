from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.utils import timezone

from .models import (
    User, Address, County, DeliveryZone,
    Category, Restaurant, MenuItem,
    Cart, CartItem, Order, OrderItem, Coupon
)
from .serializers import (
    UserSerializer, RegisterSerializer, AddressSerializer,
    CountySerializer, DeliveryZoneSerializer, CategorySerializer,
    RestaurantListSerializer, RestaurantDetailSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, CreateOrderSerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ── Location ──────────────────────────────────────────────────────────

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CountySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return County.objects.filter(is_active=True)


class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryZoneSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = DeliveryZone.objects.filter(is_active=True).select_related('county')
        county_id = self.request.query_params.get('county_id')
        if county_id:
            qs = qs.filter(county_id=county_id)
        return qs


# ── Catalogue ─────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantListSerializer

    def get_queryset(self):
        qs = Restaurant.objects.filter(is_active=True).select_related('category', 'zone')
        category = self.request.query_params.get('category')
        county_id = self.request.query_params.get('county_id')
        zone_id = self.request.query_params.get('zone_id')
        search = self.request.query_params.get('search')
        featured = self.request.query_params.get('featured')

        if category:
            qs = qs.filter(category__slug=category)
        if county_id:
            qs = qs.filter(county_id=county_id)
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        if search:
            qs = qs.filter(name__icontains=search)
        if featured:
            qs = qs.filter(is_featured=True)
        return qs

    def get_object(self):
        # Allow lookup by slug or id
        lookup = self.kwargs.get(self.lookup_field)
        try:
            return Restaurant.objects.get(slug=lookup)
        except Restaurant.DoesNotExist:
            return Restaurant.objects.get(id=lookup)


# ── Cart ──────────────────────────────────────────────────────────────

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def _get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def list(self, request):
        cart = self._get_cart(request)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self._get_cart(request)
        menu_item_id = request.data.get('menu_item_id')
        quantity = int(request.data.get('quantity', 1))
        instructions = request.data.get('special_instructions', '')

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, is_available=True)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Item not found or unavailable'}, status=404)

        # Enforce single-restaurant cart
        if cart.restaurant and cart.restaurant != menu_item.restaurant:
            return Response({
                'error': 'Your cart has items from another restaurant. Clear your cart first.',
                'conflict': True,
            }, status=status.HTTP_409_CONFLICT)

        cart.restaurant = menu_item.restaurant
        cart.save()

        item, created = CartItem.objects.get_or_create(
            cart=cart, menu_item=menu_item,
            defaults={'quantity': quantity, 'special_instructions': instructions}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        cart = self._get_cart(request)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()

        # Clear restaurant ref if cart empty
        if not cart.items.exists():
            cart.restaurant = None
            cart.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self._get_cart(request)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        code = request.data.get('code', '')
        cart = self._get_cart(request)
        try:
            coupon = Coupon.objects.get(
                code__iexact=code, is_active=True,
                valid_from__lte=timezone.now(), valid_until__gte=timezone.now()
            )
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid or expired coupon'}, status=400)

        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            return Response({'error': 'Coupon usage limit reached'}, status=400)

        if cart.total < coupon.minimum_order:
            return Response({'error': f'Minimum order of Ksh {coupon.minimum_order} required'}, status=400)

        discount = float(coupon.discount_value)
        if coupon.discount_type == 'percent':
            discount = (float(coupon.discount_value) / 100) * float(cart.total)

        return Response({'discount': discount, 'coupon_code': code})


# ── Orders ────────────────────────────────────────────────────────────

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    @transaction.atomic
    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            # Try session cart
            session_key = request.session.session_key
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key).first()
                if session_cart and session_cart.items.exists():
                    session_cart.user = request.user
                    session_cart.session_key = None
                    session_cart.save()
                    cart = session_cart

        if not cart or not cart.items.exists():
            return Response({'error': 'Your cart is empty'}, status=400)

        # Delivery fee
        delivery_fee = float(cart.restaurant.delivery_fee) if cart.restaurant else 0
        if data.get('delivery_zone_id'):
            try:
                from .models import DeliveryZone
                zone = DeliveryZone.objects.get(id=data['delivery_zone_id'])
                delivery_fee = float(zone.delivery_fee)
            except DeliveryZone.DoesNotExist:
                pass

        subtotal = float(cart.total)

        # Coupon
        discount = 0
        coupon_code = data.get('coupon_code', '').strip()
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code__iexact=coupon_code, is_active=True,
                    valid_from__lte=timezone.now(), valid_until__gte=timezone.now()
                )
                if not coupon.usage_limit or coupon.times_used < coupon.usage_limit:
                    discount = float(coupon.discount_value)
                    if coupon.discount_type == 'percent':
                        discount = (float(coupon.discount_value) / 100) * subtotal
                    coupon.times_used += 1
                    coupon.save()
            except Coupon.DoesNotExist:
                pass

        # Free delivery threshold
        if cart.restaurant and cart.restaurant.free_delivery_threshold:
            if subtotal >= float(cart.restaurant.free_delivery_threshold):
                delivery_fee = 0

        total = subtotal + delivery_fee - discount

        try:
            county = County.objects.get(id=data['delivery_county_id'])
        except County.DoesNotExist:
            return Response({'error': 'County not found'}, status=404)

        est_time = cart.restaurant.estimated_delivery_time if cart.restaurant else 30

        order = Order.objects.create(
            user=request.user,
            restaurant=cart.restaurant,
            delivery_street=data['delivery_street'],
            delivery_town=data['delivery_town'],
            delivery_county=county,
            delivery_zone_id=data.get('delivery_zone_id'),
            delivery_instructions=data.get('delivery_instructions', ''),
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            payment_method=data['payment_method'],
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            total=total,
            estimated_delivery_time=est_time,
            notes=data.get('notes', ''),
        )

        for item in cart.items.select_related('menu_item').all():
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                item_name=item.menu_item.name,
                item_description=item.menu_item.description[:200],
                quantity=item.quantity,
                unit_price=item.menu_item.price,
                subtotal=item.subtotal,
                special_instructions=item.special_instructions,
            )

        cart.items.all().delete()
        cart.restaurant = None
        cart.save()

        return Response(OrderSerializer(order).data, status=201)