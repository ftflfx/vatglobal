from rest_framework import serializers


class CoinSerializer(serializers.Serializer):
    id = serializers.CharField(
        max_length=255,
        required=True
    )
    symbol = serializers.CharField(
        max_length=255,
        required=True
    )
    name = serializers.CharField(
        max_length=255,
        required=True
    )
