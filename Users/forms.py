from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='الصورة الشخصية', required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AdminUserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    role = forms.ChoiceField(choices=[('Admin', 'Admin'), ('Operator', 'Operator'), ('Viewer', 'Viewer')])
    is_active = forms.BooleanField(required=False, initial=True, label='نشط')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password1', 'password2']


class AdminUserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=[('Admin', 'Admin'), ('Operator', 'Operator'), ('Viewer', 'Viewer')])
    is_active = forms.BooleanField(required=False, label='نشط')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']
