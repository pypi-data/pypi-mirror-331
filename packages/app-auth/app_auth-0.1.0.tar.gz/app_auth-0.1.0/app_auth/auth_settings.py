OIDC_OP_AUTHORIZATION_ENDPOINT='https://auth.gasmc.ru/application/o/authorize/'
OIDC_OP_TOKEN_ENDPOINT='https://auth.gasmc.ru/application/o/token/'
OIDC_OP_USER_ENDPOINT='https://auth.gasmc.ru/application/o/userinfo/'
OIDC_RP_SIGN_ALGO='RS256'
OIDC_RP_SCOPES='openid custom_scope email'
OIDC_CREATE_USER=True
# OIDC_USERNAME_ALGO="core.apps.app_auth.oidc_backend.get_user_name"
# AUTHENTICATION_BACKENDS="core.apps.app_auth.oidc_backend.MyOIDCAB"
OIDC_USERNAME_ALGO="app_auth.oidc_backend.get_user_name"
AUTHENTICATION_BACKENDS="app_auth.oidc_backend.MyOIDCAB"
LOGIN_REDIRECT_URL="/"
LOGOUT_REDIRECT_URL="/"



# import environ
# from pathlib import Path
# import os

# env = environ.Env()
# environ.Env.read_env(Path(os.getcwd()) / ".env")

# import os
# import environ
# # Получаем абсолютный путь к корню проекта
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # Инициализируем объект Environ
# env = environ.Env()
# # Загружаем переменные окружения из .env
# env.read_env(os.path.join(BASE_DIR, ".env"))

# Настройки OIDC
# OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID", default=None) 
# OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET", default=None)

# Endpoint URLs
# OIDC_OP_AUTHORIZATION_ENDPOINT = env('OIDC_OP_AUTHORIZATION_ENDPOINT', default=None)
# OIDC_OP_TOKEN_ENDPOINT = env('OIDC_OP_TOKEN_ENDPOINT', default=None)
# OIDC_OP_USER_ENDPOINT = env('OIDC_OP_USER_ENDPOINT', default=None)
# OIDC_OP_JWKS_ENDPOINT = env('OIDC_OP_JWKS_ENDPOINT', default=None)
# OIDC_OP_ISSUER = env('OIDC_OP_ISSUER', default=None)
# OIDC_RP_SIGN_ALGO = env('OIDC_RP_SIGN_ALGO', default=None) # Алгоритм подписи токенов
# OIDC_RP_SCOPES = env('OIDC_RP_SCOPES', default=None)
# OIDC_CREATE_USER = env('OIDC_CREATE_USER', default=None)  # Создавать пользователя при первом входе
# OIDC_USERNAME_ALGO = env('OIDC_USERNAME_ALGO', default=None)
# AUTHENTICATION_BACKENDS= env('AUTHENTICATION_BACKENDS', default=None)
# LOGIN_REDIRECT_URL = env('LOGIN_REDIRECT_URL', default=None)
# LOGOUT_REDIRECT_URL = env('LOGOUT_REDIRECT_URL', default=None)


# check = all(
#     [True,
#     None,]
# )
# print(check)