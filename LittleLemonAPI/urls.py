from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsViewSet.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewSet.as_view())
]
