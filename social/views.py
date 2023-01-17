from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Post, Comment, UserProfile, Notification, ThreadModel, MessangerModel, Image, Tag
from .forms import PostForm, CommentForm, ThreadForm, MessangerForm, SharedForm, ExploreForm
from django.views.generic import UpdateView, DeleteView, ListView
from django.urls import reverse_lazy


def handle_not_found(request, exception):
    return render(request, 'error.html')


# Create your views here.
class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # chek followers if exists
        chk_foll = UserProfile.objects.filter(followers=request.user).count()
        # if user has no followers, all posts will be displayed
        if chk_foll < 1 or chk_foll is None:
            posts = Post.objects.annotate(number_of_comments=Count('comment_set')).order_by('-shared_on', '-created_on')
        else:
            logged_in_user = request.user
            posts = Post.objects.annotate(number_of_comments=Count('comment_set')).filter \
                (Q(author__profile__followers__in=[logged_in_user.id]) | Q(
                    author__profile__name=request.user.profile.name) | Q(
                    shared_user=True
                )).order_by('-shared_on', '-created_on')

        form = PostForm()
        shared_form = SharedForm()

        context = {
            'post_list': posts,
            'shared_form': shared_form,
            'form': form,
        }
        return render(request, 'post_list.html', context)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            new_post.create_tags()

            for f in files:
                img = Image(image=f)
                img.save()
                new_post.image.add(img)

            new_post.save()

        return redirect('post-list')


class PostDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        comments = Comment.objects.filter(post=post)
        total_comments = Comment.objects.filter(post=post).count()
        context = {
            'post': post,
            'form': form,
            'comments': comments,
            'total_comments': total_comments,
        }
        return render(request, 'post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

            notification = Notification.objects.create(notification_type=2, from_user=request.user,
                                                       to_user=post.author, post=post)

        return redirect('post-detail', pk=post.id)


class PostEditView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    fields = ['body']
    template_name = 'post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    template_name = 'post_delete.html'

    def get_success_url(self):
        pk = self.request.user.id
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentDeleteView(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Comment
    template_name = 'comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        form = SharedForm()
        posts = Post.objects.annotate(number_of_comments=Count('comment_set')).filter \
            (Q(author=user) | Q(shared_user=user)).order_by('-shared_on', '-created_on')
        followers = profile.followers.all()

        is_following = None

        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)

        context = {
            'user': user,
            'profile': profile,
            'shared_form': form,
            'posts': posts,
            'number_of_followers': number_of_followers,
            'is_following': is_following,
        }

        return render(request, 'profile.html', context)


class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user,
                                                       to_user=comment.author, comment=comment)
        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

            notification = Notification.objects.create(notification_type=2, from_user=request.user,
                                                       to_user=parent_comment.author, comment=new_comment)

        return redirect('post-detail', pk=post_pk)


class ProfileViewEdit(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(notification_type=3, from_user=request.user,
                                                   to_user=profile.user)

        return redirect('profile', pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile', pk=profile.pk)


class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user,
                                                       to_user=post.author, post=post)
        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class SharedPostView(View):
    def post(self, request, pk, *args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        form = SharedForm(request.POST)

        if form.is_valid():
            new_post = Post(
                shared_body=self.request.POST.get('body'),
                body=original_post.body,
                author=original_post.author,
                created_on=original_post.created_on,
                shared_user=request.user,
                shared_on=timezone.now(),
            )

            new_post.save()
            new_post.create_tags()
            for img in original_post.image.all():
                new_post.image.add(img)
            new_post.save()

        return redirect('post-list')


class UserSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query) |
            Q(name__icontains=query)
        )

        context = {
            'profile_list': profile_list,
        }

        return render(request, 'user_search.html', context)


class ListFollower(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
            'profile': profile,
            'followers': followers,
        }

        return render(request, 'followers_list.html', context)


class PostNotification(LoginRequiredMixin, View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post-detail', pk=post_pk)


class FollowNotification(LoginRequiredMixin, View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)


class ThreadNotification(LoginRequiredMixin, View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        thread = ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)


class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('success', content_type='text/plain')


class NotificationListsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification_lists.html'
    context_object_name = 'notifications'
    ordering = '-date'
    paginate_by = 5


class ListThread(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'threads': threads
        }

        return render(request, 'inbox.html', context)


class CreateThread(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form
        }

        return render(request, 'create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)
        except:
            messages.success(request, f'Invalid Username.')
            return redirect('create-thread')


class ThreadView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        form = MessangerForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessangerModel.objects.filter(thread__pk__contains=pk)

        context = {
            'thread': thread,
            'form': form,
            'message_lists': message_list
        }

        return render(request, 'thread.html', context)


class CreateMessage(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        form = MessangerForm(request.POST, request.FILES)
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()

        notification = Notification.objects.create(
            notification_type=4,
            from_user=request.user,
            to_user=receiver,
            thread=thread,
        )

        return redirect('thread', pk=pk)


class ExploreTags(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        form = ExploreForm()
        shared_form = SharedForm()
        if tag:
            posts = Post.objects.annotate(number_of_comments=Count('comment_set')).\
                filter(tags__in=[tag]).order_by('-shared_on', '-created_on')
            # posts = Post.objects.annotate(number_of_comments=Count('comment_set')).filter \
            #     (Q(author__profile__name=request.user.profile.name) | Q(
            #         shared_user=True
            #     ), tags__in=[tag]).order_by('-shared_on', '-created_on')

        else:
             posts = Post.objects.annotate(number_of_comments=Count('comment_set')).order_by('-shared_on', '-created_on')

        context = {
            'tag': tag,
            'form': form,
            'shared_form': shared_form,
            'posts': posts,
        }

        return render(request, 'explore.html', context)

    def post(self, request, *args, **kwargs):
        form = ExploreForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            tag = Tag.objects.filter(name=query).first()

            posts = None
            if tag:
                posts = Post.objects.annotate(number_of_comments=Count('comment_set'))\
                    .filter(tags__in=[tag]).order_by('-shared_on', '-created_on')
            if posts:
                context = {
                    'tag': tag,
                    'posts': posts,
                }
            else:
                context = {
                    'tag': tag,
                }

            return HttpResponseRedirect(f'/social/explore?query={query}')
        return HttpResponseRedirect('/social/explore')