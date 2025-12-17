# sitio_web/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ProjectUpdate, Message, Document, Profile


class ProjectUpdateForm(forms.ModelForm):
    """
    Formulario para que el trabajador registre una actualización de avance
    de un proyecto (porcentaje, comentario e imagen).
    Usa el campo 'comment' tal como está en tu modelo.
    """
    class Meta:
        model = ProjectUpdate
        fields = ['progress_percent', 'comment', 'image']
        widgets = {
            'progress_percent': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'step': 0.01,
                'class': 'form-control',
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe el avance realizado...',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'progress_percent': 'Porcentaje de avance (%)',
            'comment': 'Comentarios',
            'image': 'Imagen (opcional)',
        }

    def clean_progress_percent(self):
        value = self.cleaned_data['progress_percent']
        if value < 0 or value > 100:
            raise forms.ValidationError("El porcentaje debe estar entre 0 y 100.")
        return value


class MessageForm(forms.ModelForm):
    """
    Formulario para que el cliente envíe un mensaje sobre un proyecto.
    """
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'placeholder': 'Asunto del mensaje',
                'class': 'form-control',
            }),
            'body': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe tu mensaje aquí...',
                'class': 'form-control',
            }),
        }
        labels = {
            'subject': 'Asunto',
            'body': 'Mensaje',
        }


class MessageReplyForm(forms.ModelForm):
    """
    Formulario para que el staff responda a un mensaje existente (solo cuerpo).
    """
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe tu respuesta al cliente aquí...',
                'class': 'form-control',
            }),
        }
        labels = {
            'body': 'Respuesta',
        }


class DocumentForm(forms.ModelForm):
    """
    Formulario para que el staff (ADMIN/WORKER) suba documentos de proyecto.
    Sin campo 'description', tal como tenías antes.
    """
    class Meta:
        model = Document
        fields = ['title', 'file', 'visible_to_client']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Nombre del documento',
                'class': 'form-control',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'visible_to_client': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'title': 'Título',
            'file': 'Archivo',
            'visible_to_client': '¿Visible para el cliente?',
        }


class UserRegisterForm(UserCreationForm):
    """
    Formulario de registro de nuevos usuarios.
    Por defecto se crea con rol CLIENT.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Crear perfil con rol CLIENT por defecto
            Profile.objects.get_or_create(user=user, defaults={'role': 'CLIENT'})
        return user

class UserRoleForm(forms.ModelForm):
    """
    Formulario para que el ADMIN cambie el rol de un usuario.
    """
    class Meta:
        model = Profile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'role': 'Rol del usuario',
        }