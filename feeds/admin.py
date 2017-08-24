from django.contrib import admin

from . import models

admin.site.register(models.Site)
admin.site.register(models.Feed)
admin.site.register(models.Tag)
admin.site.register(models.Error)
admin.site.register(models.Keyword)
