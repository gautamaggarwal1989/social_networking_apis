from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .models import FriendShip
from .serializers import (
    FriendshipSerializer, FriendshipDetailsSerializer,
    FriendshipUpdateSerializer
)
from user_profile.serializers import SignUpSerializer, SearchUserSerializer
from .pagination import PaginationClass

User = get_user_model()


class FriendRequestView(APIView):

    @method_decorator(ratelimit(key='user',rate='3/m', method="POST"))
    def post(self, request):
        try:
            friend_id = request.data.get('friend_id')
            serializer = FriendshipSerializer(data={
                'user1': request.user.pk,
                'user2': get_object_or_404(User, id=friend_id).pk
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {"error": "Friend not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RespondFriendRequestView(generics.UpdateAPIView):
    ''' View to respond to friend requests sent to the user.'''
    serializer_class = FriendshipUpdateSerializer
    queryset = FriendShip.objects.all()

    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user2 != self.request.user:
            return Response(
                {"error": 'Invalid user request.'},
                 status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListFriendsView(generics.ListAPIView):
    serializer_class = SignUpSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        return self.request.user.connections.all()


class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendshipDetailsSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        return self.request.user.pending_requests.all()


class UserSearchAPIView(generics.ListAPIView):
    serializer_class = SearchUserSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        search_keyword = self.request.query_params.get(
            'search_keyword', None)
        if not search_keyword or not len(search_keyword):
            return User.objects.none()
        
        return User.search(search_keyword)
         

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializerI(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
