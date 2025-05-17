from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task List Views
    path('', views.TaskListView.as_view(), name='task_list'),
    path('related/<int:content_type_id>/<int:object_id>/', 
         views.RelatedTaskListView.as_view(), name='related_task_list'),
    
    # Task CRUD Views
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('create/<int:content_type_id>/<int:object_id>/', 
         views.TaskCreateView.as_view(), name='task_create_related'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Task Action Views
    path('<int:pk>/complete/', views.complete_task, name='task_complete'),
    
    # Activity Log Views
    path('<int:task_id>/activity/', views.ActivityLogCreateView.as_view(), name='activity_create'),
]
