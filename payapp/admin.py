from django.contrib import admin
from .models import (
    Transaction, TransactionRequest
)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'amount', 'created_on', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['id', 'sender', 'receiver']


class TransactionRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'amount', 'created_on', 'checked_on', 'status']
    list_filter = ['status']
    search_fields = ['id', 'sender', 'receiver']


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionRequest, TransactionRequestAdmin)
