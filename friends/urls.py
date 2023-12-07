from django.contrib import admin
from django.urls import path

from .views import (
    FriendRequestView, ListFriendsView,
    ListPendingRequestsView,
    RespondFriendRequestView,
    UserSearchAPIView
)

urlpatterns = [
    path(
        # Keeping this simple, could use username.
        'send_request',
        FriendRequestView.as_view(),
        name='send_friend_request'
    ),
    path('', ListFriendsView.as_view()),
    path('pending', ListPendingRequestsView.as_view()),
    path('respond/<int:pk>', RespondFriendRequestView.as_view()),
    path('search', UserSearchAPIView.as_view())
]
