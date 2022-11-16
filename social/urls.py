from django.urls import path
from .views import PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, \
    ProfileView, ProfileViewEdit, AddFollower, RemoveFollower, ListFollower,\
    AddLike, AddCommentLike, CommentReplyView, SharedPostView,\
    UserSearchView, PostNotification, FollowNotification, RemoveNotification,\
    NotificationListsView, ThreadNotification, ListThread, CreateThread, ThreadView, CreateMessage,\
    ExploreTags

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/edit', PostEditView.as_view(), name='post-edit'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like', AddLike.as_view(), name='add-like'),
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentLike.as_view(), name='comment-like'),
    path('post/<int:pk>/share', SharedPostView.as_view(), name='shared-post'),

    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/edit', ProfileViewEdit.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/<int:pk>/followers/list', ListFollower.as_view(), name='followers-list'),

    path('search/', UserSearchView.as_view(), name='profile-search'),

    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/follow/<int:profile_pk>', FollowNotification.as_view(), name='follow-notification'),
    path('notification/<int:pk>/profile', NotificationListsView.as_view(), name='notification-lists'),
    path('notification/<int:notification_pk>/delete', RemoveNotification.as_view(), name='notification-remove'),

    path('notification/<int:notification_pk>/thread/<int:object_pk>', ThreadNotification.as_view(), name='thread-notification'),

    path('inbox/', ListThread.as_view(), name='inbox'),
    path('inbox/<int:pk>', ThreadView.as_view(), name='thread'),
    path('inbox/create-thread/', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),

    path('explore/', ExploreTags.as_view(), name='explore')

]