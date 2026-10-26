from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

User = get_user_model()
DUPLICATE_NICKNAME = _("This nickname has already joined.")


class JoinForm(forms.Form):
    nickname = UsernameField(
        label=_("Wartally nickname"),
        max_length=150,
        validators=[User.username_validator],
        widget=forms.TextInput(
            attrs={
                "placeholder": "jtrochim",
                "autofocus": True,
                "autocomplete": "username",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        ),
    )

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        if User.objects.filter(username=nickname).exists():
            raise forms.ValidationError(DUPLICATE_NICKNAME)
        return nickname

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["nickname"],
            password=None,
            is_active=False,
        )
