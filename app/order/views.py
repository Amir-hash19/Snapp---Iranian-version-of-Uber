from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import OrderCreateSerializer, ListRetrieveOrderSerializer
from rest_framework import generics
from rest_framework.views import APIView
from account.throttling import UserBaseThrottle
from account.permissions import IsDriverPermission
from .models import Order

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





class OrderListView(generics.ListAPIView):
    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        return Order.objects.filter(status="pending")




class OrderRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsDriverPermission]
    serializer_class = ListRetrieveOrderSerializer
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        return Order.objects.filter(status="pending")