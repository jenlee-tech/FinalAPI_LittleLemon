from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu-items/', views.MenuItemsViewSet.as_view()),
    # path('menu-items/<int:pk>', views.SingleMenuItemViewSet.as_view()),
    path('menu-items/', views.MenuItemsViewSet.as_view({'get': 'list'})),
    path('menu-items/<int:pk>',
         views.MenuItemsViewSet.as_view({'get': 'retrieve'})),
    path('categories/', views.CategoryItemsView.as_view()),
    path('categories/<int:pk>', views.SingleCategoryViewSet.as_view()),
    path('cart/menu-items/<int:pk>', views.CartItemViewSet.as_view()),
    path('orders/<int:pk>', views.OrderViewSet.as_view()),
    path('orderitem/<int:pk>', views.OrderItemViewSet.as_view()),
    path('secret', views.secret),
    # this will help user generate a token at this endpoint
    path('api-token-auth/', obtain_auth_token)
]
