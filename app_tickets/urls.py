from django.urls import path

from .views import PublicTicketList, PublicTicketRetrieve, ticket_buy

urlpatterns = [
    path("tickets/", PublicTicketList.as_view()),
    path("tickets/<int:pk>/", PublicTicketRetrieve.as_view()),
    path("tickets/<int:pk>/buy/", ticket_buy),
]
