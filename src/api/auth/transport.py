from fastapi_users.authentication import BearerTransport

from core.settings import BEARER_TRANSPORT_TOKEN_URL

bearer_transport = BearerTransport(tokenUrl=BEARER_TRANSPORT_TOKEN_URL)
