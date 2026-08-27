from django.contrib import admin

from apps.services.models import Service


# Register your models here.



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)