import os
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "whatsup.settings"))

django.setup()

def get_asgi_app():
    from channels.routing import ProtocolTypeRouter, URLRouter
    from chats import routing
    return ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": URLRouter(
            routing.websocket_urlpatterns
        ),
    })
    
application = get_asgi_app()

