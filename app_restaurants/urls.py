from django.urls import path

from .views import (
    RestaurantListCreate,
    RestaurantRetrieveUpdateDestroy,
    RestaurantTicketListCreate,
    RestaurantTicketRetrieveUpdateDestroy,
    login,
    signup,
)

urlpatterns = [
    path("restaurants/", RestaurantListCreate.as_view()),
    path("restaurants/<int:pk>/", RestaurantRetrieveUpdateDestroy.as_view()),
    path(
        "restaurants/<int:restaurant_id>/tickets/", RestaurantTicketListCreate.as_view()
    ),
    path(
        "restaurants/<int:restaurant_id>/tickets/<int:pk>/",
        RestaurantTicketRetrieveUpdateDestroy.as_view(),
    ),
    # Auth
    path("signup/", signup),
    path("login/", login),
]
