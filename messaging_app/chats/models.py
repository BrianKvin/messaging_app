from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
  """
  Custom user model extends Django's built-in AbstractUser
  """
  user_id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    help_text="Unique identified for the user"
  )
  phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="User's phone number"
  )
  created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user was created"
  )
  updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user was last updated"
  )
  bio = models.TextField(max_length=500, blank=True, null=True, help_text="A short biography about the user.")
  profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


  class Meta:
    db_table = "users"
    verbose_name = "User"
    verbose_name_plural = "Users"
    ordering = ['username']
  
  def __str__(self):
    """string representation of the user model."""
    return f"{self.username} ({self.email})"

class Conversation(models.Model):
  """Represents a conversation involving multiple users"""
  conversation_id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    help_text="Unique identified for the conversation"
  ),
  participants = models.ManyToManyField(
    'User',
    related_name='conversations',
    help_text="Users participating in this conversation"
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
    help_text="Timestamp when the conversation was created"
  )
  updated_at = models.DateTimeField(
    auto_now=True,
    help_text="Timestamp when the conversation was last updated"
  )
    
  class Meta:
    db_table = 'conversations'
    verbose_name = 'Conversation'
    verbose_name_plural = 'Conversations'
    ordering = ['-updated_at']
    
  def __str__(self):
    participant_names = ", ".join([user.username for user in self.participants.all()[:3]])
    if self.participants.count() > 3:
        participant_names += f" and {self.participants.count() - 3} others"
    return f"Conversation: {participant_names}"
  
  @property
  def last_message(self):
    """Get the most recent message in this conversation."""
    return self.messages.order_by('-created_at').first()


class Message(models.Model):
  """
  Model for individual messages within conversations.
  Each message belongs to a conversation and has a sender.
  """
  message_id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    help_text="Unique identifier for the message"
  )
  sender = models.ForeignKey(
    'User',
    on_delete=models.CASCADE,
    related_name='sent_messages',
    help_text="User who sent this message"
  )
  conversation = models.ForeignKey(
    'Conversation',
    on_delete=models.CASCADE,
    related_name='messages',
    help_text="Conversation this message belongs to"
  )
  message_body = models.TextField(
    help_text="Content of the message"
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
    help_text="Timestamp when the message was sent"
  )
  
  class Meta:
    db_table = 'messages'
    verbose_name = 'Message'
    verbose_name_plural = 'Messages'
    ordering = ['-created_at']
  
  def __str__(self):
    return f"Message from {self.sender.username} in {self.conversation.conversation_id}"
  
  def save(self, *args, **kwargs):
    """
    Override save method to update the conversation's updated_at timestamp
    whenever a new message is added.
    """
    super().save(*args, **kwargs)
    # Update the conversation's updated_at field
    self.conversation.updated_at = self.created_at
    self.conversation.save(update_fields=['updated_at'])