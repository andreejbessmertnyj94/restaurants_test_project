from rest_framework import serializers

from .models import Restaurant, Ticket


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "name", "max_purchase_count", "purchase_count"]
