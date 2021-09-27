from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.response import Response

from .models import Restaurant, Ticket
from .serializers import RestaurantSerializer, TicketSerializer


@api_view(["POST"])
def signup(request):
    try:
        user = User.objects.create_user(
            request.data["username"], password=request.data["password"]
        )

        token = Token.objects.create(user=user)

        return Response({"token": str(token)}, status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(
            {
                "error": "That username has already been taken. Please choose a new username"
            },
            status.HTTP_403_FORBIDDEN,
        )
    except (ParseError, KeyError):
        return Response(
            {"error": "Could not signup. Please check username and password"},
            status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def login(request):
    try:
        user = authenticate(
            request,
            username=request.data["username"],
            password=request.data["password"],
        )
    except (ParseError, KeyError):
        return Response(
            {"error": "Could not login. Please check username and password"},
            status.HTTP_400_BAD_REQUEST,
        )

    if user is None:
        return Response(
            {"error": "Could not login. Please check username and password"},
            status.HTTP_404_NOT_FOUND,
        )
    else:
        try:
            token = Token.objects.get(user=user)
        except ObjectDoesNotExist:
            token = Token.objects.create(user=user)
        return Response({"token": str(token)}, status.HTTP_200_OK)


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get("pk"):
            return Restaurant.objects.filter(
                owner=self.request.user, pk=self.kwargs["pk"]
            )
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RestaurantTicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            restaurant = Restaurant.objects.get(
                owner=self.request.user, pk=self.kwargs["restaurant_pk"]
            )
            if self.kwargs.get("pk"):
                return Ticket.objects.filter(
                    restaurant=restaurant,
                    pk=self.kwargs["pk"],
                )
            return restaurant.tickets.all()
        except ObjectDoesNotExist:
            raise NotFound

    def perform_create(self, serializer):
        try:
            restaurant = Restaurant.objects.get(
                owner=self.request.user, pk=self.kwargs["restaurant_pk"]
            )
            serializer.save(restaurant=restaurant)
        except ObjectDoesNotExist:
            raise PermissionDenied
        except (IntegrityError, OverflowError):
            raise ParseError

    def perform_update(self, serializer):
        try:
            serializer.save()
        except (IntegrityError, OverflowError):
            raise ParseError
