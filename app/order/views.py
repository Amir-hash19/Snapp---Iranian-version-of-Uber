from account.permissions import IsAssignedDriverPermission, IsDriverPermission
from account.throttling import UserBaseThrottle
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .pagination import StandardResultSetPagination
from .serializers import (
    DriverSerializer,
    ListRetrieveOrderSerializer,
    OrderAcceptSerializer,
    OrderCreateSerializer,
    UserOrderDetailSerializer,
)


class OrderCreateView(APIView):
    
    """
    endpoint for creating a new order
    args:
        origin_lat (decimal): Latitude of the origin location
        origin_lng (decimal): Longitude of the origin location
        destination_lat (decimal): Latitude of the destination location
        destination_lng (decimal): Longitude of the destination location
    returns:
        This endpoint returns: an Order object with details such as order ID, distance, duration, price, and status.
    exceptions:
        Raises ValidationError if there is an issue with route calculation.
    example out put:
        {
            "origin_lat": "35.6892",
            "origin_lng": "51.3890",
            "destination_lat": "35.7892",
            "destination_lng": "51.4890"
        }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {
                    "status": "success",
                    "order_id": order.id,
                    "distance_meters": order.distance_meters,
                    "duration_seconds": order.duration_seconds,
                    "price": order.price,
                    "status_order": order.status,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(cache_page(60 * 10), name="dispatch")
class OrderListView(generics.ListAPIView):

    """
    endpoint for listing all pending orders for drivers.
    args:
        None
    returns:    
        This endpoint returns: a list of pending Order objects
    exceptions:
        Raises PermissionDenied if the user is not a driver.
    example out put:
        [
            {
                "user_full_name": "John Doe",
                "origin_lat": "35.6892",
                "origin_lng": "51.3890",
                "destination_lat": "35.7892",
                "destination_lng": "51.4890"
            }
        ]
    """

    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        return Order.objects.filter(status="pending")


class OrderRetrieveView(generics.RetrieveAPIView):
    """
    endpoint for retrieving details of a specific pending order for drivers.
    args:
        order_id (int): ID of the order to retrieve
    returns:    
        This endpoint returns: details of the specified Order object 
        exceptions:
        Raises PermissionDenied if the user is not a driver.
    example out put:
        {
            "user_full_name": "John Doe",}
            "origin_lat": "35.6892",
            "origin_lng": "51.3890",
            "destination_lat": "35.7892",
            "destination_lng": "51.4890"
        }
    """
    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        return Order.objects.filter(status="pending")


class OrderAcceptView(generics.UpdateAPIView):
    """Endpoint for drivers to accept a pending order.
    args:
        order_id (int): ID of the order to accept
    returns:    
        This endpoint returns: details of the accepted Order object along with driver information
    exceptions:
        Raises PermissionDenied if the user is not a driver or if the order is not pending.
    example out put:
        {
            "status": "success",
            "message": "Order has been accepted",
            "order_id": 1,
        }
        """
    permission_classes = [IsDriverPermission]
    serializer_class = OrderAcceptSerializer
    queryset = Order.objects.all()

    def patch(self, request, *args, **kwargs):
        order = self.get_object()

        self.check_object_permissions(request, order)

        with transaction.atomic():
            if not order.driver:
                order.driver = request.user
                order.save()
            serializer = self.get_serializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Order has been accepted",
                "order_id": order.id,
                "status_value": order.status,
                "driver": DriverSerializer(order.driver).data if order.driver else None,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class UserOrderRetrieveView(generics.RetrieveAPIView):

    """
    endpoint for users to retrieve details of their accepted orders.
    args:
        None
    returns:    
        This endpoint returns: a list of accepted Order objects for the authenticated user
    exceptions:
        Raises PermissionDenied if the user is not authenticated.
        
    """
    serializer_class = UserOrderDetailSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user, status="accepted")
