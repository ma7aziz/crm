from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Customer management URLs
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/create/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update_view, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
    
    # Interaction management URLs
    path('interactions/', views.interaction_list_view, name='interaction_list'),
    path('interactions/<int:pk>/', views.interaction_detail_view, name='interaction_detail'),
    path('interactions/create/', views.interaction_create_view, name='interaction_create'),
    path('customers/<int:customer_id>/interactions/create/', views.interaction_create_view, name='customer_interaction_create'),
    path('interactions/<int:pk>/update/', views.interaction_update_view, name='interaction_update'),
    path('interactions/<int:pk>/delete/', views.interaction_delete_view, name='interaction_delete'),
    
    # User management URLs (admin only)
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('users/<int:pk>/update/', views.user_update_view, name='user_update'),
]