from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


from .model import resumes

class resumesFroms(forms.ModelForm):
    class Meta:
        model = resumes
        fields = ('resname','respdf')
       

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']