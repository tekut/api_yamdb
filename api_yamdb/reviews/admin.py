from django.contrib import admin

from .models import Review, Comment, Title, Categories, Genres


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'title', 'score')


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment)
admin.site.register(Title)
admin.site.register(Categories)
admin.site.register(Genres)
