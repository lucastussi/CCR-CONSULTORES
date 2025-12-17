# sitio_web/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Página pública
    path('', views.home, name='home'),
    
    # Autenticación
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    
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

    # Documentos de proyecto (staff)
    path('staff/project/<int:project_id>/documents/', views.staff_project_documents, name='staff_project_documents'),
    path('staff/project/<int:project_id>/documents/upload/', views.staff_upload_document, name='staff_upload_document'),

    # Gestión de usuarios (solo admin)
    # Gestión de usuarios (solo admin, rutas propias de la app, no del admin de Django)
    path('panel/usuarios/', views.admin_user_management, name='admin_user_management'),
    path('panel/usuarios/<int:user_id>/editar/', views.admin_edit_user_role, name='admin_edit_user_role'),
    path('panel/usuarios/<int:user_id>/eliminar/', views.admin_delete_user, name='admin_delete_user'),
]