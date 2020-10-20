from pycoingecko import CoinGeckoAPI

from .serializers import CoinSerializer

gecko = CoinGeckoAPI()


# The data fetch has been separated into a separate file to make it easier to manage requirement changes when
# the data has to be filtered based on the user permissions, should users ever need to be added
def get_coin_list():
    coins = gecko.get_coins()
    # The Coin Gecko Coin List includes unnecessary additional data and the CoinSerializer filters out the
    # extra data with minimal work and returns on the data required
    data = [CoinSerializer(x).data for x in coins]
    return data
