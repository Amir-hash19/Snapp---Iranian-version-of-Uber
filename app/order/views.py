from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import OrderCreateSerializer, ListRetrieveOrderSerializer, OrderAcceptSerializer, DriverSerializer, UserOrderDetailSerializer
from rest_framework import generics
from rest_framework.views import APIView
from account.throttling import UserBaseThrottle
from account.permissions import IsDriverPermission, IsAssignedDriverPermission
from .models import Order
from django.db import transaction
from .pagination import StandardResultSetPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            return Response({
                "status": "success",
                "order_id": order.id,
                "distance_meters": order.distance_meters,
                "duration_seconds": order.duration_seconds,
                "price": order.price,
                "status_order": order.status
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@method_decorator(cache_page(60*10), name="dispatch")
class OrderListView(generics.ListAPIView):
    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]
    pagination_class = StandardResultSetPagination


    def get_queryset(self):
        return Order.objects.filter(status="pending")




class OrderRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        return Order.objects.filter(status="pending")





class OrderAcceptView(generics.UpdateAPIView):
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

        return Response({
            "status":"success",
            "message":"Order has been accepted",
            "order_id":order.id,
            "status_value": order.status,
            "driver":DriverSerializer(order.driver).data if order.driver else None
        }, status=status.HTTP_202_ACCEPTED)
        




class UserOrderRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserOrderDetailSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user, status="accepted")
    