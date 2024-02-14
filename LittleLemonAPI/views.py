from django.shortcuts import render, get_object_or_404
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategoryItemsSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, UserSerializer
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from .permissions import IsManager, IsCustomer


class MenuItemsViewSet(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
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

    @permission_classes([IsAuthenticated])
    def post(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            def create(self, request, *args, **kwargs):
                serialized_item = MenuItemSerializer(data=request.data)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)
        else:
            return Response({"message": "You do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)


class SingleMenuItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            # 'pk' is the primary key parameter from the URL
            # item_id = kwargs.get('pk')
            instance = self.get_object()
            if not instance:
                return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                instance.delete()
                return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            # 'pk' is the primary key parameter from the URL
            item_id = kwargs.get('pk')
            if not MenuItem.objects.filter(pk=item_id).exists():
                return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            serialized_item = MenuItemSerializer(
                self.get_object(), data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            # 'pk' is the primary key parameter from the URL
            item_id = kwargs.get('pk')
            instance = self.get_object()

            if not instance:
                return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

            serialized_item = MenuItemSerializer(instance, data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)


class CartItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer

    @permission_classes([IsAuthenticated])
    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        serializer = CartItemSerializer(carts, many=True)
        if request.user.groups.filter(name="Customer").exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "U do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        if request.user.groups.filter(name="Customer").exists():
            serializer = CartItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Hello! - Not authorized...", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.user.groups.filter(name="Customer").exists():
            # Extract attributes from request payload
            user_id = request.data.get('user')
            menuitem_id = request.data.get('menuitem')

            # Validate user_id and menuitem_id
            if not user_id or not menuitem_id:
                return Response("User ID and MenuItem ID are required", status=status.HTTP_400_BAD_REQUEST)

            # Filter queryset based on payload attributes
            queryset = Cart.objects.filter(
                user_id=user_id, menuitem_id=menuitem_id)

            # Check if any items match the queryset
            if queryset.exists():
                # Delete items matching the queryset
                queryset.delete()
                return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response("No items to delete", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authorized", status=status.HTTP_403_FORBIDDEN)


class OrderViewSet(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if request.user.groups.filter(name="Customer").exists():
            orders = Order.objects.filter(user=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.groups.filter(name="Customer").exists():
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Hello! - Not authorized to post for this customer...", status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
        return query

    # def post(self, request, *args, **kwargs):
    #     if request.user.groups.filter(name="Customer").exists():
    #         serialized_item = OrderItemSerializer(data=request.data)
    #         serialized_item.is_valid(raise_exception=True)
    #         serialized_item.save()
    #         return Response(serialized_item.data, status.HTTP_201_CREATED)
    #     else:
    #         return Response({"message": "You do not have permission to do this as a non customer"}, status=status.HTTP_403_FORBIDDEN)

    # def patch(self, request, *args, **kwargs):
    #     if request.user.group.filter(name="Manager").exists():
    #         # item_id = kwargs.get('pk')
    #         # if not OrderItem.objects.filter(order_id=item_id):
    #         #     return Response({"message": "This order item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
    #         # else:
    #         #     serialized_item = OrderItemSerializer(
    #         #         self.get_object(), data=request.data)
    #         #     serialized_item.is_valid(raise_exception=True)
    #         #     serialized_item.save()
    #         #     return Response(serialized_item.data, status=status.HTTP_200_OK)

    #         order = OrderItem.objects.get(pk=self.kwargs['pk'])
    #         order.status = not order.status
    #         order.save()
    #         return JsonResponse(status=200, data={'message': 'Status of order #' + str(order.id)+' changed to '+str(order.status)})

    #     else:
    #         return Response({"message": "You do not have permission to edit this order item"}, status=status.HTTP_403_FORBIDDEN)


class CategoryItemsView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer


class SingleCategoryViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "Some secret message"})


# this checks if an authenticated user belongs in a group
@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Success! = The manager should see this"})
    else:
        return Response({"message": "You are not authorized to view this"}, 403)


@api_view()
# controlling the throttle rates for anonymous users
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


@api_view()
# controlling the throttle rates for authenticated users
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def throttle_check_authenticated(request):
    return Response({"message": "authenticated users throttle rate successful"})

# must keep which enables managers to add users to a manager groups
# /api/groups/manager/users endpoint


@api_view(['POST', 'DELETE'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == 'POST':
            managers.user_set.add(user)
            return Response({"message": "ok - the user was added"})
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
            return Response({"message": "ok - the user was removed from the manager group"})

    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
