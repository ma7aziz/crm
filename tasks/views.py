from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (ListView, DetailView, CreateView, 
                                 UpdateView, DeleteView, FormView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from .models import Task, ActivityLog
from .forms import TaskForm, ActivityLogForm, TaskFilterForm


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(assigned_to=self.request.user) | Q(created_by=self.request.user)
        )
        
        # Apply filters from form if present
        filter_form = TaskFilterForm(self.request.GET)
        if filter_form.is_valid():
            if filter_form.cleaned_data.get('status'):
                queryset = queryset.filter(status=filter_form.cleaned_data['status'])
            if filter_form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority=filter_form.cleaned_data['priority'])
            if filter_form.cleaned_data.get('overdue'):
                queryset = queryset.filter(due_date__lt=Task._meta.get_field('created_at').get_default(),
                                          status__in=['pending', 'in_progress'])
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TaskFilterForm(self.request.GET)
        return context


class RelatedTaskListView(TaskListView):
    def get_queryset(self):
        # Get content type from URL parameters
        content_type_id = self.kwargs.get('content_type_id')
        object_id = self.kwargs.get('object_id')
        
        # Filter by related object
        return Task.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related object to context
        content_type = get_object_or_404(ContentType, id=self.kwargs.get('content_type_id'))
        related_object = content_type.get_object_for_this_type(id=self.kwargs.get('object_id'))
        context['related_object'] = related_object
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add activity log form to context
        context['activity_form'] = ActivityLogForm(user=self.request.user, task=self.object)
        # Check permissions
        task = self.get_object()
        context['can_edit'] = self.request.user == task.assigned_to or self.request.user == task.created_by
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Set created_by to current user
        form.instance.created_by = self.request.user
        
        # If no assigned_to is specified, assign to self
        if not form.instance.assigned_to:
            form.instance.assigned_to = self.request.user
        
        # Handle related object if present in URL
        if 'content_type_id' in self.kwargs and 'object_id' in self.kwargs:
            content_type = get_object_or_404(ContentType, id=self.kwargs['content_type_id'])
            form.instance.content_type = content_type
            form.instance.object_id = self.kwargs['object_id']
        
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log form errors for debugging
        print(f"Form errors: {form.errors}")
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def test_func(self):
        # Only assigned_to or created_by can edit
        task = self.get_object()
        return self.request.user == task.assigned_to or self.request.user == task.created_by
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Create activity log for status changes
        if form.instance.pk:
            original_task = Task.objects.get(pk=form.instance.pk)
            if original_task.status != form.cleaned_data['status']:
                ActivityLog.objects.create(
                    task=form.instance,
                    user=self.request.user,
                    action='status_change',
                    note=f"Status changed from {original_task.get_status_display()} to {form.instance.get_status_display()}"
                )
            if original_task.assigned_to != form.cleaned_data['assigned_to']:
                ActivityLog.objects.create(
                    task=form.instance,
                    user=self.request.user,
                    action='reassigned',
                    note=f"Reassigned from {original_task.assigned_to} to {form.instance.assigned_to}"
                )
        
        messages.success(self.request, "Task updated successfully.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Log form errors for debugging
        print(f"Form errors: {form.errors}")
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, "Task updated successfully.")
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def test_func(self):
        # Only assigned_to or created_by can delete
        task = self.get_object()
        return self.request.user == task.assigned_to or self.request.user == task.created_by


class ActivityLogCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ActivityLog
    form_class = ActivityLogForm
    http_method_names = ['post']
    
    def test_func(self):
        # Only assigned_to or created_by can add activity logs
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        return self.request.user == task.assigned_to or self.request.user == task.created_by
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['task'] = get_object_or_404(Task, pk=self.kwargs['task_id'])
        return kwargs
    
    def form_valid(self, form):
        # Set task and user
        form.instance.task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        form.instance.user = self.request.user
        form.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            activity = {
                'id': form.instance.id,
                'user': form.instance.user.get_full_name() or form.instance.user.username,
                'action': form.instance.action,
                'note': form.instance.note,
                'timestamp': form.instance.timestamp.strftime("%b %d, %Y %H:%M"),
                'action_display': form.instance.get_action_display() if hasattr(form.instance, 'get_action_display') else form.instance.action,
            }
            
            # Render the activity HTML
            html = render_to_string('tasks/includes/activity_item.html', 
                                   {'log': form.instance})
            
            return JsonResponse({
                'success': True,
                'message': 'Activity added successfully',
                'activity': activity,
                'html': html
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return form errors as JSON
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json(),
                'message': 'Please correct the errors below.'
            }, status=400)
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.kwargs['task_id']})


def complete_task(request, pk):
    """View for quickly marking a task as completed"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check permissions
    if request.user != task.assigned_to and request.user != task.created_by:
        messages.error(request, "You don't have permission to complete this task.")
        return redirect('tasks:task_detail', pk=pk)
    
    # Update status
    original_status = task.get_status_display()
    task.status = 'completed'
    task.save()
    
    # Create activity log
    ActivityLog.objects.create(
        task=task,
        user=request.user,
        action='status_change',
        note=f"Status changed from {original_status} to Completed"
    )
    
    messages.success(request, "Task marked as completed!")
    return redirect('tasks:task_detail', pk=pk)
