from django.urls import path
from .views import PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, \
    ProfileView, ProfileViewEdit, AddFollower, RemoveFollower, AddLike

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/edit', PostEditView.as_view(), name='post-edit'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like', AddLike.as_view(), name='add-like'),

    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/edit', ProfileViewEdit.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
]