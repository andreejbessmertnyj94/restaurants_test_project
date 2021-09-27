from django.urls import include, path
from rest_framework_nested import routers

from .views import RestaurantTicketViewSet, RestaurantViewSet, login, signup

router = routers.SimpleRouter()
router.register(r"restaurants", RestaurantViewSet, basename="restaurant")

tickets_router = routers.NestedSimpleRouter(router, r"restaurants", lookup="restaurant")
tickets_router.register(
    r"tickets",
    RestaurantTicketViewSet,
    basename="ticket",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(tickets_router.urls)),
    # Auth
    path("signup/", signup),
    path("login/", login),
]
