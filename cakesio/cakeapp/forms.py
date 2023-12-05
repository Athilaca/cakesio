from django import forms
from .models import CustomUser

class ImageForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=('profile_pic',)
