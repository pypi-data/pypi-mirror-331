from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CustomUser.
    Включает основные поля пользователя.
    """

    class Meta:
        model = CustomUser
        fields = [
            'id',                  # Уникальный ID пользователя
            'username',            # Имя пользователя
            'email',               # Email пользователя
            'name',                # Полное имя
            'phone',               # Телефон
            'location',            # Регион или город пользователя
            'sub',                 # Subject — уникальный идентификатор из токена OIDC
            'surname',             # Фамилия
            'given_name',          # Имя
            'preferred_username',  # Отображаемое имя в интерфейсе
            'nickname',            # Псевдоним
            'email_verified',      # Статус подтверждения email
            'nonce',               # Криптографический параметр для предотвращения повторного использования токенов
        ]
        read_only_fields = ['id', 'email_verified', 'nonce']

    def to_representation(self, instance):
        """
        Дополнительно форматирует данные при выводе.
        Например, можно исключить чувствительные данные.
        """
        data = super().to_representation(instance)
        data.pop('password', None)
        data.pop('nonce', None)
        return data
    