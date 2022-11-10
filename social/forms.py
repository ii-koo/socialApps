from django import forms
from .models import Post, Comment, MessangerModel


class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'What do you thinking?',
            'style': 'resize:none',
        })
    )

    image = forms.ImageField(required=False,
                             widget=forms.ClearableFileInput(attrs={
                                 'multiple': True,
                             })
                             )

    class Meta:
        model = Post
        fields = ['body']


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


class MessangerForm(forms.ModelForm):
    body = forms.CharField(label='', max_length=100)
    image = forms.ImageField(required=False)

    class Meta:
        model = MessangerModel
        fields = ['body', 'image']


class SharedForm(forms.Form):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'your comments',
            'style': 'resize:none',
        }))

