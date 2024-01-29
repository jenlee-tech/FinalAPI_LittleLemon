from django.shortcuts import render
# from rest_framework import viewsets
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategoryItemsSerializer
from rest_framework import generics


class MenuItemsViewSet(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # ordering_fields = ['price']
    # search_fields = ['title', 'category__title']


class SingleMenuItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CategoryItemsView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer
