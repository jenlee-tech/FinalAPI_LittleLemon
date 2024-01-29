from rest_framework import serializers
from .models import MenuItem, Category


class CategoryItemsSerializer(serializers.ModelSerializer):
    title = serializers.ChoiceField(
        choices=Category.objects.values_list('title', flat=True))

    class Meta:
        model = Category
        fields = ['title', 'id']


class MenuItemSerializer(serializers.ModelSerializer):
    # category = CategoryItemsSerializer()

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'featured']
        extra_kwargs = {
            'price': {'min_value': 2},
        }
        depth = 1

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2)
