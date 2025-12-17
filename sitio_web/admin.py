# sitio_web/admin.py

from django.contrib import admin
from .models import Profile, Project, ProjectAssignment, ProjectUpdate, Document, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'company_name')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'company_name')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'city', 'status', 'progress_percent', 'start_date', 'end_date_estimated')
    list_filter = ('status', 'city')
    search_fields = ('name', 'client__username', 'client__email', 'address', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información general', {
            'fields': ('name', 'description', 'client', 'status', 'progress_percent')
        }),
        ('Ubicación', {
            'fields': ('address', 'city')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date_estimated', 'end_date_actual')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'worker', 'assigned_at')
    list_filter = ('project', 'worker')
    search_fields = ('project__name', 'worker__username')

@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'date', 'progress_percent')
    list_filter = ('project', 'author', 'date')
    search_fields = ('project__name', 'author__username', 'comment')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'uploaded_by', 'uploaded_at', 'visible_to_client')
    list_filter = ('visible_to_client', 'uploaded_at')
    search_fields = ('title', 'project__name', 'uploaded_by__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'project', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('subject', 'body', 'sender__username', 'receiver__username')