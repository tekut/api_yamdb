from datetime import date

# Импортируем ошибку валидации.
from django.core.exceptions import ValidationError


def chek_year(value: int) -> None:
    year = date.today().year
    if value > int(year):
        raise ValidationError(
            'Год не может быть больше текущего'
        )
