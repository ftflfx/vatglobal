from django.urls import path

from .views import CoinList

app_name = 'coin_list'
urlpatterns = [
    path(
        '',
        CoinList.as_view(),
        name='coin_list'
    ),
]
