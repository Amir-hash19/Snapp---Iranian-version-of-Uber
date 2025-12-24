from account.models import DriverProfile, User
from rest_framework import serializers

from .models import Order
from .utils import get_route_from_ors


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

        route_info = get_route_from_ors(origin_lat, origin_lng, dest_lat, dest_lng)

        if "error" in route_info:
            raise serializers.ValidationError({"route": route_info["error"]})

        from decimal import ROUND_HALF_UP, Decimal

        price = (Decimal(route_info["distance_meters"]) * Decimal("0.1")).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

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
            status=Order.PENDING,
        )


class ListRetrieveOrderSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "user_full_name",
            "origin_lat",
            "origin_lng",
            "destination_lat",
            "destination_lng",
            "distance_meters",
            "duration_seconds",
            "price",
            "created_at",
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name


class OrderAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        order = self.instance
        if order.status != Order.PENDING:
            raise serializers.ValidationError("Only pending orders can be accepted.")
        if value != Order.ACCEPTED:
            raise serializers.ValidationError("only status 'accepted' can be set")
        return value


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ["vehicle_type", "vehicle_plate", "is_available", "created_at"]


class DriverSerializer(serializers.ModelSerializer):
    driver_profile = DriverProfileSerializer()

    class Meta:
        model = User
        fields = ["phone_number", "driver_profile", "full_name"]


class UserOrderDetailSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "origin_lat",
            "origin_lng",
            "destination_lat",
            "destination_lng",
            "distance_meters",
            "duration_seconds",
            "price",
            "status",
            "driver",
            "created_at",
        ]
