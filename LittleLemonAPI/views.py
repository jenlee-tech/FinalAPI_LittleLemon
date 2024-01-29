from django.shortcuts import render
# from rest_framework import viewsets
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategoryItemsSerializer
from rest_framework import generics
from rest_framework.response import Response


class MenuItemsViewSet(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request, *args, **kwargs):
        if (request.method == 'GET'):
            items = MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            if category_name:
                items = items.filter(category__title=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            serialized_item = MenuItemSerializer(items, many=True)
            return Response(serialized_item.data)

    # ordering_fields = ['price']
    # search_fields = ['title', 'category__title']


class SingleMenuItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CategoryItemsView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer


class SingleCategoryViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer
