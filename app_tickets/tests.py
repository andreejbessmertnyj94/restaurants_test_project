from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from app_restaurants.models import Restaurant, Ticket


class TicketsTests(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user("test", password="test")
        restaurant = Restaurant.objects.create(owner=user)
        Ticket.objects.create(restaurant=restaurant, max_purchase_count=1)

    def test_allowed_methods(self):
        client = APIClient()

        only_get = ["GET", "HEAD", "OPTIONS"]
        only_patch = ["OPTIONS", "PATCH"]

        endpoints = (
            ("/tickets/", only_get),
            ("/tickets/1/", only_get),
            ("/tickets/1/buy/", only_patch),
        )

        for (endpoint, allowed_methods) in endpoints:
            response = client.options(endpoint)

            self.assertEqual(
                sorted(response.headers.get("Allow").split(", ")), allowed_methods
            )

    def test_get_tickets_list(self):
        client = APIClient()

        response = client.get("/tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(
            response.data.get("results")[0],
            {
                "id": 1,
                "name": "",
                "max_purchase_count": 1,
                "purchase_count": 0,
                "purchase_left": 1,
                "restaurant": "",
            },
        )

    def test_get_ticket_details(self):
        client = APIClient()

        response = client.get("/tickets/1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": 1,
                "name": "",
                "max_purchase_count": 1,
                "purchase_count": 0,
                "purchase_left": 1,
                "restaurant": "",
            },
        )

        response_non_existent = client.get("/tickets/2/")

        self.assertEqual(response_non_existent.status_code, status.HTTP_404_NOT_FOUND)

    def test_ticket_purchase(self):
        client = APIClient()
        endpoint = "/tickets/1/buy/"

        response_buy = client.patch(endpoint, {"tickets_to_buy": 1})

        self.assertEqual(response_buy.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_buy.data,
            {
                "id": 1,
                "name": "",
                "max_purchase_count": 1,
                "purchase_count": 1,
                "purchase_left": 0,
                "restaurant": "",
            },
        )

        response_return = client.patch(endpoint, {"tickets_to_buy": -1})

        self.assertEqual(response_return.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_return.data,
            {
                "id": 1,
                "name": "",
                "max_purchase_count": 1,
                "purchase_count": 0,
                "purchase_left": 1,
                "restaurant": "",
            },
        )

        response_wrong_amount = client.patch(endpoint, {"tickets_to_buy": 2})

        self.assertEqual(response_wrong_amount.status_code, status.HTTP_400_BAD_REQUEST)

        response_float = client.patch(endpoint, {"tickets_to_buy": 1.1})

        self.assertEqual(response_float.status_code, status.HTTP_400_BAD_REQUEST)

        response_string = client.patch(endpoint, {"tickets_to_buy": "1"})

        self.assertEqual(response_string.status_code, status.HTTP_400_BAD_REQUEST)

        response_empty_body = client.patch(endpoint, {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)
