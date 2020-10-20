from django.db import models
from django.utils.translation import gettext_lazy as _


class MarketCap(models.Model):
    coin_id = models.CharField(
        _('Coin ID'),
        max_length=255,
        null=False
    )
    date = models.DateField(
        _('Date'),
        null=False
    )
    currency = models.CharField(
        _('Currency (ISO Code)'),
        max_length=255,
        null=False
    )
    market_cap = models.CharField(
        _('Market Cap'),
        max_length=255,
        null=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['coin_id', 'date', 'currency'],
                name='unique_market_cap'
            )
        ]
