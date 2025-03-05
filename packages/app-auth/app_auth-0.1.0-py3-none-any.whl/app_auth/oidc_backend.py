from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

User = get_user_model()


class MyOIDCAB(OIDCAuthenticationBackend):
    """
    Кастомный бэкенд аутентификации через OIDC.
    Наследуется от OIDCAuthenticationBackend для переопределения логики:
    - Формирования username
    - Создания/обновления пользователя
    - Назначения групп
    """

    def get_username(self, claims):
        """
        Формирует username на основе данных из claims.
        Args:
            claims (dict): Данные из токена OIDC (email, name, groups и т.д.)
        Returns:
            str: Сгенерированный username
        """
        username = claims.get('name')
        if not username:
            username = super().get_username(claims)
        return username
    

    def create_user(self, claims):
        """
        Создает нового пользователя на основе данных из токена OIDC.
        Args:
            claims (dict): Данные из токена OIDC
        Returns:
            User: Созданный пользователь
        """
        user = super(MyOIDCAB, self).create_user(claims)
        self.update_user_fields(user, claims)
        self.assign_groups(user, claims)
        return user


    def update_user(self, user, claims):
        """
        Обновляет существующего пользователя данными из токена OIDC.
        Args:
            user (User): Существующий пользователь
            claims (dict): Данные из токена OIDC
        Returns:
            User: Обновленный пользователь
        """
        self.update_user_fields(user, claims)
        self.assign_groups(user, claims)
        return user

    def update_user_fields(self, user, claims):
        """
        Синхронизирует поля пользователя с данными из токена OIDC.
        Args:
            user (User): Пользователь для обновления
            claims (dict): Данные из токена OIDC
        """
        user_fields = {field.name: field for field in user._meta.fields}
        
        for field_name in user_fields.keys():
            if field_name in claims:
                setattr(user, field_name, claims[field_name])
        
        user.save()


    def assign_groups(self, user, claims):
        """
        Назначает пользователю группы из данных токена OIDC.
        Args:
            user (User): Пользователь для назначения групп
            claims (dict): Данные из токена OIDC
        """
        groups_claim = claims.get('groups', [])

        for group_name in groups_claim:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        user.save()
