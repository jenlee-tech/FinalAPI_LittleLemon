from django.shortcuts import render
from rest_framework import viewsets
# Create your views here.
from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    search_fields = ['title', 'category__title']
