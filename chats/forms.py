from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['is_anonymous']
        widgets = {
            'is_anonymous': forms.CheckboxInput(),
        }
    
    is_anonymous = forms.BooleanField(label="Send anonymously", required=False)