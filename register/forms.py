from django.contrib.auth.forms import UserCreationForm

from register.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'currency_type']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['currency_type'].widget.attrs.update({"class": "form-control"})

