from datetime import datetime

from django.core.cache import caches
from django.utils import timezone
from pycoingecko import CoinGeckoAPI
from rest_framework.exceptions import ParseError, Throttled

from api.models import MarketCap
from .error_messages import *
gecko = CoinGeckoAPI()


# The data fetch has been separated into a separate file to make it easier to manage requirement changes when
# the data has to be filtered based on the user permissions, should users ever need to be added
def get_coin_market_cap(coin_id, date, currency):
    try:
        # If the market cap has been cached in the database, return it instead of fetching from the API
        return MarketCap.objects.get(
            coin_id=coin_id,
            date=date,
            currency=currency
        ).market_cap
    except MarketCap.DoesNotExist:
        # Market cap does not exist, so fetch from the API
        # Before fetching, ensure that the rate limit enforced by Coin Gecko will not be abused
        check_coin_gecko_rate_limit()
        # Convert date to required format by Coin Gecko
        date_string = datetime.strftime(date, '%d-%m-%Y')
        try:
            coin = gecko.get_coin_history_by_id(coin_id, date_string)

            market_data = coin.get('market_data', None)
            if not market_data:
                raise ParseError(NO_MARKET_DATA)

            market_cap_list = market_data.get('market_cap', None)
            if not market_cap_list:
                raise ParseError(NO_MARKET_DATA)

            market_cap_in_currency = market_cap_list.get(currency)
            if market_cap_in_currency:
                return MarketCap.objects.create(
                    coin_id=coin_id,
                    date=date,
                    currency=currency,
                    market_cap=market_cap_in_currency
                ).market_cap
            else:
                raise ParseError(NO_MARKET_CAP_FOR_CURRENCY)
        except ValueError:
            raise ParseError(UNKNOWN_COIN_ID)
        except Exception as e:
            raise ParseError(e)


def check_coin_gecko_rate_limit():
    cache = caches['default']

    # Check when the API was last consumed
    coin_gecko_consumption_time = cache.get_or_set('coin_gecko_consumption_time', timezone.now(), 100)

    # Check how many times the API has been consumed in the last minute
    coin_gecko_consumption_count = cache.get('coin_gecko_consumption_count', 0)

    if coin_gecko_consumption_count == 0:
        # The API has not yet been consumed, so mark this as the first consumption and proceed
        cache.set('coin_gecko_consumption_count', 1, 60)
        return True

    delta = timezone.now() - coin_gecko_consumption_time
    if delta.seconds >= 60:
        # The rate limit is 100 requests per minute, so if the minute has passed, reset the rate limit and proceed
        cache.set('coin_gecko_consumption_count', 0, 60)
        cache.set('coin_gecko_consumption_time', timezone.now(), 100)
        return True
    else:
        # Still within the minute rate limiter, so check if there are still available requests
        if coin_gecko_consumption_count < 100:
            cache.set('coin_gecko_consumption_count', coin_gecko_consumption_count + 1)
            return True

    raise Throttled(detail=TOO_MANY_API_REQUESTS.format(delta_seconds=60-delta.seconds))
