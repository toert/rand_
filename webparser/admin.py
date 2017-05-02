from django.contrib import admin

from .models import Ad, AdAttribute


class AdAttributeInline(admin.TabularInline):
    model = AdAttribute


class AdAdmin(admin.ModelAdmin):
    exclude = ('price', )
    inlines = [AdAttributeInline, ]



admin.site.register(Ad, AdAdmin)
