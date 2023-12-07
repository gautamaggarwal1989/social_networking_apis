from rest_framework import serializers
from django.db import models
from django.contrib.auth import get_user_model

from .models import FriendShip

from user_profile.serializers import SignUpSerializer


class FriendshipDetailsSerializer(serializers.ModelSerializer):
    # Using alias for the fields to make them more clear in response
    sender = SignUpSerializer(source='user1', read_only=True)
    friendship_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = FriendShip
        fields = ['friendship_id', 'sender', 'status']


class FriendshipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendShip
        fields = ['status']

    def validate(self, data):
        instance = self.instance

        status = data.get('status')
        if status not in [
              FriendShip.REJECTED, FriendShip.ACCEPTED]:
            raise serializers.ValidationError(
                'Invalid request: Status should be either accepted or rejected')
        
        if not instance:
            raise serializers.ValidationError(
                "Request does not exist!"
            )
        
        if instance.status != FriendShip.PENDING:
            raise serializers.ValidationError(
                'Invalid request: This request is either already accepted or rejected!')
        
        return data


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendShip
        fields = ['user1', 'user2', 'status']

    def _existing_friendship_check(self, user_profile, friend_profile):

        existing_friendship = FriendShip.objects.get(
            (models.Q(
                user1=user_profile, user2=friend_profile
                ) | models.Q(
                user1=friend_profile, user2=user_profile)
            )
        )

        if existing_friendship.status == 'pending':
            raise serializers.ValidationError(
                "Friend request has already been sent.")
        elif existing_friendship.status == 'accepted':
            raise serializers.ValidationError(
                "Users are already friends.")
        else:
            # The request must have been rejected earlier.
            existing_friendship.status = 'pending'
            existing_friendship.user1 = user_profile
            existing_friendship.user2 = friend_profile
            existing_friendship.save()

            return existing_friendship

    def create(self, validated_data):
        user_profile = validated_data['user1']
        friend_profile = validated_data['user2']

        if user_profile == friend_profile:
            raise serializers.ValidationError(
                "Sender and reciever cannot be same."
            )

        try:
            return self._existing_friendship_check(
                user_profile, friend_profile
            )

        except FriendShip.DoesNotExist:
            return FriendShip.objects.create(
                user1=user_profile,
                user2=friend_profile,
                status='pending'
            )
