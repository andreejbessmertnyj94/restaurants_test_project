from time import sleep

from django.db import IntegrityError, OperationalError, transaction
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from app_restaurants.models import Ticket

from .serializers import PublicTicketSerializer


class PublicTicketList(generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = PublicTicketSerializer


class PublicTicketRetrieve(generics.RetrieveAPIView):
    serializer_class = PublicTicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(pk=self.kwargs["pk"])


def process_purchase(pk, buy_amount):
    try:
        if type(buy_amount) != int:
            raise TypeError
        with transaction.atomic():
            ticket = Ticket.objects.get(pk=pk)
            ticket.purchase_count += buy_amount
            ticket.save()

            return Response(PublicTicketSerializer(ticket).data)
    except (IntegrityError, TypeError):
        raise ParseError
    except OperationalError:
        sleep(0.1)
        return process_purchase(pk, buy_amount)


@api_view(["PATCH"])
def ticket_buy(request, pk):
    buy_amount = request.data.get("tickets_to_buy")

    return process_purchase(pk, buy_amount)
