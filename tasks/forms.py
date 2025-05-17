from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from .models import Task, ActivityLog
from django.utils import timezone
from core.models import Customer

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Select the due date and time for this task"
    )
    
    # Add a field for selecting a customer to relate this task to
    related_customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        label="Related Customer",
        help_text="Associate this task with a customer"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        
        # Get content_type and object_id if provided
        self.content_type_id = kwargs.pop('content_type_id', None)
        self.object_id = kwargs.pop('object_id', None)
        
        super(TaskForm, self).__init__(*args, **kwargs)
        
        # Filter assigned_to field to show only active users
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        
        # If we have a content_type and object_id, pre-select related_customer
        if self.content_type_id and self.object_id:
            content_type = ContentType.objects.get(id=self.content_type_id)
            if content_type.model == 'customer':
                try:
                    customer = Customer.objects.get(id=self.object_id)
                    self.fields['related_customer'].initial = customer
                except Customer.DoesNotExist:
                    pass
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'priority', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 10:
            raise forms.ValidationError("Description should provide more details (at least 10 characters)")
        return description
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        print(due_date)
        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Due date cannot be in the past")
        return due_date
        
    def save(self, commit=True):
        instance = super(TaskForm, self).save(commit=False)
        
        # If content_type_id and object_id are already set from view, use those
        if hasattr(self, 'content_type_id') and hasattr(self, 'object_id') and self.content_type_id and self.object_id:
            instance.content_type_id = self.content_type_id
            instance.object_id = self.object_id
        # Otherwise use the selected customer if provided
        elif self.cleaned_data.get('related_customer'):
            customer = self.cleaned_data['related_customer']
            content_type = ContentType.objects.get_for_model(Customer)
            instance.content_type = content_type
            instance.object_id = customer.id
            
        if commit:
            instance.save()
        return instance


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All')] + list(Task.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    overdue = forms.BooleanField(required=False)
    

class ActivityLogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.task = kwargs.pop('task', None)
        super(ActivityLogForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = ActivityLog
        fields = ['action', 'note']
        
    
    def clean_note(self):
        note = self.cleaned_data.get('note')
        if note and len(note.strip()) < 5:
            raise forms.ValidationError("Please provide a more detailed note")
        return note
    
    def save(self, commit=True):
        instance = super(ActivityLogForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if self.task:
            instance.task = self.task
        if commit:
            instance.save()
        return instance
