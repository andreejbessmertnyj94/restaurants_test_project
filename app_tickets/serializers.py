from rest_framework import serializers

from app_restaurants.models import Ticket


class PublicTicketSerializer(serializers.ModelSerializer):
    restaurant = serializers.ReadOnlyField(source="restaurant.name")
    purchase_left = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "name",
            "max_purchase_count",
            "purchase_count",
            "purchase_left",
            "restaurant",
        ]
        read_only_fields = ["name", "max_purchase_count", "purchase_count"]

    def get_purchase_left(self, ticket):
        return ticket.max_purchase_count - ticket.purchase_count
