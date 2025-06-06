from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, ConversationSerializer, ConversationListSerializer,
    MessageSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations.
    Provides CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Allow user creation without authentication.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation operations.
    Provides CRUD operations for conversations with nested message handling.
    """
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'conversation_id'
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        Use simplified serializer for list view for better performance.
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """
        Filter conversations to only show those the authenticated user participates in.
        """
        user = self.request.user
        return Conversation.objects.filter(
            participants=user
        ).prefetch_related('participants', 'messages').distinct()
    
    def perform_create(self, serializer):
        """
        Create conversation and ensure the current user is included as a participant.
        """
        conversation = serializer.save()
        # Add current user as a participant if not already included
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a new participant to an existing conversation.
        """
        conversation = self.get_object()
        participant_id = request.data.get('participant_id')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            participant = User.objects.get(user_id=participant_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.participants.filter(user_id=participant_id).exists():
            return Response(
                {'error': 'User is already a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.add(participant)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """
        Remove a participant from a conversation.
        """
        conversation = self.get_object()
        participant_id = request.data.get('participant_id')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            participant = User.objects.get(user_id=participant_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not conversation.participants.filter(user_id=participant_id).exists():
            return Response(
                {'error': 'User is not a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing the last participant
        if conversation.participants.count() <= 2:
            return Response(
                {'error': 'Cannot remove participant. Conversation must have at least 2 participants'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.remove(participant)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations.
    Provides CRUD operations for messages within conversations.
    """
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'message_id'
    
    def get_queryset(self):
        """
        Filter messages to only show those from conversations the user participates in.
        """
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation').distinct()
    
    def perform_create(self, serializer):
        """
        Create message with the current user as sender.
        """
        # Ensure the sender is the current user
        conversation_id = self.request.data.get('conversation_id')
        
        # Verify user is participant in the conversation
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
                raise PermissionError("You are not a participant in this conversation")
        except Conversation.DoesNotExist:
            raise ValueError("Conversation not found")
        
        serializer.save(sender_id=self.request.user.user_id)
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """
        Get all messages for a specific conversation.
        """
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        Send a message to a specific conversation.
        Simplified endpoint for sending messages.
        """
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')
        
        if not conversation_id or not message_body:
            return Response(
                {'error': 'conversation_id and message_body are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )
        
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)