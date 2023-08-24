from django.contrib import admin

# Из модуля models импортируем модель Category...
from .models import Titles, Categories, Genres

# ...и регистрируем её в админке:
admin.site.register(Titles) 
admin.site.register(Categories)
admin.site.register(Genres)
