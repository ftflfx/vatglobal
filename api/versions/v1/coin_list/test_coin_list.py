import json

import pytest
from django.shortcuts import reverse
from rest_framework.test import APIRequestFactory

from .get_data import get_coin_list
from .views import CoinList


def test_get_coin_market_cap():
    coin_list = get_coin_list()
    # Assuming that the API will always return a coin list greater than zero
    assert [check_coin_attributes(coin) for coin in coin_list] and len(coin_list) > 0


@pytest.mark.django_db
def test_coin_list_api_view():
    view = CoinList.as_view()
    factory = APIRequestFactory()
    request = factory.get(reverse('api:v1:coin_list:coin_list'))
    response = view(request)
    response.render()
    value = json.loads(response.content)
    # Assuming that the API will always return a coin list greater than zero
    assert [check_coin_attributes(coin) for coin in value] and len(value) > 0


def check_coin_attributes(coin):
    return coin.get('id') and coin.get('symbol') and coin.get('name')
