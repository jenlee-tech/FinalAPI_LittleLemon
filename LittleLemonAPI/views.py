from django.shortcuts import render
# from rest_framework import viewsets
from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework import generics


class MenuItemsViewSet(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # ordering_fields = ['price', 'inventory']
    # search_fields = ['title', 'category__title']


class SingleMenuItemViewSet(generics.ListAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
