from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2}),
            'is_anonymous': forms.CheckboxInput(),
        }
    
    is_anonymous = forms.BooleanField(label="Send anonymously", required=False)