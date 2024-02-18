# from rest_framework.permissions import BasePermission
# from rest_framework.response import Response
# from rest_framework import status


# class IsManager(BasePermission):
#     message = "You do not have permission to perform this action."

#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False

#         if not request.user.groups.filter(name='Manager').exists():
#             # Handle the response logic here
#             response_data = {'detail': self.message}
#             response_status = status.HTTP_403_FORBIDDEN
#             view.raise_exception = True  # Raise an exception for the framework to handle
#             return Response(response_data, status=response_status)

#         return True


# class IsCustomer(BasePermission):
#     message = "You do not have permission to perform this action."

#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False

#         if not request.user.groups.filter(name='Customer').exists():
#             # Handle the response logic here
#             response_data = {'detail': self.message}
#             response_status = status.HTTP_403_FORBIDDEN
#             view.raise_exception = True  # Raise an exception for the framework to handle
#             return Response(response_data, status=response_status)

#         return True
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


class IsManager(permissions.BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False


class IsDeliverer(permissions.BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Deliverer').exists():
            return True
        else:
            return False


class IsCustomer(permissions.BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Customer').exists():
            return True
        else:
            return False
