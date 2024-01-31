from django.shortcuts import render
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategoryItemsSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import generics, viewsets
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage


# class MenuItemsViewSet(generics.ListCreateAPIView):
class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    search_fields = ['title', 'category__title']

    def get(self, request, *args, **kwargs):
        if (request.method == 'GET'):
            # example query strings - this is for api/menu-items?category=Appetizer
            items = MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            # below is for query parameters in case user wants to search this way
            perpage = request.query_params.get('perpage', default=2)
            page = request.query_params.get('page', default=1)

            if category_name:
                items = items.filter(category__title=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            if search:
                items = items.filter(title__icontains=search)
            if ordering:
                ordering_fields = ordering.split(",")
                items = items.order_by(*ordering_fields)
                # this is for api/menu-items?ordering=price,title (order by price as an example)

            paginator = Paginator(items, per_page=perpage)
            try:
                items = paginator.page(number=page)
            except EmptyPage:
                items = []

            # preparing response based on above code
            serialized_item = MenuItemSerializer(items, many=True)
            return Response(serialized_item.data)


class SingleMenuItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CategoryItemsView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer


class SingleCategoryViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer


class CartItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer


class OrderViewSet(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(generics.RetrieveUpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
