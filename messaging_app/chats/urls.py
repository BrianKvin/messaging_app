# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# This will create the following URL patterns:
# /users/ - GET (list), POST (create)
# /users/{user_id}/ - GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
# /conversations/ - GET (list), POST (create)
# /conversations/{conversation_id}/ - GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
# /conversations/{conversation_id}/add_participant/ - POST (custom action)
# /conversations/{conversation_id}/remove_participant/ - POST (custom action)
# /messages/ - GET (list), POST (create)
# /messages/{message_id}/ - GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
# /messages/by_conversation/ - GET (custom action)
# /messages/send_message/ - POST (custom action)