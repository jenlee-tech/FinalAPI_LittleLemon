from django.urls import path
from . import views

urlpatterns = [
    path('menuitems/', views.MenuItemsViewSet, name="MenuItems")
]
