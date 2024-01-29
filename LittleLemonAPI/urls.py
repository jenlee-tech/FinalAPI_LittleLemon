from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsViewSet.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemViewSet.as_view()),
    path('categories/', views.CategoryItemsView.as_view()),
    path('categories/<int:pk>', views.SingleCategoryViewSet.as_view()),
]