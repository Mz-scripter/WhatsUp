from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2}),
        }