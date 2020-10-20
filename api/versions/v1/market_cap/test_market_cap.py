import json
from datetime import datetime, timedelta

import pytest
from django.shortcuts import reverse
from rest_framework.exceptions import ParseError
from rest_framework.test import APIRequestFactory

from .error_messages import *
from .get_data import get_coin_market_cap
from .views import MarketCap


@pytest.mark.parametrize(
    'coin_id, date, currency, expected',
    [
        ('ripple', datetime(2020, 8, 1), 'gbp', 8887692603.065351),
        ('bitcoin', datetime(2020, 1, 31), 'zar', 2551849805719.0137),
    ]
)
@pytest.mark.django_db
def test_get_coin_market_cap(coin_id, date, currency, expected):
    assert get_coin_market_cap(coin_id, date, currency) == expected


@pytest.mark.parametrize('coin_id, date, currency', [('x', datetime(2020, 1, 31), 'zar')])
@pytest.mark.django_db
def test_get_coin_market_cap_with_incorrect_coin_id(coin_id, date, currency):
    with pytest.raises(ParseError):
        get_coin_market_cap(coin_id, date, currency)


@pytest.mark.parametrize('coin_id, date, currency', [('ripple', datetime(1999, 1, 31), 'zar')])
@pytest.mark.django_db
def test_get_coin_market_cap_with_unavailable_data_for_date(coin_id, date, currency):
    with pytest.raises(ParseError):
        get_coin_market_cap(coin_id, date, currency)


@pytest.mark.parametrize('coin_id, date, currency', [('bitcoin', datetime(2020, 1, 31), 'xpc')])
@pytest.mark.django_db
def test_get_coin_market_cap_with_unknown_currency(coin_id, date, currency):
    with pytest.raises(ParseError):
        get_coin_market_cap(coin_id, date, currency)


@pytest.mark.parametrize(
    'coin_id, date, currency, expected',
    [
        ('ripple', '2020/08/01', 'gbp', 8887692603.065351),
        ('bitcoin', '2020/01/31', 'zar', 2551849805719.0137),
    ]
)
@pytest.mark.django_db
def test_market_cap_api_view(coin_id, date, currency, expected):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get(currency) == expected


@pytest.mark.parametrize('coin_id, date, currency', [('x', '2020/01/31', 'zar')])
@pytest.mark.django_db
def test_market_cap_api_view_with_incorrect_coin_id(coin_id, date, currency):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == UNKNOWN_COIN_ID


@pytest.mark.parametrize('coin_id, date, currency', [('ripple', '1991/1/31', 'zar')])
@pytest.mark.django_db
def test_market_cap_api_view_with_unavailable_data_for_date(coin_id, date, currency):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == NO_MARKET_DATA


@pytest.mark.parametrize('coin_id, date, currency', [('bitcoin', '01/02/31', 'zar')])
@pytest.mark.django_db
def test_market_cap_api_view_with_incorrect_date_format(coin_id, date, currency):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == INCORRECT_DATE_FORMAT


@pytest.mark.parametrize(
    'coin_id, date, currency', [('bitcoin', (datetime.now() + timedelta(days=365)).strftime('%Y/%m/%d'), 'zar')]
)
@pytest.mark.django_db
def test_market_cap_api_view_with_future_data(coin_id, date, currency):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == FUTURE_DATE


@pytest.mark.parametrize('coin_id, date, currency', [('bitcoin', '2020/01/31', 'xpc')])
@pytest.mark.django_db
def test_market_cap_api_view_with_unknown_currency(coin_id, date, currency):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'coin_id': coin_id, 'date': date, 'currency': currency}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == NO_MARKET_CAP_FOR_CURRENCY


@pytest.mark.parametrize('date', ['2020/01/31'])
@pytest.mark.django_db
def test_market_cap_api_view_with_missing_query_parameters(date):
    view = MarketCap.as_view()
    factory = APIRequestFactory()
    request = factory.get(
        reverse('api:v1:market_cap:market_cap'), {'date': date}
    )
    response = view(request)
    response.render()
    value = json.loads(response.content)
    assert value.get('detail') == MISSING_QUERY_PARAMETERS
