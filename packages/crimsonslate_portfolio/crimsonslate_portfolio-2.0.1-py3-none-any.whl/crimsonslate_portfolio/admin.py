from django.contrib import admin

from .models import Media, MediaCategory, MediaSourceFile

admin.site.register(Media)
admin.site.register(MediaCategory)
admin.site.register(MediaSourceFile)
