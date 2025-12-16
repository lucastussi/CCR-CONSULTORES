# sitio_web/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Página pública
    path('', views.home, name='home'),
    
    # Autenticación
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Dashboard (común para todos los roles)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Vistas de trabajador
    path('worker/project/<int:project_id>/', views.worker_project_detail, name='worker_project_detail'),
    path('worker/project/<int:project_id>/add-update/', views.worker_add_update, name='worker_add_update'),
    
    # Vistas de cliente
    path('client/project/<int:project_id>/', views.client_project_detail, name='client_project_detail'),
    path('client/project/<int:project_id>/send-message/', views.client_send_message, name='client_send_message'),
    path('client/inbox/', views.client_inbox, name='client_inbox'),
    
    # Vistas de staff (admin/worker)
    path('staff/inbox/', views.staff_inbox, name='staff_inbox'),
    path('staff/message/<int:message_id>/reply/', views.staff_reply_message, name='staff_reply_message'),
]