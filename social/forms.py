from django import forms
from .models import Post, Comment, ThreadModel, MessangerModel


class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'What do you thinking?',
            'style': 'resize:none',
        })
    )

    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['body', 'image']


class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'placeholder': 'Comment',
            'rows': 1,
            'style': 'resize: none',
        })
    )

    class Meta:
        model = Comment
        fields = ['comment']


class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)


class MessangerForm(forms.Form):
    message = forms.CharField(label='', max_length=100)