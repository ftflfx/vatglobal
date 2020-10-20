from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from .error_messages import *
from .get_data import get_coin_market_cap


class MarketCap(APIView):
    """
    get:
    !{"operationId": ["Get Market Cap"]}
    !{"tags":["Market Cap"]}
    !{"description":["Retrieve the market cap for a given coin, on a given day, in a given currency.
    Available query parameters are coin_id, date, and currency, which are all required."]}
    !{"responses": {"200": {"description": "Retrieved market cap with success"}}}
    !{"responses": {"400": {"description": "Bad Request - View error detail for more information"}}}
    """
    authentication_classes = []

    # Market cap is cached for a day, so as to alleviate using the database cache of historical market values
    # as much as possible. Although this value never changes, the fields or presentation displayed on the page
    # may change, and so it is still set to invalidate after a day
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        coin_id, date, currency = fetch_parameters_from_request(request)

        # Ensure that all query parameters are supplied
        if not coin_id or not date or not currency:
            raise ParseError(detail=MISSING_QUERY_PARAMETERS)

        # Check that the date is in the correct format
        try:
            date = datetime.strptime(date, '%Y/%m/%d').date()
        except ValueError:
            raise ParseError(detail=INCORRECT_DATE_FORMAT)

        # Check that the date is not in the future, as it will not have a market cap
        current_date = timezone.now().date()
        if date > current_date:
            raise ParseError(detail=FUTURE_DATE)

        try:
            market_cap = get_coin_market_cap(coin_id, date, currency)
            return Response({
                currency: Decimal(market_cap)
            })
        except ValueError as v:
            raise ParseError(detail=str(v))


def fetch_parameters_from_request(request):
    coin_id = request.query_params.get('coin_id', None)
    date = request.query_params.get('date', None)
    currency = request.query_params.get('currency', None)
    return coin_id, date, currency
