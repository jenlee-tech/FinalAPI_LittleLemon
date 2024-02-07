from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem


class CategoryItemsSerializer(serializers.ModelSerializer):
    title = serializers.ChoiceField(
        choices=Category.objects.values_list('title', flat=True))

    class Meta:
        model = Category
        fields = ['title', 'id', 'slug']


class MenuItemSerializer(serializers.ModelSerializer):
    # category = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'featured']
        extra_kwargs = {
            'price': {'min_value': 2},
        }
        depth = 1
        # comment this out if you want to Post menu item and select a category in the serializer from the Category model, otherwise leave it there to see details of the Category object when listing.

    # def get_category(self, obj):
    #     return {'title': obj.category.title}


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model: OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
