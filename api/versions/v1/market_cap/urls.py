from django.urls import path

from .views import MarketCap

app_name = 'market_cap'
urlpatterns = [
    path(
        '',
        MarketCap.as_view(),
        name='market_cap'
    ),
]
