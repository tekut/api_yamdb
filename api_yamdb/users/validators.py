from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]+$'


def no_me_as_username_allowed(username):
    if username.lower() == "me":
        raise ValidationError(
            "Использовать имя 'me' в качестве `username запрещено."
        )
