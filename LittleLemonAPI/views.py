from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategoryItemsSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, UserSerializer, OrderStatusSerializer, OrderPutSerializer
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from .permissions import IsManager, IsCustomer, IsDeliverer


class MenuItemsViewSet(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    search_fields = ['title', 'category__title']

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]

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

    def post(self, request, *args, **kwargs):
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)


class SingleMenuItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            instance.delete()
            return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # 'pk' is the primary key parameter from the URL
        item_id = kwargs.get('pk')
        if not MenuItem.objects.filter(pk=item_id).exists():
            return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        serialized_item = MenuItemSerializer(
            self.get_object(), data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance:
            return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        serialized_item = MenuItemSerializer(instance, data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_200_OK)


class CartItemViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)
        serializer = CartItemSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Extract attributes from request payload
        user_id = request.data.get('user')
        # Filter queryset based on user
        queryset = Cart.objects.filter(
            user_id=user_id)
        # Check if any items match the queryset
        if queryset.exists():
            # Delete items matching the queryset
            queryset.delete()
            return Response({"message": "All the item(s) in the cart have been deleted."}, status=status.HTTP_200_OK)
        else:
            return Response("No items to delete", status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # if request.user.groups.filter(name="Customer").exists():
        if IsCustomer().has_permission(request, self):
            orders = Order.objects.filter(user=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif IsDeliverer().has_permission(request, self):
            orders = Order.objects.filter(delivery_crew_id=user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif IsManager().has_permission(request, self):
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if IsCustomer().has_permission(request, self):
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Hello! - Not authorized to post for this customer...", status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('id')
        if IsManager().has_permission(request, self):
            if order_id is not None:
                try:
                    # Retrieve the order object based on the provided id
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    return Response(f"Order with id {order_id} does not exist", status=status.HTTP_404_NOT_FOUND)

                # Update the order object with data from request.data
                serializer = OrderSerializer(order, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Order id is missing from the payload", status=status.HTTP_400_BAD_REQUEST)

        elif IsDeliverer().has_permission(request, self):
            user = request.user
            deliverer_id = request.data.get('delivery_crew')
            requested_order = Order.objects.filter(
                delivery_crew_id=user, id=order_id)

            if requested_order is not None:
                try:
                    order = Order.objects.get(
                        delivery_crew_id=user, id=order_id)
                except Order.DoesNotExist:
                    return Response(f"Order with id {order_id} does not exist", status=status.HTTP_404_NOT_FOUND)
                serializer = OrderStatusSerializer(
                    order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(f"you are not allowed to edit other Deliverer's orders, this is the deliverer_crew id: {deliverer_id} and this is the user: {user}", status=status.HTTP_403_FORBIDDEN)
        else:
            return Response("You cannot update the order", status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if IsManager().has_permission(request, self):
            order_id = request.data.get('id')
            if order_id is not None:
                try:
                    # Retrieve the order object based on the provided id
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    return Response(f"Order with id {order_id} does not exist", status=status.HTTP_404_NOT_FOUND)

                # Update the order object with data from request.data
                serializer = OrderSerializer(order, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Order id is missing from the payload", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Hello! - Not authorized to update for this user...", status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        pk = self.kwargs.get('pk')
        if user.id == int(pk):
            query = OrderItem.objects.filter(order_id=pk)
            return query
        elif user.groups.filter(name='Manager').exists():
            return OrderItem.objects.all()
        else:
            return OrderItem.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "You can't get other people's order items"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew']
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=201, data={'message': str(crew.username)+' was assigned to order #'+str(order.id)})

    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            instance = self.get_object()
            if not instance:
                return Response({"message": "This item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                instance.delete()
                return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You do not have permission to do this"}, status=status.HTTP_403_FORBIDDEN)


class CategoryItemsView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


class SingleCategoryViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryItemsSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


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


@api_view(['POST', 'DELETE', 'GET'])
@permission_classes([IsAdminUser, IsManager])
def managers(request):
    if request.method == 'GET':
        # Retrieve the "Manager" group
        managers_group = Group.objects.get(name="Manager")
        manager_users = managers_group.user_set.all()
        # Serialize the manager_users queryset if needed
        serialized_data = UserSerializer(manager_users, many=True).data

        return Response(serialized_data)

    elif request.method == 'POST' or request.method == 'DELETE':
        username = request.data.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": f"Username {username} was not found"}, status=status.HTTP_404_NOT_FOUND)
            managers_group = Group.objects.get(name="Manager")

            if request.method == 'POST':
                managers_group.user_set.add(user)
                return Response({"message": "ok - the user was added to the Managers group"}, status=status.HTTP_201_CREATED)
            elif request.method == 'DELETE':
                managers_group.user_set.remove(user)
                return Response({"message": "ok - the user was removed from the manager group"}, status=status.HTTP_200_OK)
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAdminUser, IsManager])
def manager_delivery(request):
    deliverer_group = Group.objects.get(name="Deliverer")
    if request.method == 'GET':
        deliverer_users = deliverer_group.user_set.all()
        serialized_data = UserSerializer(deliverer_users, many=True).data
        return Response(serialized_data)

    elif request.method == "POST" or request.method == 'DELETE':
        username = request.data.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": f"Username {username} was not found"}, status=status.HTTP_404_NOT_FOUND)
            deliverer_group = Group.objects.get(name="Deliverer")
            if request.method == 'POST':
                deliverer_group.user_set.add(user)
                return Response({"message": "ok - the user was added to the Deliverer group"}, status=status.HTTP_201_CREATED)
            elif request.method == 'DELETE':
                deliverer_group.user_set.remove(user)
                return Response({"message": "ok - the user was removed from the deliverer group"}, status=status.HTTP_200_OK)
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser, IsManager])
def manager_delivery_remove(request, pk):

    deliverer_group = Group.objects.get(name="Deliverer")
    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": f"Username {user} was not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Deliverer").exists():
            deliverer_group.user_set.remove(user)
            return Response({"message": "ok - the user was removed from the deliverer group"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"User with ID {pk} is not in the Deliverer group"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser, IsManager])
def manager_manager_remove(request, pk):
    manager_group = Group.objects.get(name="Manager")
    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": f"Username {user} was not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.groups.filter(name="Manager").exists():
            manager_group.user_set.remove(user)
            return Response({"message": "ok - the user was removed from the Manager group"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"User with ID {pk} is not in the Manager group"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
