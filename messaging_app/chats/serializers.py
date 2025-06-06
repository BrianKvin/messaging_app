from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles user data serialization with read-only fields for security.
    """
    user_id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 
            'last_name', 'phone_number', 'password', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        """Create user with encrypted password."""
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Handles message data with nested sender information.
    """
    message_id = serializers.UUIDField(read_only=True)
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    conversation_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation_id',
            'message_body', 'created_at'
        ]
        read_only_fields = ['message_id', 'created_at', 'sender']
    
    def create(self, validated_data):
        """Create message with proper sender and conversation assignment."""
        sender_id = validated_data.pop('sender_id')
        conversation_id = validated_data.pop('conversation_id')
        
        try:
            sender = User.objects.get(user_id=sender_id)
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except (User.DoesNotExist, Conversation.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid sender or conversation: {str(e)}")
        
        # Verify sender is a participant in the conversation
        if not conversation.participants.filter(user_id=sender_id).exists():
            raise serializers.ValidationError("Sender must be a participant in the conversation")
        
        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            **validated_data
        )
        return message


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    Handles conversation data with nested participants and messages.
    """
    conversation_id = serializers.UUIDField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'messages', 'last_message', 'message_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_msg = obj.last_message
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_message_count(self, obj):
        """Get total number of messages in the conversation."""
        return obj.messages.count()
    
    def create(self, validated_data):
        """Create conversation with specified participants."""
        participant_ids = validated_data.pop('participant_ids')
        
        # Validate that all participant IDs exist
        participants = User.objects.filter(user_id__in=participant_ids)
        if len(participants) != len(participant_ids):
            raise serializers.ValidationError("One or more participant IDs are invalid")
        
        # Create conversation
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        
        return conversation
    
    def validate_participant_ids(self, value):
        """Validate participant IDs list."""
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants")
        
        if len(set(value)) != len(value):
            raise serializers.ValidationError("Duplicate participant IDs are not allowed")
        
        return value


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing conversations without nested messages.
    Used for performance optimization in list views.
    """
    conversation_id = serializers.UUIDField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'last_message',
            'message_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_msg = obj.last_message
        if last_msg:
            return {
                'message_id': last_msg.message_id,
                'sender': last_msg.sender.username,
                'message_body': last_msg.message_body[:100] + '...' if len(last_msg.message_body) > 100 else last_msg.message_body,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_message_count(self, obj):
        """Get total number of messages in the conversation."""
        return obj.messages.count()