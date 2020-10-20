from rest_framework.views import APIView
from rest_framework.response import Response
from .get_data import get_coin_list
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .serializers import CoinSerializer


class CoinList(APIView):
    """
    get:
    !{"operationId": ["Get Coin List"]}
    !{"tags":["Coin List"]}
    !{"description":["Retrieve a list of all coins in the Coin Gecko API"]}
    !{"responses": {"200": {"description": "Retrieved coin list with success"}}}
    !{"responses": {"400": {"description": "Bad Request - View error detail for more information"}}}
    """
    authentication_classes = []
    serializer_class = CoinSerializer

    # Coin list is cached for an hour, as a business decision determining that waiting an hour for new coins in the
    # list is acceptable. This largely reduces the hits on the Coin Gecko API, as it will only be consumed once
    # every hour for the coin list
    @method_decorator(cache_page(60 * 60))
    def get(self, request):
        data = get_coin_list()
        return Response(data)
