from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('addresses', views.AddressViewSet, basename='address')
router.register('counties', views.CountyViewSet, basename='county')
router.register('zones', views.DeliveryZoneViewSet, basename='zone')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('restaurants', views.RestaurantViewSet, basename='restaurant')
router.register('cart', views.CartViewSet, basename='cart')
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]