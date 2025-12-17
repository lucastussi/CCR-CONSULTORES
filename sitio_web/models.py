# sitio_web/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

# --- Constantes y Choices ---
ROLE_CHOICES = (
    ('ADMIN', 'Administrador'),
    ('WORKER', 'Trabajador'),
    ('CLIENT', 'Cliente'),
)

PROJECT_STATUS_CHOICES = (
    ('PENDIENTE', 'Pendiente'),
    ('EN_PROGRESO', 'En Progreso'),
    ('COMPLETADO', 'Completado'),
    ('PAUSADO', 'Pausado'),
    ('CANCELADO', 'Cancelado'),
)

# --- Modelos ---

class Profile(models.Model):
    """
    Extiende el modelo User de Django para añadir información específica
    y el rol del usuario en la plataforma.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True,
                                    help_text="Nombre de la empresa si el usuario es un cliente.")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Project(models.Model):
    """
    Representa un proyecto de construcción o servicio que CCR Consultores ofrece.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='client_projects',
                               limit_choices_to={'profile__role': 'CLIENT'})
    
    start_date = models.DateField()
    end_date_estimated = models.DateField(blank=True, null=True)
    end_date_actual = models.DateField(blank=True, null=True)
    
    address = models.CharField(max_length=255, help_text="Dirección completa de la obra.")
    city = models.CharField(max_length=100, help_text="Ciudad donde se ubica la obra.")
    
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='PENDIENTE')
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                           help_text="Porcentaje de avance del proyecto (0.00 a 100.00).")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_projects',
                                   limit_choices_to={'profile__role__in': ['ADMIN', 'WORKER']})

    def __str__(self):
        return self.name

class ProjectAssignment(models.Model):
    """
    Asigna trabajadores a proyectos específicos.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_projects',
                               limit_choices_to={'profile__role': 'WORKER'})
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'worker')

    def __str__(self):
        return f"{self.worker.username} asignado a {self.project.name}"

def project_update_image_path(instance, filename):
    """
    Define la ruta donde se guardarán las imágenes de las actualizaciones de proyecto.
    """
    project_name = instance.project.name.replace(" ", "_")
    return os.path.join('project_updates', project_name, filename)

class ProjectUpdate(models.Model):
    """
    Registra las actualizaciones de progreso de un proyecto.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='project_updates_made',
                               limit_choices_to={'profile__role': 'WORKER'})
    
    date = models.DateField(auto_now_add=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2,
                                           help_text="Porcentaje de avance en esta actualización.")
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=project_update_image_path, blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Actualización de {self.project.name} al {self.date}: {self.progress_percent}%"

def project_document_path(instance, filename):
    """
    Define la ruta donde se guardarán los documentos del proyecto.
    """
    project_name = instance.project.name.replace(" ", "_")
    return os.path.join('project_documents', project_name, filename)

class Document(models.Model):
    """
    Almacena documentos relacionados con un proyecto.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=project_document_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    visible_to_client = models.BooleanField(default=True,
                                            help_text="Indica si el cliente puede ver este documento.")

    def __str__(self):
        return f"Documento '{self.title}' para {self.project.name}"

class Message(models.Model):
    """
    Sistema de mensajería interna.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='received_messages',
                                 help_text="Si es nulo, se asume que es para el equipo administrativo.")
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"De {self.sender.username} a {self.receiver.username if self.receiver else 'Equipo Admin'}: {self.subject[:50] if self.subject else 'Sin asunto'}..."