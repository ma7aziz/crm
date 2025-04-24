from django.contrib import admin
from .models import Customer, Interaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'created_at', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email', 'company')
    date_hierarchy = 'created_at'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'interaction_type', 'date', 'created_by')
    list_filter = ('interaction_type', 'date', 'created_by')
    search_fields = ('customer__first_name', 'customer__last_name', 'notes')
    date_hierarchy = 'date'
