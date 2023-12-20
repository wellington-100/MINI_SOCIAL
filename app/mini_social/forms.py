from django import forms
from .models import Post, CustomUser
from .models import Message

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image', 'video', 'link']

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image', 'video', 'link']


class MessageForm(forms.ModelForm):
    recipient_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Message
        fields = ['body']
    
    def save(self, commit=True):
        instance = super(MessageForm, self).save(commit=False)
        recipient_id = self.cleaned_data.get('recipient_id')
        instance.recipient = CustomUser.objects.get(pk=recipient_id) # Это должно сработать правильно
        if commit:
            instance.save()
        return instance
