from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    
    # GenericForeignKey to relate this task to Lead, Opportunity, or Customer
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_to = GenericForeignKey('content_type', 'object_id')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-due_date', 'priority']
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != 'completed'


class TaskManager(models.Manager):
    def get_overdue_tasks(self):
        return self.filter(due_date__lt=timezone.now(), status__in=['pending', 'in_progress'])


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('comment', 'Comment'),
        ('status_change', 'Status Change'),
        ('reassigned', 'Reassigned'),
        ('priority_change', 'Priority Change'),
        ('due_date_change', 'Due Date Change'),
    )
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.task.title}"
    
    class Meta:
        ordering = ['-timestamp']
