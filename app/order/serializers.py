from rest_framework import serializers
from .utils import get_route_from_ors
from .models import Order


class OrderCreateSerializer(serializers.Serializer):
    origin_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
       
        
        route_info = get_route_from_ors(
            validated_data['origin_lat'],
            validated_data['origin_lng'],
            validated_data['destination_lat'],
            validated_data['destination_lng']
        )
        if "error" in route_info:
            raise serializers.ValidationError(route_info["error"])

       
        price_per_meter = 0.1
        price = int(route_info["distance_meters"] * price_per_meter)

       
        
        user = self.context["request"].user
        order = Order.objects.create(
            user=user,
            origin_lat=validated_data['origin_lat'],
            origin_lng=validated_data['origin_lng'],
            destination_lat=validated_data['destination_lat'],
            destination_lng=validated_data['destination_lng'],
            distance_meters=route_info["distance_meters"],
            duration_seconds=route_info["duration_seconds"],
            price=price,
            status=Order.PENDING
        )
        return order
