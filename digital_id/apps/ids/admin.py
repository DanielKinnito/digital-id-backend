from django.contrib import admin
from .models import ID

@admin.register(ID)
class IDAdmin(admin.ModelAdmin):
    list_display = ('user', 'id_type', 'issue_date', 'expiration_date')
    search_fields = ('user__username', 'id_type')
    list_filter = ('id_type', 'expiration_date')