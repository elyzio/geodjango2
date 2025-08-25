from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
# from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthForm
from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 
                #   'email', 
                  'password1', 
                  'password2'
                  ]
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control rounded-0',
                'placeholder': 'Enter your username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control rounded-0',
            'placeholder': 'Enter your password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control rounded-0',
            'placeholder': 'Confirm your password',
        })
        


class CustomAuthenticationForm(forms.Form):
    """
    Custom authentication form that mimics Django's built-in but allows for extension
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control rounded-0', 'placeholder': 'Enter your username'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','class': 'form-control rounded-0', 'placeholder': 'Enter your password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter correct credentials. Both fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        Initialize the form with optional request object
        """
        self.request = request
        self.user_cache = None  # Will store authenticated user
        super().__init__(*args, **kwargs)

        # Set username field parameters from User model
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        
        # Configure username field
        self.fields['username'].max_length = self.username_field.max_length or 254
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        """
        Main validation method that handles authentication
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Verify the user is allowed to login (active status)
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        """
        Return the authenticated user instance
        """
        return self.user_cache

    def get_invalid_login_error(self):
        """
        Return standardized invalid login error
        """
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
        )
    