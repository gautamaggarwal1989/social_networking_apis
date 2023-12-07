from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendShip(models.Model):

    PENDING ='pending'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'

    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('rejected', 'rejected'),
        ('accepted', 'accepted')
    ]

    # This user is the sender of the request 
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='connection1')
    # User that recieves the request.
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='connection2')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
