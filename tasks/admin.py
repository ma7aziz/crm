from django.contrib import admin
from .models import Task, ActivityLog


class ActivityLogInline(admin.TabularInline):
    model = ActivityLog
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['user', 'action', 'note', 'timestamp']
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'priority', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority', 'assigned_to', 'created_by']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
    inlines = [ActivityLogInline]
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'action', 'timestamp']
    list_filter = ['action', 'user']
    search_fields = ['task__title', 'note', 'user__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
