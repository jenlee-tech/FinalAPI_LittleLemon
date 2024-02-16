from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items/',
         views.MenuItemsViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('menu-items/<int:pk>',
         views.SingleMenuItemViewSet.as_view()),
    path('categories/', views.CategoryItemsView.as_view()),
    path('categories/<int:pk>', views.SingleCategoryViewSet.as_view()),
    path('cart/menu-items/', views.CartItemViewSet.as_view()),
    path('cart/menu-items/<int:pk>', views.CartItemViewSet.as_view()),
    path('orders/', views.OrderViewSet.as_view()),
    path('orders/<int:pk>/',
         views.OrderItemViewSet.as_view({'get': 'list', 'patch': 'update', 'put': 'update'})),
    path('secret', views.secret),
    path('api-token-auth/', obtain_auth_token),
    path('manager-view/', views.manager_view),
    path('throttle-check', views.throttle_check),
    path('throttle-check-authenticated', views.throttle_check_authenticated),
    path('groups/manager/users/', views.managers),
    path('groups/delivery-crew/users/', views.manager_delivery),
    path('groups/delivery-crew/users/<int:pk>', views.manager_delivery_remove),

]
