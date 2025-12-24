from rest_framework import serializers
from .utils import get_route_from_ors
from .models import Order



class OrderCreateSerializer(serializers.Serializer):
    origin_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
        origin_lat = float(validated_data["origin_lat"])
        origin_lng = float(validated_data["origin_lng"])
        dest_lat = float(validated_data["destination_lat"])
        dest_lng = float(validated_data["destination_lng"])

        route_info = get_route_from_ors(
            origin_lat, origin_lng, dest_lat, dest_lng
        )

        if "error" in route_info:
            raise serializers.ValidationError({
                "route": route_info["error"]
            })

        from decimal import Decimal, ROUND_HALF_UP

        price = (
            Decimal(route_info["distance_meters"])
            * Decimal("0.1")
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        user = self.context["request"].user
        return Order.objects.create(
            user=user,
            origin_lat=validated_data["origin_lat"],
            origin_lng=validated_data["origin_lng"],
            destination_lat=validated_data["destination_lat"],
            destination_lng=validated_data["destination_lng"],
            distance_meters=route_info["distance_meters"],
            duration_seconds=route_info["duration_seconds"],
            price=int(price),
            status=Order.PENDING
        )



class ListRetrieveOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["user",
                "origin_lat",
                "origin_lng", 
                "destination_lat", 
                "destination_lng",
                "distance_meters",
                "duration_seconds",
                "price","created_at"]