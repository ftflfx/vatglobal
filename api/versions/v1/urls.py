from django.urls import path, include

app_name = 'v1'
urlpatterns = [
    path(
        'coinList/',
        include('api.versions.v1.coin_list.urls')
    ),
    path(
        'marketCap/',
        include('api.versions.v1.market_cap.urls')
    ),
]
