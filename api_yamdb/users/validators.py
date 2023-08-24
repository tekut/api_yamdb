from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]+\z',
    message = 'Имя содержит недопустимые символы'
