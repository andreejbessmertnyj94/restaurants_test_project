from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from app_restaurants.models import Restaurant, Ticket


class AuthorizationTests(TestCase):
    def test_allowed_methods(self):
        client = APIClient()

        only_post = ["OPTIONS", "POST"]

        endpoints = (
            ("/signup/", only_post),
            ("/login/", only_post),
        )

        for (endpoint, allowed_methods) in endpoints:
            response = client.options(endpoint)

            self.assertEqual(
                sorted(response.headers.get("Allow").split(", ")), allowed_methods
            )

    def test_signup(self):
        client = APIClient()
        endpoint = "/signup/"

        response = client.post(endpoint, {"username": "test", "password": "test"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("token"))

        response_existent = client.post(
            endpoint, {"username": "test", "password": "test"}
        )

        self.assertEqual(response_existent.status_code, status.HTTP_403_FORBIDDEN)

        response_empty_body = client.post(endpoint, {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        User.objects.create_user("test", password="test")

        client = APIClient()
        endpoint = "/login/"

        response = client.post(endpoint, {"username": "test", "password": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("token"))

        response_non_existent = client.post(
            endpoint, {"username": "test1", "password": "test1"}
        )

        self.assertEqual(response_non_existent.status_code, status.HTTP_404_NOT_FOUND)

        response_empty_body = client.post(endpoint, {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)


class RestaurantsTests(TestCase):
    def setUp(self) -> None:
        user1 = User.objects.create_user("test1", password="test1")
        user2 = User.objects.create_user("test2", password="test2")

        Token.objects.create(user=user1)
        Token.objects.create(user=user2)

    def test_allowed_methods(self):
        client = APIClient()

        list_create = ["GET", "HEAD", "OPTIONS", "POST"]
        retrieve_update_destroy = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "PUT"]

        endpoints = (
            ("/restaurants/", list_create),
            ("/restaurants/1/", retrieve_update_destroy),
            ("/restaurants/1/tickets/", list_create),
            ("/restaurants/1/tickets/1/", retrieve_update_destroy),
        )

        for (endpoint, allowed_methods) in endpoints:
            response = client.options(endpoint)

            self.assertEqual(
                sorted(response.headers.get("Allow").split(", ")), allowed_methods
            )

    def test_restaurants_list(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        Restaurant.objects.create(owner=user1)
        Restaurant.objects.create(owner=user2)

        endpoint = "/restaurants/"

        client = APIClient()
        response = client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.get(endpoint)

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user1.data.get("count"), 1)
        self.assertEqual(
            response_user1.data.get("results")[0],
            {
                "id": 1,
                "name": "",
            },
        )

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_user2 = client.get(endpoint)

        self.assertEqual(response_user2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user2.data.get("count"), 1)
        self.assertEqual(
            response_user2.data.get("results")[0],
            {
                "id": 2,
                "name": "",
            },
        )

    def test_restaurant_create(self):
        user = User.objects.get(username="test1")
        token = Token.objects.get(user=user)

        client = APIClient()

        endpoint = "/restaurants/"

        response_unauthorized = client.post(endpoint)

        self.assertEqual(
            response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED
        )

        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = client.post(endpoint, {"name": "test_restaurant"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {"id": 1, "name": "test_restaurant"},
        )

        response_bad_value_type = client.post(endpoint, {"name": []})

        self.assertEqual(
            response_bad_value_type.status_code, status.HTTP_400_BAD_REQUEST
        )

        response_empty_body = client.post(endpoint, {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restaurant_retrieve(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        Restaurant.objects.create(owner=user1)

        endpoint = "/restaurants/1/"

        client = APIClient()
        response = client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.get(endpoint)

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_user1.data,
            {"id": 1, "name": ""},
        )

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_user2 = client.get(endpoint)

        self.assertEqual(response_user2.status_code, status.HTTP_404_NOT_FOUND)

    def test_restaurant_update(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        Restaurant.objects.create(owner=user1)

        endpoint = "/restaurants/1/"

        client = APIClient()
        response = client.put(endpoint, {"name": "a"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_user2 = client.put(endpoint, {"name": "a"})

        self.assertEqual(response_user2.status_code, status.HTTP_404_NOT_FOUND)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.put(endpoint, {"name": "a"})

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_user1.data,
            {"id": 1, "name": "a"},
        )

        response_user1_bad_value_type = client.put(endpoint, {"name": []})

        self.assertEqual(
            response_user1_bad_value_type.status_code, status.HTTP_400_BAD_REQUEST
        )

        response_user1_empty_body = client.put(endpoint, {})

        self.assertEqual(
            response_user1_empty_body.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_restaurant_destroy(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        Restaurant.objects.create(owner=user1)

        endpoint = "/restaurants/1/"

        client = APIClient()
        response = client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_user2 = client.delete(endpoint)

        self.assertEqual(response_user2.status_code, status.HTTP_404_NOT_FOUND)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.delete(endpoint)

        self.assertEqual(response_user1.status_code, status.HTTP_204_NO_CONTENT)

    def test_tickets_list(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        restaurant1 = Restaurant.objects.create(owner=user1)
        restaurant2 = Restaurant.objects.create(owner=user1)

        Ticket.objects.create(restaurant=restaurant1)
        Ticket.objects.create(restaurant=restaurant2)

        client = APIClient()
        response = client.get("/restaurants/1/tickets/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.get("/restaurants/1/tickets/")

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user1.data.get("count"), 1)
        self.assertEqual(
            response_user1.data.get("results")[0],
            {"id": 1, "name": "", "max_purchase_count": 0, "purchase_count": 0},
        )

        response_user2 = client.get("/restaurants/2/tickets/")

        self.assertEqual(response_user2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user2.data.get("count"), 1)
        self.assertEqual(
            response_user2.data.get("results")[0],
            {"id": 2, "name": "", "max_purchase_count": 0, "purchase_count": 0},
        )

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_not_owner = client.get("/restaurants/1/tickets/")

        self.assertEqual(response_not_owner.status_code, status.HTTP_404_NOT_FOUND)

    def test_ticket_create(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        Restaurant.objects.create(owner=user1)

        endpoint = "/restaurants/1/tickets/"

        client = APIClient()
        response = client.post(endpoint, {"name": "a"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_not_owner = client.post(endpoint, {"name": "a"})

        self.assertEqual(response_not_owner.status_code, status.HTTP_403_FORBIDDEN)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.post(endpoint, {"name": "a"})

        self.assertEqual(response_user1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response_user1.data,
            {"id": 1, "name": "a", "max_purchase_count": 0, "purchase_count": 0},
        )

        response_bad_value_type = client.post(endpoint, {"name": []})

        self.assertEqual(
            response_bad_value_type.status_code, status.HTTP_400_BAD_REQUEST
        )

        response_empty_body = client.post(endpoint, {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)

        response_wrong_counts = client.post(
            endpoint, {"name": "a", "purchase_count": 1}
        )

        self.assertEqual(response_wrong_counts.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ticket_retrieve(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        restaurant1 = Restaurant.objects.create(owner=user1)
        restaurant2 = Restaurant.objects.create(owner=user1)

        Ticket.objects.create(restaurant=restaurant1)
        Ticket.objects.create(restaurant=restaurant2)

        client = APIClient()
        response = client.get("/restaurants/1/tickets/1/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_not_owner = client.get("/restaurants/1/tickets/1/")

        self.assertEqual(response_not_owner.status_code, status.HTTP_404_NOT_FOUND)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.get("/restaurants/1/tickets/1/")

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_user1.data,
            {"id": 1, "name": "", "max_purchase_count": 0, "purchase_count": 0},
        )

        response_user1_wrong_path = client.get("/restaurants/1/tickets/2/")

        self.assertEqual(
            response_user1_wrong_path.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_ticket_update(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        restaurant1 = Restaurant.objects.create(owner=user1)
        restaurant2 = Restaurant.objects.create(owner=user1)

        Ticket.objects.create(restaurant=restaurant1)
        Ticket.objects.create(restaurant=restaurant2)

        client = APIClient()
        response = client.put("/restaurants/1/tickets/1/", {"name": "a"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_not_owner = client.put("/restaurants/1/tickets/1/", {"name": "a"})

        self.assertEqual(response_not_owner.status_code, status.HTTP_404_NOT_FOUND)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.put("/restaurants/1/tickets/1/", {"name": "a"})

        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_user1.data,
            {"id": 1, "name": "a", "max_purchase_count": 0, "purchase_count": 0},
        )

        response_bad_value_type = client.put("/restaurants/1/tickets/1/", {"name": []})

        self.assertEqual(
            response_bad_value_type.status_code, status.HTTP_400_BAD_REQUEST
        )

        response_empty_body = client.put("/restaurants/1/tickets/1/", {})

        self.assertEqual(response_empty_body.status_code, status.HTTP_400_BAD_REQUEST)

        response_wrong_counts = client.put(
            "/restaurants/1/tickets/1/", {"name": "a", "purchase_count": 1}
        )

        self.assertEqual(response_wrong_counts.status_code, status.HTTP_400_BAD_REQUEST)

        response_user1_wrong_path = client.put(
            "/restaurants/1/tickets/2/", {"name": "a"}
        )

        self.assertEqual(
            response_user1_wrong_path.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_ticket_destroy(self):
        user1 = User.objects.get(username="test1")
        user2 = User.objects.get(username="test2")

        restaurant1 = Restaurant.objects.create(owner=user1)
        restaurant2 = Restaurant.objects.create(owner=user1)

        Ticket.objects.create(restaurant=restaurant1)
        Ticket.objects.create(restaurant=restaurant2)

        client = APIClient()
        response = client.delete("/restaurants/1/tickets/1/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token2 = Token.objects.get(user=user2)
        client.credentials(HTTP_AUTHORIZATION="Token " + token2.key)

        response_not_owner = client.delete("/restaurants/1/tickets/1/")

        self.assertEqual(response_not_owner.status_code, status.HTTP_404_NOT_FOUND)

        token1 = Token.objects.get(user=user1)
        client.credentials(HTTP_AUTHORIZATION="Token " + token1.key)

        response_user1 = client.delete("/restaurants/1/tickets/1/")

        self.assertEqual(response_user1.status_code, status.HTTP_204_NO_CONTENT)

        response_user1_wrong_path = client.delete("/restaurants/1/tickets/2/")

        self.assertEqual(
            response_user1_wrong_path.status_code, status.HTTP_404_NOT_FOUND
        )
