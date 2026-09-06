from django.urls import path
from . import views

urlpatterns = [
    # Auth & Trigger Execution
    path('auth/register/', views.register_view, name='auth-register'),
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    path('auth/me/', views.current_user_view, name='auth-me'),

    # Admin Matrix & Template Management
    path('matrix/', views.matrix_view, name='admin-matrix'),
    path('templates/<int:template_id>/toggle/', views.toggle_template_view, name='template-toggle'),
    path('templates/<int:template_id>/', views.update_template_view, name='template-update'),
    path('templates/<int:template_id>/test-send/', views.test_send_template_view, name='template-test-send'),

    # Web Push
    path('webpush/vapid-key/', views.vapid_public_key_view, name='webpush-vapid-key'),
    path('webpush/subscribe/', views.subscribe_web_push_view, name='webpush-subscribe'),

    # Logs
    path('logs/', views.notification_logs_view, name='notification-logs'),
]
